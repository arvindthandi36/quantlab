'use strict';
const $ = id => document.getElementById(id);
const esc = v => String(v ?? '').replace(/[&<>"']/g, x => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));
const gbp = v => v == null ? '—' : '£' + Number(v).toFixed(5).replace(/0+$/, '').replace(/\.$/, '.00');
const num = v => v == null ? '—' : Number(v).toLocaleString('en-GB', {maximumFractionDigits:5});
const clock = us => {const ms=Math.floor(us/1000), sec=Math.floor(ms/1000);return `09:${String(30+Math.floor(sec/60)).padStart(2,'0')}:${String(sec%60).padStart(2,'0')}.${String(ms%1000).padStart(3,'0')}`;};
const signClass = value => Number(value) < 0 ? 'negative' : Number(value) > 0 ? 'positive' : '';
const kv = (k,v) => `<div class="key-value"><span>${esc(k)}</span><strong>${esc(v)}</strong></div>`;
const table = (heads,rows) => rows.length ? `<table><thead><tr>${heads.map(h=>`<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map(c=>`<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table>` : '<p class="empty">Nothing to show yet.</p>';
let state, token, side='buy', busy=false, selectedOrder=null, latest=-1;
function notice(message,error=false){$('notice').textContent=message;$('notice').classList.toggle('error',error);}
async function command(kind,payload={}){
  if(busy)return;
  busy=true; lockControls();
  try{
    const response=await fetch('/api/command',{method:'POST',headers:{'Content-Type':'application/json','X-QuantLab-Token':token},body:JSON.stringify({kind,payload})});
    const body=await response.json();
    if(!response.ok)throw Error(body.error || 'Command failed');
    if(body.result.order_id)selectedOrder=body.result.order_id;
    render(body.state,true); notice(body.result.message,!body.result.ok);
    document.dispatchEvent(new CustomEvent('quantlab-public-state',{detail:body.state}));
  }catch(error){notice(error.message,true);}
  finally{busy=false;lockControls();}
}
function lockControls(){
  const closed=state?.status==='ended'||state?.status==='failed'||state?.replay;
  for(const id of ['submit-order','cancel-all','quote-form','learn']){
    const el=$(id);if(el.tagName==='FORM'){el.querySelectorAll('button').forEach(b=>b.disabled=busy||closed);}else el.disabled=busy||closed;
  }
  ['run','end'].forEach(id=>$(id).disabled=busy||closed);
  ['step-event','step-time'].forEach(id=>$(id).disabled=busy||closed||state?.status==='running');
  document.querySelectorAll('[data-cancel]').forEach(b=>b.disabled=busy||closed);
  document.querySelectorAll('#new-session button').forEach(b=>b.disabled=busy);
}
function chooseSide(value){side=value;$('buy').setAttribute('aria-pressed',String(side==='buy'));$('sell').setAttribute('aria-pressed',String(side==='sell'));$('submit-order').textContent=`Submit ${side}`;$('submit-order').className=`submit-${side}`;}
function orderType(){const isLimit=$('order-type').value==='limit';$('limit-label').hidden=!isLimit;$('limit-price').required=isLimit;$('order-hint').textContent=isLimit?'Your price is a boundary. If it cannot trade now, the remaining units join the FIFO queue.':'Your order takes the best opposite prices first, then moves through deeper levels if needed.';}
function depth(levels){return '<div class="depth-head"><span>Price (£)</span><span>Quantity</span><span>Orders</span></div>'+levels.slice(0,8).map(l=>`<details class="level"><summary><span>${esc(Number(l.price).toFixed(2))}${l.own_quantity?' ●':''}</span><span>${l.quantity}</span><span>${l.order_count}</span></summary>${l.queue.map((o,i)=>`<p class="${o.yours?'mine':''}">${i+1}. ${esc(o.id)}${o.yours?' · you':''} · ${o.quantity} units</p>`).join('')}</details>`).join('')+(levels.length?'':'<p class="empty">No resting orders</p>');}
function render(next,force=false){
  if(!force&&next.server_revision===latest)return;
  if(next.server_revision<latest)return;
  latest=next.server_revision;state=next;
  $('session-title').textContent=next.scenario+' · '+({free:'Free trading',manual_maker:'Manual market making',challenge:'Scenario challenge'}[next.mode]);
  $('objective').textContent=next.objective;
  $('status').textContent=next.replay?'REPLAY':next.status.toUpperCase();$('status').classList.toggle('running',next.status==='running'&&!next.replay);
  $('clock').textContent=clock(next.time_us);$('progress').textContent=`${(next.time_us/1e6).toFixed(2)} / ${next.duration_us/1e6}s · ${next.public_event} public actions`;
  $('run').textContent=next.status==='running'?'Pause':next.time_us?'Resume':'Start';
  const a=next.account;
  const metrics=[['Position',num(a.position),`Limit ±${a.position_limit} units`],['Net P&L',gbp(a.total_pnl),'Realised + unrealised'],['Cash',gbp(a.cash),'After all execution fees'],['Realised P&L',gbp(a.realised),'FIFO · fees expensed'],['Unrealised P&L',gbp(a.unrealised),'Open lots at public mark'],['Average entry',gbp(a.average_entry),'Remaining FIFO lots']];
  $('account').innerHTML=metrics.map(([label,value,note])=>`<div class="metric"><span>${esc(label)}</span><strong class="${label.includes('P&L')?signClass(a[{ 'Net P&L':'total_pnl','Realised P&L':'realised','Unrealised P&L':'unrealised'}[label]]):''}">${esc(value)}</strong><small>${esc(note)}</small></div>`).join('');
  $('prices').innerHTML=[['Last trade',next.last_price],['Best bid',next.best_bid],['Best ask',next.best_ask],['Spread',next.spread]].map(([k,v])=>`<div><span>${esc(k)}</span><strong>${esc(gbp(v))}</strong></div>`).join('');
  // Preserve expanded depth levels across public updates.
  const opened=new Set([...document.querySelectorAll('.level[open]')].map(el=>el.parentElement.id+':'+el.querySelector('summary span').textContent.split(' ●')[0]));
  $('bids').innerHTML=depth(next.bids);$('asks').innerHTML=depth(next.asks);
  document.querySelectorAll('.level').forEach(el=>{el.open=opened.has(el.parentElement.id+':'+el.querySelector('summary span').textContent.split(' ●')[0]);});
  $('capacity').textContent=`Available: buy ${a.buy_capacity} · sell ${a.sell_capacity} units`;
  $('quote-controls').hidden=next.mode!=='manual_maker';
  $('risk').innerHTML=kv('Position / limit',`${a.position} / ±${a.position_limit}`)+kv('Public reference',gbp(next.reference))+kv('Reference source',next.reference_source)+kv('Visible book mid',gbp(next.mid))+kv('Signed notional exposure',gbp(a.exposure))+kv('Drawdown now',gbp(a.drawdown))+kv('Maximum drawdown',gbp(a.max_drawdown))+kv('Fees paid',gbp(a.fees));
  $('orders').innerHTML=table(['Order / details','Side','Type / limit','Original','Filled','Remaining','Status','VWAP','Action'],next.orders.slice().reverse().map(o=>[
    `<button data-order="${esc(o.order_id)}">${esc(o.order_id)}</button>`,esc(o.side),esc(o.type+(o.price?' '+gbp(o.price):'')),o.original,o.filled,o.remaining,esc(o.status),esc(gbp(o.vwap)),o.remaining?`<button data-cancel="${esc(o.order_id)}">Cancel</button>`:'—']));
  showOrder();
  $('trades').innerHTML=table(['Time','Order','Side','Price','Units','Fee','Role'],next.trades.slice(-30).reverse().map(t=>[clock(t.time_us),esc(t.order_id),esc(t.side),gbp(t.price),t.quantity,gbp(t.fee),esc(t.role)]));
  $('tape').innerHTML=table(['Time','Aggressor','Price','Units'],next.tape.slice(-12).reverse().map(t=>[clock(t.time_us),esc(t.side),gbp(t.price),t.quantity]));
  $('timeline').innerHTML=next.timeline.slice().reverse().map(t=>`<p><time>${clock(t.time_us)} · action ${t.event} · position ${t.position} · ref ${gbp(t.reference)}</time>${esc(t.message)}</p>`).join('')||'<p class="empty">Your market is paused and ready.</p>';
  $('markouts').innerHTML=table(['Trade / role','Horizon','Mark / status'],next.markouts.slice(-9).reverse().map(m=>[`${m.trade_id} · ${esc(m.role)}`,m.horizon,esc(m.status==='matured'?gbp(m.value):m.status)]));
  const q=next.quant;
  $('quant').innerHTML=kv('Top-5 depth imbalance',num(q.depth_imbalance_top_5))+kv('Last log return',num(q.last_log_return))+kv('Trade-window realised volatility',num(q.realised_volatility_trade_window))+kv('Return observations',q.return_observations)+kv('Recent buy / sell executed units',`${q.aggressor_buy_volume} / ${q.aggressor_sell_volume}`)+kv('Flow imbalance',num(q.flow_imbalance));
  $('glossary').innerHTML=Object.entries(next.glossary).map(([k,v])=>`<div><strong>${esc(k)}</strong><p>${esc(v)}</p></div>`).join('');
  const tutor=next.tutor;
  $('tutor').innerHTML=tutor.stage==='idle'?'':`<p><strong>${esc(tutor.stage.toUpperCase())}</strong></p><p>${esc(tutor.question)}</p>`+(tutor.stage==='predict'?`<button data-answer="yes">Yes</button><button data-answer="no">No</button><p>${esc(tutor.hint)}</p>`:`<p>${esc(tutor.instruction)}</p><p>${esc(tutor.result)}</p><p>${esc(tutor.explanation)}</p>`);
  $('report-panel').hidden=!next.report;
  if(next.report)showReport(next.report, next.saved_path);
  $('report-panel').querySelector('a').hidden=next.replay;
  $('replay-controls').hidden=!next.replay;
  if(next.replay)$('replay-position').textContent=` Frame ${next.frame_index+1} of ${next.frame_count}`;
  if(next.server_error)notice(next.server_error,true);
  viewMode();charts();lockControls();
}
function showOrder(){
  const o=state?.orders.find(o=>o.order_id===selectedOrder);
  $('order-detail').innerHTML=o?`<h3>${esc(o.order_id)} · Execution breakdown</h3>`+kv('VWAP',gbp(o.vwap))+kv('Exact VWAP (ticks)',o.vwap==null?'—':o.vwap_exact_ticks)+table(['Time','Price','Quantity','Fee','Role'],o.fills.map(f=>[clock(f.time_us),gbp(f.price),f.quantity,gbp(f.fee),esc(f.role)])):'<p class="fine">Choose an order ID to inspect every fill and its exact VWAP.</p>';
}
function showReport(r, savedPath){
  const performance=kv('Final net P&L',gbp(r.final_pnl))+kv('Realised / unrealised',gbp(r.realised_pnl)+' / '+gbp(r.unrealised_pnl))+kv('Maximum drawdown',gbp(r.maximum_drawdown))+kv('Turnover',gbp(r.turnover))+kv('Executions / units',`${r.trade_count} / ${r.filled_units}`);
  const execution=kv('Buy / sell VWAP',gbp(r.buy_vwap)+' / '+gbp(r.sell_vwap))+kv('Pooled execution VWAP',gbp(r.pooled_execution_vwap))+kv('Fees',gbp(r.fees))+kv('Limit fill rate (filled / submitted)',r.limit_fill_rate==null?'—':num(r.limit_fill_rate*100)+'%')+kv('Orders with cancelled quantity',r.cancelled_orders)+kv('Orders ever partially filled',r.orders_ever_partially_filled);
  const position=kv('Maximum long / short units',`${r.max_long_units} / ${r.max_short_units}`)+kv('Time-average absolute position',num(r.average_absolute_position))+kv('Time-average absolute notional',gbp(r.average_absolute_notional));
  $('report').innerHTML=`<div class="report-grid"><div><h3>Performance</h3>${performance}</div><div><h3>Execution</h3>${execution}</div><div><h3>Position</h3>${position}</div></div><p class="fine">${esc(r.valuation_note)}</p>`+(r.challenge?'<h3>Challenge criteria</h3>'+kv('Full duration completed',r.challenge.completed_duration?'Yes':'No')+kv('Target position',r.challenge.target_position??'No fixed target')+kv('Target met',r.challenge.target_met==null?'—':r.challenge.target_met?'Yes':'No')+kv('Within drawdown budget',r.challenge.drawdown_within_budget?'Yes':'No'):'')+'<details><summary>Complete decision timeline</summary><div class="timeline">'+r.decisions.map(d=>`<p><time>${clock(d.time_us)} · reference ${gbp(d.reference)} · position ${d.position}</time>${esc(d.message)}${d.observed_before?'<br>Before: bid '+gbp(d.observed_before.best_bid)+' · ask '+gbp(d.observed_before.best_ask)+' · position '+d.observed_before.position:''}</p>`).join('')+'</div></details><details><summary>All provider / aggressor markouts</summary>'+table(['Trade','Role','Horizon (events)','Status','Mark (£ per unit)'],r.markouts.map(m=>[m.trade_id,esc(m.role),m.horizon,esc(m.status),gbp(m.value)]))+'</details>'+(savedPath?'<p class="fine">Automatically saved: '+esc(savedPath)+'</p>':'');
}
function viewMode(){const beginner=$('view').value==='beginner';document.querySelectorAll('.beginner').forEach(e=>e.hidden=!beginner);document.querySelectorAll('.quant-only').forEach(e=>e.hidden=beginner);}
function plot(id,points,label,color,stepped=false){
  const canvas=$(id),ratio=window.devicePixelRatio||1,w=canvas.clientWidth;
  const h=Number(canvas.dataset.plotHeight||canvas.getAttribute('height'));
  canvas.dataset.plotHeight=String(h);
  canvas.width=w*ratio;canvas.height=h*ratio;canvas.style.height=h+'px';
  const ctx=canvas.getContext('2d');ctx.scale(ratio,ratio);ctx.clearRect(0,0,w,h);
  ctx.font='11px system-ui';ctx.fillStyle='#748490';
  if(!points.length){ctx.fillText('No trades yet. Place an order or step.',12,50);return;}
  const left=68,right=w-15,top=15,bottom=h-27;
  let lo=Math.min(...points.map(p=>p[1])),hi=Math.max(...points.map(p=>p[1]));
  if(hi===lo){hi+=.01;lo-=.01;}const pad=(hi-lo)*.1;lo-=pad;hi+=pad;
  const end=Math.max(state.time_us,points.at(-1)[0],1);
  const x=t=>left+t/end*(right-left),y=v=>bottom-(v-lo)/(hi-lo)*(bottom-top);
  for(let i=0;i<4;i++){const value=lo+(hi-lo)*i/3,py=y(value);ctx.strokeStyle='#e7edf1';ctx.beginPath();ctx.moveTo(left,py);ctx.lineTo(right,py);ctx.stroke();ctx.fillStyle='#748490';ctx.fillText(value.toFixed(label==='Units'?1:3),3,py+4);}
  ctx.fillText('0s',left,bottom+20);ctx.fillText((end/1e6).toFixed(2)+'s',right-45,bottom+20);
  ctx.strokeStyle=color;ctx.lineWidth=2;ctx.beginPath();points.forEach((p,i)=>{if(!i)ctx.moveTo(x(p[0]),y(p[1]));else{if(stepped)ctx.lineTo(x(p[0]),y(points[i-1][1]));ctx.lineTo(x(p[0]),y(p[1]));}});ctx.stroke();
  ctx.fillStyle=color;points.forEach(p=>{ctx.beginPath();ctx.arc(x(p[0]),y(p[1]),2.3,0,Math.PI*2);ctx.fill();});
}
function charts(){if(!state)return;plot('price-chart',state.tape.map(t=>[t.time_us,Number(t.price)]),'GBP','#254c94');const kind=$('chart-kind').value;plot('account-chart',state.history.map(t=>[t.time_us,Number(t[kind])]),kind==='position'?'Units':'GBP','#096c63',true);}
$('buy').onclick=()=>chooseSide('buy');$('sell').onclick=()=>chooseSide('sell');$('order-type').onchange=orderType;
$('order-form').onsubmit=e=>{e.preventDefault();const p={side,order_type:$('order-type').value,quantity:$('quantity').valueAsNumber};if(p.order_type==='limit')p.price=$('limit-price').value;command('order',p);};
$('run').onclick=()=>command(state.status==='running'?'pause':state.time_us?'resume':'start');
$('step-event').onclick=()=>command('step_event');$('step-time').onclick=()=>command('step_interval',{delta_us:1_000_000});$('end').onclick=()=>command('end');$('cancel-all').onclick=()=>command('cancel_all');
$('orders').onclick=e=>{const b=e.target.closest('button');if(b?.dataset.cancel)command('cancel',{order_id:b.dataset.cancel});if(b?.dataset.order){selectedOrder=b.dataset.order;showOrder();}};
$('quote-form').onsubmit=e=>{e.preventDefault();command('quotes',{bid_distance:$('bid-distance').value,ask_distance:$('ask-distance').value,bid_size:$('bid-size').valueAsNumber,ask_size:$('ask-size').valueAsNumber,shift:$('quote-shift').value});};
$('scenario').onchange=()=>{$('initial-position').disabled=$('scenario').value!=='position';};
$('new-session').onsubmit=async e=>{e.preventDefault();selectedOrder=null;await command('new',{key:$('scenario').value,mode:$('mode').value,seed:$('seed').valueAsNumber,position_limit:$('position-limit').valueAsNumber,duration_seconds:$('duration').valueAsNumber,initial_position:$('scenario').value==='position'?$('initial-position').valueAsNumber:0});if(state?.status==='paused')$('setup').open=false;};
$('learn').onclick=()=>command('learn');$('tutor').onclick=e=>{if(e.target.dataset.answer)command('predict',{answer:e.target.dataset.answer});};
$('view').onchange=viewMode;$('chart-kind').onchange=charts;
$('replay-file').onchange=async e=>{const file=e.target.files[0];if(!file)return;if(file.size>20_000_000){notice('Journal is larger than the 20 MB local import limit.',true);return;}try{await command('load_replay',{journal_text:await file.text()});}catch(err){notice(err.message,true);}e.target.value='';};
$('replay-first').onclick=()=>command('replay_step',{index:0});$('replay-next').onclick=()=>command('replay_step',{index:Math.min(state.frame_index+1,state.frame_count-1)});$('replay-last').onclick=()=>command('replay_step',{index:state.frame_count-1});
document.addEventListener('keydown',e=>{if(e.ctrlKey||e.metaKey||e.altKey||e.target.closest('input,select,textarea,[contenteditable]'))return;if(e.key.toLowerCase()==='b'||e.key.toLowerCase()==='s'){e.preventDefault();chooseSide(e.key.toLowerCase()==='b'?'buy':'sell');$('quantity').focus();}});
window.addEventListener('resize',charts);
async function poll(){try{const response=await fetch('/api/state');const body=await response.json();if(!response.ok)throw Error(body.error);render(body);}catch(e){notice('Connection / session error: '+e.message,true);}}
async function start(){try{const response=await fetch('/api/bootstrap');const data=await response.json();token=data.token;$('scenario').innerHTML=data.scenarios.map(s=>`<option value="${esc(s.key)}">${esc(s.title)}</option>`).join('');orderType();await poll();setInterval(poll,500);}catch(e){notice(e.message,true);}}
start();

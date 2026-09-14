/* Presentation only. Pricing, Greeks, IV, payoff curves, hedges and accounting live in Python. */
(() => {
'use strict';
const $=id=>document.getElementById(id);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num=(v,n=4)=>v===null||v===undefined?'—':Number(v).toLocaleString('en-GB',{maximumFractionDigits:n,minimumFractionDigits:n});
const cash=v=>v===null||v===undefined?'—':(Number(v)<0?'−£'+num(-Number(v),4):'£'+num(v,4));
const heading=v=>String(v).replaceAll('_',' ');
let state,token,busy=false,expiry='',lastSelected='',researchKey='';
function message(text,error=false){$('options-message').textContent=text;$('options-message').className=error?'error':'';}
async function get(url){const r=await fetch(url);const d=await r.json();if(!r.ok)throw Error(d.error||'Local request failed');return d;}
async function command(kind,payload={}){
 if(busy){message('Please wait for the current calculation.');return;}busy=true;
 try{const r=await fetch('/api/options',{method:'POST',headers:{'Content-Type':'application/json','X-QuantLab-Token':token},body:JSON.stringify({kind,payload})});const data=await r.json();if(!r.ok)throw Error(data.error||'Options request failed');state=data.state;render();
 const result=data.result;
 message(state.save_warning || result?.message || (kind==='option_order'?`${result.filled} contract(s) filled at £${num(result.premium,6)} per unit; ${result.cancelled} cancelled. Premium cash flow ${cash(result.premium_cash_flow)}, fee ${cash(result.fee)}.`:`${heading(kind)} complete.`));
 document.dispatchEvent(new CustomEvent('quantlab-options-state',{detail:state}));return data;
 }catch(e){message(e.message,true);}finally{busy=false;}
}
function grid(items){return '<div class="result-grid">'+items.map(([a,b])=>`<div><span>${esc(a)}</span><strong>${esc(b)}</strong></div>`).join('')+'</div>';}
function table(headers,rows){return '<div class="table-scroll"><table><thead><tr>'+headers.map(x=>`<th>${esc(x)}</th>`).join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map(x=>`<td>${esc(x)}</td>`).join('')+'</tr>').join('')+'</tbody></table></div>';}
function chart(id,rows,xKey,series,{xLabel='Stock price (£)',yLabel=''}={}){
 const box=$(id);if(!rows?.length){box.innerHTML='<div class="chart-empty">No observations yet.</div>';return;}
 const good=rows.filter(r=>Number.isFinite(r[xKey]));const ys=good.flatMap(r=>series.map(s=>r[s.key])).filter(v=>v!==null&&Number.isFinite(v));
 if(!ys.length){box.innerHTML='<div class="chart-empty">Undefined at this boundary.</div>';return;}
 let xmin=Math.min(...good.map(r=>r[xKey])),xmax=Math.max(...good.map(r=>r[xKey]));let ymin=Math.min(...ys),ymax=Math.max(...ys);
 if(xmin===xmax){xmin-=.5;xmax+=.5;}if(ymin===ymax){ymin-=.5;ymax+=.5;}const margin=(ymax-ymin)*.08;ymin-=margin;ymax+=margin;
 const px=x=>50+(x-xmin)/(xmax-xmin)*485,py=y=>205-(y-ymin)/(ymax-ymin)*165;
 let svg=`<svg viewBox="0 0 560 255" role="img" aria-label="${esc(yLabel+' versus '+xLabel)}"><rect width="560" height="255" fill="#fbfdfe"/>`;
 for(let i=0;i<4;i++){const y=ymin+(ymax-ymin)*i/3;svg+=`<line x1="50" x2="535" y1="${py(y)}" y2="${py(y)}" stroke="#e1e8ed"/><text x="44" y="${py(y)+4}" text-anchor="end" font-size="11" fill="#5d727e">${esc(num(y,2))}</text>`;}
 for(let i=0;i<4;i++){const x=xmin+(xmax-xmin)*i/3;svg+=`<text x="${px(x)}" y="223" text-anchor="middle" font-size="11" fill="#5d727e">${esc(num(x,1))}</text>`;}
 series.forEach(s=>{const points=good.filter(r=>r[s.key]!==null&&Number.isFinite(r[s.key]));svg+=`<polyline fill="none" stroke="${s.color}" stroke-width="2.5" points="${points.map(r=>px(r[xKey])+','+py(r[s.key])).join(' ')}"/>`;if(points.length===1)svg+=`<circle cx="${px(points[0][xKey])}" cy="${py(points[0][s.key])}" r="3" fill="${s.color}"/>`;});
 svg+=`<text x="295" y="246" text-anchor="middle" font-size="12" fill="#425e6c">${esc(xLabel)}</text><text x="50" y="22" font-size="12" fill="#425e6c">${esc(yLabel)}</text></svg>`;
 box.innerHTML=svg+'<div class="chart-legend">'+series.map(s=>esc(s.label)).join(' · ')+'</div>';
}
function activateTab(name){document.querySelectorAll('[data-tab]').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.tab===name)));document.querySelectorAll('[data-page]').forEach(p=>p.hidden=p.dataset.page!==name);}
document.querySelectorAll('[data-tab]').forEach(b=>b.addEventListener('click',()=>activateTab(b.dataset.tab)));
function render(){
 const s=state,q=s.selected,a=s.accounts,g=s.greeks;const live=s.status==='active'&&!s.replay;
 $('options-clock').textContent=`${s.replay?'REPLAY':s.status.toUpperCase()} · day ${num(s.elapsed_days,1)} · ${s.step}/${s.steps} steps`;
 $('option-step').textContent=`Step ${num(s.step_days,2)} day(s)`;$('option-five').textContent='Advance 5 steps';
 ['option-step','option-five','option-end','option-submit','hedge-once'].forEach(id=>$(id).disabled=!live);
 $('option-submit').disabled=!live||q.expired;
 $('auto-frequency').value=String(s.auto_frequency);$('auto-frequency').disabled=!live;
 $('option-metrics').innerHTML=[['Stock reference',cash(s.spot)],['Portfolio net P&L',cash(a.total_pnl)],['Cash balance',cash(a.cash)],['Portfolio delta',num(g.delta,2)],['Stock held',num(s.stock.account.position,0)],['Explicit fees',cash(a.fees)]].map(([l,v])=>`<div><small>${esc(l)}</small><strong>${esc(v)}</strong></div>`).join('');
 const expiries=[...new Set(s.chain.map(c=>String(c.expiry_days)))];if(!expiries.includes(expiry))expiry=expiries.includes(String(q.expiry_days))?String(q.expiry_days):expiries[0]||'';
 $('option-expiry').innerHTML=expiries.map(e=>`<option value="${e}">Day ${e} from origin</option>`).join('');$('option-expiry').value=expiry;
 renderChain();
 $('selected-contract').textContent=`${heading(q.type).toUpperCase()} · strike £${num(q.strike,2)}`;
 $('model-title').textContent=`${q.type.toUpperCase()} £${num(q.strike,2)} · ${num(q.remaining_days,2)} days remaining`;
 $('selected-description').textContent=`Expiry: model day ${q.expiry_days} · ${num(q.remaining_days,2)} days remaining · multiplier ${q.multiplier}${q.expired?' · CASH-SETTLED / EXPIRED':' · '+q.moneyness}`;
 $('quote-cards').innerHTML=q.expired?grid([['Expiry payoff per unit',cash(q.payoff)]]):`<div><small>SELL AT BID</small><strong>£${num(q.bid,6)}</strong><small>${q.bid_size} contracts</small></div><div><small>BUY AT ASK</small><strong>£${num(q.ask,6)}</strong><small>${q.ask_size} contracts</small></div><div class="model"><small>MODEL VALUE</small><strong>£${num(q.model_value,6)}</strong><small>Theoretical, per unit</small></div>`;
 $('premium-preview').textContent=`Premium is quoted per underlying unit. Each contract represents ${q.multiplier} units. ${q.expired?'Expiry stock reference '+cash(q.expiry_spot):'Current intrinsic '+cash(q.intrinsic)+'; midpoint minus intrinsic '+cash(q.time_value)+'.'} Trades are immediate-or-cancel dealer-quote executions.`;
 const last=s.option_trades.at(-1);$('last-option-fill').innerHTML=last?grid([['Last option fill',`${last.side} ${last.filled} contract(s)`],['Premium cash flow',cash(last.premium_cash_flow)],['Execution premium / unit','£'+num(last.premium,6)],['Option fee',cash(last.fee)]]):'';
 $('hedge-context').textContent=`Current option delta: ${num(g.option_delta,3)} stock units. Actual stock position: ${s.stock.account.position}. Combined delta: ${num(g.delta,3)}. The hedge is a current sensitivity offset, not protection against every risk.`;
 $('stock-limit').disabled=$('stock-type').value!=='limit';
 $('stock-book').innerHTML=['bids','asks'].map(side=>`<div><h3>${side==='bids'?'Stock bids':'Stock asks'} · real FIFO</h3>`+table(['Price (£)','Units','Orders'],s.stock[side].map(l=>[num(l.price,2),l.quantity,l.order_count]))+'</div>').join('');
 $('stock-open-orders').innerHTML=s.stock.orders.filter(o=>o.remaining).map(o=>`<p>${esc(o.side)} ${o.remaining} stock units at ${esc(o.price)} <button data-cancel="${esc(o.order_id)}">Cancel ${esc(o.order_id)}</button></p>`).join('');
 $('option-positions').innerHTML=s.positions.length?s.positions.map(p=>`<div class="position-card"><strong>${esc(p.type.toUpperCase())} £${num(p.strike,2)} · day ${p.expiry_days}</strong><p>${p.quantity} contracts × ${p.multiplier}${p.settled?' · settled':''}</p><p>Marked value ${cash(p.value)}<br>Realised gross ${cash(p.realised_gross)} · unrealised ${cash(p.unrealised)}</p><p>Delta ${num(p.position_greeks.delta,3)} · Gamma ${num(p.position_greeks.gamma,4)}<br>Vega / 1.00 vol ${num(p.position_greeks.vega,3)} · Theta / year ${num(p.position_greeks.theta,3)}</p></div>`).join(''):'<p>No option position yet. Select a contract and trade its quoted bid/ask.</p>';
 chart('hedge-pnl-chart',s.history,'elapsed_days',[{key:'total_pnl',color:'#345d89',label:'Net P&L'}],{xLabel:'Observed model day',yLabel:'GBP'});
 chart('hedge-position-chart',s.history,'elapsed_days',[{key:'stock_position',color:'#3a857b',label:'Stock units'},{key:'delta',color:'#bf8253',label:'Residual delta'}],{xLabel:'Observed model day',yLabel:'Underlying units'});
 renderModels();renderResearch();renderReport();
 if(lastSelected!==q.id){lastSelected=q.id;$('iv-price').value=q.midpoint??0;$('shock-days').value=Math.min(1,q.remaining_days);}
 $('current-iv').value=Number(s.current_volatility_input*100).toFixed(2);
}
function renderChain(){const rows=state.chain.filter(c=>String(c.expiry_days)===expiry);const strikes=[...new Set(rows.map(c=>c.strike))].sort((a,b)=>a-b);
 if(!strikes.length){$('option-chain').innerHTML='<p>No unexpired dealer quotes remain. Inspect settlement or open a new session.</p>';return;}
 const cell=(c,k,n=4)=>c?num(k==='iv'?c.iv.volatility:k==='delta'?c.greeks.delta:c[k],n):'—';
 $('option-chain').innerHTML='<table><thead><tr><th>Call bid</th><th>Call ask</th><th>IV (decimal)</th><th>Delta</th><th>Strike (£)</th><th>Put bid</th><th>Put ask</th><th>IV (decimal)</th><th>Delta</th></tr></thead><tbody>'+strikes.map(k=>{const c=rows.find(x=>x.strike===k&&x.type==='call'),p=rows.find(x=>x.strike===k&&x.type==='put');return `<tr class="${state.selected.strike===k?'selected-row':''}"><td><button class="chain-pick" data-contract="${esc(c?.id)}" aria-label="Select call strike ${k}">${cell(c,'bid')}</button></td><td>${cell(c,'ask')}</td><td>${cell(c,'iv')}</td><td>${cell(c,'delta')}</td><td>${num(k,2)}</td><td><button class="chain-pick" data-contract="${esc(p?.id)}" aria-label="Select put strike ${k}">${cell(p,'bid')}</button></td><td>${cell(p,'ask')}</td><td>${cell(p,'iv')}</td><td>${cell(p,'delta')}</td></tr>`;}).join('')+'</tbody></table>';
}
function renderModels(){const s=state,q=s.selected,g=q.greeks||{},cg=q.contract_greeks||{};
 $('option-greeks').innerHTML=table(['Greek / convention','Per unit','Per contract'],[['Delta / £1 stock',num(g.delta,6),num(cg.delta,6)],['Gamma / £1 stock',num(g.gamma,6),num(cg.gamma,6)],['Vega / 1.00 annual vol',num(g.vega,6),num(cg.vega,6)],['Vega / 1 percentage point',num(g.vega_per_vol_point,6),num(cg.vega_per_vol_point,6)],['Theta / model year',num(g.theta,6),num(cg.theta,6)],['Theta / ACT/365 day',num(g.theta_per_day,6),num(cg.theta_per_day,6)],['Rho / 1.00 annual rate',num(g.rho,6),num(cg.rho,6)]])+`<p class="learning-note">${esc(g.status||'Expired: no ongoing position Greeks. Payoff has a strike kink.')}</p>`;
 const analysis=s.analysis;
 const fd=analysis.greek_check?.data;
 $('greek-check').innerHTML=fd?table(['Greek','Analytic','Finite difference'],['delta','gamma','vega','theta','rho'].map(k=>[k,num(fd.analytic[k],7),num(fd.finite_difference[k],7)]))+`<p>Call ${cash(fd.call)} · Put ${cash(fd.put)} · Put-call parity residual ${num(fd.parity_residual,10)}.</p>`:'';
 const sh=analysis.shock?.data;
 $('shock-result').innerHTML=sh?grid([['Exact repriced value',cash(sh.repriced)],['Exact value change',cash(sh.exact_change)],['Delta-only change',cash(sh.delta_only_change)],['Greeks including gamma',cash(sh.greek_change)],['Approximation error',cash(sh.approximation_error)],['Units','GBP per underlying unit']]):'';
 const iv=analysis.iv?.data;
 $('iv-result').innerHTML=iv?grid([['IV (annual decimal)',iv.converged?num(iv.volatility,8):'No reliable IV'],['Status',iv.status],['Method',iv.method],['Iterations',iv.iterations],['Pricing residual',num(iv.residual,12)],['Newton / bracket steps',`${iv.newton_steps} / ${iv.bisection_steps}`]]):'';
 const mc=analysis.mc?.data;
 $('mc-result').innerHTML=mc?grid([['Monte Carlo value',cash(mc.estimate)],['Analytical value',cash(mc.analytic)],['Standard error',cash(mc.standard_error)],['95% mean interval',`${cash(mc.confidence_interval.low)} to ${cash(mc.confidence_interval.high)}`],['IID paths',num(mc.paths,0)],['Error from analytical',cash(mc.error)]])+(mc.warnings||[]).map(w=>'<p class="learning-note">'+esc(w)+'</p>').join(''):'';
 for(const [id,key,label] of [['payoff-curve','payoff','Expiry payoff'],['value-curve','value','Model value'],['delta-curve','delta','Delta'],['gamma-curve','gamma','Gamma']])chart(id,s.curves,'spot',[{key,color:'#345d89',label}],{yLabel:label});
 const smile=s.chain.filter(c=>c.type==='call'&&String(c.expiry_days)===expiry).map(c=>({strike:c.strike,iv:c.iv.volatility}));
 chart('smile-curve',smile,'strike',[{key:'iv',color:'#3a857b',label:'Synthetic midpoint IV'}],{xLabel:'Strike (£)',yLabel:'Annual decimal volatility'});
}
function renderResearch(){const r=state.research,key=JSON.stringify(r);if(key===researchKey)return;researchKey=key;$('study-options-research').disabled=r.status!=='complete';
 if(r.status==='idle'){$('options-research-result').innerHTML='<p class="learning-note">No derivative experiment run in this app session yet.</p>';return;}
 let content=`<p><strong>${esc(r.status.toUpperCase())}</strong> · ${r.completed??0} / ${r.runs??0} paired paths</p><p>${esc(r.hypothesis)}</p>`;
 if(r.error)content+=`<p class="learning-error">${esc(r.error)}</p>`;
 if(r.summaries){for(const metric of ['net_pnl','fees','gross_hedging_error','rms_delta','drawdown','turnover','realised_volatility']){content+=`<h3>${esc(heading(metric))}</h3>`+table(['Variant','Mean','SD','SE','5th percentile','95th percentile'],Object.entries(r.summaries).map(([name,v])=>[name,...['mean','standard_deviation','standard_error','p05','p95'].map(k=>num(v[metric][k],5))]));}content+=`<p>Recorded in ${esc(r.path)} · ${num(r.elapsed_seconds,2)} seconds. Mean estimates are conditional on this synthetic model.</p>`;}
 if(r.paired&&Object.keys(r.paired).length)content+='<h3>Paired net P&L differences (£)</h3>'+table(['Comparison','Mean difference','Standard error','95% mean interval'],Object.entries(r.paired).map(([name,p])=>[name,num(p.summary.mean,5),num(p.summary.standard_error,5),num(p.summary.mean_ci?.low,5)+' to '+num(p.summary.mean_ci?.high,5)]));
 for(const warning of r.warnings||[])content+=`<p class="learning-error">${esc(warning)}</p>`;$('options-research-result').innerHTML=content;
}
function renderReport(){const s=state,a=s.accounts;
 $('options-report').innerHTML=`<p>${s.status==='ended'?'Ended session':'Current marked report'} · ${s.step} observed steps. Remaining stock is not automatically liquidated.</p>`+grid([['Option realised gross',cash(a.option_realised_gross)],['Option unrealised',cash(a.option_unrealised)],['Stock realised gross',cash(a.stock_realised_gross)],['Stock unrealised',cash(a.stock_unrealised)],['Cash financing',cash(a.financing)],['Explicit fees (spread included in fills)',cash(a.fees)],['Total net P&L',cash(a.total_pnl)],['Maximum drawdown',cash(a.drawdown)],['Executed hedge occasions',num(a.hedges,0)],['Stock turnover (units)',num(a.turnover,0)],['Interval RMS delta (units)',num(a.rms_delta,3)],['Maximum absolute delta',num(a.max_absolute_delta,3)],['Starting quote-vol input',num(s.starting_volatility_input,4)],['Observed realised vol',num(a.realised_volatility,4)],['Ending selected quote IV',num(s.ending_quote_iv,4)],['Automatic frequency',s.auto_frequency?`Every ${s.auto_frequency} steps`:'Off']])+table(['Portfolio Greek','After first option fill','Now'],['delta','gamma','vega','theta','rho'].map(k=>[k,num(s.starting_greeks?.[k],5),num(s.greeks[k],5)]))+`<p>Maximum absolute gamma ${num(a.max_absolute_gamma,5)}; maximum absolute vega ${num(a.max_absolute_vega,5)}. Realised volatility uses observed close-to-close quadratic variation; it is not guaranteed to equal the process setting.</p>`+table(['Contract','Contracts','Marked value','Settled'],s.positions.map(p=>[`${p.type} K${p.strike} day ${p.expiry_days}`,p.quantity,cash(p.value),p.settled?'Yes':'No']))+`<p>Underlying position: ${s.stock.account.position} units. ${s.saved_path?'Saved journal: '+esc(s.saved_path):''}</p>${s.save_warning?'<p class="learning-error">'+esc(s.save_warning)+'</p>':''}`;
 $('options-journal').hidden=s.status!=='ended';$('options-replay-controls').hidden=!s.replay;
 if(s.replay){$('replay-position').textContent=`Frame ${s.frame_index+1} of ${s.frame_count}`;$('replay-previous').disabled=s.frame_index===0;$('replay-next').disabled=s.frame_index===s.frame_count-1;}
}
$('option-expiry').addEventListener('change',()=>{expiry=$('option-expiry').value;renderChain();renderModels();});
$('option-chain').addEventListener('click',e=>{const id=e.target.closest('[data-contract]')?.dataset.contract;if(id)command('select',{contract_id:id});});
$('stock-open-orders').addEventListener('click',e=>{const id=e.target.closest('[data-cancel]')?.dataset.cancel;if(id)command('cancel_stock',{order_id:id});});
$('option-step').onclick=()=>command('step',{count:1});$('option-five').onclick=()=>command('step',{count:5});$('option-end').onclick=()=>command('end');
$('option-order').onsubmit=e=>{e.preventDefault();command('option_order',{contract_id:state.selected.id,side:$('option-side').value,quantity:Number($('option-quantity').value),quote_revision:state.selected.revision});};
$('stock-hedge').onsubmit=e=>{e.preventDefault();const p={side:$('stock-side').value,quantity:Number($('stock-quantity').value),order_type:$('stock-type').value};if(p.order_type==='limit')p.price=$('stock-limit').value;command('stock_order',p);};
$('stock-type').onchange=()=>{$('stock-limit').disabled=$('stock-type').value!=='limit';};
$('hedge-once').onclick=()=>command('hedge');$('auto-frequency').onchange=()=>command('set_auto',{frequency:Number($('auto-frequency').value)});
$('apply-iv').onclick=()=>command('set_iv',{volatility:Number($('current-iv').value)/100});
$('options-view').onchange=()=>document.body.classList.toggle('quant-view',$('options-view').value==='quant');
$('options-setup').onsubmit=e=>{e.preventDefault();const p={};for(const [k,v]of new FormData(e.target)){p[k]=['strikes','expiries_days'].includes(k)?String(v).split(',').map(Number):Number(v);if(['implied_volatility','process_volatility','rate'].includes(k))p[k]/=100;}command('new',p);};
$('check-greeks').onclick=()=>command('greek_check');
$('shock-form').onsubmit=e=>{e.preventDefault();command('shock',{spot_change:Number($('shock-spot').value),volatility_change:Number($('shock-vol').value)/100,elapsed_days:Number($('shock-days').value),rate_change:Number($('shock-rate').value)/100});};
$('iv-form').onsubmit=e=>{e.preventDefault();command('iv',{market_price:Number($('iv-price').value),initial:Number($('iv-initial').value)/100,newton_iterations:$('iv-bracket').checked?0:8});};
$('mc-form').onsubmit=e=>{e.preventDefault();message('Running risk-neutral Monte Carlo pricing…');command('mc',{paths:Number($('mc-paths').value),seed:Number($('mc-seed').value)});};
$('options-research').onsubmit=e=>{e.preventDefault();command('research',{experiment:$('research-experiment').value,runs:Number($('options-research-runs').value),root:Number($('research-root').value),quantity:Number($('research-quantity').value)});};
$('study-options-research').onclick=async()=>{await command('study_research');activateTab('trade');document.querySelector('.option-tutor').scrollIntoView({behavior:'smooth'});};
$('options-replay-file').onchange=async e=>{const f=e.target.files[0];if(!f)return;try{await command('load_replay',{journal_text:await f.text()});}catch(err){message(err.message,true);}};
$('replay-previous').onclick=()=>command('replay_frame',{index:state.frame_index-1});$('replay-next').onclick=()=>command('replay_frame',{index:state.frame_index+1});$('replay-final').onclick=()=>command('replay_frame',{index:state.frame_count-1});
async function init(){token=(await get('/api/bootstrap')).token;state=await get('/api/options');render();}
init().catch(e=>message(e.message,true));
setInterval(async()=>{if(busy||!state)return;try{const fresh=await get('/api/options');if(fresh.revision!==state.revision||fresh.frame_index!==state.frame_index||fresh.selected.id!==state.selected.id){state=fresh;render();}else{state.research=fresh.research;renderResearch();}}catch(e){message(e.message,true);}},2000);
})();

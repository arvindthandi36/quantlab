/* UI only: public facts, server-created questions and server-graded answers. */
(() => {
'use strict';
const $ = id => document.getElementById(id);
const root = document.querySelector('[data-tutor]');
if (!root) return;
const statarbMode=root.hasAttribute('data-statarb-tutor');
const riskMode=root.hasAttribute('data-risk-tutor');
const optionsMode=root.hasAttribute('data-options-tutor')||riskMode||statarbMode;
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const title = value => String(value).replaceAll('_',' ').replace(/^./, c => c.toUpperCase()).replace(/Vwap/g,'VWAP').replace(/Pnl/g,'P&L');
const date = value => value ? new Date(value).toLocaleString([], {dateStyle:'medium',timeStyle:'short'}) : 'Not yet';
const list = values => '<ul>' + values.map(v => '<li>' + esc(v) + '</li>').join('') + '</ul>';
const button = (action, text) => '<button type="button" data-action="' + action + '">' + text + '</button>';
let token, state, market, renderKey='', busy=false, dashboardKey='', lastMarketKey='';
let selectedConcept='', selectedMode='learn', toolsOpen=false, reviewVisible=false;
async function get(path) {
  const response = await fetch(path);
  const data = await response.json();
  if (!response.ok) throw Error(data.error || 'Local request failed');
  return data;
}
function message(text, error=false) {
  const box = root.querySelector('.tutor-message');
  if (box) { box.textContent=text; box.className='tutor-message '+(error?'learning-error':'learning-note'); }
  if ($('learning-message')) { $('learning-message').textContent=text; $('learning-message').className=error?'learning-error':''; }
}
async function command(kind, payload={}) {
  if (busy) return null;
  busy=true;
  try {
    const response=await fetch('/api/tutor',{method:'POST',headers:{'Content-Type':'application/json','X-QuantLab-Token':token},body:JSON.stringify({kind,payload})});
    const result=await response.json();
    if (!response.ok) throw Error(result.error || 'Tutor request failed');
    if (result.review) renderReview(result.review);
    else if (result.observer_only) renderObserver(result);
    else { state=result; render(); }
    if (result.research) renderResearch(result);
    await dashboard();
    return result;
  } catch (error) { message(error.message,true); return null; }
  finally { busy=false; }
}
function layers(question) {
  if (!question.layers) return '';
  return Object.entries(question.layers).map(([key,text])=>'<div class="teaching-layer"><h4>'+esc(key.toUpperCase())+'</h4><p>'+esc(text)+'</p></div>').join('');
}
function render() {
  const current=state?.current;
  const key=JSON.stringify([state?.enabled,state?.error,current,state?.encountered,market?.status,market?.replay]);
  if (key===renderKey) return;
  renderKey=key;
  toolsOpen=root.querySelector('[data-tools]')?.open ?? toolsOpen;
  let content='<label class="tutor-switch"><input id="tutor-enabled" type="checkbox" '+(state?.enabled?'checked':'')+'>Enable tutor</label>';
  if (state?.error) content+='<p class="learning-error">'+esc(state.error)+'</p><p>Trading remains available. Preserve your progress file before resetting learning from the dashboard.</p>';
  if (!state?.enabled) content+='<p class="tutor-empty">The tutor is off. Your trading controls remain available.</p>';
  else {
    if (current) {
      const q=current.question;
      content+='<p class="question-meta">'+esc(title(current.mode))+' · Level '+q.difficulty+' · '+esc(title(q.concept))+' · '+esc(title(current.stage))+'</p>';
      content+='<div class="question-context">'+esc(q.quantlab)+'</div>';
      if(current.mode!=='learn') content+='<p class="tutor-interview-note">One submitted answer, at most one hint, then a separate debrief. Difficulty follows assessed prerequisites. Speaking fluency is not graded.</p>';
      content+='<p class="question-prompt">'+esc(q.prompt)+'</p>';
      if(!current.closed) {
        content+='<form class="answer-form" id="tutor-answer">';
        if(q.answer_type==='number') content+='<label>Numerical answer<input name="answer" inputmode="decimal" autocomplete="off" required></label><p class="learning-note">Tolerance: '+esc(q.tolerance)+'. A fraction is accepted. No currency symbol.</p>';
        else content+=q.options.map(o=>'<label class="answer-option"><input name="answer" type="'+(q.answer_type==='choices'?'checkbox':'radio')+'" value="'+esc(o.id)+'"><span>'+esc(o.text)+'</span></label>').join('');
        content+='<button class="primary" type="submit">Submit answer</button></form>';
      }
      if(current.feedback) content+='<p class="tutor-feedback" role="status">'+esc(current.feedback)+'</p>';
      if(current.result) content+='<h3>Actual result</h3><p>'+esc(current.result)+'</p>';
      content+='<div class="tutor-actions">'+(!current.closed?button('hint','Hint'):'')+button('explain',current.mode==='learn'?'Explain':'Show debrief')+button('deeper','Go deeper')+'</div>';
      content+='<details><summary>Why does this matter?</summary><p class="learning-note">'+esc(current.why)+'</p></details>';
      content+=layers(q);
      if(current.learning_update) {
        const u=current.learning_update;
        content+='<p class="learning-update">'+esc(title(u.result))+'. '+esc(u.before.category)+' → '+esc(u.after.category)+'. '+(u.credited?'Answer evidence recorded.':'Practice recorded; this repeated/revealed item earns no extra score.')+'</p>';
      }
      if(current.deeper) content+='<h3>Go deeper · Level '+current.deeper.difficulty+'</h3><p>'+esc(current.deeper.prompt)+'</p>'+layers(current.deeper);
    } else content+=optionsMode ? '<p class="tutor-empty">Trade and inspect a risk or options concept using your actual portfolio state.</p>' : '<p class="tutor-empty">Place an order to meet a concept in the market, or make a prediction about the current book.</p>';
    content+='<div class="tutor-actions">'+button('quiz','Quiz me')+(optionsMode?'':button('predict','Predict before trading'))+'</div>';
    content+='<details data-tools class="tutor-tools" '+(toolsOpen?'open':'')+'><summary>Revisit a concept / Interview / Project defence</summary>';
    content+='<label>Practice mode<select id="tutor-mode"><option value="learn">Learn · hints and feedback</option><option value="interview">Interview · delayed debrief</option><option value="defence">Project defence</option></select></label><label>Concept<select id="tutor-concept"></select></label>'+button('chosen','Start selected question')+'</details>';
  }
  if(!optionsMode&&market?.status==='ended') content+='<div class="tutor-actions">'+button('review','Review this session')+'</div>';
  content+='<p class="tutor-message" role="status" aria-live="polite"></p><p class="learning-note">Answers stay on this computer. Trading is never gated by quizzes.</p>';
  if(!$('learning-dashboard')) content+='<a href="/learning" class="learning-note">Learning dashboard · progress, reviews & research →</a>';
  root.innerHTML=content;
  if($('tutor-mode')) { $('tutor-mode').value=selectedMode; populateConcepts(); }
}
function populateConcepts() {
  const choices=selectedMode==='defence'?
    ['architecture','queue_priority','sample_mean','randomness','reproducibility','model_criticism','research_integrity']:
    (state.encountered || []);
  $('tutor-concept').innerHTML=choices.map(key=>'<option value="'+esc(key)+'">'+esc(title(key))+'</option>').join('');
  if(choices.includes(selectedConcept)) $('tutor-concept').value=selectedConcept;
  else selectedConcept=$('tutor-concept').value;
}
root.addEventListener('change',e=>{
  if(e.target.id==='tutor-enabled') command('configure',{enabled:e.target.checked});
  if(e.target.id==='tutor-mode') { selectedMode=e.target.value;populateConcepts(); }
  if(e.target.id==='tutor-concept') selectedConcept=e.target.value;
});
root.addEventListener('submit',e=>{
  if(e.target.id!=='tutor-answer') return;
  e.preventDefault();
  const values=new FormData(e.target).getAll('answer');
  const q=state.current.question;
  if(!values.length) return message('Select an answer first.',true);
  command('answer',{question_id:state.current.id,answer:q.answer_type==='choices'?values:values[0]});
});
root.addEventListener('click',e=>{
  const action=e.target.closest('[data-action]')?.dataset.action;
  if(!action) return;
  if(action==='chosen') command('quiz',{concept:selectedConcept,mode:selectedMode});
  else command(action);
});
async function dashboard() {
  if(!$('learning-dashboard')) return;
  let d;
  try { d=await get('/api/learning'); } catch(error) { message(error.message,true); return; }
  const key=JSON.stringify(d);
  if(key===dashboardKey) return;
  dashboardKey=key;
  const open=[...document.querySelectorAll('.domain-row[open]')].map(e=>e.dataset.domain);
  const assessed=d.concepts.filter(c=>c.score!==null).length;
  $('learning-dashboard').innerHTML='<div class="learning-summary"><div><strong>'+assessed+'</strong><span>Concepts with answer evidence</span></div><div><strong>'+d.concepts.reduce((n,c)=>n+c.attempts,0)+'</strong><span>Graded attempts</span></div><div><strong>'+d.due.length+'</strong><span>Due for review</span></div></div>'+
    d.domains.map(domain=>'<details class="domain-row" data-domain="'+esc(domain.domain)+'" '+(open.includes(domain.domain)?'open':'')+'><summary><strong>'+esc(domain.domain)+'</strong><span>'+esc(domain.status)+' · '+domain.attempts+' attempts</span></summary>'+
      '<div class="table-scroll"><table><thead><tr><th>Concept / prerequisites</th><th>Status</th><th>Answer evidence</th><th>Recent / next review</th><th>Practice</th></tr></thead><tbody>'+
      d.concepts.filter(c=>c.domain===domain.domain).map(c=>'<tr><td>'+esc(c.title)+'<span class="concept-dependency">'+(c.prerequisites.length?esc(c.prerequisites.map(title).join(' + '))+' → '+esc(c.title):'Foundation')+'</span></td><td>'+esc(c.category)+(c.score!==null?' · ≈'+c.score:'/ '+(c.implemented?'Available':'Prepared only'))+'</td><td>'+c.attempts+' attempts<br>'+c.correct_first+' first · '+c.correct_after_hint+' helped · '+c.incorrect+' incorrect</td><td>'+esc(c.recent_performance.slice(-3).map(title).join(', ')||'No graded answers')+'<br><span class="concept-dependency">Next: '+esc(date(c.review_at))+'</span></td><td>'+(c.implemented&&(state.encountered||[]).includes(c.id)?'<button data-revisit="'+esc(c.id)+'">Review now</button>':'—')+'</td></tr>').join('')+'</tbody></table></div></details>').join('');
  $('learning-review').innerHTML='<h3>Due for review</h3>'+(d.due.length?d.due.map(r=>'<div class="review-item"><strong>'+esc(title(r.concept))+'</strong><p>'+esc(r.reason)+'</p><button data-revisit="'+esc(r.concept)+'">Revisit</button></div>').join(''):'<p class="learning-note">Nothing is due today. You can revisit any encountered concept from the learning map.</p>')+
    '<h3>Weak concepts</h3><p>'+esc(d.weak.map(title).join(', ')||'No assessed weak concepts yet.')+'</p><h3>Mistake log</h3>'+
    (d.mistakes.length?d.mistakes.map(m=>'<div class="review-item"><strong>'+esc(m.classification)+' · '+esc(title(m.concept))+'</strong><p>'+esc(title(m.id))+'</p><p class="mistake-evidence">'+esc(m.evidence.join(' · '))+'</p><button data-revisit="'+esc(m.concept)+'">Practice this idea</button></div>').join(''):'<p class="learning-note">No graded misconceptions recorded. This is not evidence of mastery.</p>')+
    '<h3>Recent answer history</h3>'+d.recent.slice(-10).reverse().map(r=>'<div class="review-item"><strong>'+esc(title(r.concept))+' · '+esc(title(r.result))+'</strong><p>'+esc(r.mode)+' · Level '+r.level+' · '+esc(date(r.at))+'</p><p>'+esc(r.evidence)+'</p></div>').join('');
  if(document.activeElement!==$('event-gap')) $('event-gap').value=d.settings.event_gap;
  if(document.activeElement!==$('max-attempts')) $('max-attempts').value=d.settings.max_attempts;
}
document.addEventListener('click',e=>{
  const concept=e.target.closest('[data-revisit]')?.dataset.revisit;
  if(concept) { selectedConcept=concept; command('quiz',{concept}).then(()=>root.scrollIntoView({behavior:'smooth',block:'start'})); }
});
function renderResearch(result) {
  if(!$('research-result')) return;
  const selected=$('research-variant').value;
  $('research-variant').innerHTML='<option value="">All variants</option>'+result.variants.map(v=>'<option value="'+esc(v)+'">'+esc(v)+'</option>').join('');
  if(result.variants.includes(selected)) $('research-variant').value=selected;
  $('research-result').innerHTML=result.research.map(c=>{
    const f=c.facts;
    const fields=[['Sessions',f.n],['Mean',f.mean.toPrecision(5)],['Session SD',f.sd.toPrecision(5)],['Mean SE',f.se.toPrecision(5)],['Observed minimum',f.minimum.toPrecision(5)],['Observed maximum',f.maximum.toPrecision(5)]];
    return '<h3>'+esc(f.variant)+' · '+esc(f.metric)+'</h3><p class="learning-note">'+esc(f.unit)+' · verified source '+esc(f.source_digest.slice(0,12))+'</p><div class="research-metrics">'+fields.map(([label,value])=>'<div><span>'+label+'</span><strong>'+esc(value)+'</strong></div>').join('')+'</div>'+
      '<p class="learning-note">95% mean interval: '+esc(f.ci_low.toPrecision(5))+' to '+esc(f.ci_high.toPrecision(5))+'. This is not a range guaranteed to contain the next outcome.</p>'+
      (f.paired?'<p>Paired difference mean: '+esc(f.mean_difference.toPrecision(5))+'. Paired SE: '+esc(f.paired_se.toPrecision(5))+'; independent-sample SE benchmark: '+esc(f.unpaired_se.toPrecision(5))+'. Pairing need not always help.</p>':'');
  }).join('');
}
function renderReview(review) {
  if(market?.status!=='ended') return;
  reviewVisible=true;
  $('teaching-review').hidden=false;
  const node=document.querySelector('[data-session-review]');
  node.innerHTML='<div class="review-columns"><div><h3>What happened</h3><p>Final marked P&L £'+esc(review.what_happened.final_pnl)+' · '+review.what_happened.trade_count+' executions · fees £'+esc(review.what_happened.fees)+'</p><h3>Specific actions / reasoning</h3>'+list(review.what_you_did_well)+'<h3>What to improve</h3>'+list(review.what_to_improve)+'</div><div><h3>Decision quality ≠ outcome quality</h3><div class="decision-grid">'+review.decision_vs_outcome.map(x=>'<div>'+esc(x)+'</div>').join('')+'</div><p>'+esc(review.assessment)+'</p></div></div>'+
    '<h3>Concepts encountered</h3><p>'+esc(review.concepts_encountered.map(title).join(', '))+'</p><h3>Answer-based mastery updates</h3>'+
    (review.mastery_updates.length?list(review.mastery_updates.map(r=>title(r.concept)+': '+title(r.result)+'; '+r.before.category+' → '+r.after.category)):'<p>No graded answer evidence from this session. P&L did not change your score.</p>')+
    '<div class="review-columns"><div><h3>What you knew then</h3>'+list(review.known_then.map(a=>(a.time_us/1e6).toFixed(3)+'s: '+a.order+' · before submitting, bid £'+a.observed.best_bid+', ask £'+a.observed.best_ask+', position '+a.observed.position))+'</div><div><h3>What happened afterwards · public</h3>'+list(review.later_public.slice(-8).map(a=>(a.time_us/1e6).toFixed(3)+'s: reference £'+a.reference+', position '+a.position))+'</div></div>'+
    '<h3>Three questions to revisit</h3>'+review.three_questions.map(q=>'<div class="review-item"><p>'+esc(q.prompt)+'</p><button data-revisit="'+esc(q.concept)+'">Practise '+esc(title(q.concept))+'</button></div>').join('')+
    '<h3>Interview transfer</h3><p>'+esc(review.interview.prompt)+'</p><button id="review-interview">Defend decision quality</button>'+
    '<details class="reset-learning"><summary>Separate observer-only forensics</summary><p>After the session, you may explicitly reveal hidden model state. You did not know it when deciding. This view is excluded from tutor questions, grading and learning exports.</p><button id="show-observer">Reveal observer-only state</button><div id="observer-view"></div></details>';
  $('show-observer').onclick=()=>command('observer',{reveal:true});
  $('review-interview').onclick=()=>command('quiz',{concept:'decision_quality',mode:'interview'}).then(()=>root.scrollIntoView({behavior:'smooth'}));
  $('teaching-review').scrollIntoView({behavior:'smooth',block:'start'});
}
function renderObserver(result) {
  if(!$('observer-view') || market?.status!=='ended') return;
  $('observer-view').innerHTML='<div class="observer-only"><h3>'+esc(result.label)+'</h3><p>'+esc(result.note)+'</p><div class="table-scroll"><table><thead><tr><th>Time (s)</th><th>Latent before (ticks)</th><th>Latent after (ticks)</th><th>Signal error (ticks)</th></tr></thead><tbody>'+result.observer_only.map(r=>'<tr><td>'+esc(r.time_us/1e6)+'</td><td>'+esc(r.latent_before_ticks)+'</td><td>'+esc(r.latent_after_ticks)+'</td><td>'+esc(r.signal_error_ticks??'No private signal')+'</td></tr>').join('')+'</tbody></table></div></div>';
}
document.addEventListener('quantlab-public-state',e=>{
  market=e.detail;
  if(market.status!=='ended' && $('teaching-review')) {
    $('teaching-review').hidden=true;
    document.querySelector('[data-session-review]').innerHTML='';
    reviewVisible=false;
  }
  if(!busy) poll();
});
document.addEventListener('quantlab-statarb-state',e=>{if(statarbMode){market=e.detail;if(!busy)poll();}});
document.addEventListener('quantlab-risk-state',e=>{if(riskMode){market=e.detail;if(!busy)poll();}});
document.addEventListener('quantlab-options-state',e=>{if(optionsMode){market=e.detail;if(!busy)poll();}});
async function poll() {
  if(busy) return;
  try {
    [state,market]=await Promise.all([get('/api/tutor'),get(statarbMode?'/api/statarb':riskMode?'/api/risk':optionsMode?'/api/options':'/api/state')]);
    const marketKey=String(market.status)+':'+String(market.scenario)+':'+String(market.replay);
    if(reviewVisible&&(market.status!=='ended'||marketKey!==lastMarketKey)) {
      $('teaching-review').hidden=true;document.querySelector('[data-session-review]').innerHTML='';reviewVisible=false;
    }
    lastMarketKey=marketKey;
    render(); await dashboard();
  } catch(error) { message(error.message,true); }
}
async function init() {
  token=(await get('/api/bootstrap')).token;
  if($('research-form')) {
    const experiments=await get('/api/learning/experiments');
    $('research-select').innerHTML=experiments.map(e=>'<option value="'+esc(e.id)+'">'+esc(e.title)+'</option>').join('');
    $('research-select').onchange=()=>{$('research-variant').innerHTML='<option value="">All variants</option>';};
    $('research-form').onsubmit=e=>{e.preventDefault();const payload={experiment:$('research-select').value};if($('research-variant').value) payload.variant=$('research-variant').value;command('research',payload);};
    $('learning-settings').onsubmit=e=>{e.preventDefault();command('configure',{event_gap:Number($('event-gap').value),max_attempts:Number($('max-attempts').value)}).then(r=>{if(r)message('Preferences saved locally.');});};
    $('reset-learning').onclick=()=>command('reset',{confirmation:$('reset-confirmation').value}).then(r=>{if(r){$('reset-confirmation').value='';message('Learning progress reset. Trading history is unchanged.');}});
  }
  await poll();
  setInterval(poll,1500);
}
init().catch(error=>{root.textContent='Tutor unavailable: '+error.message+'. Trading remains available.';});
})();

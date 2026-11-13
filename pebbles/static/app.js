'use strict';
const $ = id => document.getElementById(id);
const token = document.querySelector('meta[name="pebbles-token"]').content;
let selection = null, current = null, filter = 'all', busy = false, reading = false, generation = 0;
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(path, data) {
  const response = await fetch(path, data === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json','X-Pebbles-Token':token},body:JSON.stringify(data)});
  const value = await response.json();
  if (!response.ok) throw new Error(value.error || 'The request could not be completed.');
  return value;
}
function notice(message) { $('notice').textContent=message; $('notice').hidden=!message; }
function reset() {
  if(busy)return;
  $('intake-view').hidden=true;
  $('workspace-view').hidden=true;
  if(busy)return;
  generation++;reading=false;$('run').disabled=false;current=null;selection=null;notice('');$('result-view').hidden=true;$('load-view').hidden=false;$('loaded-panel').hidden=true;
  $('folder-input').value='';$('files-input').value='';
  document.querySelectorAll('.example').forEach(x=>x.classList.remove('selected'));
  history();window.scrollTo(0,0);
}
function setSelection(value) {
  generation++;reading=false;$('run').disabled=false;selection=value;notice('');$('loaded-panel').hidden=false;$('experiment-name').value=value.label;
  $('loaded-description').textContent=value.example?'Included synthetic experiment. The investigation has not run yet.':`${value.files.length} files selected. Review the name, then run the investigation.`;
  $('loaded-files').innerHTML=value.files?value.files.map(f=>`<span class="chip">${esc(f.name)}</span>`).join(''):'<span class="chip">Configuration</span><span class="chip">Scorecard</span><span class="chip">Available definitions and events</span>';
  fillAnalysisPlan(value.analysisPlan);
  $('analysis-settings').hidden=!!value.publicDataset;$('decision-settings').hidden=!!value.publicDataset;
  if(value.publicDataset){$('loaded-files').innerHTML='<span class="chip">Public player CSV</span><span class="chip">Analyst notebook and readout</span><span class="chip">Source fingerprints</span>';}
  if(value.publicDataset)$('loaded-description').textContent='Public retention snapshot: reproduce the published analysis and compare populations. Missing original study and shipping evidence will remain unresolved.';
  if(value.controlledExercise)$('loaded-description').textContent='Controlled exercise based on Cookie Cats. The reported summary/export may contain an introduced problem. Pebbles will compare the evidence with the supplied reference; the original public analyst is not responsible for these changes.';
  $('loaded-panel').scrollIntoView({behavior:'auto',block:'nearest'});
}
async function loadFiles(event) {
  if(busy)return;
  const ticket=++generation;reading=true;selection=null;$('loaded-panel').hidden=true;$('run').disabled=true;
  try {
    const files=Array.from(event.target.files);
    if(!files.length)return;
    if(files.length>10)throw new Error('Choose the files from one evidence package, with no more than 10 files.');
    if(files.reduce((n,f)=>n+f.size,0)>50_000_000)throw new Error('This package is larger than 50 MB. Choose a smaller export.');
    if(!files.some(f=>f.name==='inventory.json'))throw new Error('This selection is missing inventory.json. Download the example package to see the supported format.');
    const contents=await Promise.all(files.map(async f=>({name:f.name,content:await f.text()})));
    if(ticket!==generation)return;
    const folder=files[0].webkitRelativePath?.split('/')[0];
    let plan=null;try{plan=JSON.parse(contents.find(f=>f.name==='configuration.json')?.content||'{}').analysis_plan;}catch(_){}
    let controlled=false;try{controlled=JSON.parse(contents.find(f=>f.name==='investigation.json')?.content||'{}').controlled_exercise===true;}catch(_){}
    setSelection({label:folder||'My experiment',files:contents,analysisPlan:plan,publicDataset:contents.some(f=>f.name==='cookie_cats.csv'),controlledExercise:controlled});
    document.querySelectorAll('.example').forEach(x=>x.classList.remove('selected'));
  } catch(e){if(ticket===generation)notice(e.message);}
  finally{if(ticket===generation){reading=false;$('run').disabled=false;}}
}
async function history() {
  try {
    const runs=await api('/api/runs');
    $('history').innerHTML=runs.length?runs.map(r=>`<button class="${current?.run_id===r.run_id?'selected':''}" data-run="${esc(r.run_id)}"><strong>${esc(r.source_label)}</strong><small>${esc(new Date(r.created_at).toLocaleString(undefined,{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'}))}</small></button>`).join(''):'<p class="muted">Your completed investigations will appear here.</p>';
    $('history').querySelectorAll('button').forEach(b=>b.onclick=async()=>{if(busy)return;try{show(await api('/api/runs/'+b.dataset.run));}catch(e){notice(e.message);}});
  } catch(e){notice('Could not load saved investigations: '+e.message);}
}
function find(id){return current.findings.find(f=>f.check_id===id);}
function rateText(n,d){return d?`${(100*n/d).toFixed(1)}%`:'Undefined';}
function explain() {
  const summary=explainReport(current);
  $('comparison').hidden=!summary.comparison;
  if(summary.comparison){
    const c=summary.comparison;
    const percentage=v=>v===null||v===undefined?'Undefined':String(v)+'%';
    $('comparison').innerHTML=`<h2>${esc(c.arm)} conversion, side by side</h2><div class="comparison-boxes"><div class="calculation"><span>Reported scorecard</span><strong>${esc(percentage(c.reportedPercent))}</strong><p>Fields: ${c.reportedNumerator} purchasers ÷ ${c.reportedDenominator}</p></div><div class="calculation"><span>Calculated from supplied records</span><strong>${esc(percentage(c.calculatedPercent))}</strong><p>${c.numerator} purchasers ÷ ${c.denominator} ${esc(c.denominatorLabel)}</p></div></div><p class="small-note">A change in the calculation is not evidence of a statistically reliable treatment effect.</p>`;
  }
  $('explanation').className='explanation '+summary.type;
  $('explanation').innerHTML=`<div class="outcome-label">${esc(summary.label)}</div><h2>${esc(summary.title)}</h2><p>${esc(summary.body)}</p><p class="next-action"><strong>What to do next</strong><br>${esc(summary.next)}</p><p class="boundary">These measurement checks support the separate decision summary. Rendering and production completeness are not independently established. Treatment-effect conclusions are conditional on the study assumptions shown above.</p>`;
}
function renderFindings(){
  const selected=current.findings.filter(f=>filter==='all'||filter==='attention'&&(f.evidence_outcome==='Failed'||f.execution_state!=='Completed')||filter==='unknown'&&f.evidence_outcome==='Insufficient evidence'||filter==='verified'&&f.evidence_outcome==='Verified');
  $('findings-count').textContent=`${current.findings.length} checks`;
  $('findings').innerHTML=selected.length?selected.map(original=>{
    const f=current.controlled_exercise?{...original,question:original.question.replace(/published/gi,'supplied readout'),explanation:original.explanation.replace(/published/gi,'supplied readout')}:original;
    const state=f.evidence_outcome,kind=state==='Failed'?'failed':state==='Verified'?'verified':'unknown';
    const label=state==='Failed'?'Contradiction found':state==='Verified'?'Supported by these files':state==='Insufficient evidence'?'Insufficient evidence':'Could not run';
    return `<details class="finding"><summary><div class="finding-title"><h3>${esc(f.question)}</h3><span class="badge ${kind}">${esc(label)}</span></div></summary><div class="finding-body"><p>${esc(f.explanation)}</p>${f.next_evidence_request?`<p><strong>Next evidence:</strong> ${esc(f.next_evidence_request)}</p>`:''}${f.values?`<details><summary>See the calculation or record details</summary><pre>${esc(JSON.stringify(f.values,null,2))}</pre></details>`:''}<p>Evidence used</p>${f.evidence.map(e=>`<button class="source-link" data-file="${esc(e.path)}">${esc(e.path)}</button>`).join('')||'<p>No supporting file supplied.</p>'}<details><summary>Provenance and check details</summary><pre>${esc(JSON.stringify({check:f.check_id,execution:f.execution_state,outcome:f.evidence_outcome,evidence:f.evidence},null,2))}</pre></details></div></details>`;
  }).join(''):'<p class="empty-filter">No checks in this category.</p>';
  $('findings').querySelectorAll('[data-file]').forEach(b=>b.onclick=()=>evidence(b.dataset.file));
}
async function evidence(name){
  try {
    const data=await api(`/api/runs/${current.run_id}/evidence/${encodeURIComponent(name)}`);
    $('evidence-name').textContent=name;$('evidence-content').textContent=data.content;
    $('evidence-truncation').textContent=data.truncated?'Showing the first 200 KB. The complete file is saved locally with this run.':'The original file supplied for this investigation.';
    $('evidence-dialog').showModal();
  }catch(e){notice(e.message);}
}
function fillAnalysisPlan(plan){
  const p=plan||{};
  fillDecisionPlan(p);
  $('plan-control').value=p.control||'control';$('plan-treatment').value=p.treatment||'treatment';
  $('plan-goal').value=p.minimum_effect_pp??1;$('plan-share').value=(p.expected_treatment_share??.5)*100;
  for(const [id,key] of [['plan-predeclared','predeclared'],['plan-randomized','randomized_independent'],['plan-complete','window_complete'],['plan-coverage','complete_assigned_outcomes']])$(id).checked=p[key]===true;
  $('plan-origin').textContent=plan?'Plan loaded from the experiment configuration. Review it before running. These are supplied declarations, not independent verification.':'These are your study declarations; Pebbles cannot independently prove them from the files. Leave unknown statements unchecked.';
}
function readAnalysisPlan(){
  return {...readDecisionPlan(),schema_version:'1.0.0',control:$('plan-control').value.trim(),treatment:$('plan-treatment').value.trim(),minimum_effect_pp:$('plan-goal').value===''?null:Number($('plan-goal').value),expected_treatment_share:$('plan-share').value===''?null:Number($('plan-share').value)/100,predeclared:$('plan-predeclared').checked,randomized_independent:$('plan-randomized').checked,window_complete:$('plan-complete').checked,complete_assigned_outcomes:$('plan-coverage').checked};
}
function renderAnalysis(){
  const a=current.analysis,host=$('treatment-analysis');
  if(current.intake){host.hidden=false;host.innerHTML=`<h2>Mapped binary outcome</h2><p>${esc(current.intake.explanation)}</p><p>95% Newcombe/Wilson interval, conditional on independent users and the confirmed fixed observation window. No practical benefit threshold was supplied.</p><button class="button secondary" id="reuse-csv">Import corrected CSV with this mapping</button><p>Attach this run to an experiment first to link a revision.</p>`;$('reuse-csv').onclick=()=>openIntake(current);return;}
  host.hidden=!!current.public_dataset;if(host.hidden)return;
  if(!a){host.innerHTML='<h2>Treatment effect has not been assessed for this saved run.</h2><p>Load the evidence and run a new investigation with an analysis plan. Earlier results remain unchanged.</p>';return;}
  const c=a.comparison, pct=v=>(100*v).toFixed(2)+'%', pp=v=>(v>=0?'+':'')+(100*v).toFixed(2)+' pp';
  let numbers='',interval='';
  if(c){
    numbers=`<div class="arm-rates"><div><span>${esc(a.plan?.control||'Control')}</span><strong>${pct(c.control_rate)}</strong><small>${c.control.purchasers.toLocaleString()} purchasers / ${c.control.users.toLocaleString()} users</small></div><div><span>${esc(a.plan?.treatment||'Treatment')}</span><strong>${pct(c.treatment_rate)}</strong><small>${c.treatment.purchasers.toLocaleString()} purchasers / ${c.treatment.users.toLocaleString()} users</small></div></div><div class="effect-line"><span>Observed difference <strong>${pp(c.difference)}</strong></span><span>Relative lift <strong>${c.relative_lift===null?'Undefined (zero control conversion)':pct(c.relative_lift)}</strong></span></div>`;
    if(c.difference_ci){
      const [lo,hi]=c.difference_ci,goal=a.plan.minimum_effect_pp/100;
      const min=Math.min(lo,0,goal),max=Math.max(hi,0,goal),pad=Math.max((max-min)*.15,.001),low=min-pad,high=max+pad;
      const position=x=>100*(x-low)/(high-low);
      interval=`<div class="interval"><h3>Uncertainty around the difference</h3><p>95% confidence interval: <strong>${pp(lo)} to ${pp(hi)}</strong></p><div class="interval-track" role="img" aria-label="95% difference interval ${pp(lo)} to ${pp(hi)}; worthwhile threshold ${a.plan.minimum_effect_pp} points"><span class="zero-line" style="left:${position(0)}%"></span><span class="goal-line" style="left:${position(goal)}%"></span><span class="confidence-band" style="left:${position(lo)}%;width:${position(hi)-position(lo)}%"></span><span class="estimate-dot" style="left:${position(c.difference)}%"></span></div><div class="interval-legend"><span>Solid marker: no change</span><span>Dashed marker: ${esc(a.plan.minimum_effect_pp)} pp goal</span><span>Dot: observed difference</span></div></div>`;
    }else interval='<p class="small-note">Rates above are descriptive only. No uncertainty interval or treatment-effect verdict is issued while prerequisites are unresolved.</p>';
  }
  const label={improvement:'Primary metric · worthwhile improvement',harm:'Primary metric · evidence of harm',inconclusive:'Primary metric · inconclusive',below_threshold:'Primary metric · below goal',blocked:'Treatment effect · cannot assess'}[a.status]||'Treatment effect';
  host.className='treatment-analysis '+a.status;
  host.innerHTML=`<div class="outcome-label">${esc(label)}</div><h2>${esc(a.title)}</h2><p>${esc(a.explanation)}</p>${numbers}${interval}${a.blockers.length?`<details open><summary>What needs to be resolved (${a.blockers.length})</summary><ul>${a.blockers.map(b=>`<li>${esc(b)}</li>`).join('')}</ul></details>`:''}<p class="next-action"><strong>What this means for your decision</strong><br>${esc(a.next_action)}</p><p class="boundary">${esc(a.limitations)}</p><details class="analysis-method"><summary>Method, assumptions and connection to the problem tree</summary><p><strong>OP-5 / CP-3:</strong> Can a correct number support a valid conclusion? Uses a fixed-horizon, independent-binomial Newcombe interval built from Wilson intervals, at 95% confidence. A frequentist interval is not a 95% probability that this particular effect lies inside it.</p><p>Only the assigned-user primary conversion metric is assessed. No sequential stopping, multiple-metric correction, clustering, covariate adjustment within this primary-metric calculation. Guardrails are assessed separately in the decision summary.</p><p>Assignment ratio: ${a.srm?`p=${a.srm.p_value.toPrecision(4)}; flag threshold 0.001. ${a.srm.flagged?'Mismatch flagged.':'No mismatch flagged; this does not prove valid randomization.'}`:'Not assessed.'}</p><p>Guardrails: ${esc(a.guardrails)}. Plan source: ${esc(a.plan_source)}. Method version: ${esc(a.method)}.</p><pre>${esc(JSON.stringify(a.plan,null,2))}</pre></details>`;
}
function show(report){
  $('intake-view').hidden=true;
  $('workspace-view').hidden=true;
  generation++;reading=false;current=report;filter='all';notice('');$('load-view').hidden=true;$('result-view').hidden=false;
  $('result-kind').textContent=report.controlled_exercise?'Controlled exercise · modified public data, not an original analyst error':report.public_dataset?'Public dataset · retrospective analyst comparison':report.synthetic_example?'Synthetic example · investigation completed':'Your experiment · investigation result';
  if(report.execution_state!=='Completed')$('result-kind').textContent='Investigation incomplete';
  $('result-name').textContent=report.source_label;$('result-time').textContent=new Date(report.created_at).toLocaleString()+' · Saved on this computer';
  renderDiscrepancy();renderPublicComparison();renderDecision();renderAnalysis();explain();renderFindings();
  document.querySelectorAll('[data-filter]').forEach(b=>b.classList.toggle('active',b.dataset.filter==='all'));
  $('evidence-list').innerHTML=report.evidence_files.map(f=>`<button class="evidence-file" data-file="${esc(f.name)}">${esc(f.name)}<small>${f.bytes.toLocaleString()} bytes</small></button>`).join('');
  $('evidence-list').querySelectorAll('[data-file]').forEach(b=>b.onclick=()=>evidence(b.dataset.file));
  $('exports').innerHTML=`<a href="/api/runs/${report.run_id}/report.html" target="_blank" rel="noopener">Open standalone report</a><a href="/api/runs/${report.run_id}/report.md" download>Download Markdown</a><a href="/api/runs/${report.run_id}/report.json" download>Download JSON</a>`;
  history();window.scrollTo(0,0);
}
$('run').onclick=async()=>{
  if(!selection||busy||reading)return;
  busy=true;notice('');$('run').disabled=true;$('run').textContent='Investigating…';$('loaded-description').textContent='Reading the evidence, checking calculations and preparing your explanation…';
  try{show(await api('/api/investigate',selection.example?{example:selection.example,label:$('experiment-name').value,analysis_plan:readAnalysisPlan()}:{files:selection.files,label:$('experiment-name').value,analysis_plan:readAnalysisPlan()}));}
  catch(e){notice(e.message);$('loaded-description').textContent='The investigation did not finish. Correct the issue above and try again.';}
  finally{busy=false;$('run').disabled=false;$('run').textContent='Run investigation';}
};
$('new-run').onclick=reset;$('run-again').onclick=reset;$('folder-input').onchange=loadFiles;$('files-input').onchange=loadFiles;
$('close-evidence').onclick=()=>$('evidence-dialog').close();
document.querySelectorAll('[data-filter]').forEach(b=>b.onclick=()=>{filter=b.dataset.filter;document.querySelectorAll('[data-filter]').forEach(x=>x.classList.toggle('active',x===b));renderFindings();});
(async()=>{try{const examples=await api('/api/examples');$('examples').closest('.example-panel').hidden=examples.length===0;$('examples').innerHTML=examples.map(e=>`<button class="example" data-example="${esc(e.id)}"><strong>${esc(e.name)}</strong><span>${esc(e.description)}</span></button>`).join('');$('examples').querySelectorAll('button').forEach(b=>b.onclick=()=>{if(busy)return;const example=examples.find(e=>e.id===b.dataset.example);setSelection({example:example.id,label:example.name,analysisPlan:example.analysis_plan,publicDataset:example.public_dataset,controlledExercise:example.controlled_exercise});document.querySelectorAll('.example').forEach(x=>x.classList.toggle('selected',x===b));});await history();}catch(e){notice(e.message);}})();

let guardrailImportError=null;
function addGuardrail(s={}){
  s=s&&typeof s==='object'&&!Array.isArray(s)?s:{};
  const host=$('guardrail-inputs');if(host.children.length>=10)return;
  const row=document.createElement('fieldset');row.className='guardrail-input';
  row.innerHTML=`<legend>Required guardrail</legend><div class="plan-grid"><label>Metric ID<input data-key="id" value="${esc(s.id||'')}"></label><label>Display name<input data-key="name" value="${esc(s.name||'')}"></label><label>Definition version<input data-key="version" value="${esc(s.version||'v1')}"></label><label>Preferred direction<select data-key="direction"><option value="lower">Lower is better (e.g. refunds)</option><option value="higher">Higher is better (e.g. retention)</option></select></label><label>Maximum acceptable harm (percentage points)<input data-key="max_harm_pp" type="number" min="0" max="100" step="0.1" value="${esc(s.max_harm_pp??'')}"></label></div><label>Exact binary metric definition<textarea data-key="definition" rows="2">${esc(s.definition||'')}</textarea></label><button type="button" class="button secondary">Remove guardrail</button>`;
  row.querySelector('select').value=s.direction||'lower';row.querySelector('button').onclick=()=>row.remove();host.appendChild(row);
}
function fillDecisionPlan(p){
  $('guardrail-inputs').replaceChildren();
  guardrailImportError=guardrailPlanError(p.guardrails);
  if(guardrailImportError)notice(guardrailImportError);else (p.guardrails||[]).forEach(addGuardrail);
  for(const id of ['guardrails-predeclared','guardrails-complete','guardrails-set-complete','business-review-complete'])$(id).checked=p[id.replaceAll('-','_')]===true;
  $('business-review-notes').value=p.business_review_notes||'';
}
function readDecisionPlan(){
  if(guardrailImportError)throw new Error(guardrailImportError);
  const p={guardrails:Array.from($('guardrail-inputs').children).map(row=>Object.fromEntries(Array.from(row.querySelectorAll('[data-key]')).map(el=>[el.dataset.key,el.dataset.key==='max_harm_pp'?(el.value===''?null:Number(el.value)):el.value.trim()]))),business_review_notes:$('business-review-notes').value.trim()};
  for(const id of ['guardrails-predeclared','guardrails-complete','guardrails-set-complete','business-review-complete'])p[id.replaceAll('-','_')]=$(id).checked;
  return p;
}
$('add-guardrail').onclick=()=>addGuardrail();
function renderDecision(){
  const d=current.decision,host=$('decision-summary');
  if(!d){host.className='treatment-analysis';host.innerHTML='<h2>Shipping review was not part of this saved run.</h2><p>Load the evidence and run again to assess guardrails and the decision summary. This saved result is unchanged.</p>';return;}
  host.className='treatment-analysis '+(d.status==='supported'?'improvement':d.status==='do_not_ship'?'harm':'blocked');
  const list=(title,items,empty)=>`<div><h3>${title}</h3>${items.length?`<ul>${items.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:`<p>${empty}</p>`}</div>`;
  host.innerHTML=`<div class="outcome-label">Shipping decision · conditional evidence review</div><h2>${esc(d.title)}</h2><div class="decision-reasons">${list((current.public_dataset||current.intake)?'What the snapshot establishes':'What supports a recommendation',d.supporting,'No supporting evidence established yet.')}${list('What blocks a recommendation',d.blockers,'No blockers under the saved declarations. Review the remaining assumptions below.')}</div><h3>Required guardrails</h3>${d.guardrails.length?d.guardrails.map(g=>`<article class="guardrail-result"><strong>${esc(g.name)} · ${esc({within_limit:'Within declared harm limit',harm:'Unacceptable harm',uncertain:'Safety uncertain',blocked:'Cannot assess'}[g.status])}</strong><p>${esc(g.explanation)}</p>${g.comparison?`<p class="small-note">${(100*g.comparison.confidence_level).toFixed(2)}% interval per metric, adjusted for ${d.guardrails.length} required guardrail(s). Control: ${g.comparison.control.purchasers}/${g.comparison.control.users}; treatment: ${g.comparison.treatment.purchasers}/${g.comparison.treatment.users} users with this outcome.</p>`:''}<details><summary>Definition and evidence</summary><p>${esc(g.definition||'Definition unresolved')} · ${esc(g.metric_version||'')}</p><p>Source: ${esc(g.source)}; ${esc(g.direction)} is better; harm limit ${esc(g.max_harm_pp)} percentage points. Inspect the original file in Evidence in this run.</p></details></article>`).join(''):'<p>No required guardrails declared. This does not establish safety.</p>'}<p class="next-action"><strong>What to do next</strong><br>${esc(d.next_action)}</p><details><summary>Remaining assumptions and problem-tree connection</summary>${list('Not independently established',d.unresolved,'')}<p>OP-1: a defensible decision. OP-5: benefit must survive guardrail review. OP-2 saves definitions and limits; OP-3/4 check population and calculations; OP-6 preserves reasoning; OP-7 brings it into this workflow.</p><p>${esc(d.method)}</p></details><p class="boundary">${esc(d.limitations)}</p>`;
}

function renderPublicComparison(){
  const p=current.public_comparison,host=$('public-comparison');host.hidden=!p;if(!p)return;
  const pct=v=>(v*100).toFixed(3)+'%', pp=v=>(v*100).toFixed(3)+' pp';
  const metricName=m=>m==='retention_7'?'Day-7 retention':'Day-1 retention';
  const rows=['retention_7','retention_1'].map(m=>{const a=p.all_users[m],b=p.analyst_population[m],r=p.readout.metrics[m];return `<tr><th>${metricName(m)}</th><td>${pct(a.control_rate)}<br><small>${a.control.retained_users.toLocaleString()}/${a.control.users.toLocaleString()}</small></td><td>${pct(a.treatment_rate)}<br><small>${a.treatment.retained_users.toLocaleString()}/${a.treatment.users.toLocaleString()}</small></td><td>${pp(a.difference)}<br><small>95% interval ${pp(a.difference_ci[0])} to ${pp(a.difference_ci[1])}</small></td><td>${pp(b.difference)}<br><small>Supplied readout: ${pp(r.difference)} (rounded)</small></td></tr>`;}).join('');
  host.innerHTML=`<div class="outcome-label">Retention snapshot · supplied readout comparison</div><h2>${current.controlled_exercise?'Supplied reference readout versus export':'Does Pebbles reproduce the retention result?'}</h2>${current.controlled_exercise?'<p>This auxiliary comparison uses the readout included in this packet. It is separate from the reported claim assessed above; it must not be assumed to be an original company result. The supplied export may be incomplete.</p>':''}<p class="next-action"><strong>${esc(p.population_warning||"These calculations describe the supplied export, not verified production completeness.")}</strong></p><p>Supplied-export result only: ${esc(p.interpretation)}</p><div class="scroll"><table class="replay-table"><thead><tr><th>Metric</th><th>Gate 30 · supplied export</th><th>Gate 40 · supplied export</th><th>Pebbles · supplied export</th><th>Export with notebook exclusion rule</th></tr></thead><tbody>${rows}</tbody></table></div><p><strong>${p.readout_checks.every(c=>c.matches)?'Supplied readout values reproduced at their displayed precision.':'Some supplied readout values disagree; inspect the comparison checks.'}</strong> The exclusion-rule replay checks rates, differences, z-test p-values and Wald interval bounds. Pebbles’ main interval uses Newcombe/Wilson; the notebook uses Wald. Both calculations are saved.</p><h3>What changes when we apply the notebook’s exclusion rule?</h3><p>All ${p.row_count.toLocaleString()} supplied-export users are included in this table. The notebook removes ${p.excluded_users.length} maximum-rounds player(s), leaving ${p.analyst_row_count.toLocaleString()}. We replay that separately because filtering on post-assignment behavior can change the population. ${esc(p.exclusion_note||"Applying the same exclusion rule does not establish matching populations.")}</p><p>Against an assumed 50/50 split, the sample-ratio p-value is ${esc(p.srm.display_p_value||(p.srm.p_value<0.000001?"< 0.000001":p.srm.p_value.toFixed(6)))}. The allocation contract is missing; this diagnostic does not establish correct randomization.</p><p><strong>Supplied recommendation:</strong> ${esc(p.readout.recommendation_summary)}</p><p class="boundary">${esc(p.readout.readout_kind)}. Retrospective, unadjusted per-metric intervals under independent-user assumptions. Day-1 retention is not a validated safety guardrail; no harm limit was supplied. Calendar dates, exposure logs and original decision criteria were not invented.</p><details><summary>Source, comparison checks and problem tree</summary><p>${esc(p.readout.source_url)}</p><p>OP-4: reproduce calculations and reconcile populations. OP-3: expose missing provenance. OP-5/OP-1: separate a retention finding from a justified shipping decision. OP-2/6 preserve definitions and source hashes; OP-7 makes the replay usable.</p><pre>${esc(JSON.stringify(p.readout_checks,null,2))}</pre></details>`;
}

function renderDiscrepancy(){
  const d=current.discrepancy,host=$('discrepancy-investigation');host.hidden=!d;if(!d)return;
  const metricLabel=d.metric==='retention_7'?'day-7':'day-1';
  const labels={lower_retention:`Lower ${metricLabel} retention`,higher_retention:`Higher ${metricLabel} retention`,inconclusive:'Direction unresolved'};
  const diagnosis={agreement:'The reported claim agrees with the supplied evidence.',denominator_mismatch:'The reported denominator does not match the users.',population_mismatch:'The export and reference contain different users or records.',metric_mismatch:'The reported counts belong to a different metric.',unexplained_counts:'The counts disagree; the cause is unresolved.'};
  const pp=x=>(x*100).toFixed(3)+' pp';
  const views=[['Reported claim',d.reported],['Recomputed from supplied export',d.supplied],['Recomputed from supplied reference',d.reference]];
  host.className='treatment-analysis '+(d.diagnosis==='agreement'?'improvement':'harm');
  host.innerHTML=`<div class="outcome-label">Controlled discrepancy investigation · ${esc(d.metric)}</div><h2>${esc(diagnosis[d.diagnosis])}</h2><p class="boundary">Introduced exercise, not a mistake attributed to the original analyst. The reference is supplied evidence, not verified production truth.</p><div class="scroll"><table class="replay-table"><thead><tr><th>Result source</th><th>Gate 30 retained / users</th><th>Gate 40 retained / users</th><th>Difference and 95% interval</th></tr></thead><tbody>${views.map(([label,c])=>`<tr><th>${label}</th><td>${c.control.retained_users.toLocaleString()} / ${c.control.users.toLocaleString()}<br>${(100*c.control_rate).toFixed(3)}%</td><td>${c.treatment.retained_users.toLocaleString()} / ${c.treatment.users.toLocaleString()}<br>${(100*c.treatment_rate).toFixed(3)}%</td><td>${pp(c.difference)}<br><small>${pp(c.difference_ci[0])} to ${pp(c.difference_ci[1])}</small></td></tr>`).join('')}</tbody></table></div><h3>${d.diagnosis==='agreement'?'Why they agree':'Why they disagree'}</h3><ul>${d.why.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><p>${d.reported_matches_supplied?'The reported claim matches the supplied export. Agreement alone does not establish that the export contains the intended population.':'The reported claim does not match a fresh calculation from the supplied export.'}</p><div class="next-action"><strong>${d.conclusion_changed?'The retention conclusion changes.':'The retention conclusion does not change.'}</strong><p>${esc(labels[d.reported_conclusion])} → ${esc(labels[d.reference_conclusion])}</p><p>Shipping readiness remains blocked in both views. ${d.diagnosis==='agreement'?'Agreement does not supply':'Resolving the discrepancy does not supply'} the missing original plan, instrumentation, guardrails or business review.</p></div><h3>Trace the evidence</h3>${d.evidence.map(e=>`<p><button class="source-link" data-file="${esc(e.file)}">${esc(e.file)}</button> · ${esc(e.locator)}</p>`).join('')}<h3>Population reconciliation</h3><p>Compared the supplied export with reference.csv by user ID: <strong>${d.population.missing_count.toLocaleString()} missing</strong>, <strong>${d.population.extra_count.toLocaleString()} extra</strong>, and <strong>${d.population.changed_count.toLocaleString()} changed</strong> user records. This checks agreement with the supplied reference, not production completeness.</p><details><summary>Detailed counts and user IDs</summary><pre>${esc(JSON.stringify({count_differences:d.count_differences,population:d.population},null,2))}</pre></details><p><strong>Next action:</strong> ${esc(d.next_action)}</p><details><summary>Method and problem-tree connection</summary><p>${esc(d.limits)}</p><p>OP-3: identify population differences. OP-4: trace disagreement to counts and definitions. OP-5: show whether the numerical conclusion changes. OP-2/6 preserve contracts and source fingerprints. OP-1/7 still require an analyst study to establish usefulness.</p></details>`;
  host.querySelectorAll('[data-file]').forEach(b=>b.onclick=()=>evidence(b.dataset.file));
}

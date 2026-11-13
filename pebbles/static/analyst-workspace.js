'use strict';
let analystView='investigation', analystSelected={}, analystReports={}, layoutTicket=0;
const originalWorkspaceRender=renderWorkspace;
const originalShow=show;
function taskDisclosure(title,node,open=false){const d=document.createElement('details');d.className='task-disclosure';d.open=open;const summary=document.createElement('summary');summary.textContent=title;d.append(summary,node);return d;}
function wrapTask(title,node){const parent=node.parentNode,next=node.nextSibling;const d=taskDisclosure(title,node);parent.insertBefore(d,next);return d;}
function experimentState(e){const d=e.decisions?.at(-1);if(d&&JSON.stringify(d.context.runs)!==JSON.stringify(e.runs))return 'Review needs renewal';if(d?.review)return 'Reviewed';if(d)return 'Awaiting review';return e.runs.length?'Investigating':'Needs evidence';}
function experimentNav(e){return `<div class="workspace-top"><button class="text-button" id="back-experiments">Experiments</button><span>/</span><span>${esc(e.name)}</span></div><header class="analyst-header"><div><h1>${esc(e.name)}</h1><p>${esc(e.owner||'No owner assigned')} <span class="separator">/</span> ${e.runs.length} saved runs</p></div><span class="status-pill">${esc(experimentState(e))}</span></header><nav class="workspace-tabs" aria-label="Experiment views"><button data-work-tab="investigation" ${analystView==='investigation'?'aria-current="page"':''}>Investigation</button><button data-work-tab="decision" ${analystView==='decision'?'aria-current="page"':''}>Decision <span>${e.decisions?.length||0}</span></button></nav>`;}
renderWorkspace=function(){
  originalWorkspaceRender();const ticket=++layoutTicket;
  const host=$('workspace-view'),e=workspaceData.experiments.find(x=>x.id===activeExperiment);
  const create=$('create-experiment');
  if(!e){
    host.innerHTML=`<header class="analyst-header"><div><h1>Experiments</h1><p>Pick up an investigation. See what needs a decision.</p></div><button class="button primary" id="queue-import">Import CSV</button></header><div class="queue-tools"><label class="search-field">Find an experiment<input id="experiment-search" type="search" placeholder="Search name or owner"></label><button class="button secondary" id="queue-create">New experiment</button></div><div class="experiment-table"><div class="queue-row queue-labels"><span>Experiment</span><span>Evidence</span><span>Follow-ups</span><span>Review</span></div>${workspaceData.experiments.map(x=>`<button class="queue-row" data-experiment="${esc(x.id)}" data-search="${esc((x.name+' '+x.owner).toLowerCase())}"><span><strong>${esc(x.name)}</strong><small>${esc(x.owner||'Unassigned')}</small><small class="mobile-queue-meta">${x.runs.length} runs · ${x.followups.filter(f=>!['resolved','dismissed'].includes(f.status)).length} open follow-ups</small></span><span>${x.runs.length} runs</span><span>${x.followups.filter(f=>!['resolved','dismissed'].includes(f.status)).length} open</span><span class="queue-status">${esc(experimentState(x))}</span></button>`).join('')||'<div class="empty-state"><h2>Your first investigation starts here.</h2><p>Create an experiment, then attach a saved run or import a CSV.</p></div>'}</div><p id="queue-no-match" hidden>No experiments match that search.</p><div id="queue-create-host"></div>`;
    const disclosure=taskDisclosure('Create experiment',create);$('queue-create-host').append(disclosure);
    $('queue-create').onclick=()=>{disclosure.open=!disclosure.open;if(disclosure.open)create.elements.name.focus();};
    $('queue-import').onclick=()=>openIntake();
    host.querySelectorAll('[data-experiment]').forEach(b=>b.onclick=()=>{analystView='investigation';openWorkspace(b.dataset.experiment);});
    $('experiment-search').oninput=ev=>{let n=0;host.querySelectorAll('[data-experiment]').forEach(b=>{b.hidden=!b.dataset.search.includes(ev.target.value.toLowerCase());if(!b.hidden)n++;});$('queue-no-match').hidden=!!n;};
    location.replace('#experiments');return;
  }
  const originalChildren=Array.from(host.children);
  const attach=$('attach-run'),track=$('track-finding');
  const recommend=$('recommend-form')?.parentElement,records=recommend?.nextElementSibling;
  const revision=$('revision-form')?.parentElement,comparisons=revision?.nextElementSibling;
  const followups=originalChildren.find(n=>n.querySelector('[data-followup]')||n.textContent.startsWith('Follow-ups'));
  const tree=originalChildren.at(-1);
  host.innerHTML=experimentNav(e)+'<div id="analyst-content"></div>';
  $('back-experiments').onclick=()=>openWorkspace(null);
  host.querySelectorAll('[data-work-tab]').forEach(b=>b.onclick=()=>{analystView=b.dataset.workTab;renderWorkspace();});
  location.replace('#experiment/'+e.id+'/'+analystView);
  const content=$('analyst-content');
  if(analystView==='decision'){
    const intro=document.createElement('div');intro.className='section-intro';intro.innerHTML='<div><h2>Decision record</h2><p>Your recommendation and review, tied to the evidence you saw.</p></div><button class="button primary" id="compose-decision">New recommendation</button>';content.append(intro);
    if(recommend){const formSection=taskDisclosure('Prepare a recommendation',recommend);content.append(formSection);$('compose-decision').onclick=()=>{formSection.open=true;recommend.querySelector('select').focus();};}
    else{$('compose-decision').disabled=true;content.insertAdjacentHTML('beforeend','<p>Attach an investigation run before preparing a recommendation.</p>');}
    if(recommend){const form=$('recommend-form');form.elements.run_id.value=e.runs.includes(analystSelected[e.id])?analystSelected[e.id]:e.runs.at(-1);form.elements.author.value=e.owner||'';form.elements.run_id.onchange();}
    if(records){records.classList.add('decision-records');content.append(records);records.querySelectorAll('article').forEach((article,i)=>{if(i){const h=article.querySelector('h3');wrapTask('Earlier record: '+h.textContent,article);}});}
  }else{
    content.innerHTML=`<div class="run-toolbar"><label>Evidence run<select id="analyst-run">${e.runs.slice().reverse().map((id,i)=>`<option value="${esc(id)}">${esc(workspaceRuns.find(r=>r.run_id===id)?.source_label||id)}${i===0?' · last attached':''}</option>`).join('')}</select></label><button class="button secondary" id="inspect-full">Open full report</button><button class="button primary" id="correct-evidence">Add corrected evidence</button></div><div id="investigation-overview" aria-live="polite"><p>Loading evidence summary…</p></div><div class="investigation-columns"><section id="investigation-work"><div class="section-intro"><h2>Investigation work</h2></div></section><aside id="investigation-side"><h2>Evidence & history</h2></aside></div>`;
    const selected=analystSelected[e.id];if(e.runs.includes(selected))$('analyst-run').value=selected;
    if(!e.runs.length){$('analyst-run').disabled=true;$('inspect-full').disabled=true;$('correct-evidence').disabled=true;$('investigation-overview').innerHTML='<div class="empty-state"><h2>Bring in the evidence.</h2><p>Import evidence directly into this experiment. New runs will be attached automatically.</p><button id="empty-import" class="button primary">Import CSV into this experiment</button></div>';}
    if($('empty-import'))$('empty-import').onclick=()=>openIntake();
    $('investigation-side').append(taskDisclosure('Attach a saved run',attach));
    if(track)$('investigation-work').append(taskDisclosure('Request evidence or track a finding',track));
    if(followups){followups.classList.add('compact-followups');followups.querySelectorAll('form[data-followup]').forEach(f=>{const item=e.followups.find(x=>x.id===f.dataset.followup);const label=(item?.status||'Follow-up')+' · '+f.querySelector('h3').textContent;wrapTask(label,f);});$('investigation-work').append(followups);}
    if(comparisons){comparisons.classList.add('compact-comparisons');comparisons.querySelectorAll('article').forEach(a=>{const label=a.querySelector('h3').textContent;wrapTask(label,a);});$('investigation-side').append(comparisons);}
    if(revision)$('investigation-side').append(taskDisclosure('Revise a prepared evidence package',revision));
    if(tree)$('investigation-side').append(tree);
    const load=async()=>{const rid=$('analyst-run').value;if(!rid)return;analystSelected[e.id]=rid;const request=++layoutTicket;$('investigation-overview').innerHTML='<p class="loading-state">Loading the selected run…</p>';$('investigation-side').querySelector('.source-list')?.remove();$('inspect-full').disabled=true;$('correct-evidence').disabled=true;try{const r=analystReports[rid]||await api('/api/runs/'+rid);analystReports[rid]=r;if(request!==layoutTicket||analystView!=='investigation')return;renderInvestigationSummary(r,e);$('inspect-full').disabled=false;$('correct-evidence').disabled=false;}catch(err){if(request===layoutTicket){$('investigation-overview').innerHTML='<p class="empty-state">This run could not be loaded. Select another run or try again.</p>';notice(err.message);}}};
    $('analyst-run').onchange=load;$('inspect-full').onclick=()=>{const r=analystReports[$('analyst-run').value];if(r)show(r);};
    $('correct-evidence').onclick=()=>{const r=analystReports[$('analyst-run').value];if(!r)return;if(r.intake)openIntake(r);else if(revision){revision.parentElement.open=true;revision.querySelector('select').value=r.run_id;revision.querySelector('textarea').focus();}};
    load();
  }
};
function findingAction(r,f,e){
  const tracked=e.followups.find(x=>x.run_id===r.run_id&&x.finding_id===f.check_id);
  if(tracked)return `<p class="finding-action"><button type="button" class="button secondary" data-view-followup="${esc(tracked.id)}">View evidence request</button> <span>${esc(tracked.status)}</span></p>`;
  return `<details class="finding-action"><summary>Request evidence</summary><form data-request-finding="${esc(f.check_id)}"><p class="small-note">Saved to this experiment and this finding. No message is sent.</p><label class="name-label">Evidence request<textarea name="request" required maxlength="4000">${esc(f.next_evidence_request||'')}</textarea></label><label class="name-label">Follow-up owner<input name="owner" maxlength="120" placeholder="Optional"></label><label class="name-label">Investigation notes<textarea name="notes" maxlength="4000" placeholder="Optional context"></textarea></label><button class="button primary">Save evidence request</button></form></details>`;
}
function revealFollowup(id){
  const form=Array.from(document.querySelectorAll('[data-followup]')).find(f=>f.dataset.followup===id);
  if(!form)return;
  form.closest('details').open=true;
  form.scrollIntoView({block:'center',behavior:'smooth'});
  form.elements.request.focus({preventScroll:true});
}
function renderInvestigationSummary(r,e){
  const d=r.decision||{},i=r.intake,p=r.public_comparison;
  const c=i?.comparison||r.discrepancy?.reference||p?.all_users?.retention_7||r.analysis?.comparison;
  const title=i?.mapping.metric|| (p?'Day-7 retention':r.analysis?.title||'Experiment result');
  const percent=n=>(100*n).toFixed(2)+'%',pp=n=>(n>=0?'+':'')+(100*n).toFixed(3)+' pp';
  const label=r.discrepancy?('Reference result: '+r.discrepancy.reference_conclusion.replaceAll('_',' ')):i?.direction==='lower'?'Lower outcome rate':i?.direction==='higher'?'Higher outcome rate':i?'Direction unresolved':r.analysis?.title||p?.interpretation||r.headline;
  const summary=$('investigation-overview');
  summary.innerHTML=`<div class="result-sheet"><div class="result-sheet-main"><div class="section-intro"><h2>${esc(title)}</h2><span class="quiet-label">${r.discrepancy?'Supplied reference':'Selected run'}</span></div><h3 class="result-conclusion">${esc(label)}</h3>${c?`<div class="rate-row"><div><span>${esc(i?.mapping.control||r.analysis?.plan?.control||'Control')}</span><strong>${percent(c.control_rate)}</strong><small>${c.control.users.toLocaleString()} users</small></div><span class="rate-versus">vs</span><div><span>${esc(i?.mapping.treatment||r.analysis?.plan?.treatment||'Treatment')}</span><strong>${percent(c.treatment_rate)}</strong><small>${c.treatment.users.toLocaleString()} users</small></div></div><div class="effect-summary"><strong>${pp(c.difference)}</strong><span>Treatment minus control${c.difference_ci?`<br>95% interval ${pp(c.difference_ci[0])} to ${pp(c.difference_ci[1])}`:'<br>Descriptive only; uncertainty not assessed'}</span></div>`:'<p>Inspect the findings and source report for the available calculations.</p>'}<p class="scope-note">${esc(i?'Conditional on declared independent users and a fixed window. A higher rate is not automatically better.':r.scope)}</p><details><summary>Interpretation and method</summary><p>${esc(i?.explanation||r.analysis?.explanation||p?.interpretation||r.headline)}</p><p>${esc(d.limitations||'')}</p></details></div><aside class="decision-rail"><span class="status-pill">${esc(d.status||'Not assessed')}</span><h3>${d.status==='blocked'?'Not ready for a shipping decision':esc(d.title||'Decision evidence')}</h3><ul>${(d.blockers||[]).slice(0,3).map(x=>`<li>${esc(x)}</li>`).join('')}</ul>${(d.blockers||[]).length>3?`<details><summary>${d.blockers.length-3} more blockers</summary><ul>${d.blockers.slice(3).map(x=>`<li>${esc(x)}</li>`).join('')}</ul></details>`:''}<button id="summary-decision" class="button secondary">Review decision</button><p class="small-note">A recommendation can be hold, stop or iterate. Missing evidence stays unresolved.</p></aside></div><section class="finding-list"><div class="section-intro"><h2>Findings</h2><span>${r.findings.length} checks in this run</span></div>${r.findings.map(f=>`<details class="finding-row"><summary><span class="finding-status ${f.evidence_outcome==='Verified'?'supported':''}">${esc(f.evidence_outcome==='Verified'?'Supported':f.evidence_outcome==='Failed'?'Needs attention':'Unresolved')}</span><span>${esc(f.question)}</span></summary><div class="finding-content"><p>${esc(f.explanation)}</p>${f.next_evidence_request?`<p><strong>Next evidence:</strong> ${esc(f.next_evidence_request)}</p>`:''}${findingAction(r,f,e)}<details><summary>Calculations and source references</summary><pre>${esc(JSON.stringify({values:f.values,evidence:f.evidence},null,2))}</pre></details></div></details>`).join('')}</section>`;
  summary.querySelectorAll('[data-view-followup]').forEach(b=>b.onclick=()=>revealFollowup(b.dataset.viewFollowup));
  summary.querySelectorAll('[data-request-finding]').forEach(form=>form.onsubmit=async ev=>{
    ev.preventDefault();
    const result=await workspaceSave({action:'track',experiment_id:e.id,run_id:r.run_id,finding_id:form.dataset.requestFinding,...Object.fromEntries(new FormData(form))},form);
    if(result){const saved=result.experiment.followups.find(f=>f.run_id===r.run_id&&f.finding_id===form.dataset.requestFinding);if(saved)revealFollowup(saved.id);}
  });
  $('summary-decision').onclick=()=>{analystView='decision';renderWorkspace();};
  const side=$('investigation-side');side.querySelector('.source-list')?.remove();const files=document.createElement('div');files.className='source-list';files.innerHTML=`<h3>Files in this run</h3>${(r.evidence_files||[]).map(f=>`<button class="source-link" data-source="${esc(f.name)}"><span>${esc(f.name)}</span><small>${(f.bytes/1024).toFixed(0)} KB</small></button>`).join('')}<a class="source-link" href="/api/runs/${esc(r.run_id)}/report.html" target="_blank" rel="noopener">Standalone report</a>`;side.insertBefore(files,side.children[1]);files.querySelectorAll('[data-source]').forEach(b=>b.onclick=()=>{current=r;evidence(b.dataset.source);});
}
show=function(r){const attached=workspaceData?.experiments.some(e=>e.runs.includes(r.run_id));if(attached&&r.decision?.next_action?.startsWith('Attach this run'))r={...r,decision:{...r.decision,next_action:'Track the missing evidence and request review before making a shipping decision.'}};originalShow(r);$('run-again').textContent=attached?'Import more evidence':'Load another experiment';$('result-view').querySelector('.report-back')?.remove();if(activeExperiment&&workspaceData?.experiments.some(e=>e.id===activeExperiment&&e.runs.includes(r.run_id))){const back=document.createElement('button');back.className='text-button report-back';back.textContent='Back to investigation';back.onclick=()=>{analystView='investigation';analystSelected[activeExperiment]=r.run_id;openWorkspace(activeExperiment);};$('result-view').querySelector('.report-back')?.remove();$('result-view').prepend(back);}};
$('open-workspace').textContent='Experiments';$('open-workspace').onclick=()=>openWorkspace(null);
$('new-run').textContent='Import / run evidence';
const sidebar=document.querySelector('.sidebar');const quick=document.createElement('button');quick.className='new-button';quick.textContent='Import CSV';quick.onclick=()=>openIntake();sidebar.insertBefore(quick,$('new-run'));
const match=location.hash.match(/^#experiment\/([^/]+)\/(investigation|decision)$/);if(match){analystView=match[2];openWorkspace(match[1]);}else openWorkspace(null);

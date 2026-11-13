'use strict';
let workspaceData=null, workspaceRuns=[], activeExperiment=null, workspaceBusy=false;
const workflowStatuses=['open','waiting for evidence','ready to recheck','resolved','dismissed'];
async function openWorkspace(id=activeExperiment){
  if(busy)return;
  try{
    const [data,runs]=await Promise.all([api('/api/workspace'),api('/api/runs')]);
    workspaceData=data;workspaceRuns=runs;activeExperiment=id;
    $('intake-view').hidden=true;$('load-view').hidden=true;$('result-view').hidden=true;$('workspace-view').hidden=false;notice('');
    renderWorkspace();window.scrollTo(0,0);
  }catch(e){notice(e.message);}
}
async function workspaceSave(body,form){
  if(workspaceBusy)return;
  workspaceBusy=true;const buttons=form?Array.from(form.querySelectorAll('button')):[];buttons.forEach(b=>b.disabled=true);
  try{const result=await api('/api/workspace',body);if(body.action==='create')analystView='investigation';await openWorkspace(result.experiment.id);}
  catch(e){notice(e.message);}
  finally{workspaceBusy=false;buttons.forEach(b=>b.disabled=false);}
}
function renderWorkspace(){
  const host=$('workspace-view'),experiments=workspaceData.experiments;
  const e=experiments.find(x=>x.id===activeExperiment);
  const runName=id=>workspaceRuns.find(r=>r.run_id===id)?.source_label||'Unavailable run';
  host.innerHTML=`<header class="page-header"><span class="step">Investigation workspace</span><h1>Keep the investigation moving.</h1><p>Track evidence requests and return to unfinished work. Workflow status never changes a scientific finding or shipping blocker.</p></header>
  <div class="load-grid"><section class="load-panel"><h2>Your experiments</h2><div class="history">${experiments.map(x=>`<button data-experiment="${esc(x.id)}"><strong>${esc(x.name)}</strong><small>${x.followups.filter(f=>!['resolved','dismissed'].includes(f.status)).length} active follow-ups · ${x.runs.length} runs</small></button>`).join('')||'<p>No experiments yet. Create one below.</p>'}</div>
  <form id="create-experiment"><h3>Create an experiment</h3><label class="name-label">Experiment workspace name<input name="name" maxlength="120" required></label><label class="name-label">Experiment owner<input name="owner" maxlength="120"></label><button class="button primary">Create experiment</button></form></section>
  <section class="load-panel">${e?`<h2>${esc(e.name)}</h2><p>Owner: ${esc(e.owner||'Unassigned')} · Created ${esc(new Date(e.created_at).toLocaleString())}</p><p class="small-note">Local owner labels are not authenticated identities.</p>
  <h3>Attached runs</h3>${e.runs.map(id=>`<p><button class="button secondary" data-open-run="${esc(id)}">Open ${esc(runName(id))}</button><small> · ${esc(id.slice(0,8))}</small></p>`).join('')||'<p>No runs attached. Existing investigations remain unchanged.</p>'}
  <form id="attach-run"><label class="name-label">Run to attach<select name="run_id" required><option value="">Choose a saved run</option>${workspaceRuns.filter(r=>!e.runs.includes(r.run_id)).map(r=>`<option value="${esc(r.run_id)}">${esc(r.source_label)} · ${esc(new Date(r.created_at).toLocaleString())} · ${esc(r.run_id.slice(0,8))}</option>`).join('')}</select></label><button class="button secondary">Attach run</button></form>
  ${e.runs.length?`<form id="track-finding"><h3>Track a finding</h3><label class="name-label">Source run<select id="finding-run" name="run_id" required><option value="">Choose an attached run</option>${e.runs.map(id=>`<option value="${esc(id)}">${esc(runName(id))} · ${esc(id.slice(0,8))}</option>`).join('')}</select></label><label class="name-label">Finding<select id="finding-select" name="finding_id" required disabled><option value="">Choose a source run first</option></select></label><label class="name-label">Evidence request<textarea name="request" maxlength="4000" required placeholder="What evidence do we need, and why?"></textarea></label><label class="name-label">Follow-up owner<input name="owner" maxlength="120"></label><label class="name-label">Investigation notes<textarea name="notes" maxlength="4000"></textarea></label><button class="button primary">Track finding</button></form>`:''}`:'<h2>Select or create an experiment</h2><p>Attach a saved run, track a finding and record the evidence you need next.</p>'}</section></div>
  ${e&&e.runs.length?decisionPanel(e,runName):''}
  ${e&&e.runs.length?revisionPanel(e,runName):''}
  ${e?`<section class="findings-section"><h2>Follow-ups</h2>${e.followups.map(f=>`<form class="followup load-panel" data-followup="${esc(f.id)}"><h3>${esc(f.question)}</h3><p>Original check: <strong>${esc(f.check_outcome)}</strong> · ${esc(f.finding_id)} · Run ${esc(f.run_id.slice(0,8))}</p><button type="button" class="button secondary" data-open-run="${esc(f.run_id)}">Open source run</button><p>Workflow: <strong>${esc(f.status)}</strong> · Saved ${esc(new Date(f.updated_at).toLocaleString())}</p>${f.rechecks?.length?`<p><strong>Latest recheck: ${esc(f.rechecks[f.rechecks.length-1].outcome)}</strong> · Run ${esc(f.rechecks[f.rechecks.length-1].run_id.slice(0,8))}. Review the revision comparison before closing this follow-up.</p>`:""}<label class="name-label">Workflow status<select name="status">${workflowStatuses.map(s=>`<option ${s===f.status?'selected':''}>${esc(s)}</option>`).join('')}</select></label><label class="name-label">Owner<input name="owner" maxlength="120" value="${esc(f.owner)}"></label><label class="name-label">Requested evidence<textarea name="request" maxlength="4000" required>${esc(f.request)}</textarea></label><label class="name-label">Notes or resolution rationale<textarea name="notes" maxlength="4000">${esc(f.notes)}</textarea></label><p class="small-note">Resolved and dismissed require a rationale. These labels do not clear analytical blockers; new evidence must be investigated separately.</p><button class="button primary">Save follow-up</button></form>`).join('')||'<p>No findings tracked yet.</p>'}<details><summary>Activity history</summary>${e.events.slice().reverse().map(ev=>`<p><strong>${esc(ev.action)}</strong> · ${esc(new Date(ev.at).toLocaleString())}</p><pre>${esc(JSON.stringify(ev.details,null,2))}</pre>`).join('')}</details></section>`:''}
  <details class="load-panel"><summary>Connection to the problem tree</summary><p>OP-3/OP-4: follow up on integrity and reconciliation findings. OP-6: preserve run links and investigation history. OP-7: resume work in one place. OP-1/OP-5: workflow progress does not prove validity or authorize shipping.</p><p>M1 tracks the investigation; M2 preserves evidence revisions and compares reruns. OP-2/4/5 connect changed definitions and calculations to changed conclusions. Reviewed decisions remain M4.</p></details>`;
  host.querySelectorAll('[data-experiment]').forEach(b=>b.onclick=()=>openWorkspace(b.dataset.experiment));
  host.querySelectorAll('[data-open-run]').forEach(b=>b.onclick=async()=>{try{show(await api('/api/runs/'+b.dataset.openRun));}catch(err){notice(err.message);}});
  $('create-experiment').onsubmit=ev=>{ev.preventDefault();workspaceSave({action:'create',...Object.fromEntries(new FormData(ev.target))},ev.target);};
  if(!e)return;
  bindRevision(e);
  bindDecisions(e);
  $('attach-run').onsubmit=ev=>{ev.preventDefault();workspaceSave({action:'attach',experiment_id:e.id,...Object.fromEntries(new FormData(ev.target))},ev.target);};
  if($('finding-run')){
    let ticket=0;
    $('finding-run').onchange=async ev=>{const mine=++ticket,select=$('finding-select');select.disabled=true;select.innerHTML='<option value="">Loading findings…</option>';if(!ev.target.value){select.innerHTML='<option value="">Choose a source run first</option>';return;}
      try{const run=await api('/api/runs/'+ev.target.value);if(mine!==ticket)return;select.innerHTML='<option value="">Choose a finding</option>'+run.findings.map(f=>`<option value="${esc(f.check_id)}">${esc(f.check_id)} · ${esc(f.question)} · ${esc(f.evidence_outcome||f.execution_state)}</option>`).join('');select.disabled=false;}catch(err){notice(err.message);}
    };
    $('track-finding').onsubmit=ev=>{ev.preventDefault();workspaceSave({action:'track',experiment_id:e.id,...Object.fromEntries(new FormData(ev.target))},ev.target);};
  }
  host.querySelectorAll('[data-followup]').forEach(form=>form.onsubmit=ev=>{ev.preventDefault();const f=e.followups.find(x=>x.id===form.dataset.followup);workspaceSave({action:'update',experiment_id:e.id,followup_id:f.id,revision:f.revision,...Object.fromEntries(new FormData(form))},form);});
}
$('open-workspace').onclick=()=>openWorkspace();

function resultSummary(r){
  if(!r)return 'Not assessed';
  const words=value=>String(value).replaceAll('_',' ');
  const population=r.control&&r.treatment?` · control ${r.control.users.toLocaleString()} users / treatment ${r.treatment.users.toLocaleString()} users`:'';
  return `${r.basis}: ${words(r.conclusion)}${population}${r.difference!==undefined?` · ${(r.difference*100).toFixed(3)} percentage points (95% interval ${(r.interval[0]*100).toFixed(3)} to ${(r.interval[1]*100).toFixed(3)})`:''}${r.reported_conclusion?` · reported claim: ${words(r.reported_conclusion)}`:''}`;
}
function revisionPanel(e,runName){
  return `<section class="load-panel"><h2>Revise evidence and rerun</h2><p>For guided CSV imports, open the original run and choose “Import corrected CSV with this mapping”. For other runs, upload a complete evidence package, including inventory.json. Unselected files are not inherited. Select a parent from this same experiment and explain the correction. Original runs remain unchanged.</p><form id="revision-form"><label class="name-label">Parent run<select name="parent_run_id" required><option value="">Choose the run to revise</option>${e.runs.map(id=>`<option value="${esc(id)}">${esc(runName(id))} · ${esc(id.slice(0,8))}</option>`).join('')}</select></label><label class="name-label">Revision reason<textarea name="reason" required maxlength="4000" placeholder="What evidence changed and why? Confirm this is the same experiment."></textarea></label><label class="name-label">Revision name<input name="label" required maxlength="120" placeholder="Corrected export"></label><label class="name-label">Complete revised evidence package<input id="revision-files" type="file" multiple accept=".json,.jsonl,.csv,.sql,.txt,.ipynb" required></label><p id="revision-preview">Choose files to preview the replacement package. Explicit user-entered analysis settings are retained; otherwise the new configuration supplies the settings.</p><button class="button primary">Run evidence revision</button></form></section>
  <section class="findings-section"><h2>Revision comparisons</h2>${(e.revisions||[]).slice().reverse().map(r=>{const c=r.comparison;return `<article class="load-panel"><h3>${esc(runName(r.run_id))}</h3><p>${esc(r.reason)}</p><p>Parent ${esc(r.parent_run_id.slice(0,8))} → revision ${esc(r.run_id.slice(0,8))}</p><button class="button secondary" data-open-run="${esc(r.parent_run_id)}">Open original run</button> <button class="button secondary" data-open-run="${esc(r.run_id)}">Open revised run</button><h4>Conclusion before and after</h4><p><strong>Before:</strong> ${esc(resultSummary(c.before_result))}</p><p><strong>After:</strong> ${esc(resultSummary(c.after_result))}</p><p><strong>Shipping status:</strong> ${esc(c.before_decision.status)} → ${esc(c.after_decision.status)}. A resolved check does not automatically support shipping.</p>${c.before_result.export_treatment&&c.after_result.export_treatment?`<h4>Supplied export population</h4><p>Control users: ${c.before_result.export_control.users.toLocaleString()} → ${c.after_result.export_control.users.toLocaleString()}. Treatment users: ${c.before_result.export_treatment.users.toLocaleString()} → ${c.after_result.export_treatment.users.toLocaleString()}.</p><p>Treatment retained users: ${c.before_result.export_treatment.retained_users.toLocaleString()} → ${c.after_result.export_treatment.retained_users.toLocaleString()}. Review changed files before attributing a cause.</p>`:""}<h4>Evidence changes</h4><ul>${c.files.map(f=>`<li>${esc(f.file)}: ${esc(f.change)}</li>`).join('')||'<li>No input file hashes changed.</li>'}</ul><p>Analysis settings or method changed: <strong>${c.settings_changed?'Yes — inspect settings below':'No'}</strong>. File changes may also include metric definitions; inspect the sources.</p><h4>Checks before and after</h4><div class="scroll"><table><thead><tr><th>Check</th><th>Before</th><th>After</th></tr></thead><tbody>${c.findings.map(f=>`<tr><td>${esc(f.check_id)} · ${esc(f.question)}</td><td>${esc(f.before)}</td><td>${esc(f.after)}</td></tr>`).join('')}</tbody></table></div><h4>Remaining shipping blockers</h4><ul>${c.after_decision.blockers.map(x=>`<li>${esc(x)}</li>`).join('')||'<li>None reported. Inspect the decision assumptions.</li>'}</ul><details><summary>Changed blockers, populations, settings and file fingerprints</summary><pre>${esc(JSON.stringify(c,null,2))}</pre></details><p>${esc(c.limits)}</p><p>Tracked findings are ready for review after a verified recheck; failed or absent rechecks reopen them. Original run outcomes are preserved.</p></article>`;}).join('')||'<p>No revisions yet.</p>'}</section>`;
}
function bindRevision(e){
  const form=$('revision-form');if(!form)return;
  $('revision-files').onchange=ev=>{const files=Array.from(ev.target.files);$('revision-preview').textContent=`${files.length} files selected: ${files.map(f=>f.name).join(', ')}. This replaces the entire package for the new run; originals remain saved.`;};
  form.onsubmit=async ev=>{
    ev.preventDefault();if(workspaceBusy)return;workspaceBusy=true;
    const button=form.querySelector('button');button.disabled=true;button.textContent='Investigating revision…';
    try{
      const chosen=Array.from($('revision-files').files);
      if(!chosen.length||chosen.length>10||chosen.reduce((n,f)=>n+f.size,0)>50000000)throw new Error('Choose 1–10 files totaling at most 50 MB.');
      if(!chosen.some(f=>f.name==='inventory.json'))throw new Error('The complete package needs inventory.json with current hashes.');
      const files=await Promise.all(chosen.map(async f=>({name:f.name,content:await f.text()})));
      const values=Object.fromEntries(new FormData(form));
      const report=await api('/api/investigate',{files,label:values.label,revision:{experiment_id:e.id,parent_run_id:values.parent_run_id,reason:values.reason}});
      await finishInvestigation(report,e.id);
    }catch(err){notice(err.message);}
    finally{workspaceBusy=false;button.disabled=false;button.textContent='Run evidence revision';}
  };
}

// Capture the destination when entering an import, not from a later global selection.
function importContext(){
  const e=workspaceData?.experiments.find(e=>e.id===activeExperiment);
  if(!e)return null;
  if(!$('workspace-view').hidden)return e;
  if(!$('result-view').hidden&&current&&e.runs.includes(current.run_id))return e;
  return null;
}
async function finishInvestigation(report,experimentId=null){
  if(!experimentId){show(report);return;}
  busy=false;analystView='investigation';analystSelected[experimentId]=report.run_id;
  await openWorkspace(experimentId);
}

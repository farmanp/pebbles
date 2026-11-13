'use strict';
async function openIntake(parent=null){
  const host=$('intake-view');let content='',filename='',previewTicket=0,validated=false,working=false;
  const context=importContext();
  const mapping={...(parent?.intake?.mapping||{})};
  if(!parent&&context)mapping.experiment=context.name;
  let experiments=[];
  if(parent){try{experiments=(await api('/api/workspace')).experiments.filter(e=>e.runs.includes(parent.run_id));}catch(e){notice(e.message);return;}}
  const destination=parent?(experiments.find(e=>e.id===context?.id)|| (experiments.length===1?experiments[0]:null)):context;
  $('load-view').hidden=true;$('result-view').hidden=true;$('workspace-view').hidden=true;host.hidden=false;notice('');
  host.innerHTML=`<header class="page-header"><span class="step">Guided CSV intake</span><h1>${parent?'Correct the evidence':'Start with your export.'}</h1>${destination?`<p><strong>${esc(destination.name)}</strong> · This run will be attached here automatically.</p>`:''}<p>One row per user, two variants and one binary outcome. Pebbles preserves the source CSV and your mapping; it does not infer missing assignment or exposure logs.</p></header><section class="load-panel"><form id="intake-form"><label class="name-label">Investigation name<input name="label" required maxlength="120" value="${esc(parent?parent.source_label+' · correction':destination?.name||'CSV investigation')}"></label><label class="name-label">CSV file<input id="intake-file" type="file" accept=".csv" required></label><p id="csv-description">UTF-8, comma-separated; up to 100,000 rows and 20 MB. Outcome values: 0/1 or true/false. Blank outcomes are never treated as false.</p><div id="csv-mapping" hidden><h2>Map and confirm meaning</h2>${['unit','variant','outcome'].map((k,i)=>`<label class="name-label">${['User ID column','Variant column','Binary outcome column'][i]}<select name="${k}" required></select></label>`).join('')}${[['control','Control value'],['treatment','Treatment value'],['experiment','Experiment identity'],['metric','Metric meaning (what does true / 1 mean?)'],['population','Population and export filters'],['window','Observation window (dates and follow-up duration)']].map(([k,label])=>`<label class="name-label">${label}<input name="${k}" required maxlength="1000" value="${esc(mapping[k]||'')}"></label>`).join('')}<label class="name-label">Study design<select name="design" required><option value="">Choose the design</option><option value="independent-fixed-binary">Fixed-horizon, independent users, binary outcome</option><option value="clustered">Clustered or repeated-user observations</option><option value="sequential">Sequential / repeatedly inspected for stopping</option><option value="unknown">Unknown or other</option></select></label><p>Only the first design is supported. Confirm the experiment has ended and each user has a complete observation over the same defined window. Snapshot declarations cannot prove randomization or production completeness.</p><label><input name="confirmed" type="checkbox" required> I confirm this mapping, population and completed fixed-window independent-user design.</label>${parent?`<h2>Link the correction</h2>${destination?`<input type="hidden" name="experiment_id" value="${esc(destination.id)}">`:`<label class="name-label">Experiment workspace<select name="experiment_id" required><option value="">Choose the workspace containing the original</option>${experiments.map(e=>`<option value="${esc(e.id)}">${esc(e.name)}</option>`).join('')}</select></label>`}<label class="name-label">Revision reason<textarea name="reason" required maxlength="4000"></textarea></label><p>${experiments.length?'The original run will be preserved. Confirm this CSV is the same experiment.':'Attach the original run to an experiment workspace before creating a correction.'}</p>`:''}<button type="button" id="preview-csv" class="button secondary">Validate mapping and preview</button><div id="csv-validation" role="status"></div><button id="run-csv" class="button primary" disabled>Run CSV investigation</button></div></form></section><details class="load-panel"><summary>Connection to the problem tree</summary><p>OP-2: explicit metric and scope. OP-3: missing values, duplicate users and arm counts. OP-4: reproducible calculations. OP-5: supported-design boundary. OP-6: saved source and mapping. OP-7: import without special files. Original plan, assignment evidence, guardrails and reviewed decisions remain separate.</p></details>`;
  const form=$('intake-form');
  const values=()=>{const v=Object.fromEntries(new FormData(form));v.confirmed=form.elements.confirmed.checked;return v;};
  const invalidate=()=>{previewTicket++;validated=false;$('run-csv').disabled=true;$('csv-validation').textContent='Validate the current mapping before running.';};
  form.oninput=ev=>{if(ev.target.id!=='intake-file')invalidate();};form.onchange=ev=>{if(ev.target.id!=='intake-file')invalidate();};
  $('intake-file').onchange=async ev=>{
    invalidate();const ticket=previewTicket;content='';$('csv-mapping').hidden=true;const file=ev.target.files[0];if(!file)return;
    try{if(file.size>20000000)throw new Error('Choose a CSV under 20 MB.');const text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(await file.arrayBuffer());const p=await api('/api/intake/preview',{content:text});if(ticket!==previewTicket)return;content=text;filename=file.name;
      $('csv-description').textContent=`${filename}: ${p.rows.toLocaleString()} rows, ${p.columns.length} columns. All rows are retained; validation does not silently drop or deduplicate.`;
      for(const k of ['unit','variant','outcome']){form.elements[k].innerHTML='<option value="">Choose a column</option>'+p.columns.map(c=>`<option value="${esc(c)}">${esc(c)}</option>`).join('');form.elements[k].value=mapping[k]||'';}
      $('csv-mapping').hidden=false;form.elements.design.value=mapping.design||'';
    }catch(e){notice(e.message);}
  };
  $('preview-csv').onclick=async()=>{
    if(working||!form.reportValidity())return;notice('');invalidate();const ticket=previewTicket;working=true;
    try{const p=await api('/api/intake/preview',{content,mapping:values()});if(ticket!==previewTicket)return;
      const unsupported=values().design!=='independent-fixed-binary';
      $('csv-validation').innerHTML=`<h3>Validation preview</h3><p>${p.rows.toLocaleString()} rows · missing ${p.issues.missing} · duplicate users ${p.issues.duplicates} · unknown variants ${p.issues.unknown_variants} · invalid outcomes ${p.issues.invalid_outcomes}</p><ul>${Object.entries(p.counts).map(([arm,c])=>`<li>${esc(arm)}: ${c.users.toLocaleString()} users, ${c.positive.toLocaleString()} positive outcomes</li>`).join('')}</ul>${p.errors.length?`<p>Correct before running: ${esc(p.errors.join('; '))}</p>`:'<p>Mapped rows passed validation. This does not verify assignment or capture completeness.</p>'}${unsupported?'<p>This design is unsupported. Use a method appropriate to the actual study; do not change the declaration to bypass this check.</p>':''}<details><summary>First five source rows</summary><pre>${esc(JSON.stringify(p.sample,null,2))}</pre></details>`;
      validated=!p.errors.length&&!unsupported;$('run-csv').disabled=!validated;
    }catch(e){notice(e.message);}finally{working=false;}
  };
  form.onsubmit=async ev=>{
    ev.preventDefault();if(!validated||working)return;working=true;busy=true;form.querySelectorAll('input,select,textarea,button').forEach(x=>x.disabled=true);
    try{ // Disabled controls are omitted by FormData; restore while reading synchronously.
      form.querySelectorAll('input,select,textarea').forEach(x=>x.disabled=false);const v=values();form.querySelectorAll('input,select,textarea').forEach(x=>x.disabled=true);
      const body={label:v.label,intake:{content,filename,mapping:v}};
      if(parent)body.revision={experiment_id:v.experiment_id,parent_run_id:parent.run_id,reason:v.reason};
      else if(destination)body.experiment_id=destination.id;
      const report=await api('/api/investigate',body);await finishInvestigation(report,parent?v.experiment_id:destination?.id);
    }catch(e){notice(e.message);}finally{working=false;busy=false;form.querySelectorAll('input,select,textarea,button').forEach(x=>x.disabled=false);$('run-csv').disabled=!validated;}
  };
  window.scrollTo(0,0);
}
$('open-intake').onclick=()=>openIntake();

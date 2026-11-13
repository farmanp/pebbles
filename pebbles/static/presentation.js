'use strict';
function explainReport(report) {
  if(report.intake)return {type:'unknown',label:'Mapped CSV evidence',title:'The supplied rows can be compared; study validity remains unresolved.',body:'Pebbles used every supplied row and the saved column mapping. No analyst readout or reference population was supplied, so agreement and omitted users cannot be checked.',next:'Review the saved mapping and obtain original plan, assignment, population-completeness and guardrail evidence.',comparison:null};
  if(report.public_comparison)return {type:'unknown',label:'Public snapshot evidence',title:'Calculations can be reproduced; production validity remains unresolved.',body:'The public CSV supplies group labels and retention flags, not the original assignment, exposure and event logs. The checks below distinguish numerical reproduction from decision readiness.',next:'Inspect the population and method comparisons above, then obtain the missing original study and guardrail evidence.',comparison:null};
  const find=id=>report.findings.find(f=>f.check_id===id);
  const metric=find('C02'),agree=find('C05'),discrepancy=find('C06');
  const result={type:'unknown',label:'Some questions remain open',title:'The evidence has limits.',body:'',next:'Review the unanswered checks and collect the evidence needed for your decision.',comparison:null};
  if(report.execution_state!=='Completed'){
    result.label='Some checks could not run';result.title='Fix the input issues to finish the investigation.';
    result.body=report.findings.filter(f=>f.execution_state!=='Completed').map(f=>f.explanation).filter((s,i,a)=>a.indexOf(s)===i).join(' ');
    result.next='Open the affected checks below, correct the files or definitions, then load the updated package and run it again.';
  }else if(agree?.evidence_outcome==='Failed'&&agree.values?.computed){
    result.type='attention';result.label='A measurement discrepancy';result.title='The scorecard does not match the calculation.';result.body=agree.explanation;result.next='Correct the calculation and regenerate the scorecard before relying on this measurement.';
    const computed=agree.values.computed,reported=agree.values.reported;
    const arm=Object.keys(computed).find(a=>reported[a]&&(reported[a].numerator!==computed[a].numerator||reported[a].denominator!==computed[a].denominator||reported[a].rate_percent!==computed[a].rate_percent));
    if(arm){
      const c=computed[arm],r=reported[arm];
      const versionOne=metric?.explanation.startsWith('Computed v1 ');
      result.comparison={arm,reportedPercent:r.rate_percent,reportedNumerator:r.numerator,reportedDenominator:r.denominator,calculatedPercent:c.rate_percent,numerator:c.numerator,denominator:c.denominator,denominatorLabel:versionOne?'distinct exposed users':'assigned users'};
      const sql=find('C03');
      const rowExpression=sql?.evidence_outcome==='Failed'&&sql.explanation.includes(`counts exposure rows for ${arm};`);
      if(versionOne&&rowExpression&&r.denominator===c.exposure_rows&&c.exposure_rows>c.distinct_exposed&&r.numerator===c.numerator){
        result.title='A repeat encounter changed the denominator.';
        result.body=`In the ${arm} arm, ${c.distinct_exposed} distinct users appear in ${c.exposure_rows} exposure events. ${c.numerator} of those users purchased. The supplied definition counts people, but the supplied SQL counts exposure events and the scorecard uses that denominator. The scorecard displays ${r.rate_percent}%; the supported calculation is ${c.rate_percent}%.`;
      }
    }
  }else if(agree?.evidence_outcome==='Failed'){
    result.type='attention';result.label='Definitions do not agree';result.title='Resolve the metric version before comparing results.';result.body=agree.explanation;result.next='Obtain a scorecard and definition for the same metric version.';
  }else if(discrepancy?.evidence_outcome==='Failed'){
    result.type='attention';result.label='Sources disagree';result.title='These files tell different stories.';
    result.body=Object.entries(discrepancy.values).filter(([a,v])=>v.reported_distinct_exposed!==v.export_distinct_users).map(([a,v])=>`The ${a} scorecard lists ${v.reported_distinct_exposed} distinct exposed users; the export contains ${v.export_distinct_users}.`).join(' ')+' This discrepancy alone does not establish which account is correct.';
    result.next='Align the export filters, observation window and snapshots with the scorecard before deciding which count to use.';
  }else if(metric?.evidence_outcome==='Insufficient evidence'){
    result.label='The calculation is unresolved';result.title='There is not enough evidence to validate the conversion.';result.body=metric.explanation+' The report can still check any supported record facts and scorecard arithmetic.';result.next=metric.next_evidence_request||'Obtain the metric definition and required event exports from the metric owner.';
  }else if(report.findings.some(f=>f.evidence_outcome==='Failed')){
    result.type='attention';result.label='A check found a contradiction';result.title='Investigate the flagged measurement checks.';result.body=report.findings.filter(f=>f.evidence_outcome==='Failed').map(f=>f.explanation).join(' ');result.next='Review the cited evidence and correct the conflicting calculation or definition.';
  }else if(agree?.evidence_outcome==='Verified'){
    result.type='supported';result.label='The supplied calculations agree';result.title='The scorecard matches these records.';result.body='Pebbles independently recalculated the declared metric and found agreement with the scorecard under the declared source scope. This is a check of the supplied records, not independent proof of their production lineage.';result.next='Use the supported calculations as part of your review. Resolve decision-critical questions about instrumentation, completeness and statistical analysis separately.';
  }else{
    result.label='Scorecard agreement is unresolved';result.title='The calculation is available, but the comparison is not established.';result.body=agree?.explanation||'The evidence does not establish scorecard agreement.';result.next=agree?.next_evidence_request||'Obtain the missing definitions and aligned source provenance before comparing the result.';
  }
  return result;
}
function guardrailPlanError(specs){
  if(specs===undefined)return null;
  if(!Array.isArray(specs)||specs.length>10||specs.some(s=>s===null||typeof s!=='object'||Array.isArray(s)))return 'The imported guardrail plan must contain at most ten metric objects. Correct the configuration and reload it; no metrics have been silently removed.';
  return null;
}
if(typeof module!=='undefined')module.exports={explainReport,guardrailPlanError};

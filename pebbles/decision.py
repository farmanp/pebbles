"""Conditional shipping recommendations from explicit primary and guardrail evidence."""
from .analysis import compare_proportions, numeric

LIMITS = ('A conditional analyst recommendation, not authorization to deploy. Binary observations and study/review declarations are supplied evidence; Pebbles does not independently verify production capture, randomization, rendering or the business review.')

def decide(report, plan, evidence, assignments, config, evidence_error=None):
    result={'version':'1.0.0','status':'blocked','title':'Not ready for a shipping recommendation.',
            'supporting':[],'blockers':[],'unresolved':[
                'Production capture, randomization and treatment rendering are not independently verified.',
                'Cost and implementation review is an analyst declaration, not an automated audit.'],
            'guardrails':[],'limitations':LIMITS,'plan':plan,
            'problem_tree':{'branch':'OP-1 / OP-5','supporting':['OP-2','OP-3','OP-4','OP-6','OP-7']},
            'method':'Newcombe/Wilson with Bonferroni adjustment across the declared guardrail family; primary interval remains separate.'}
    support,blocks=result['supporting'],result['blockers']
    primary=report.get('analysis',{})
    primary_status=primary.get('status','blocked')
    adverse=primary_status in ('harm','below_threshold')
    if primary_status=='improvement': support.append('Primary conversion: the entire 95% interval exceeds the predeclared worthwhile-improvement goal.')
    else:
        blocks.append('Primary metric: '+primary.get('title','Treatment effect has not been assessed.'))
        blocks.extend(primary.get('blockers',[]))
    plan=plan if isinstance(plan,dict) else {}
    for key,message in [
        ('guardrails_predeclared','Confirm guardrail definitions, directions and acceptable harm limits were chosen before inspecting results.'),
        ('guardrails_complete','Confirm complete binary observations for every assigned user over the declared window.'),
        ('guardrails_set_complete','Confirm the declared guardrails cover all decision-critical metrics; omitted metrics are not assessed.'),
        ('business_review_complete','Complete the cost and implementation-risk review.')]:
        if plan.get(key) is not True: blocks.append(message)
    notes=plan.get('business_review_notes')
    if not isinstance(notes,str) or not notes.strip(): blocks.append('Record the rationale for accepting costs and implementation risks.')
    elif plan.get('business_review_complete') is True: support.append('Analyst-declared cost and implementation review: '+notes.strip())
    specs=plan.get('guardrails')
    if not isinstance(specs,list) or not 1<=len(specs)<=10:
        blocks.append('Declare between one and ten required binary guardrails; an empty set is not evidence of safety.')
        specs=[]
    ids=[s.get('id') if isinstance(s,dict) else None for s in specs]
    valid_ids=all(isinstance(i,str) and i.strip() for i in ids) and len(set(i for i in ids if isinstance(i,str)))==len(ids)
    if not valid_ids: blocks.append('Guardrail IDs must be nonempty and unique.')
    data_error=evidence_error
    if not isinstance(evidence,dict): data_error=data_error or 'Supply guardrails.json with complete per-user binary observations.'
    elif evidence.get('schema_version')!='1.0.0': data_error='Unsupported guardrail evidence version.'
    elif any(evidence.get(k)!=config.get(k) or config.get(k) is None for k in ('experiment_id','revision','window_start','window_end')):
        data_error='Guardrail experiment, revision and observation window must match the primary experiment.'
    metrics=evidence.get('metrics') if isinstance(evidence,dict) else None
    if not isinstance(metrics,list) or len(metrics)>10 or any(not isinstance(m,dict) or not isinstance(m.get('id'),str) for m in (metrics or [])):
        data_error=data_error or 'Guardrail evidence needs a list of at most ten named metrics.'
        metrics=[]
    if len({m['id'] for m in metrics})!=len(metrics): data_error='Duplicate metric IDs in guardrail evidence.'
    if sum(len(m.get('rows',[])) if isinstance(m.get('rows'),list) else 0 for m in metrics)>100_000: data_error='Guardrail evidence exceeds 100,000 observations.'
    if data_error: blocks.append(str(data_error))
    people={}
    for row,_ in assignments or []:
        uid,arm=row.get('user_id'),row.get('variant_id')
        if uid in people and people[uid]!=arm: data_error='Conflicting assignment variants prevent guardrail analysis.'
        people[uid]=arm
    if data_error and str(data_error) not in blocks: blocks.append(str(data_error))
    inference_ok=primary_status!='blocked' and report.get('execution_state')=='Completed' and all(plan.get(k) is True for k in ('guardrails_predeclared','guardrails_complete'))
    for spec in specs:
        s=spec if isinstance(spec,dict) else {}
        ident=s.get('id');label=s.get('name') if isinstance(s.get('name'),str) and s.get('name').strip() else str(ident)
        g={'id':ident,'name':label,'status':'blocked','comparison':None,'max_harm_pp':s.get('max_harm_pp'),'direction':s.get('direction'),'explanation':'','source':'guardrails.json','definition':None}
        result['guardrails'].append(g)
        error=None
        margin=s.get('max_harm_pp')
        if not valid_ids or s.get('direction') not in ('lower','higher') or not numeric(margin) or not 0<=margin<=100:
            error='Use a unique metric ID, higher/lower direction, and a finite harm limit from 0 to 100 percentage points.'
        m=next((m for m in metrics if m['id']==ident),None)
        if not m: error=error or 'Required metric observations are missing.'
        elif not isinstance(m.get('definition'),str) or not m['definition'].strip(): error=error or 'A versioned metric definition is required.'
        elif not isinstance(m.get('version'),str) or not m['version'].strip(): error=error or 'A metric version is required.'
        if m and (s.get('version')!=m.get('version') or s.get('definition')!=m.get('definition')):
            error=error or 'Evidence definition/version differs from the declared guardrail contract.'
        rows=m.get('rows') if m else None
        observed={}
        if not isinstance(rows,list): error=error or 'Complete per-user observations are required.'
        elif not data_error:
            for row in rows:
                if not isinstance(row,dict) or not isinstance(row.get('user_id'),str) or type(row.get('value')) is not bool:
                    error=error or 'Each observation needs a user_id and a literal true/false value.';break
                uid=row['user_id']
                if uid in observed: error=error or 'Duplicate user observations must be reconciled.';break
                observed[uid]=row['value']
            if set(observed)!=set(people): error=error or 'Observations must cover exactly the assigned population; missing users are not treated as false.'
        error=error or data_error
        if not inference_ok: error=error or 'Resolve primary evidence and guardrail study declarations before interpreting this guardrail.'
        if not error:
            control,treatment=plan.get('control'),plan.get('treatment')
            if set(people.values())!={control,treatment} or not people: error='Assignment population must contain exactly the selected two arms.'
        if error:
            g['explanation']=str(error);blocks.append(label+': '+str(error));continue
        counts={arm:(sum(observed[u] for u in people if people[u]==arm),sum(a==arm for a in people.values())) for arm in (control,treatment)}
        comp=compare_proportions(*counts[control],*counts[treatment],confidence=1-.05/len(specs))
        lo,hi=comp['difference_ci']
        if s['direction']=='higher': lo,hi=-hi,-lo
        g.update(comparison=comp,harm_interval=[lo,hi],definition=m['definition'],metric_version=m['version'])
        limit=margin/100
        if hi<limit: g['status']='within_limit';word='The full harm interval stays below the acceptable-harm limit.'
        elif lo>limit: g['status']='harm';word='The full harm interval exceeds the acceptable-harm limit.';adverse=True
        else: g['status']='uncertain';word='The interval includes unacceptable harm; safety has not been established.'
        g['explanation']=(f"Control {100*comp['control_rate']:.2f}%, treatment {100*comp['treatment_rate']:.2f}%. "
            f"Harm-oriented interval {100*lo:+.2f} to {100*hi:+.2f} percentage points; acceptable harm {margin:g} points. "+word)
        (support if g['status']=='within_limit' else blocks).append(label+': '+g['explanation'])
    result['blockers']=list(dict.fromkeys(blocks))
    if adverse:
        result.update(status='do_not_ship',title='Evidence argues against shipping this change.',next_action='Address the failed primary goal or harmful guardrail before considering a new experiment. Resolve any additional blockers listed below.')
    elif not result['blockers']:
        result.update(status='supported',title='Evidence supports a conditional shipping recommendation.',next_action='The analyst can recommend shipping under the saved assumptions and review rationale. Confirm operational rollout and monitoring before deployment.')
    else: result['next_action']='Resolve the blockers and run a new investigation. Do not equate an uncertain or missing guardrail with safety.'
    return result

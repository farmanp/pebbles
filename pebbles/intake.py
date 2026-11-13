"""Guided user-level binary CSV intake; never invent event evidence."""
import csv
import io
import json
import hashlib
import uuid
from datetime import datetime, timezone
from .analysis import compare_proportions

GAPS = ['Original assignment/exposure logs and production completeness are unverified.',
        'Original dated analysis plan, practical benefit threshold and guardrail evidence are absent.',
        'Cost and implementation-risk review is absent.']

def inspect(content, mapping=None):
    if not isinstance(content,str) or len(content.encode())>20_000_000: raise ValueError('Choose a UTF-8 CSV under 20 MB.')
    try:
        reader=csv.reader(io.StringIO(content.lstrip('\ufeff')),strict=True)
        headers=next(reader,None)
        if not headers or any(not h.strip() for h in headers) or len(set(headers))!=len(headers): raise ValueError('CSV needs unique, nonempty column headers.')
        rows=[]
        for n,values in enumerate(reader,2):
            if len(rows)>=100000: raise ValueError('CSV exceeds 100,000 rows.')
            if len(values)!=len(headers): raise ValueError(f'CSV row {n} has missing or extra fields (including blank records).')
            rows.append(dict(zip(headers,values)))
    except csv.Error as ex: raise ValueError('Malformed CSV: '+str(ex)) from ex
    if not rows: raise ValueError('CSV has no data rows.')
    result={'columns':headers,'rows':len(rows),'sample':rows[:5],'errors':[], 'counts':{}}
    if mapping is None:return result
    if not isinstance(mapping,dict): raise ValueError('Choose a column mapping.')
    cols=[mapping.get(k) for k in ('unit','variant','outcome')]
    if any(c not in headers for c in cols) or len(set(cols))!=3: raise ValueError('Map three distinct columns for user, variant and outcome.')
    control,treatment=mapping.get('control'),mapping.get('treatment')
    if not isinstance(control,str) or not isinstance(treatment,str) or not control or not treatment or control==treatment: raise ValueError('Provide distinct control and treatment values exactly as they appear in the CSV.')
    counts={a:{'users':0,'positive':0} for a in (control,treatment)};seen=set();issues={'missing':0,'duplicates':0,'unknown_variants':0,'invalid_outcomes':0}
    for row in rows:
        uid,arm,value=[row[c] for c in cols]
        if not uid.strip() or not arm.strip() or not value.strip():issues['missing']+=1
        if uid in seen:issues['duplicates']+=1
        seen.add(uid)
        if arm not in counts:issues['unknown_variants']+=1
        flag=value.strip().lower()
        if flag not in ('0','1','true','false'):issues['invalid_outcomes']+=1
        if arm in counts:
            counts[arm]['users']+=1;counts[arm]['positive']+=int(flag in ('1','true'))
    result.update(counts=counts,issues=issues)
    result['errors']=[f'{v} rows: {k.replace("_"," ")}' for k,v in issues.items() if v]
    if any(v['users']<2 for v in counts.values()):result['errors'].append('Each arm needs at least two users.')
    return result

def package(body):
    content=body.get('content');m=body.get('mapping');preview=inspect(content,m)
    if preview['errors']:raise ValueError('Correct the CSV before running: '+'; '.join(preview['errors']))
    for key in ('metric','population','window','experiment'):
        if not isinstance(m.get(key),str) or not m[key].strip() or len(m[key])>1000:raise ValueError('Confirm experiment, metric meaning, population and observation window.')
    if m.get('design')!='independent-fixed-binary':raise ValueError('Only fixed-horizon, independent-user binary designs are supported. Clustered, sequential or unknown designs need another method.')
    if m.get('confirmed') is not True:raise ValueError('Confirm the mapped scope and design before running.')
    recipe=dict({k:m[k] for k in ('unit','variant','outcome','control','treatment','metric','population','window','experiment','design','confirmed')},schema_version='1.0.0',recipe_version='csv-binary-v1',source_filename=str(body.get('filename','uploaded.csv'))[:255])
    files=[{'name':'source.csv','content':content},{'name':'import.json','content':json.dumps(recipe,indent=2)}]
    inventory={'schema_version':'1.0.0','artifacts':[{'path':f['name'],'sha256':hashlib.sha256(f['content'].encode()).hexdigest(),'schema_version':'1.0.0','source':'Analyst supplied CSV and confirmed mapping'} for f in files]}
    files.append({'name':'inventory.json','content':json.dumps(inventory,indent=2)})
    return files

def investigate_import(e):
    from .core import InputProblem
    if e.global_error:raise ValueError(str(e.global_error))
    if e.errors:raise ValueError('; '.join(str(x) for x in e.errors.values()))
    if set(e.entries)!={'source.csv','import.json'}:raise ValueError('Guided imports require only source.csv and import.json in the inventory.')
    missing=e.require('source.csv','import.json')
    if missing:raise ValueError('Missing import evidence.')
    m=e.data['import.json'];content=e.data['source.csv']
    package({'content':content,'mapping':m}) # Revalidate saved packages, including declarations.
    p=inspect(content,m);c=p['counts'][m['control']];t=p['counts'][m['treatment']]
    comparison=compare_proportions(c['positive'],c['users'],t['positive'],t['users'])
    lo,hi=comparison['difference_ci'];direction='higher' if lo>0 else 'lower' if hi<0 else 'unresolved'
    explanation=f"{m['metric']}: control {c['positive']}/{c['users']} ({100*comparison['control_rate']:.2f}%), treatment {t['positive']}/{t['users']} ({100*comparison['treatment_rate']:.2f}%). Treatment minus control is {100*comparison['difference']:.3f} percentage points; 95% interval {100*lo:.3f} to {100*hi:.3f}. "
    explanation+=('The interval includes zero; the direction is unresolved.' if direction=='unresolved' else f'The interval supports a {direction} outcome rate under the confirmed independent-user assumptions.')+' Higher or lower is not automatically better; practical value and shipping safety remain unassessed.'
    def f(cid,q,text,status,values=None):return {'check_id':cid,'check_version':'1.0.0','question':q,'scope':'Supplied CSV only','execution_state':'Completed','evidence_outcome':status,'explanation':text,'values':values,'evidence':e.refs(('source.csv','import.json')),'limitations':'Confirmed declarations are not independently verified.','next_evidence_request':None if status=='Verified' else 'Recover original study, assignment, completeness and guardrail evidence.'}
    findings=[f('I01','Are the mapped rows usable?',f"{p['rows']} unique users, two arms and complete binary observations. No rows were excluded.",'Verified',p),f('I02','What does treatment versus control show?',explanation,'Verified',comparison),f('I03','What meaning and scope were confirmed?','The saved mapping records analyst declarations, not independent proof of study design.','Insufficient evidence',m),f('I04','Is the evidence sufficient to recommend shipping?',' '.join(GAPS),'Insufficient evidence')]
    return {'schema_version':'1.0.0','prototype_version':'guided-csv-1','run_id':str(uuid.uuid4()),'created_at':datetime.now(timezone.utc).isoformat(),'input_hashes':e.hashes,'execution_state':'Completed','uncompleted_checks':[],'headline':'CSV investigated; shipping evidence remains incomplete','scope':'One row per user; one binary outcome; fixed-horizon independent-user comparison. No invented assignment or exposure records.','findings':findings,'analysis':None,'intake':{'mapping':m,'preview':p,'comparison':comparison,'direction':direction,'explanation':explanation},'decision':{'status':'blocked','title':'The CSV alone does not support a shipping recommendation.','supporting':[explanation],'blockers':GAPS,'unresolved':['Study assumptions and exported population are analyst declarations.'],'guardrails':[],'plan':None,'limitations':'No readout or reference comparison was supplied. No allocation diagnostic without a planned allocation.','next_action':'Attach this run to an experiment, track missing evidence, and request review.'},'not_evaluated':GAPS}

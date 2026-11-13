"""Describe evidence and result changes without inferring why they occurred."""

def compare_runs(before, after):
    old = before.get('input_hashes', {})
    new = after.get('input_hashes', {})
    files = [{'file':name, 'change':'added' if name not in old else 'removed' if name not in new else 'changed',
              'before':old.get(name), 'after':new.get(name)}
             for name in sorted(old.keys() | new.keys()) if old.get(name)!=new.get(name)]
    a={f['check_id']:f for f in before['findings']}
    b={f['check_id']:f for f in after['findings']}
    def outcome(f):
        if not f: return 'Not evaluated'
        return f['evidence_outcome'] if f['execution_state']=='Completed' else f['execution_state']
    findings=[{'check_id':key,'question':(b.get(key) or a[key])['question'],
               'before':outcome(a.get(key)), 'after':outcome(b.get(key)),
               'explanation':b.get(key,{}).get('explanation','This check is absent in the new run; absence is not resolution.')}
              for key in sorted(a.keys() | b.keys())]
    def result(r):
        if r.get('intake'):
            i=r['intake'];c=i['comparison']
            return {'basis':'mapped CSV: '+i['mapping']['metric'],'conclusion':i['direction'],'difference':c['difference'],'interval':c['difference_ci'],'control':c['control'],'treatment':c['treatment']}
        d=r.get('discrepancy')
        if d:
            return {'basis':'supplied reference', 'conclusion':d['reference_conclusion'],
                    'reported_conclusion':d['reported_conclusion'], 'difference':d['reference']['difference'],
                    'interval':d['reference']['difference_ci'], 'control':d['reference']['control'],
                    'treatment':d['reference']['treatment'], 'export_control':d['supplied']['control'],
                    'export_treatment':d['supplied']['treatment'], 'diagnosis':d['diagnosis']}
        public=r.get('public_comparison')
        if public:
            c=public['all_users']['retention_7']
            lo,hi=c['difference_ci']
            return {'basis':'supplied export, day-7 retention',
                    'conclusion':'lower retention' if hi<0 else 'higher retention' if lo>0 else 'inconclusive',
                    'difference':c['difference'],'interval':c['difference_ci'],
                    'control':c['control'],'treatment':c['treatment'],
                    'export_control':c['control'],'export_treatment':c['treatment']}
        analysis=r.get('analysis') or {}
        c=analysis.get('comparison')
        result={'basis':'primary analysis','conclusion':analysis.get('status','Not assessed')}
        if c:
            result.update(difference=c['difference'],interval=c['difference_ci'],
                          control=c['control'],treatment=c['treatment'])
        return result
    def settings(r):
        analysis=r.get('analysis') or {}
        return {'import_mapping':{k:v for k,v in ((r.get('intake') or {}).get('mapping') or {}).items() if k in ('unit','variant','outcome','control','treatment','metric','population','window','experiment','design','confirmed','recipe_version')},'analysis_plan':analysis.get('plan',r.get('submitted_analysis_plan')),
                'method':analysis.get('method') or (r.get('public_comparison') or {}).get('method'),
                'decision_plan':(r.get('decision') or {}).get('plan'),
                'prototype_version':r.get('prototype_version')}
    def decision(r):
        d=r.get('decision') or {}
        return {'status':d.get('status','Not assessed'),'blockers':d.get('blockers',[])}
    previous,current=decision(before),decision(after)
    return {'files':files,'findings':findings,'before_result':result(before),'after_result':result(after),
            'before_settings':settings(before),'after_settings':settings(after),
            'settings_changed':settings(before)!=settings(after),
            'before_decision':previous,'after_decision':current,
            'new_blockers':[x for x in current['blockers'] if x not in previous['blockers']],
            'removed_blockers':[x for x in previous['blockers'] if x not in current['blockers']],
            'limits':'Changes describe these snapshots; they do not prove a causal explanation, production completeness or shipping safety. A missing or uncompleted check is not a resolved finding.'}

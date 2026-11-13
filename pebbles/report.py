"""Deterministic reports; input strings are escaped, never interpreted as HTML."""
import html
import json


def markdown(report):
    lines = ['# Pebbles investigation', '', report['headline'], '', report['scope'], '',
             f"Run: `{report['run_id']}` · execution: **{report['execution_state']}**", '',
             '[Open HTML report](report.html) · [Machine-readable report](report.json)', '']
    if report.get('revision'):
        lines += ['## Evidence revision', '', 'Parent run: '+report['revision']['parent_run_id'],
                  '', 'Reason: '+report['revision']['reason'], '',
                  'Original runs remain unchanged. Check transitions do not by themselves authorize shipping.',
                  '', '```json', json.dumps(report['revision_comparison'],indent=2,ensure_ascii=False),'```','']
    discrepancy=report.get('discrepancy')
    if discrepancy:
        lines += ['## Controlled discrepancy investigation', '', 'Controlled exercise; not an error attributed to the original analyst.', '', '**'+discrepancy['diagnosis'].replace('_',' ')+'**', ''] + discrepancy['why'] + ['', discrepancy['decision_impact'], '', discrepancy['next_action'], '', discrepancy['limits'], '', '```json',json.dumps(discrepancy,indent=2,ensure_ascii=False),'```','']
    if discrepancy:
        lines += ['| Source | Control retained/users | Treatment retained/users | Difference (pp) | 95% interval (pp) |','|---|---:|---:|---:|---|']
        for label,c in [('Reported claim',discrepancy['reported']),('Supplied export',discrepancy['supplied']),('Supplied reference',discrepancy['reference'])]:
            lines.append(f"| {label} | {c['control']['retained_users']}/{c['control']['users']} | {c['treatment']['retained_users']}/{c['treatment']['users']} | {100*c['difference']:.3f} | {100*c['difference_ci'][0]:.3f} to {100*c['difference_ci'][1]:.3f} |")
        lines.append('')
    p=report.get('public_comparison')
    if p:
        lines += ['## Supplied readout versus export', '', p.get('population_warning','Supplied export only; production completeness is not established.'), '', 'Supplied-export result only: '+p['interpretation'], '', p.get('exclusion_note','Applying an exclusion rule does not establish matching populations.'), '', 'Sample-ratio p-value: '+p['srm'].get('display_p_value',str(p['srm']['p_value'])), '', '| Metric | Supplied export: control | Supplied export: treatment | Difference (pp) | 95% Newcombe interval (pp) | Export with notebook exclusion (pp) |', '|---|---:|---:|---:|---|---:|']
        for metric,a in p['all_users'].items():
            b=p['analyst_population'][metric]
            lines.append(f"| {metric} | {100*a['control_rate']:.4f}% | {100*a['treatment_rate']:.4f}% | {100*a['difference']:.4f} | {100*a['difference_ci'][0]:.4f} to {100*a['difference_ci'][1]:.4f} | {100*b['difference']:.4f} |")
        lines += ['', 'Supplied readout values match at display precision: '+str(all(c['matches'] for c in p['readout_checks'])), '', 'Source: '+p['readout']['source_url'], '', '```json',json.dumps(p,indent=2,ensure_ascii=False),'```','']
    d=report.get('decision')
    if d:
        lines += ['## Shipping decision', '', d['title'], '', '### Supporting evidence', ''] + ['- '+x for x in d['supporting']] + ['', '### Blockers', ''] + (['- '+x for x in d['blockers']] or ['None under the saved declarations.']) + ['', d['next_action'], '', d['limitations'], '', '```json', json.dumps(d,indent=2,ensure_ascii=False), '```', '']
    a=report.get('analysis')
    if a:
        lines += ['## Treatment versus control', '', '**'+a['title']+'**', '', a['explanation'], '', a['next_action'], '', a['limitations'], '']
        if a['blockers']: lines += ['Prerequisite: '+b for b in a['blockers']] + ['']
        lines += ['```json',json.dumps(a,indent=2,ensure_ascii=False),'```','']
    for f in report['findings']:
        status = f['evidence_outcome'] or f['execution_state']
        lines += [f"## {f['check_id']} — {f['question']}", '', f'**{status} · supplied evidence only**', '', f['explanation'], '']
        if f['values'] is not None:
            lines += ['```json', json.dumps(f['values'], indent=2, ensure_ascii=False), '```', '']
        if f['next_evidence_request']:
            lines += ['Next evidence: ' + f['next_evidence_request'], '']
        lines += ['Sources: ' + ', '.join(f"`{e['path']}` ({e['locator']}; SHA-256 `{e['sha256']}`)" for e in f['evidence']), '']
    lines += ['## Not evaluated', ''] + ['- ' + x for x in report['not_evaluated']]
    return '\n'.join(lines) + '\n'


def html_report(report):
    esc = html.escape
    cards = []
    if report.get('revision'):
        revision=report['revision']
        cards.append('<article><h2>Evidence revision</h2><p>Parent run: '+esc(revision['parent_run_id'])+'</p><p>'+esc(revision['reason'])+'</p><p>Original runs remain unchanged. Check transitions do not by themselves authorize shipping.</p><details><summary>Evidence and result comparison</summary><pre>'+esc(json.dumps(report['revision_comparison'],indent=2,ensure_ascii=False))+'</pre></details></article>')
    discrepancy=report.get('discrepancy')
    if discrepancy:
        rows=''.join('<tr><td>'+label+'</td><td>'+f"{c['control']['retained_users']}/{c['control']['users']}"+'</td><td>'+f"{c['treatment']['retained_users']}/{c['treatment']['users']}"+'</td><td>'+f"{100*c['difference']:.3f} pp (95% interval {100*c['difference_ci'][0]:.3f} to {100*c['difference_ci'][1]:.3f})"+'</td></tr>' for label,c in [('Reported claim',discrepancy['reported']),('Supplied export',discrepancy['supplied']),('Supplied reference',discrepancy['reference'])])
        cards.append('<article><div class="meta">Controlled discrepancy investigation · OP-3 / OP-4 / OP-5</div><h2>'+esc(discrepancy['diagnosis'].replace('_',' '))+'</h2><p>Introduced exercise, not an error attributed to the original analyst.</p><table><tr><th>Source</th><th>Gate 30 retained/users</th><th>Gate 40 retained/users</th><th>Difference</th></tr>'+rows+'</table><ul>'+''.join('<li>'+esc(x)+'</li>' for x in discrepancy['why'])+'</ul><p>'+esc(discrepancy['decision_impact'])+'</p><p>'+esc(discrepancy['next_action'])+'</p><p>'+esc(discrepancy['limits'])+'</p><details><summary>Affected records, evidence and intervals</summary><pre>'+esc(json.dumps(discrepancy,indent=2,ensure_ascii=False))+'</pre></details></article>')
    p=report.get('public_comparison')
    if p:
        rows=''.join('<tr><td>'+esc(m)+'</td><td>'+f"{100*a['control_rate']:.4f}%"+'</td><td>'+f"{100*a['treatment_rate']:.4f}%"+'</td><td>'+f"{100*a['difference']:.4f} pp"+'</td><td>'+f"{100*a['difference_ci'][0]:.4f} to {100*a['difference_ci'][1]:.4f} pp"+'</td></tr>' for m,a in p['all_users'].items())
        cards.append('<article><div class="meta">Retention snapshot · supplied readout comparison</div><h2>Supplied readout versus export</h2><p>'+esc(p.get('population_warning','Supplied export only; production completeness is not established.'))+'</p><p>Supplied-export result only: '+esc(p['interpretation'])+'</p><div class="scroll"><table><tr><th>Metric</th><th>Gate 30 · supplied export</th><th>Gate 40 · supplied export</th><th>Difference</th><th>95% Newcombe interval</th></tr>'+rows+'</table></div><p>All supplied-export users are included above. '+esc(p.get('exclusion_note','Applying the same exclusion rule does not establish matching populations.'))+'</p><p>Sample-ratio p-value: '+esc(p['srm'].get('display_p_value',str(p['srm']['p_value'])))+'. Original study and guardrail evidence remain missing.</p><details><summary>Supplied readout, exclusion rule, methods and sources</summary><pre>'+esc(json.dumps(p,indent=2,ensure_ascii=False))+'</pre></details></article>')
    d=report.get('decision')
    if d:
        sections=''.join('<h3>'+title+'</h3><ul>'+''.join('<li>'+esc(x)+'</li>' for x in items)+'</ul>' for title,items in [('Established snapshot findings' if report.get('public_dataset') else 'Supporting evidence',d['supporting']),('Blockers',d['blockers'] or ['None under the saved declarations.']),('Remaining assumptions',d['unresolved'])])
        cards.append('<article><div class="meta">Shipping decision · OP-1 / OP-5</div><h2>'+esc(d['title'])+'</h2>'+sections+'<p>'+esc(d['next_action'])+'</p><p>'+esc(d['limitations'])+'</p><details><summary>Guardrails and saved decision plan</summary><pre>'+esc(json.dumps(d,indent=2,ensure_ascii=False))+'</pre></details></article>')
    a=report.get('analysis')
    if a:
        kind='verified' if a['status']=='improvement' else 'failed' if a['status']=='harm' else 'unknown'
        cards.append('<article class="'+kind+'"><div class="meta">Treatment versus control · OP-5 / CP-3</div><h2>'+esc(a['title'])+'</h2><p>'+esc(a['explanation'])+'</p><p>'+esc(a['next_action'])+'</p><p>'+esc(a['limitations'])+'</p><details><summary>Analysis, assumptions and prerequisites</summary><pre>'+esc(json.dumps(a,indent=2,ensure_ascii=False))+'</pre></details></article>')
    # Put actionable discrepancies first, then operational issues, unknowns and supported facts.
    priority = lambda f: 0 if f['evidence_outcome'] == 'Failed' else 1 if f['execution_state'] != 'Completed' else 2 if f['evidence_outcome'] == 'Insufficient evidence' else 3
    for f in sorted(report['findings'], key=priority):
        status = f['evidence_outcome'] or f['execution_state']
        kind = 'failed' if status == 'Failed' else 'verified' if status == 'Verified' else 'unknown'
        values = ''
        if f['check_id'] == 'C02' and f['values']:
            rows = ''.join('<tr>' + ''.join(f'<td>{esc(str(v))}</td>' for v in [arm,d['assigned'],d['distinct_exposed'],d['exposure_rows'],d['numerator'],d['denominator'],d['rate'] or 'undefined']) + '</tr>' for arm,d in f['values'].items())
            values = '<div class="scroll"><table><thead><tr><th>Arm</th><th>Assigned</th><th>Exposed users</th><th>Exposure events</th><th>Purchasers</th><th>Denominator</th><th>Rate</th></tr></thead><tbody>' + rows + '</tbody></table></div>'
        elif f['values'] is not None:
            values = '<details><summary>Inspect calculation and records</summary><pre>' + esc(json.dumps(f['values'], indent=2, ensure_ascii=False)) + '</pre></details>'
        sources = ''.join('<li><strong>' + esc(e['path']) + '</strong> · ' + esc(e['locator']) + '<code>' + esc(e['sha256']) + '</code></li>' for e in f['evidence'])
        next_step = '<p class="next"><strong>Next evidence</strong><br>' + esc(f['next_evidence_request']) + '</p>' if f['next_evidence_request'] else ''
        cards.append(f'<article class="{kind}"><div class="meta">{esc(f["check_id"])} · <strong>{esc(status)}</strong> · supplied evidence only</div><h2>{esc(f["question"])}</h2><p>{esc(f["explanation"])}</p>{values}{next_step}<details><summary>Evidence and fingerprints</summary><ul>{sources}</ul></details></article>')
    exclusions = ''.join('<li>'+esc(x)+'</li>' for x in report['not_evaluated'])
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pebbles · Evidence investigation</title><style>
:root{color-scheme:light;font-family:system-ui,-apple-system,sans-serif;color:#172b31;background:#f3f2ed}*{box-sizing:border-box}body{margin:0}main{max-width:1060px;margin:auto;padding:40px 24px 70px}header{border-bottom:1px solid #bdc8c7;padding-bottom:30px;margin-bottom:28px}.brand{font-weight:700;letter-spacing:.12em;font-size:14px;color:#32605d}h1{font-size:clamp(28px,4vw,44px);line-height:1.12;max-width:850px;margin:20px 0}h2{font-size:22px;margin:12px 0}p{line-height:1.65}.scope{max-width:850px;color:#455d62}a{color:#165e65}nav{display:flex;gap:20px;margin:20px 0}.run{font-size:12px;overflow-wrap:anywhere;color:#52696d}article{background:#fff;border:1px solid #d2dcda;border-left:5px solid #b77a2d;border-radius:7px;padding:24px;margin:18px 0}.failed{border-left-color:#b64735}.verified{border-left-color:#327269}.meta{font-size:12px;letter-spacing:.02em;color:#52696d}.next{background:#f5f4ed;padding:14px}details{margin-top:16px;font-size:14px}summary{cursor:pointer;color:#235d62}pre{white-space:pre-wrap;overflow-wrap:anywhere;padding:16px;background:#f4f7f6;font-size:12px}code{display:block;font-size:11px;overflow-wrap:anywhere;margin:5px 0 12px;color:#52696d}table{border-collapse:collapse;width:100%;font-size:13px;margin-top:18px}th,td{text-align:left;padding:12px 9px;border-bottom:1px solid #d2dcda}th{color:#426066}.scroll{overflow-x:auto}footer{border-top:1px solid #bdc8c7;margin-top:30px;padding-top:18px;line-height:1.7}@media print{body{background:white}details{display:block}article{break-inside:avoid}nav{display:none}}
</style></head><body><main><header><div class="brand">PEBBLES / PROTOTYPE 0.1</div><h1>''' + esc(report['headline']) + '</h1><p class="scope">' + esc(report['scope']) + '</p><nav><a href="report.json">Download JSON</a><a href="report.md">Read Markdown</a></nav><div class="run">Execution: ' + esc(report['execution_state']) + ' · Run ' + esc(report['run_id']) + ' · ' + esc(report['created_at']) + '</div></header>' + ''.join(cards) + '<footer><strong>Outside this investigation</strong><ul>' + exclusions + '</ul><p>Any shipping recommendation is conditional on the saved evidence and declarations; deployment remains a human decision.</p></footer></main></body></html>'

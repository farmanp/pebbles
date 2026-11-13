"""Runtime reads only the selected evidence directory; no evaluation answer keys."""
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import math
import re
import uuid

from . import __version__

EVENTS = {'assignments.jsonl': ('assignment_id', 'assigned_at'),
          'exposures.jsonl': ('exposure_id', 'exposed_at'),
          'outcomes.jsonl': ('outcome_id', 'occurred_at')}
FILES = set(EVENTS) | {'source.csv', 'import.json', 'configuration.json', 'metric.json', 'scorecard.json', 'metric.sql', 'guardrails.json', 'cookie_cats.csv', 'reference.csv', 'investigation.json', 'analyst.ipynb', 'readout.json', 'notes.txt', 'task.txt'}
QUESTIONS = {
'C01': 'What records are present?', 'C02': 'What does the declared metric calculate?',
'C03': 'Does the supplied SQL use the intended denominator?', 'C04': 'Do the scorecard fields agree arithmetically?',
'C05': 'Does the scorecard match the declared calculation?', 'C06': 'Do the reported and exported exposure counts agree?',
'C07': 'Do the sources declare a shared analytical scope?', 'C08': 'Which supplied records qualify or conflict?',
'C09': 'Was treatment actually rendered correctly?', 'C10': 'Do these exports establish production completeness?'}
LIMITATION = 'Integrity findings concern supplied records and declared rules. They do not independently establish production completeness, rendering or valid randomization. Treatment-effect conclusions are assessed separately under the saved study assumptions; the decision summary separately evaluates a conditional recommendation, never deployment authorization.'
COMMON_RULES = {
'assignment': 'matching experiment/revision/variant; assigned_at in [window_start,window_end)',
'exposure': 'matching assignment experiment/revision/user/variant; exposed_at >= assigned_at and in [window_start,window_end)',
'event_identity': 'same ID same payload deduplicate; conflicting payload blocks affected metrics',
'exclusions': 'exclude orphan, mismatched revision and conflicting-arm exposures; report references and subset scope',
'outcome_mapping': 'purchase records join by user_id to unique valid assignment; inherit experiment/revision/variant; ambiguous assignment blocks attribution',
'unit': 'user_id', 'zero_denominator': 'undefined'}
VERSION_RULES = {
'v1': {'denominator': 'distinct qualifying exposed users', 'numerator': 'denominator users with >=1 purchase strictly after first qualifying exposure and before window_end'},
'v2': {'denominator': 'distinct valid assigned users', 'numerator': 'assigned users with purchase strictly after assignment and before window_end'}}


class InputProblem(Exception):
    def __init__(self, message, state='blocked-invalid-input'):
        super().__init__(message)
        self.state = state


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('timestamp must be an ISO-8601 string with timezone')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('timestamp must include timezone')
    try:
        return result.astimezone(timezone.utc)
    except OverflowError as ex:
        raise ValueError('timestamp falls outside supported UTC date range') from ex


def json_read(text):
    def bad(value):
        raise ValueError(f'non-finite JSON number {value}')
    return json.loads(text, parse_constant=bad)


def sql_code_mask(text):
    """Preserve offsets while hiding comments and quoted contents from recognition."""
    result = list(text)
    i = 0
    while i < len(text):
        start = i
        if text.startswith('--', i):
            end = text.find('\n', i)
            i = len(text) if end == -1 else end
        elif text.startswith('/*', i):
            end = text.find('*/', i + 2)
            if end == -1 or '/*' in text[i+2:end]:
                raise InputProblem('Unsupported or unterminated SQL comment.', 'blocked-unsupported-operation')
            i = end + 2
        elif text[i] in "'\"":
            quote = text[i]
            i += 1
            while i < len(text):
                if text[i] == quote:
                    if i + 1 < len(text) and text[i+1] == quote:
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            else:
                raise InputProblem('Unterminated SQL quote.', 'blocked-unsupported-operation')
        else:
            i += 1
            continue
        result[start:i] = [' ' if ch != '\n' else '\n' for ch in text[start:i]]
    return ''.join(result)


class Evidence:
    def __init__(self, folder):
        self.folder = Path(folder).resolve()
        self.data, self.errors, self.hashes, self.entries = {}, {}, {}, {}
        self.global_error = None
        try:
            if not self.folder.is_dir():
                raise InputProblem('Evidence folder does not exist.')
            paths = list(self.folder.iterdir())
            if len(paths) > 10:
                raise InputProblem('Package exceeds the 10-file limit (including inventory).')
            if any(p.is_symlink() or not p.is_file() for p in paths):
                raise InputProblem('Only regular files directly inside the evidence folder are supported; no symlinks or subdirectories.')
            if sum(p.stat().st_size for p in paths) > 50_000_000:
                raise InputProblem('Package exceeds the 50 MB limit.')
            raw = {p.name: p.read_bytes() for p in paths}
            self.hashes = {n: hashlib.sha256(b).hexdigest() for n, b in raw.items()}
            if 'inventory.json' not in raw:
                raise InputProblem('inventory.json is required to admit an evidence package.')
            inv = json_read(raw['inventory.json'].decode('utf-8'))
            if not isinstance(inv, dict) or inv.get('schema_version') != '1.0.0':
                raise InputProblem('Unsupported inventory schema version.', 'blocked-unsupported-operation')
            if not isinstance(inv.get('artifacts'), list):
                raise InputProblem('inventory.json: artifacts must be a list.')
            for entry in inv['artifacts']:
                if not isinstance(entry, dict):
                    raise InputProblem('inventory.json: each artifact must be an object.')
                name = entry.get('path')
                if name not in FILES or name in self.entries:
                    raise InputProblem(f'inventory.json: unsupported or duplicate artifact path {name!r}.')
                self.entries[name] = entry
            if set(raw) != set(self.entries) | {'inventory.json'}:
                raise InputProblem('Inventory file list does not match the supplied files; no unlisted files are admitted.')
            self.data['inventory.json'] = inv
            row_count = 0
            for name, entry in self.entries.items():
                try:
                    if entry.get('sha256') != self.hashes[name]:
                        raise InputProblem(f'{name}: SHA-256 hash differs from inventory.')
                    if entry.get('schema_version') != '1.0.0':
                        raise InputProblem(f'{name}: unsupported schema version.', 'blocked-unsupported-operation')
                    text = raw[name].decode('utf-8')
                    if name in EVENTS:
                        rows = []
                        for line, content in enumerate(text.splitlines(), 1):
                            if not content.strip():
                                continue
                            try:
                                record = json_read(content)
                                self.validate_row(name, record)
                            except (ValueError, TypeError, KeyError) as ex:
                                raise InputProblem(f'{name}: line {line}: {ex}') from ex
                            rows.append((record, line))
                        self.data[name] = rows
                        row_count += len(rows)
                    elif name.endswith('.json'):
                        value = json_read(text)
                        self.validate_object(name, value)
                        self.data[name] = value
                    else:
                        self.data[name] = text
                except (ValueError, TypeError, KeyError, InputProblem) as ex:
                    self.errors[name] = ex if isinstance(ex, InputProblem) else InputProblem(f'{name}: {ex}')
            if row_count > 100_000:
                raise InputProblem('Package exceeds the 100,000 event-row limit.')
        except (OSError, ValueError, TypeError, KeyError, InputProblem) as ex:
            self.global_error = ex if isinstance(ex, InputProblem) else InputProblem(f'Package admission failed: {ex}')

    @staticmethod
    def validate_row(name, row):
        if not isinstance(row, dict):
            raise ValueError('event must be an object')
        ident, time = EVENTS[name]
        required = [ident, 'user_id', time]
        required += ['event_type'] if name == 'outcomes.jsonl' else ['experiment_id', 'variant_id']
        for key in required:
            if not isinstance(row.get(key), str) or not row[key]:
                raise ValueError(f'{key} must be a nonempty string')
        timestamp(row[time])
        if name != 'outcomes.jsonl' and (type(row.get('revision')) is not int or row['revision'] < 1):
            raise ValueError('revision must be a positive integer')

    @staticmethod
    def validate_object(name, value):
        if not isinstance(value, dict):
            raise ValueError('expected a JSON object')
        if value.get('schema_version') != '1.0.0':
            raise InputProblem(f'{name}: unsupported schema version.', 'blocked-unsupported-operation')
        if name == 'configuration.json':
            if value.get('unit') != 'user_id':
                raise InputProblem('configuration.json: only user_id units are supported.', 'blocked-unsupported-operation')
            if not isinstance(value.get('experiment_id'), str) or not value['experiment_id']:
                raise ValueError('experiment_id is required')
            if type(value.get('revision')) is not int or value['revision'] < 1:
                raise ValueError('revision must be a positive integer')
            arms = value.get('variants')
            if not isinstance(arms, list) or len(arms) != 2 or any(not isinstance(a, str) or not a for a in arms) or len(set(arms)) != 2:
                raise ValueError('exactly two distinct variant names are required')
            if timestamp(value['window_start']) >= timestamp(value['window_end']):
                raise ValueError('observation window must have positive length')
        elif name == 'scorecard.json':
            if not isinstance(value.get('arms'), dict) or not value['arms']:
                raise ValueError('arms must be a nonempty object')
            for arm, fields in value['arms'].items():
                if not isinstance(fields, dict):
                    raise ValueError(f'{arm}: expected an object')
                for key in ('numerator', 'denominator'):
                    if type(fields.get(key)) is not int:
                        raise ValueError(f'{arm}.{key}: expected an integer')
                rate = fields.get('rate_percent')
                if rate is not None and (type(rate) not in (float, int) or not math.isfinite(rate)):
                    raise ValueError(f'{arm}.rate_percent: expected finite number or null')
                if 'distinct_exposed' in fields and (type(fields['distinct_exposed']) is not int or fields['distinct_exposed'] < 0):
                    raise ValueError(f'{arm}.distinct_exposed: expected nonnegative integer')

    def require(self, *names):
        if self.global_error:
            raise self.global_error
        for name in names:
            if name in self.errors:
                raise self.errors[name]
        return [name for name in names if name not in self.data]

    def refs(self, names):
        return [{'path': n, 'locator': 'all records' if n.endswith('.jsonl') else '/', 'sha256': self.hashes[n]}
                for n in names if n in self.hashes]


def metric_version(e):
    m, c = e.data['metric.json'], e.data['configuration.json']
    version = m.get('version')
    if version not in VERSION_RULES:
        raise InputProblem('Unsupported metric version; supply a v1/v2 definition matching the documented contract.', 'blocked-unsupported-operation')
    expected = COMMON_RULES | VERSION_RULES[version]
    missing = [k for k in expected if k not in m]
    if missing:
        return None, 'Metric definition lacks explicit rules: ' + ', '.join(missing)
    changed = [k for k, v in expected.items() if m[k] != v]
    if changed:
        raise InputProblem('Unsupported metric semantics: ' + ', '.join(changed) + '. This prototype does not interpret arbitrary metric prose.', 'blocked-unsupported-operation')
    if m.get('window_start') != c['window_start'] or m.get('window_end') != c['window_end']:
        return None, 'Metric and configuration windows disagree; resolve the intended observation window.'
    if c.get('metric_ref') != f"{m.get('metric_id')}@{version}":
        return None, 'Configuration metric reference does not resolve to the supplied definition.'
    return version, None


def calculate(e, version):
    c = e.data['configuration.json']
    start, end = timestamp(c['window_start']), timestamp(c['window_end'])
    diagnostics, conflicts, replays = [], [], 0
    tables = {}
    for name, (idkey, _) in EVENTS.items():
        seen = {}
        for row, line in e.data[name]:
            key = row[idkey]
            if key in seen:
                if seen[key] != row:
                    conflicts.append({'path': name, 'record_id': key, 'line': line, 'reason': 'conflicting payloads for one event ID'})
                else:
                    replays += 1
                continue
            seen[key] = row
        tables[name] = list(seen.values())
    assigned = {}
    for a in tables['assignments.jsonl']:
        if a['experiment_id'] != c['experiment_id'] or a['revision'] != c['revision'] or a['variant_id'] not in c['variants'] or not start <= timestamp(a['assigned_at']) < end:
            diagnostics.append({'path': 'assignments.jsonl', 'record_id': a['assignment_id'], 'reason': 'assignment outside declared experiment/revision/arm/window'})
            continue
        if a['user_id'] in assigned and assigned[a['user_id']] != a:
            conflicts.append({'path': 'assignments.jsonl', 'record_id': a['assignment_id'], 'reason': 'multiple assignments for one user; attribution unresolved'})
        assigned[a['user_id']] = a
    exposed, exposure_rows = {}, {arm: 0 for arm in c['variants']}
    for x in tables['exposures.jsonl']:
        a = assigned.get(x['user_id'])
        reason = None
        if x['experiment_id'] != c['experiment_id'] or x['revision'] != c['revision']:
            reason = 'experiment/revision mismatch'
        elif a is None:
            reason = 'orphan relative to supplied assignments'
        elif x['variant_id'] != a['variant_id']:
            reason = 'conflicting arm'
        elif not start <= timestamp(x['exposed_at']) < end or timestamp(x['exposed_at']) < timestamp(a['assigned_at']):
            reason = 'exposure outside attribution window or before assignment'
        if reason:
            diagnostics.append({'path': 'exposures.jsonl', 'record_id': x['exposure_id'], 'reason': reason})
            continue
        exposure_rows[x['variant_id']] += 1
        exposed[x['user_id']] = min(exposed.get(x['user_id'], timestamp(x['exposed_at'])), timestamp(x['exposed_at']))
    anchors = exposed if version == 'v1' else {u: timestamp(a['assigned_at']) for u, a in assigned.items()}
    purchasers = set()
    for o in tables['outcomes.jsonl']:
        a = assigned.get(o['user_id'])
        # Explicit scope fields, if provided, must agree with inherited assignment scope.
        scoped = a and all(k not in o or o[k] == a[k] for k in ('experiment_id', 'revision', 'variant_id'))
        if o['event_type'] != 'purchase' or not scoped or o['user_id'] not in anchors or not anchors[o['user_id']] < timestamp(o['occurred_at']) < end:
            diagnostics.append({'path': 'outcomes.jsonl', 'record_id': o['outcome_id'], 'reason': 'outcome does not qualify under declared attribution'})
            continue
        purchasers.add(o['user_id'])
    values = {}
    for arm in c['variants']:
        users = {u for u, a in assigned.items() if a['variant_id'] == arm}
        denominator = len(users & anchors.keys())
        numerator = len(users & purchasers)
        values[arm] = {'assigned': len(users), 'distinct_exposed': len(users & exposed.keys()),
                       'exposure_rows': exposure_rows[arm], 'numerator': numerator, 'denominator': denominator,
                       'rate': str(Fraction(numerator, denominator)) if denominator else None,
                       'rate_percent': round(100 * numerator / denominator, 3) if denominator else None}
    integrity = {'excluded': sorted(diagnostics, key=lambda x: (x['path'], x['record_id'])),
                 'conflicts': sorted(conflicts, key=lambda x: (x['path'], x['record_id'])),
                 'identical_replays': replays, 'repeat_encounters': sum(exposure_rows.values()) - len(exposed)}
    return values, integrity


def investigate(folder, analysis_plan=None):
    e = Evidence(folder)
    if 'source.csv' in e.hashes or 'import.json' in e.hashes:
        from .intake import investigate_import
        return investigate_import(e)
    if 'cookie_cats.csv' in e.hashes or 'readout.json' in e.hashes:
        from .public_comparison import investigate_snapshot
        return investigate_snapshot(e,analysis_plan)
    findings = {}

    def add(cid, explanation, outcome='Insufficient evidence', state='Completed', values=None, refs=(), request=None):
        findings[cid] = {'check_id': cid, 'check_version': '1.0.0', 'question': QUESTIONS[cid],
                         'scope': 'Supplied evidence only', 'execution_state': state,
                         'evidence_outcome': outcome if state == 'Completed' else None,
                         'explanation': explanation, 'values': values, 'evidence': e.refs(refs),
                         'limitations': LIMITATION,
                         'next_evidence_request': request or ('Resolve the stated input limitation with the data owner.' if state != 'Completed' else None)}

    def run(cid, names, operation):
        try:
            missing = e.require(*names)
            if missing:
                add(cid, 'Required evidence is missing: ' + ', '.join(missing), refs=names,
                    request='Ask the analyst or metric owner for ' + ', '.join(missing) + ' to assess this check.')
            else:
                operation()
        except InputProblem as ex:
            add(cid, str(ex), state=ex.state, refs=names)
        except (ValueError, TypeError, KeyError, IndexError) as ex:
            add(cid, f'Invalid supplied structure: {ex}', state='blocked-invalid-input', refs=names)

    def counts():
        existing = [n for n in EVENTS if n in e.data or n in e.errors]
        e.require(*existing)
        if not existing:
            add('C01', 'No event exports supplied; event-level counts cannot be verified.', request='Provide assignment, exposure and outcome exports.')
            return
        v = {name: {'rows': len(e.data[name]), 'distinct_users': len({r['user_id'] for r, _ in e.data[name]})} for name in existing}
        add('C01', 'These are literal counts in the supplied files; they do not establish metric eligibility or production coverage.', 'Verified', values=v, refs=existing)
    run('C01', (), counts)

    metric_names = ('configuration.json', 'metric.json', *EVENTS)
    calculation = {}
    def metric():
        version, issue = metric_version(e)
        if issue:
            add('C02', issue, refs=metric_names, request='Obtain an explicit, consistent versioned metric from the metric owner.')
            return
        values, integrity = calculate(e, version)
        calculation.update(values=values, integrity=integrity, version=version)
        if integrity['conflicts']:
            add('C02', 'Conflicting record identities prevent unambiguous attribution. Resolve the listed conflicts before calculating the metric.', state='blocked-invalid-input', refs=metric_names)
        else:
            add('C02', f'Computed {version} over the valid subset of supplied records using the declared assignment, identity and time rules. Zero denominators are undefined.', 'Verified', values=values, refs=metric_names)
    run('C02', metric_names, metric)

    if calculation:
        detail = calculation['integrity']
        add('C08', f"Identified {len(detail['excluded'])} excluded records, {len(detail['conflicts'])} identity conflicts, {detail['identical_replays']} identical replays and {detail['repeat_encounters']} repeat encounters. A repeat encounter is not itself a defect; an orphan in these files does not prove a production tracking failure.", 'Verified', values=detail, refs=metric_names)
    else:
        def record_integrity():
            seen, conflicts, replays = {}, [], 0
            for row, line in e.data['exposures.jsonl']:
                key = row['exposure_id']
                if key in seen:
                    if seen[key] == row:
                        replays += 1
                    else:
                        conflicts.append({'path':'exposures.jsonl', 'record_id':key, 'line':line})
                else:
                    seen[key] = row
            users = {r['user_id'] for r, _ in e.data['assignments.jsonl']}
            orphans = sorted(r['exposure_id'] for r in seen.values() if r['user_id'] not in users)
            values = {'conflicts':conflicts, 'identical_replays':replays, 'orphan_record_ids':orphans,
                      'repeat_encounters':len(seen)-len({r['user_id'] for r in seen.values()})}
            add('C08', 'Counted repeated IDs, repeat encounters and users absent from the supplied assignments. These are record facts only; metric eligibility and production root causes remain unresolved.', 'Verified', values=values, refs=('assignments.jsonl','exposures.jsonl'))
        run('C08', ('assignments.jsonl','exposures.jsonl'), record_integrity)

    def sql():
        version = e.data['metric.json'].get('version')
        if version != 'v1' or e.data['metric.json'].get('denominator') != VERSION_RULES['v1']['denominator']:
            raise InputProblem('SQL denominator inspection supports only the declared distinct-exposed-user v1 rule.', 'blocked-unsupported-operation')
        text = e.data['metric.sql']
        mask = sql_code_mask(text)
        # Deliberately recognize only the supplied denominator CTE, not arbitrary SQL equivalence.
        match = re.search(r'\bdenominators\s+AS\s*\(\s*SELECT\s+variant_id\s*,\s*(.*?)\s+AS\s+denominator\s+FROM\s+valid\s+GROUP\s+BY\s+variant_id\s*\)', mask, re.I | re.S)
        if not match or mask.count(';') > 1:
            raise InputProblem('Unsupported SQL shape. SQL was not executed; structured metric calculation remains separate.', 'blocked-unsupported-operation')
        expr = ' '.join(text[match.start(1):match.end(1)].split())
        good = re.fullmatch(r'COUNT\s*\(\s*DISTINCT\s+user_id\s*\)', expr, re.I)
        bad = re.fullmatch(r"CASE WHEN variant_id='([^']+)' THEN COUNT\(\*\) ELSE COUNT\(DISTINCT user_id\) END", expr, re.I)
        if not good and not bad:
            raise InputProblem('Unsupported SQL denominator expression; no arbitrary SQL is executed.', 'blocked-unsupported-operation')
        explanation = ('The denominator expression counts distinct user IDs.' if good else f'The denominator expression counts exposure rows for {bad.group(1)}; the supplied definition requires distinct users.')
        add('C03', explanation + ' This is expression inspection only; the rest of the SQL and general query equivalence are not verified.', 'Verified' if good else 'Failed', values={'expression': expr}, refs=('metric.json', 'metric.sql'))
    run('C03', ('metric.json', 'metric.sql'), sql)

    def arithmetic():
        score = e.data['scorecard.json']
        if score.get('display') != 'percent with 3 decimals':
            raise InputProblem('Unsupported scorecard display precision.', 'blocked-unsupported-operation')
        bad = []
        for arm, row in score['arms'].items():
            n, d, rate = row['numerator'], row['denominator'], row.get('rate_percent')
            ok = 0 <= n <= d and ((d == 0 and rate is None) or (d > 0 and rate is not None and abs(Fraction(str(rate))/100 - Fraction(n,d)) <= Fraction(5,1_000_000)))
            if not ok:
                bad.append(arm)
        add('C04', 'Scorecard arithmetic is inconsistent for: ' + ', '.join(bad) if bad else 'Reported percentages match the scorecard’s own numerator and denominator fields within three-decimal percentage rounding. This does not validate the intended denominator.', 'Failed' if bad else 'Verified', values=score['arms'], refs=('scorecard.json',))
    run('C04', ('scorecard.json',), arithmetic)

    def comparable():
        names = ('assignments.jsonl', 'exposures.jsonl', 'outcomes.jsonl', 'scorecard.json', 'metric.json')
        missing = e.require(*names)
        if missing:
            add('C07', 'Cannot establish shared analytical scope without ' + ', '.join(missing), refs=('inventory.json',), request='Provide the missing definitions/exports and aligned population, filters, window and snapshot metadata.')
            return
        keys = ('population', 'filters', 'window', 'export_timestamp', 'experiment_id', 'revision')
        entries = [e.entries[n] for n in names]
        valid = all(all(a.get(k) not in (None, '', 'unknown') and a.get(k) == entries[0].get(k) for a in entries) for k in keys)
        c = e.data['configuration.json']
        valid = valid and entries[0]['experiment_id'] == c['experiment_id'] and entries[0]['revision'] == c['revision'] and entries[0]['window'] == {'start': c['window_start'], 'end_exclusive': c['window_end']}
        add('C07', 'Inventory declares matching population, filters, window, snapshot and experiment revision. This is declared alignment, not independently proven upstream lineage.' if valid else 'Population, filters, window or snapshot are unknown or inconsistent. Neither the scorecard nor the export can be treated as authoritative.', 'Verified' if valid else 'Insufficient evidence', refs=('inventory.json', 'configuration.json', 'metric.json'), request=None if valid else 'Ask the data owner for aligned export filters, population, window and snapshot metadata.')
    run('C07', ('inventory.json', 'configuration.json'), comparable)

    def agreement():
        score, metric = e.data['scorecard.json'], e.data['metric.json']
        ref = f"{metric.get('metric_id')}@{metric.get('version')}"
        if score.get('metric_ref') != ref:
            add('C05', f"Scorecard metric reference {score.get('metric_ref')!r} differs from requested {ref!r}. This does not establish that the old scorecard is wrong under its own definition.", 'Failed', refs=('scorecard.json','metric.json','configuration.json'))
            return
        calc = findings['C02']
        if calc['execution_state'] != 'Completed':
            raise InputProblem('Metric calculation did not complete: ' + calc['explanation'], calc['execution_state'])
        if calc['evidence_outcome'] != 'Verified' or findings['C07']['evidence_outcome'] != 'Verified':
            add('C05', 'Semantic agreement is unresolved: metric definition/calculation or shared source scope is not established. A numerical discrepancy alone cannot decide which source is correct.', refs=metric_names + ('scorecard.json','inventory.json'), request='Obtain a resolved metric definition and aligned source provenance from the metric/data owner.')
            return
        differences = []
        values = calculation['values']
        if set(score['arms']) != set(values):
            differences.append('Scorecard variants differ from the experiment variants.')
        for arm, v in values.items():
            row = score['arms'].get(arm)
            if row is None:
                continue
            if (row['numerator'],row['denominator']) != (v['numerator'],v['denominator']):
                differences.append(f"{arm}: reported {row['numerator']}/{row['denominator']}; supported calculation {v['numerator']}/{v['denominator']} ({v['rate_percent']}%).")
            elif v['denominator'] and (row.get('rate_percent') is None or abs(Fraction(str(row['rate_percent']))/100 - Fraction(v['numerator'],v['denominator'])) > Fraction(5,1_000_000)):
                differences.append(f'{arm}: displayed percentage differs from the supported calculation.')
            elif not v['denominator'] and row.get('rate_percent') is not None:
                differences.append(f'{arm}: zero denominator requires an undefined rate.')
        add('C05', ' '.join(differences) + ' Reconcile the scorecard before relying on this measurement.' if differences else 'Scorecard numerators, denominators and rates agree with the declared calculation over the supplied records.', 'Failed' if differences else 'Verified', values={'computed': values, 'reported': score['arms']}, refs=metric_names + ('scorecard.json','inventory.json'), request='Ask the metric owner to correct and regenerate the scorecard using the versioned denominator rule.' if differences else None)
    run('C05', metric_names + ('scorecard.json','inventory.json'), agreement)

    def literal():
        score = e.data['scorecard.json']
        values = {}
        for arm, row in score['arms'].items():
            if 'distinct_exposed' not in row:
                add('C06', 'Scorecard does not supply distinct-exposed counts.', refs=('scorecard.json','exposures.jsonl'))
                return
            observed = len({r['user_id'] for r, _ in e.data['exposures.jsonl'] if r['variant_id'] == arm})
            values[arm] = {'reported_distinct_exposed': row['distinct_exposed'], 'export_distinct_users': observed}
        equal = all(v['reported_distinct_exposed'] == v['export_distinct_users'] for v in values.values())
        add('C06', 'The displayed distinct-exposure counts equal the distinct users by arm in the exposure file.' if equal else 'The scorecard and exposure export contain different distinct-user counts. This establishes a literal discrepancy, not which source is correct.', 'Verified' if equal else 'Failed', values=values, refs=('scorecard.json','exposures.jsonl'), request=None if equal else 'Ask the data owner to reconcile source filters, snapshots and the cited counts.')
    run('C06', ('scorecard.json', 'exposures.jsonl'), literal)

    for cid, explanation, request in [
        ('C09','Analytical files do not establish that treatment was actually rendered correctly. This prototype does not validate application or SDK behavior.','Ask the implementation owner for relevant render/instrumentation evidence if delivery is decision-critical.'),
        ('C10','Export counts and completeness declarations do not independently establish capture of all production activity.','Ask the data owner for independent capture reconciliation and source lineage if completeness is decision-critical.')]:
        run(cid, (), lambda cid=cid, explanation=explanation, request=request: add(cid, explanation, request=request, refs=('inventory.json',)))
    ordered = [findings[k] for k in sorted(findings)]
    blocked = [f['check_id'] for f in ordered if f['execution_state'] != 'Completed']
    failed = [f['check_id'] for f in ordered if f['evidence_outcome'] == 'Failed']
    execution = 'failed' if len(blocked) == len(ordered) else 'partial' if blocked else 'Completed'
    report = {'schema_version':'1.0.0','prototype_version':__version__, 'run_id':str(uuid.uuid4()),
            'metric_version':calculation.get('version'),
            'created_at':datetime.now(timezone.utc).isoformat(), 'input_hashes':e.hashes,
            'execution_state':execution, 'uncompleted_checks':blocked,
            'headline': 'Input limitations prevented a complete investigation' if blocked else 'Evidence discrepancies require investigation' if failed else 'Supported checks completed; important evidence limits remain',
            'scope':LIMITATION, 'findings':ordered,
            'not_evaluated':['Production randomization implementation and interference','Production treatment delivery','Production capture completeness','Human shipping judgment','Independent report-quality scoring (C11)','Cross-run replay validation (C13; demonstrated separately in tests)']}

    from .analysis import analyze
    supplied_plan=e.data.get('configuration.json',{}).get('analysis_plan')
    report['analysis']=analyze(report,analysis_plan if analysis_plan is not None else supplied_plan,
                               source='user-entered run settings' if analysis_plan is not None else 'configuration.json/analysis_plan')
    from .decision import decide
    report['decision']=decide(report, report['analysis']['plan'], e.data.get('guardrails.json'),
        e.data.get('assignments.jsonl',[]),e.data.get('configuration.json',{}),
        str(e.global_error or e.errors.get('guardrails.json')) if e.global_error or e.errors.get('guardrails.json') else None)
    return report

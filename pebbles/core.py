"""Runtime reads only the selected evidence directory; no evaluation answer keys."""
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import math


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
    """Route the selected evidence format to its investigator."""
    evidence = Evidence(folder)
    if 'source.csv' in evidence.hashes or 'import.json' in evidence.hashes:
        from .intake import investigate_import
        return investigate_import(evidence)
    if 'cookie_cats.csv' in evidence.hashes or 'readout.json' in evidence.hashes:
        from .public_comparison import investigate_snapshot
        return investigate_snapshot(evidence, analysis_plan)
    from .investigation import Investigation
    return Investigation(evidence).investigate(analysis_plan)

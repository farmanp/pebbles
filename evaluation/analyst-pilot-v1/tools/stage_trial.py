"""Copy one neutral task and, when assigned, a fresh Pebbles runtime."""
import argparse
import json
import shutil
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
ROOT = KIT.parents[1]
p = argparse.ArgumentParser()
p.add_argument('--session')
p.add_argument('--period', type=int)
p.add_argument('--practice', action='store_true')
p.add_argument('--destination', required=True, type=Path)
a = p.parse_args()
if a.practice:
    packet, condition = 'r-450', 'Pebbles'
else:
    trials = [r for r in json.loads((KIT/'facilitator/schedule.json').read_text())
              if r['session_id'] == a.session and r['period'] == a.period]
    if len(trials) != 1:
        p.error('Choose an existing session and period, or --practice.')
    packet, condition = trials[0]['packet_id'], trials[0]['condition']
dest = a.destination.resolve()
if dest.exists():
    p.error('Destination must not exist; each task needs a fresh workspace.')
dest.mkdir(parents=True)
shutil.copytree(KIT/'packets'/packet, dest/packet)
for f in (KIT/'participant').glob('*.md'):
    shutil.copy2(f, dest/f.name)
instructions = f'# Current task: {packet}\n\nCondition: {condition}. Read INSTRUCTIONS.md and {packet}/TASK.md. Write your answer in RESPONSE.md.\n'
if condition == 'Pebbles':
    shutil.copytree(ROOT/'pebbles', dest/'pebbles', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (dest/'serve.py').write_text('from pathlib import Path\nfrom pebbles import web\nweb.EXAMPLES = {}\nserver = web.make_server(8850, Path(__file__).parent / "session-runs")\nprint("Open http://127.0.0.1:8850", flush=True)\nserver.serve_forever()\n')
    instructions += '\nRun `python3 serve.py` from this folder, then open http://127.0.0.1:8850. Select the files inside the packet’s evidence folder. Stop the server after the task. If port 8850 is busy, ask the facilitator to stop the previous session server.\n'
(dest/'START.md').write_text(instructions)
print(f'Staged {packet} ({condition}) at {dest}. No session has run.')

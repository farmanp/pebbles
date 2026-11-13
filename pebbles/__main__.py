"""python3 -m pebbles EVIDENCE_FOLDER --output NEW_REPORT_FOLDER"""
import argparse
import json
from pathlib import Path
import sys

from .core import investigate
from .report import html_report, markdown


def main():
    parser = argparse.ArgumentParser(description='Investigate a local experiment evidence package. Produces HTML, Markdown and JSON; reads no private answer keys.')
    parser.add_argument('evidence', type=Path, help='Folder containing inventory.json and admitted evidence files')
    parser.add_argument('--output', required=True, type=Path, help='New output folder; existing paths are never overwritten')
    args = parser.parse_args()
    source, output = args.evidence.resolve(), args.output.resolve()
    if output == source or source in output.parents:
        parser.error('Output must be outside the evidence folder.')
    if output.exists():
        parser.error('Output path already exists. Choose a new directory to preserve prior runs.')
    try:
        report = investigate(source)
        rendered = {'report.json': json.dumps(report, indent=2, ensure_ascii=False) + '\n',
                    'report.md': markdown(report), 'report.html': html_report(report)}
        output.mkdir(parents=True, exist_ok=False)
        for name, content in rendered.items():
            (output / name).write_text(content, encoding='utf-8')
    except (OSError, ValueError) as ex:
        print(f'Pebbles could not complete the run: {ex}', file=sys.stderr)
        return 2
    print(report['headline'])
    for f in report['findings']:
        print(f"  {f['check_id']} {f['evidence_outcome'] or f['execution_state']}: {f['question']}")
    print(f'\nOpen {output / "report.html"}')
    return 2 if report['execution_state'] != 'Completed' else 0


if __name__ == '__main__':
    raise SystemExit(main())

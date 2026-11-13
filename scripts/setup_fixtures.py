"""Rebuild development fixtures; optional downloads are pinned and hash checked."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

def run(relative):
    subprocess.run([sys.executable, str(ROOT / relative)], cwd=ROOT, check=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--with-public-data', action='store_true', help='Download pinned Cookie Cats comparison files; see THIRD_PARTY_NOTICES.md')
    args = parser.parse_args()
    run('evaluation/tools/build_packages.py')
    run('examples/analysis/build_examples.py')
    run('examples/analysis/build_guardrails.py')
    if args.with_public_data:
        base = ROOT / 'public_comparisons/cookie_cats'
        provenance = json.loads((base / 'provenance.json').read_text())
        source = base / 'source'
        source.mkdir(exist_ok=True)
        for name, spec in provenance['files'].items():
            target = source / name
            raw = target.read_bytes() if target.exists() else urllib.request.urlopen(spec['url'], timeout=60).read()
            if hashlib.sha256(raw).hexdigest() != spec['sha256']:
                raise SystemExit(f'Fingerprint mismatch: {name}. Refusing to use changed source.')
            if not target.exists():
                target.write_bytes(raw)
        # prepare.py records a fresh retrieval timestamp; retain the pinned manifest.
        manifest = (base / 'provenance.json').read_bytes()
        try:
            run('public_comparisons/cookie_cats/prepare.py')
        finally:
            (base / 'provenance.json').write_bytes(manifest)
        (ROOT / 'evaluation/discrepancy').mkdir(parents=True, exist_ok=True)
        run('public_comparisons/cookie_cats/build_cases.py')
        (ROOT / 'evaluation/analyst-pilot-v1/distribute').mkdir(parents=True, exist_ok=True)
        run('evaluation/analyst-pilot-v1/tools/build_kit.py')
    print('Fixtures ready. Public-data tests require --with-public-data.')

if __name__ == '__main__':
    main()

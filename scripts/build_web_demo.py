"""Build a static, tab-isolated demo; only allowlisted app and synthetic files ship."""
import argparse
from pathlib import Path
import re
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def build(destination):
    destination=Path(destination)
    destination.mkdir(parents=True,exist_ok=True)
    if any(destination.iterdir()):raise ValueError("Demo output directory must be empty; use a fresh build directory.")
    static=ROOT/'pebbles/static'
    for p in static.iterdir():
        if p.suffix in ('.js','.css'):
            text=p.read_text().replace('Saved on this computer','Saved for this tab only')
            (destination/p.name).write_text(text)
    for name in ('worker.js','bootstrap.js','demo.css'):shutil.copyfile(ROOT/'webdemo'/name,destination/name)
    html=(static/'index.html').read_text()
    html=re.sub(r'<script\b[^>]*>\s*</script>','',html)
    html=html.replace('href="/','href="./').replace('__TOKEN__','browser-demo')
    html=html.replace('</head>','<link rel="stylesheet" href="./demo.css"><script src="./bootstrap.js" defer></script></head>')
    banner='''<div class="demo-bar"><span id="demo-status" role="status">Starting your private demo session…</span><span><a href="https://github.com/farmanp/pebbles">GitHub & local version</a> · <button id="demo-reset" type="button">Start over</button></span></div>
<section id="demo-loading" class="demo-loading"><h1>An experiment, explained.</h1><p>Try Pebbles on a synthetic checkout experiment. Compare the original result with corrected evidence, investigate findings, and review the decision.</p><p id="demo-loading-message" role="status">Loading Python in your browser. The first visit downloads the runtime and may take a little longer.</p><p>No sign-in. Selected files are processed in this tab, not uploaded to an analysis server. Reloading clears your demo work.</p><button id="demo-retry" hidden>Try again</button><p><a href="https://github.com/farmanp/pebbles#run-locally">Prefer a durable workspace? Run locally.</a></p></section>'''
    html=html.replace('Running on your computer','Running in this browser tab').replace('Files and results stay local.','Reload clears demo work.').replace('Selected files are saved locally with this investigation.','Selected files stay in this tab until you reload or close it.')
    html=html.replace('<body>','<body>'+banner).replace('<div class="app-shell">','<div class="app-shell" hidden>')
    html=html.replace('Explore synthetic examples or the public Cookie Cats analyst comparison.','Explore the included synthetic experiments. Cookie Cats remains available in the local version.')
    (destination/'index.html').write_text(html)
    (destination/'.nojekyll').write_text('')
    # Never glob the workspace: runs, user CSVs, keys and downloaded datasets stay out.
    sources=list((ROOT/'pebbles').glob('*.py'))+[ROOT/'start.py',ROOT/'webdemo/bridge.py']
    from pebbles.web import example_folder,FILES
    for key in ('checkout','missing','conflict','clean','benefit','uncertain','harm','ship-supported','ship-harm','ship-uncertain'):
        folder=example_folder(key)
        if not (folder/'inventory.json').is_file():raise RuntimeError('Build synthetic fixtures first: python3 scripts/setup_fixtures.py')
        sources += [p for p in folder.iterdir() if p.is_file() and p.name in FILES|{'inventory.json'}]
    with zipfile.ZipFile(destination/'engine.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(set(sources)):archive.write(p,p.relative_to(ROOT).as_posix())
    return destination

if __name__=='__main__':
    import sys
    sys.path.insert(0,str(ROOT))
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'dist-demo')
    build(parser.parse_args().output)

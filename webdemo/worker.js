/* Pinned runtime; all investigations execute in this tab's worker filesystem. */
importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js');
let python;
async function initialize() {
  python = await loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v0.27.7/full/'});
  await python.loadPackage(['sqlite3','hashlib','ssl']);
  const response = await fetch(new URL('engine.zip',self.location.href));
  if(!response.ok) throw new Error('The analysis engine could not be downloaded.');
  python.unpackArchive(await response.arrayBuffer(),'zip',{extractDir:'/app'});
  await python.runPythonAsync(`
import sys, json
from pathlib import Path
sys.path.insert(0, '/app')
from start import seed_demo
from webdemo.bridge import dispatch
storage = Path('/session')
experiment_id = seed_demo(storage)
`);
  return python.globals.get('experiment_id');
}
// One queue prevents overlapping initialization, SQLite writes and Python execution.
let queue = Promise.resolve();
self.onmessage = ({data}) => {
  queue = queue.then(async () => {
    try {
      if(data.type==='init') {
        self.postMessage({id:data.id,experimentId:await initialize()});
      } else {
        python.globals.set('request_method',data.method);
        python.globals.set('request_path',data.path);
        python.globals.set('request_body',data.body||'');
        const result = python.runPython('json.dumps(dispatch(storage, request_method, request_path, request_body))');
        self.postMessage({id:data.id,result:JSON.parse(result)});
      }
    } catch(error) {
      console.error(error);
      self.postMessage({id:data.id,error:'The demo could not complete this operation. Reload to start a fresh session, or run Pebbles locally.'});
    }
  });
};

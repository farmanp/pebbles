"""In-memory transport for a browser worker; no socket or remote API is exposed."""
import base64
import io
import json
from pathlib import Path
from types import SimpleNamespace
from pebbles.web import Handler

class BrowserRequest(Handler):
    def __init__(self, storage, method, path, body):
        self.server = SimpleNamespace(storage=Path(storage))
        self.server.storage.mkdir(parents=True, exist_ok=True)
        self.path = path
        raw = body.encode('utf-8')
        self.headers = {'Content-Length': str(len(raw)), 'Content-Type': 'application/json'}
        self.rfile = io.BytesIO(raw)
        if method == 'GET': self.do_GET()
        elif method == 'POST': self.do_POST()
        else: self.send({'error':'Unsupported method.'},405)

    def allowed(self, mutation=False):
        # This adapter only receives local worker messages, never HTTP requests.
        # The actual localhost Handler retains its origin/token checks.
        return True

    def send(self, value, status=200, content_type='application/json; charset=utf-8', download=None):
        raw = json.dumps(value).encode() if content_type.startswith('application/json') else value if isinstance(value,bytes) else value.encode()
        self.response = {'status':status,'content_type':content_type,'download':download,
                         'body':base64.b64encode(raw).decode('ascii')}

def dispatch(storage, method, path, body=''):
    if not path.startswith('/api/'):
        return {'status':404,'content_type':'application/json','download':None,
                'body':base64.b64encode(b'{"error":"Unknown demo API."}').decode()}
    return BrowserRequest(storage,method,path,body).response

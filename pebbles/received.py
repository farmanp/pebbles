"""Immutable received files and explicit request/rerun linkage; receipt is not verification."""
import hashlib
import uuid
from pathlib import PurePosixPath

KINDS=('supporting','corrected_csv')

def related(followup, run_id):
    return run_id==followup['run_id'] or any(r['run_id']==run_id for r in followup.get('rechecks',[]))

def receive(experiment, body, now, text):
    followup=next((f for f in experiment['followups'] if f['id']==body.get('followup_id')),None)
    if followup is None:raise ValueError('Unknown evidence request.')
    name=text(body,'name',120,True)
    if PurePosixPath(name).name!=name or '\\' in name or any(ord(c)<32 for c in name) or PurePosixPath(name).suffix.lower() not in ('.csv','.json','.txt','.md','.sql'):
        raise ValueError('Choose a CSV, JSON, TXT, MD or SQL filename without directories.')
    content=body.get('content')
    if not isinstance(content,str) or not content.strip() or len(content.encode('utf-8'))>1_000_000 or '\x00' in content:
        raise ValueError('Received evidence must be nonempty UTF-8 text, at most 1 MB.')
    kind=body.get('kind')
    if kind not in KINDS or (kind=='corrected_csv' and not name.lower().endswith('.csv')):raise ValueError('Choose supporting evidence or a corrected outcome CSV.')
    receipts=followup.setdefault('receipts',[])
    if len(receipts)>=10:raise ValueError('At most 10 received files per request.')
    digest=hashlib.sha256(content.encode()).hexdigest()
    if any(x['sha256']==digest and x['kind']==kind for x in receipts):raise ValueError('This evidence is already received for this request.')
    receipt={'id':str(uuid.uuid4()),'name':name,'content':content,'bytes':len(content.encode()),'sha256':digest,'kind':kind,'note':text(body,'note',4000,True),'at':now,'runs':[]}
    receipts.append(receipt)
    followup.update(status='ready to recheck',revision=followup['revision']+1,updated_at=now)
    return receipt

def linked_receipt(experiment, revision):
    fid,rid=revision.get('followup_id'),revision.get('receipt_id')
    if fid is None and rid is None:return None
    f=next((f for f in experiment['followups'] if f['id']==fid),None)
    if f is None or not related(f,revision.get('parent_run_id')):raise ValueError('Choose a parent run from this evidence request’s lineage.')
    receipt=next((x for x in f.get('receipts',[]) if x['id']==rid),None)
    if receipt is None or receipt['kind']!='corrected_csv':raise ValueError('Choose a received corrected outcome CSV for this request.')
    return receipt

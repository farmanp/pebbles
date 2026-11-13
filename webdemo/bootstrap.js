'use strict';
(() => {
  const base=new URL('./',location.href);
  const build='__DEMO_BUILD__';
  function assetURL(name){const url=new URL(name,base);url.searchParams.set('v',build);return url;}
  let worker;
  try { worker=new Worker(assetURL('worker.js')); }
  catch(error) {
    document.getElementById('demo-loading-message').textContent='This browser could not start the analysis engine. Try a current browser or run Pebbles locally.';
    const retry=document.getElementById('demo-retry');retry.hidden=false;retry.onclick=()=>location.reload();
    return;
  }
  const requests=new Map();let sequence=0,failed=false;
  const nativeFetch=window.fetch.bind(window);
  function fail(message) {
    failed=true;
    for(const {reject,timer} of requests.values()){clearTimeout(timer);reject(new Error(message));}
    requests.clear();
  }
  worker.onerror=()=>fail('The browser analysis engine failed to load. Check your connection and reload.');
  worker.onmessage=({data})=>{
    const request=requests.get(data.id);if(!request)return;
    clearTimeout(request.timer);requests.delete(data.id);
    if(data.error)request.reject(new Error(data.error));else request.resolve(data);
  };
  function request(payload){
    if(failed)return Promise.reject(new Error('Reload to restart the browser engine.'));
    return new Promise((resolve,reject)=>{
      const id=++sequence;
      const timer=setTimeout(()=>{worker.terminate();fail('The demo timed out. Reload to try again or use Pebbles locally for larger inputs.');},120000);
      requests.set(id,{resolve,reject,timer});worker.postMessage({id,...payload});
    });
  }
  function apiPath(value){
    const url=new URL(value,location.href);
    if(url.origin!==location.origin)return null;
    if(url.pathname.startsWith('/api/'))return url.pathname+url.search;
    if(url.pathname.startsWith(base.pathname+'api/'))return url.pathname.slice(base.pathname.length-1)+url.search;
    return null;
  }
  window.fetch=async(input,options={})=>{
    const path=apiPath(typeof input==='string'||input instanceof URL?input:input.url);
    if(!path)return nativeFetch(input,options);
    const {result}=await request({type:'request',path,method:options.method||'GET',body:options.body||''});
    const bytes=Uint8Array.from(atob(result.body),c=>c.charCodeAt(0));
    const headers={'Content-Type':result.content_type};
    if(result.download)headers['Content-Disposition']=`attachment; filename="${result.download}"`;
    return new Response(bytes,{status:result.status,headers});
  };
  // Downloads are local worker responses, not requests to a server API.
  document.addEventListener('click',async event=>{
    const link=event.target.closest('a[href]');
    if(link?.classList.contains('brand')){event.preventDefault();document.getElementById('open-workspace').click();return;}
    if(!link||!apiPath(link.href))return;
    event.preventDefault();
    const preview=link.href.endsWith('.html')?window.open('about:blank','_blank'):null;
    if(preview)preview.opener=null;
    try{
      const response=await fetch(link.href);
      if(!response.ok)throw new Error((await response.json()).error||'Export unavailable.');
      const url=URL.createObjectURL(await response.blob());
      if(preview)preview.location.replace(url);
      else {const a=document.createElement('a');a.href=url;a.download=response.headers.get('Content-Disposition')?.match(/filename="([^"]+)"/)?.[1]||new URL(link.href).pathname.split('/').at(-1);a.click();}
      setTimeout(()=>URL.revokeObjectURL(url),60000);
    }catch(error){preview?.close();document.getElementById('demo-status').textContent=error.message;}
  });
  function script(name){return new Promise((resolve,reject)=>{const s=document.createElement('script');s.src=assetURL(name);s.onload=resolve;s.onerror=()=>reject(new Error('The interface could not load. Please reload.'));document.head.append(s);});}
  async function start(){
    try{
      const {experimentId}=await request({type:'init'});
      // Every visit starts with new IDs; old bookmarked run IDs cannot be restored.
      location.hash=`experiment/${experimentId}/investigation`;
      for(const name of ['presentation.js','app.js','decisions.js','workspace.js','intake.js','analyst-workspace.js'])await script(name);
      document.getElementById('demo-loading').remove();
      document.querySelector('.app-shell').hidden=false;
      document.getElementById('demo-status').textContent='Live demo · Runs in this tab. Reload resets your work; download reports to keep them.';
    }catch(error){
      document.getElementById('demo-loading-message').textContent=error.message;
      document.getElementById('demo-retry').hidden=false;
    }
  }
  document.getElementById('demo-retry').onclick=()=>location.reload();
  document.getElementById('demo-reset').onclick=()=>{if(confirm('Start a fresh demo? This clears this tab’s investigations. Download anything you want to keep first.'))location.reload();};
  start();
})();

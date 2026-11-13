const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('pebbles/static/workspace.js','utf8');
const ctx=vm.createContext({workspaceData:{experiments:[{id:'a',runs:['r']},{id:'b',runs:[]}]},activeExperiment:'a',current:{run_id:'r'},busy:true,analystView:'decision',analystSelected:{},$:id=>({hidden:id!=='workspace-view'}),show:r=>{ctx.shown=r;},openWorkspace:async id=>{ctx.opened=id;}});
vm.runInContext(source.slice(source.indexOf('// Capture the destination')),ctx);
assert.equal(ctx.importContext().id,'a');ctx.$=()=>({hidden:true});assert.equal(ctx.importContext(),null);
ctx.$=id=>({hidden:id!=='result-view'});assert.equal(ctx.importContext().id,'a');ctx.current={run_id:'elsewhere'};assert.equal(ctx.importContext(),null);
(async()=>{await ctx.finishInvestigation({run_id:'new'},'b');assert.equal(ctx.opened,'b');assert.equal(ctx.analystView,'investigation');assert.equal(ctx.analystSelected.b,'new');assert.equal(ctx.busy,false);assert.equal(ctx.shown,undefined);await ctx.finishInvestigation({run_id:'standalone'});assert.equal(ctx.shown.run_id,'standalone');console.log('Workflow context and return-view checks passed');})().catch(e=>{console.error(e);process.exitCode=1;});

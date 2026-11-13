import fs from 'node:fs/promises';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';
const root='/Users/farman/Documents/pebbles';
const schedule=JSON.parse(await fs.readFile(root+'/evaluation/analyst-pilot-v1/facilitator/schedule.json','utf8'));
const wb=Workbook.create();
const sh=wb.worksheets.add('Results');
const headers=['Trial ID','Phase','Session','Period','Packet','Condition','Status','Elapsed seconds','Assistance count','Diagnosis 0–2','Evidence 0–2','Impact 0–2','False assurance 0–1','Total 0–6','Justified success','Time to justified (s)','Capped resolution (s)','Submission reference','Notes / scorer'];
sh.getRange('A1:S27').values=[headers,...schedule.map(r=>[r.session_id+'-'+r.period,r.phase,r.session_id,r.period,r.packet_id,r.condition,'Not run',...Array(12).fill(null)])];
for(let r=2;r<=27;r++) {
 sh.getRange(`N${r}`).formulas=[[`=IF(COUNT(J${r}:L${r})=3,SUM(J${r}:L${r}),"")`]];
 sh.getRange(`O${r}`).formulas=[[`=IF(OR(G${r}="Not run",G${r}="Technical failure"),"",IF(G${r}="Timeout",0,IF(AND(G${r}="Submitted",COUNT(J${r}:M${r})=4),IF(AND(N${r}=6,M${r}=0),1,0),"")))`]];
 sh.getRange(`P${r}`).formulas=[[`=IF(AND(ISNUMBER(O${r}),O${r}=1,ISNUMBER(H${r})),H${r},"")`]];
 sh.getRange(`Q${r}`).formulas=[[`=IF(ISNUMBER(O${r}),IF(O${r}=1,IF(ISNUMBER(H${r}),H${r},""),900),"")`]];
}
sh.getRange('G2:G27').dataValidation={rule:{type:'list',values:['Not run','Submitted','Timeout','Technical failure']}};
sh.getRange('A1:S27').format.font={name:'Arial',size:10};
sh.getRange('A1:S27').format.columnWidth=17;
sh.getRange('A1:S27').format.rowHeight=24;
sh.getRange('A1:S1').format.fill='#173e4a';
sh.getRange('A1:S1').format.font={bold:true,color:'#ffffff'};
sh.getRange('A1:S1').format.wrapText=true;
sh.getRange('A1:S1').format.rowHeight=42;
sh.getRange('H2:M27').format.fill='#fff3d6';
sh.getRange('N2:Q27').format.fill='#e3efee';
sh.getRange('R1:S27').format.columnWidth=35;
sh.getRange('H2:Q27').setNumberFormat('0');
sh.showGridLines=false;sh.freezePanes.freezeRows(1);
const guide=wb.worksheets.add('Read me');
guide.getRange('A1:B9').values=[['Pilot v1 — NOT RUN','Entry and interpretation'],['Purpose','Planned assignments only. All participant outcomes are blank.'],['Yellow cells','Observed time, help and reviewer scores; do not encode missing as zero.'],['Green cells','Derived scores and times. Do not overwrite formulas.'],['Pilot','P00 is an unscored rehearsal. Exclude Pilot rows from scored comparisons.'],['Success','Submitted, all three dimensions 2, false assurance 0.'],['Time','Correct-only time is selection-biased. Capped time assigns 900s to unsuccessful/timeout tasks.'],['Technical failure','Log and report separately. Do not silently exclude or replace.'],['Protocol','Read evaluation/analyst-pilot-v1/facilitator/results-guide.md and protocol.md before use.']];
guide.getRange('A1:B9').format.font={name:'Arial',size:11};
guide.getRange('A1:A9').format.columnWidth=25;guide.getRange('B1:B9').format.columnWidth=90;
guide.getRange('A1:B9').format.wrapText=true;guide.getRange('A1:B9').format.rowHeight=42;
guide.getRange('A1:B1').format.fill='#173e4a';guide.getRange('A1:B1').format.font={bold:true,color:'#ffffff'};guide.showGridLines=false;
wb.recalculate();
console.log('BLANK',JSON.stringify(sh.getRange('N2:Q2').values));
for(const [status,elapsed,score,flag] of [['Submitted',100,2,0],['Submitted',50,1,0],['Timeout',900,2,0],['Technical failure',20,2,0]]){
 sh.getRange('G2:M2').values=[[status,elapsed,0,score,score,score,flag]];wb.recalculate();
 console.log(status,score,JSON.stringify(sh.getRange('N2:Q2').values));
}
sh.getRange('G2:M2').values=[['Not run',null,null,null,null,null,null]];wb.recalculate();
console.log(await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!',options:{useRegex:true,maxResults:30}}));
for(const [sheetName,range,file] of [['Results','A1:I7','results'],['Results','J1:S7','scores'],['Read me','A1:B9','guide']]){
 const png=await wb.render({sheetName,range,scale:1,format:'png'});await fs.writeFile('/tmp/pebbles-workbook-build/'+file+'.png',new Uint8Array(await png.arrayBuffer()));
}
const out=await SpreadsheetFile.exportXlsx(wb);await out.save(root+'/outputs/analyst-pilot-v1/results.xlsx');

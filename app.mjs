import {names,models,selectRows,metric,csv} from './core.mjs';
const $=id=>document.getElementById(id);
const fmt=n=>n===null?'—':Math.round(n).toLocaleString('en-US')+' m';
const pct=n=>n===null?'—':(n*100).toFixed(1)+'%';
let report, rows=[], selected=0;
function renderPlot(e){
  const model=$('model').value,p=e.predictions[model],radius=report.radii[model],reveal=$('reveal').checked;
  // Hidden later observations never affect plot extents. Revealed ones must fit.
  const points=[...e.history,[p[0]-radius,p[1]-radius],[p[0]+radius,p[1]+radius]];
  if(reveal)points.push(...e.future);
  const extent=Math.max(500,...points.flatMap(p=>p.map(Math.abs)))*1.12;
  const scale=245/extent, tx=x=>400+x*scale, ty=y=>300-y*scale;
  const line=pts=>pts.map(p=>`${tx(p[0]).toFixed(2)},${ty(p[1]).toFixed(2)}`).join(' ');
  let svg=`<defs><clipPath id="bounds"><rect x="45" y="32" width="715" height="520"/></clipPath></defs><text x="20" y="25" fill="#a9bdc8" font-size="14">NORTH (m)</text><text x="660" y="585" fill="#a9bdc8" font-size="14">EAST (m)</text>`;
  const tick=Math.ceil(extent/3/250)*250;
  for(let v=-Math.floor(extent/tick)*tick;v<=extent;v+=tick){
    if(ty(v)>=35&&ty(v)<=550)svg+=`<line x1="45" x2="760" y1="${ty(v)}" y2="${ty(v)}" stroke="#243a48"/><text x="47" y="${ty(v)-5}" fill="#7893a3" font-size="12">${v}</text>`;
    if(tx(v)>=45&&tx(v)<=760)svg+=`<line y1="32" y2="552" x1="${tx(v)}" x2="${tx(v)}" stroke="#243a48"/><text x="${tx(v)+4}" y="548" fill="#7893a3" font-size="12">${v}</text>`;
  }
  svg+=`<g clip-path="url(#bounds)"><circle cx="${tx(p[0])}" cy="${ty(p[1])}" r="${radius*scale}" fill="#70e1ca" fill-opacity=".045" stroke="#70e1ca" stroke-opacity=".5" stroke-dasharray="5 6"/><polyline points="${line(e.history)}" fill="none" stroke="#a9bdc8" stroke-width="3"/><line x1="400" y1="300" x2="${tx(p[0])}" y2="${ty(p[1])}" stroke="#70e1ca" stroke-width="2" stroke-dasharray="8 6"/><circle cx="400" cy="300" r="6" fill="#edf4f7"/><circle cx="${tx(p[0])}" cy="${ty(p[1])}" r="7" fill="#70e1ca"/>`;
  if(reveal)svg+=`<polyline points="${line(e.future)}" fill="none" stroke="#ffb881" stroke-width="3"/><path d="M${tx(e.actual[0])-6},${ty(e.actual[1])-6}l12,12m0,-12l-12,12" stroke="#ffb881" stroke-width="3"/><line x1="${tx(p[0])}" y1="${ty(p[1])}" x2="${tx(e.actual[0])}" y2="${ty(e.actual[1])}" stroke="#ffb881" stroke-dasharray="3 5"/>`;
  svg+='</g><text x="411" y="290" fill="#edf4f7" font-size="13">ORIGIN</text>';
  $('plot').innerHTML=svg;
  $('plot').setAttribute('aria-label',`${e.vessel}, ${names[model]}. Past positions and forecast radius ${fmt(radius)}. ${reveal?'Later observations revealed.':'Later observations hidden.'}`);
}
function renderCase(){
  if(!rows.length){$('plot').innerHTML='';$('details').innerHTML='';$('vessel').textContent='No cases';$('outcome').textContent='No observations in this selection.';return;}
  const e=rows[selected],m=$('model').value;
  $('case').value=String(selected);$('prev').disabled=selected===0;$('next').disabled=selected===rows.length-1;
  $('plotTitle').textContent=`${e.vessel} · ${e.origin.slice(11,19)} UTC`;
  $('vessel').textContent=`${e.vessel} / ${e.kind}`;
  const pairs=[['Origin (UTC)',e.origin.slice(11,19)],['History starts (UTC)',e.history_start.slice(11,19)],['Target (UTC)',e.target.slice(11,19)],['Observed lead',`${(e.lead_seconds/60).toFixed(2)} minutes`],['Reported origin speed',`${e.speed.toFixed(1)} knots`],['Forecast',names[m]],['Calibration radius',fmt(report.radii[m])]];
  if($('reveal').checked)pairs.push(['Endpoint error',fmt(e.errors[m])]);
  $('details').innerHTML=pairs.map(([k,v])=>`<dt>${k}</dt><dd>${v}</dd>`).join('');
  $('outcome').textContent=$('reveal').checked?(e.errors[m]<=report.radii[m]?'Observed endpoint is inside the radius.':'Observed endpoint is outside the radius.'):'Later observations hidden. Aggregate metrics below remain retrospective.';
  renderPlot(e);
}
function render(){
  const m=$('model').value;rows=selectRows(report.examples,$('split').value,$('kind').value);selected=0;
  const x=metric(rows,m,report.radii[m]);
  $('n').textContent=`${x.n} / ${new Set(rows.map(e=>e.vessel)).size} vessels`;
  $('median').textContent=fmt(x.median);$('p90').textContent=fmt(x.p90);$('coverage').textContent=pct(x.coverage);
  $('case').innerHTML=rows.map((e,i)=>`<option value="${i}">${i+1} · ${e.vessel} · ${e.origin.slice(11,19)} UTC</option>`).join('');
  $('export').disabled=!rows.length;
  $('scoreCaption').textContent=`${$('split').selectedOptions[0].textContent} · ${rows.length} cases`;
  $('scoresBody').innerHTML=models.map(k=>{const a=metric(rows,k,report.radii[k]);return `<tr class="${m===k?'selected':''}"><td>${names[k]}</td><td>${fmt(a.median)}</td><td>${fmt(a.mean)}</td><td>${fmt(a.p90)}</td><td>${fmt(report.radii[k])}</td><td>${pct(a.coverage)}</td></tr>`}).join('');
  renderCase();
}
try{
  const response=await fetch('report.json');if(!response.ok)throw Error('Report unavailable');report=await response.json();
  $('headline').textContent=fmt(report.metrics.test.velocity.median_m);
  $('finding').textContent=`Median endpoint error for constant velocity on ${report.metrics.test.velocity.n} evening cases across ${report.metrics.test.velocity.vessels} vessels. The fitted scale (${report.scale.toFixed(3)}) increased median error to ${fmt(report.metrics.test.fitted.median_m)}.`;
  for(const id of ['split','kind','model'])$(id).addEventListener('change',render);
  $('case').addEventListener('change',()=>{selected=Number($('case').value);renderCase()});
  $('prev').onclick=()=>{if(selected>0){selected--;renderCase()}};
  $('next').onclick=()=>{if(selected<rows.length-1){selected++;renderCase()}};
  $('reveal').addEventListener('change',renderCase);
  $('export').onclick=()=>{const url=URL.createObjectURL(new Blob([csv(rows)],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=`wakecast-${$('split').value}-${$('kind').value}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);$('status').textContent=`Exported ${rows.length} cases with all three models.`};
  render();
}catch(error){$('status').textContent='The research report could not load. Please reload or download it from GitHub.';console.error(error)}

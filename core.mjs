export const names={hold:'Hold position',velocity:'Constant velocity',fitted:'Fitted velocity'};
export const models=Object.keys(names);
export function selectRows(rows,split,kind='all') {return rows.filter(e=>e.split===split&&(kind==='all'||e.kind===kind));}
export function metric(rows,model,radius) {
  if(!rows.length)return {n:0,median:null,p90:null,mean:null,coverage:null};
  const e=rows.map(r=>r.errors[model]).sort((a,b)=>a-b);
  return {n:e.length,median:e[Math.ceil(e.length*.5)-1],p90:e[Math.ceil(e.length*.9)-1],mean:e.reduce((a,b)=>a+b,0)/e.length,coverage:e.filter(x=>x<=radius).length/e.length};
}
export function csv(rows) {
  const header=['id','vessel','kind','split','origin','target','lead_seconds',...models.flatMap(m=>[m+'_error_m',m+'_east_m',m+'_north_m'])];
  return [header.join(','),...rows.map(e=>[e.id,e.vessel,e.kind,e.split,e.origin,e.target,e.lead_seconds,...models.flatMap(m=>[e.errors[m],...e.predictions[m]])].join(','))].join('\n')+'\n';
}

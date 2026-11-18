import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {models,metric,selectRows,csv} from '../core.mjs';
const r=JSON.parse(readFileSync(new URL('../report.json',import.meta.url)));
test('browser metrics reconcile all splits and models',()=>{
  for(const s of ['train','calibration','test'])for(const m of models){
    const x=metric(selectRows(r.examples,s),m,r.radii[m]),y=r.metrics[s][m];
    assert.equal(x.n,y.n);assert.ok(Math.abs(x.median-y.median_m)<1e-7);assert.equal(x.coverage,y.coverage);
  }
});
test('export includes exactly the filtered cases and errors',()=>{
  const rows=selectRows(r.examples,'test','tanker');const lines=csv(rows).trim().split('\n');
  assert.equal(lines.length,rows.length+1);
  assert.deepEqual(lines.slice(1).map(l=>l.split(',')[0]),rows.map(e=>e.id));
  for(let i=0;i<rows.length;i++)assert.equal(Number(lines[i+1].split(',')[10]),rows[i].errors.velocity);
});
test('empty cohort has no fabricated metrics',()=>assert.deepEqual(metric([], 'hold',1),{n:0,median:null,p90:null,mean:null,coverage:null}));
test('all endpoint errors independently match coordinates',()=>{
  for(const e of r.examples)for(const m of models)assert.ok(Math.abs(Math.hypot(e.actual[0]-e.predictions[m][0],e.actual[1]-e.predictions[m][1])-e.errors[m])<1e-7);
});

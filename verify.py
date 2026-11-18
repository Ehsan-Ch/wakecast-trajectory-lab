"""Rebuild all forecasts/metrics and compare with the committed report."""
import json
import math
from build import ROOT, build

def compare(a,b,path='report'):
    if isinstance(a,float):
        if not isinstance(b,(float,int)) or not math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-8):
            raise AssertionError(path)
    elif isinstance(a,dict):
        assert a.keys()==b.keys(),path
        for k in a:compare(a[k],b[k],path+'.'+k)
    elif isinstance(a,list):
        assert len(a)==len(b),path
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,f'{path}[{i}]')
    else:assert a==b,path

if __name__=='__main__':
    a=build(); b=json.loads((ROOT/'report.json').read_text())
    compare(a,b)
    q=a['quality']
    assert q['candidate_origins']==sum(q[k] for k in ('insufficient_history','missing_target','coverage_gap','split_boundary','accepted'))
    print('Verified all forecasts, temporal partitions, metrics, radii and input hashes.')

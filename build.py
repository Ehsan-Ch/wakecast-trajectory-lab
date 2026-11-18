"""Reproduce the complete included benchmark from retained observations."""
import hashlib
import json
from pathlib import Path
from analysis import load_points,run

ROOT=Path(__file__).resolve().parent
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def build():
    cfg=json.loads((ROOT/'config.json').read_text())
    groups=load_points(ROOT/'data/points.csv',cfg)
    result=run(groups,cfg)
    result.update({'name':'WakeCast','day':'2024-01-01','config':cfg,
        'data':{'rows':sum(map(len,groups.values())),'vessels':len(groups),
                'points_sha256':sha(ROOT/'data/points.csv'),'config_sha256':sha(ROOT/'config.json')},
        'provenance':json.loads((ROOT/'data/source_manifest.json').read_text())})
    return result
if __name__=='__main__':
    result=build()
    (ROOT/'report.json').write_text(json.dumps(result,separators=(',',':'),allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('scale','quality','metrics')},indent=2))

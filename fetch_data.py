"""Restore the exact historical retained extract; no credentials required."""
import hashlib
from pathlib import Path
import urllib.request

URL='https://raw.githubusercontent.com/Ehsan-Ch/harborscope-ais-lab/d8e1dcee1e8433e4153e24c00a3e49dc803b0e76/points.csv'
EXPECTED='f36a975111b3e1fcbebd2ef6012ec635b9f44ddcf296b5b24590d4b429ac0484'
if __name__=='__main__':
    request=urllib.request.Request(URL,headers={'User-Agent':'WakeCast-research/1.0'})
    with urllib.request.urlopen(request,timeout=60) as response:data=response.read(2_000_000)
    if hashlib.sha256(data).hexdigest()!=EXPECTED:raise ValueError('Extract SHA256 mismatch; existing file untouched')
    target=Path(__file__).resolve().parent/'data/points.csv'
    target.parent.mkdir(exist_ok=True)
    temp=target.with_suffix('.tmp');temp.write_bytes(data);temp.replace(target)
    print('Restored and verified retained AIS extract.')

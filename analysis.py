"""Chronological trajectory benchmark. Standard-library only; no future features."""
import bisect
import csv
import math
from datetime import datetime, timezone

MODELS = ('hold', 'velocity', 'fitted')

def stamp(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()

def iso(t):
    return datetime.fromtimestamp(t, timezone.utc).isoformat().replace('+00:00', 'Z')

def xy(lat, lon, cfg):
    """Local equirectangular metres; appropriate only for this small rectangle."""
    r = cfg['earth_radius_m']
    return [r * math.radians(lon-cfg['reference_longitude']) * math.cos(math.radians(cfg['reference_latitude'])),
            r * math.radians(lat-cfg['reference_latitude'])]

def load_points(path, cfg):
    groups = {}
    seen = set()
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            t = stamp(row['time']); lat = float(row['lat']); lon = float(row['lon']); speed = float(row['speed'])
            key = row['vessel'], t
            if key in seen: raise ValueError('Duplicate vessel/time')
            if not all(map(math.isfinite, [lat, lon, speed])): raise ValueError('Non-finite point')
            if not (-90 <= lat <= 90 and -180 <= lon <= 180 and speed >= 0): raise ValueError('Invalid point')
            seen.add(key)
            groups.setdefault(row['vessel'], []).append({'t':t, 'xy':xy(lat,lon,cfg), 'speed':speed, 'kind':row['kind']})
    return {k:sorted(v, key=lambda p:p['t']) for k,v in sorted(groups.items())}

def partition(origin, target, cfg):
    """Embargo labels crossing a split, including exactly on the next boundary."""
    a, b = stamp(cfg['train_end']), stamp(cfg['calibration_end'])
    if origin < a: return 'train' if target < a else None
    if origin < b: return 'calibration' if target < b else None
    return 'test'

def examples(groups, cfg):
    out=[]; counts={'candidate_origins':0,'insufficient_history':0,'missing_target':0,'coverage_gap':0,'split_boundary':0,'accepted':0}
    h=cfg['horizon_seconds']; tolerance=cfg['target_tolerance_seconds']
    for vessel, points in groups.items():
        times=[p['t'] for p in points]; last=-math.inf
        for i,p in enumerate(points):
            if p['speed'] < cfg['minimum_speed_knots'] or p['t']-last < cfg['origin_spacing_seconds']: continue
            last=p['t']; counts['candidate_origins']+=1
            lo=bisect.bisect_left(times,p['t']-cfg['history_seconds'])
            if p['t']-times[lo] < cfg['minimum_history_seconds']:
                counts['insufficient_history']+=1; continue
            wanted=p['t']+h; at=bisect.bisect_left(times,wanted)
            candidates=[j for j in (at-1,at) if i<j<len(points)]
            j=min(candidates,key=lambda j:(abs(times[j]-wanted),times[j])) if candidates else None
            if j is None or abs(times[j]-wanted)>tolerance:
                counts['missing_target']+=1; continue
            if any(times[k]-times[k-1]>cfg['maximum_gap_seconds'] for k in range(lo+1,j+1)):
                counts['coverage_gap']+=1; continue
            split=partition(p['t'],times[j],cfg)
            if split is None: counts['split_boundary']+=1; continue
            # Fixed-origin forecast at actual observed target lead, explicitly reported.
            lead=times[j]-p['t']; dt=p['t']-times[lo]
            v=[(p['xy'][k]-points[lo]['xy'][k])/dt for k in (0,1)]
            delta=[v[k]*lead for k in (0,1)]
            actual=[points[j]['xy'][k]-p['xy'][k] for k in (0,1)]
            history=[[q['xy'][k]-p['xy'][k] for k in (0,1)] for q in points[lo:i+1]]
            future=[[q['xy'][k]-p['xy'][k] for k in (0,1)] for q in points[i:j+1]]
            out.append({'id':f'{vessel}-{int(p["t"])}','vessel':vessel,'kind':p['kind'],
                        'origin':iso(p['t']),'target':iso(times[j]),'history_start':iso(times[lo]),
                        'split':split,'speed':p['speed'],'lead_seconds':lead,'history':history,
                        'future':future,'delta':delta,'actual':actual})
            counts['accepted']+=1
    return sorted(out,key=lambda e:(e['origin'],e['vessel'])),counts

def fit_scale(rows, bounds):
    if not rows: raise ValueError('No training examples')
    numerator=math.fsum(sum(a*d for a,d in zip(e['actual'],e['delta'])) for e in rows)
    denominator=math.fsum(sum(d*d for d in e['delta']) for e in rows)
    raw=numerator/denominator if denominator else 0
    return min(bounds[1],max(bounds[0],raw))

def radius(errors, coverage):
    """Finite-sample rank; fail rather than invent a finite unattainable quantile."""
    rank=math.ceil((len(errors)+1)*coverage)
    if not errors or rank>len(errors): raise ValueError('Too few calibration examples')
    return sorted(errors)[rank-1]

def percentile(values, q):
    return sorted(values)[max(0,math.ceil(len(values)*q)-1)] if values else None

def summarize(rows, model, r):
    errors=[e['errors'][model] for e in rows]
    by_vessel={}
    for e in rows: by_vessel.setdefault(e['vessel'],[]).append(e['errors'][model])
    return {'n':len(rows),'vessels':len(by_vessel),
            'median_m':percentile(errors,.5),'p90_m':percentile(errors,.9),
            'mean_m':math.fsum(errors)/len(errors) if errors else None,
            'vessel_macro_mean_m':math.fsum(math.fsum(v)/len(v) for v in by_vessel.values())/len(by_vessel) if by_vessel else None,
            'coverage':sum(e<=r for e in errors)/len(errors) if errors else None,'radius_m':r}

def run(groups, cfg):
    rows,quality=examples(groups,cfg)
    train=[e for e in rows if e['split']=='train']
    scale=fit_scale(train,cfg['scale_bounds'])
    for e in rows:
        e['predictions']={'hold':[0,0],'velocity':e['delta'],'fitted':[d*scale for d in e['delta']]}
        e['errors']={m:math.dist(p,e['actual']) for m,p in e['predictions'].items()}
    radii={m:radius([e['errors'][m] for e in rows if e['split']=='calibration'],cfg['nominal_coverage']) for m in MODELS}
    metrics={s:{m:summarize([e for e in rows if e['split']==s],m,radii[m]) for m in MODELS} for s in ('train','calibration','test')}
    # No model selection on calibration or test. All three are always reported.
    return {'scale':scale,'radii':radii,'metrics':metrics,'quality':quality,'examples':rows}

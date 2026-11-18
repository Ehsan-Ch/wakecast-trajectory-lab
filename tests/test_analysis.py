import copy
import csv
import json
import math
from pathlib import Path
import tempfile
import unittest
from analysis import examples, fit_scale, iso, load_points, partition, radius, stamp, xy

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/'config.json').read_text())

def track(start='2024-01-01T01:00:00Z', n=30):
    base=stamp(start)
    return {'V1':[{'t':base+i*60,'xy':[i*60,0], 'speed':3, 'kind':'cargo'} for i in range(n)]}

class ForecastTests(unittest.TestCase):
    def test_linear_trajectory(self):
        rows,_=examples(track(),C)
        self.assertTrue(rows)
        for e in rows:
            self.assertEqual(e['actual'],e['delta'])
            self.assertTrue(540 <= e['lead_seconds'] <= 660)
            self.assertEqual(e['history'][-1],[0,0])
        self.assertEqual(fit_scale(rows,C['scale_bounds']),1)

    def test_future_changes_do_not_change_features(self):
        a=track(); b=copy.deepcopy(a)
        # Origin 01:05 uses only its past. Later positions may change labels.
        for p in b['V1'][6:]: p['xy'][1]=1000
        x=next(e for e in examples(a,C)[0] if e['origin'].endswith('01:05:00Z'))
        y=next(e for e in examples(b,C)[0] if e['id']==x['id'])
        self.assertEqual(x['delta'],y['delta'])
        self.assertEqual(x['history'],y['history'])
        self.assertNotEqual(x['actual'],y['actual'])

    def test_split_embargo(self):
        a=stamp(C['train_end']); b=stamp(C['calibration_end'])
        self.assertIsNone(partition(a-600,a,C))
        self.assertIsNone(partition(b-600,b,C))
        self.assertEqual(partition(a,a+600,C),'calibration')
        self.assertEqual(partition(b,b+600,C),'test')

    def test_gap_rejection(self):
        a=track(n=20); a['V1']=[p for i,p in enumerate(a['V1']) if i not in (6,7,8,9)]
        rows,q=examples(a,C)
        self.assertGreater(q['coverage_gap'],0)
        self.assertFalse(any(e['origin'].endswith('01:05:00Z') for e in rows))

    def test_no_target_extrapolation(self):
        rows,q=examples(track(n=8),C)
        self.assertEqual(rows,[])
        self.assertGreater(q['missing_target'],0)

    def test_low_speed_exclusion(self):
        a=track()
        for p in a['V1']:p['speed']=1.9
        self.assertEqual(examples(a,C)[0],[])

    def test_origin_spacing(self):
        rows,_=examples(track(),C)
        self.assertTrue(all(stamp(b['origin'])-stamp(a['origin'])>=300 for a,b in zip(rows,rows[1:])))

    def test_rank_quantile(self):
        self.assertEqual(radius(list(range(22)),.9),20)
        with self.assertRaises(ValueError):radius([1,2],.9)

    def test_scale_clipped(self):
        rows=[{'actual':[100,0],'delta':[1,0]}]
        self.assertEqual(fit_scale(rows,[0,1.5]),1.5)
        rows[0]['actual']=[-100,0]
        self.assertEqual(fit_scale(rows,[0,1.5]),0)

    def test_projection(self):
        self.assertEqual(xy(33.75,-118.215,C),[0,0])
        self.assertAlmostEqual(xy(33.76,-118.215,C)[1],1111.9493,places=3)

    def test_duplicate_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'p.csv'
            path.write_text('vessel,time,lat,lon,speed,kind\nV1,2024-01-01T00:00:00Z,33,-118,2,cargo\nV1,2024-01-01T00:00:00Z,33,-118,2,cargo\n')
            with self.assertRaises(ValueError):load_points(path,C)

    def test_fixed_target_tolerance(self):
        # Reports every 150s give exact ten-minute targets; 9–11 min bound is enforced.
        a=track(n=30)
        for i,p in enumerate(a['V1']):p['t']=stamp('2024-01-01T01:00:00Z')+i*150
        rows,_=examples(a,C)
        self.assertTrue(rows)
        self.assertTrue(all(540<=e['lead_seconds']<=660 for e in rows))

if __name__=='__main__':unittest.main()

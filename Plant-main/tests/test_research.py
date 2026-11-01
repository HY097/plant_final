"""Run from the repository root: python -m unittest discover -s tests"""
import hashlib
import json
import unittest
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]

class DataAndCharts(unittest.TestCase):
    def test_required_files(self):
        for name in ['grid_analysis.parquet','grid_maps.parquet','transitions_10cm.parquet',
                     'model_metrics.csv','observation_audit.csv']:
            self.assertGreater((ROOT/'data'/name).stat().st_size,100)

    def test_existing_results_unmodified(self):
        known={
            'grid_analysis.parquet':'098ac29b5d827e073b34520f3194d9246f7fb5f36fe6f2ff62a6c8a5fec0b37f',
            'grid_maps.parquet':'c5b2c4f798d457f5ab9620c7ae192f195bb74c3ec6b103f2e2faa254a8d71440',
            'model_metrics.csv':'630760c3b7461b075cb51cb543a3d359ecae08e003243c6de4dcc057f54ab3e3',
        }
        for name,expected in known.items():
            self.assertEqual(hashlib.sha256((ROOT/'data'/name).read_bytes()).hexdigest(),expected)

    def test_core_findings(self):
        from research import load,state_counts,neighbor_summary
        d,m,t=load()
        self.assertEqual(len(t),len(d[(d.size_cm==10)&(d.threshold==0)]))
        x,s=state_counts(t[t.species=='Bouteloua gracilis'])
        self.assertEqual(len(x),194)
        self.assertEqual(dict(zip(s.state,s.n)),{
            '타종 신규 기록':75,'종 식별 불확실':94,'다각형 식물 기록 없음':25})
        a,_=neighbor_summary(t[t.species=='Bouteloua gracilis'])
        self.assertEqual(list(a.n),[13463,7713,4597])

    def test_figures_construct(self):
        from research import load,state_counts,neighbor_summary
        from viz import states_bar,neighbor_bar,transition_map,compare_prediction
        _,_,t=load()
        z=t[t.species=='Bouteloua gracilis']
        _,s=state_counts(z); a,_=neighbor_summary(z)
        self.assertEqual(len(states_bar(s).data),1)
        self.assertEqual(len(neighbor_bar(a).data),1)
        metrics=pd.read_csv(ROOT/'data/model_metrics.csv')
        self.assertEqual(len(compare_prediction(metrics).data),2)
        example=json.loads((ROOT/'data/representative.json').read_text(encoding='utf8'))
        self.assertGreater(len(transition_map(t,example['species'],example['quadrat'],example['year']).data),1)

if __name__=='__main__':unittest.main()

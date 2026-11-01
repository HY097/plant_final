"""Tests of exported figures that do not require Parquet/Streamlit."""
import sys
import unittest
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from viz import states_bar, neighbor_bar, compare_prediction, grazing_points
from research import TREAT

class OfflineFigureChecks(unittest.TestCase):
    def test_public_aggregate_numbers(self):
        df=pd.read_csv(ROOT/'data/q2_top_species_counts.csv').set_index('species')
        a=df.loc['Bouteloua gracilis']
        self.assertEqual(sum(int(a[x]) for x in ['다각형 식물 기록 없음','식별 불확실 포함','타종 기록']),194)
        s=pd.DataFrame({'state':['타종 신규 기록','종 식별 불확실','다각형 식물 기록 없음'],
                        'n':[int(a['타종 기록']),int(a['식별 불확실 포함']),int(a['다각형 식물 기록 없음'])]})
        self.assertEqual(len(states_bar(s).data),1)
        n=pd.read_csv(ROOT/'data/q1_neighbor_summary.csv')
        n['rate']=n['loss']*100
        self.assertAlmostEqual(n.iloc[-1].rate,12.312377637589732,places=8)
        self.assertEqual(len(neighbor_bar(n).data),1)

    def test_grazing_is_unordered_categorical_comparison(self):
        g=pd.read_csv(ROOT/'data/q1_grazing_summary.csv')
        g['rate']=g.loss*100
        g['losses']=(g.loss*g.n).round().astype(int)
        f=grazing_points(g,TREAT)
        self.assertEqual(len(f.data),6)
        self.assertTrue(all(trace.mode=='markers' for trace in f.data))
        self.assertEqual(list(f.data[0].x),list(TREAT.values()))

    def test_model_values(self):
        df=pd.read_csv(ROOT/'data/model_metrics.csv')
        self.assertEqual(df.n.to_list(),[400,400])
        self.assertEqual(df.positives.to_list(),[91,91])
        self.assertEqual(len(compare_prediction(df).data),2)

if __name__=='__main__':unittest.main()

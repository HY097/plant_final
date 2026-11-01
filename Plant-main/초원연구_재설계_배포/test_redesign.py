from pathlib import Path
import sys,json,hashlib
import pandas as pd
from streamlit.testing.v1 import AppTest
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from research import *
checks=[]
def check(ok,name):
 assert ok,name
 checks.append(name)
d,m,t=load();old=R.parent/'final/revision/data'
expected_hashes={
 'grid_analysis.parquet':'098ac29b5d827e073b34520f3194d9246f7fb5f36fe6f2ff62a6c8a5fec0b37f',
 'grid_maps.parquet':'c5b2c4f798d457f5ab9620c7ae192f195bb74c3ec6b103f2e2faa254a8d71440',
 'test_predictions.parquet':'ece0631805a9ab00e6a42221d28a1ed4eeae229229d0630ec6ebc0aacd9b216b',
 'model_metrics.csv':'630760c3b7461b075cb51cb543a3d359ecae08e003243c6de4dcc057f54ab3e3',
}
for n,sha in expected_hashes.items():
 check(hashlib.sha256((R/'data'/n).read_bytes()).hexdigest()==sha,'original_checksum_'+n)
 if old.exists():check((R/'data'/n).read_bytes()==(old/n).read_bytes(),'original_unchanged_'+n)
check(len(t)==len(d[(d.size_cm==10)&(d.threshold==0)]),'map_population')
check((t.loc[t.lost==0,'map_state']=='점유 유지').all(),'all_maintained')
check((t.loc[t.map_state=='타종 신규 기록','new_species'].str.len()>0).all(),'new_species_present')
check((t.loc[t.map_state=='기존 타종만 기록','new_species'].str.len()==0).all(),'existing_not_new')
check((t.loc[(t.lost==1)&t.uncertain_end,'map_state']=='종 식별 불확실').all(),'unknown_not_absence')
a,s=state_counts(t[t.species==TOP[0]]);check(len(a)==194 and s.n.sum()==194,'exclusive_denominator_194')
check(dict(zip(s.state,s.n))=={'다각형 식물 기록 없음':25,'종 식별 불확실':94,'타종 신규 기록':75},'exclusive_counts_unchanged')
a,_=neighbor_summary(t[t.species==TOP[0]]);b=pd.read_csv(R/'data/q1_neighbor_summary.csv');check((a.n.to_numpy()==b.n.to_numpy()).all(),'neighbor_denominators');check(np.allclose(a.rate,b.loss*100),'neighbor_rates')
obs=pd.read_csv(R/'data/observation_audit.csv');g=matched_grazing(t[t.species==TOP[0]],obs,(1997,2009));prev=pd.read_csv(R/'data/q1_grazing_summary.csv');merged=g.merge(prev,on=['pasture','treatment']);check(np.allclose(merged.rate,merged.loss*100),'grazing_rates')
rep=read_json('representative.json');check(len(t[(t.quadrat==rep['quadrat'])&(t.year==rep['year'])&(t.species==rep['species'])])==rep['initial_cells'],'representative')
app=AppTest.from_file(str(R/'app.py'),default_timeout=90).run();check(not app.exception,'app_intro')
for page in ['공간 변화','소실의 조건','예측 비교','결론','방법과 검증']:
 app.radio[0].set_value(page).run();check(not app.exception,'page_'+page)
app.radio[0].set_value('공간 변화').run();app.selectbox[0].set_value('Stipa comata').run();check(not app.exception,'map_species');app.checkbox[0].set_value(True).run();check(not app.exception,'map_only')
app.radio[0].set_value('소실의 조건').run();app.slider[0].set_value((2000,2000)).run();app.checkbox[0].set_value(True).run();check(not app.exception,'year_and_exclusion');app.selectbox[0].set_value('Artemisia dracunculus').run();check(not app.exception,'rare_or_empty_state')
app.radio[0].set_value('방법과 검증').run();app.selectbox[0].set_value('Stipa comata').run();check(not app.exception,'sensitivity_species')
(R/'validation.json').write_text(json.dumps({'passed':True,'checks':checks,'browser_desktop':False,'browser_mobile':False,'public_deployment_verified':False},ensure_ascii=False,indent=2),encoding='utf8');print('PASS',len(checks),flush=True)


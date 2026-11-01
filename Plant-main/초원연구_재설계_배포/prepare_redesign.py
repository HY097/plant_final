from pathlib import Path
import shutil,json,ast
import pandas as pd
R=Path('outputs/grassland-research');old=R/'final/revision';out=R/'redesign'
(out/'data').mkdir(parents=True,exist_ok=True)
(out/'screenshots').mkdir(exist_ok=True)
for p in (old/'data').iterdir():
 if p.is_file():shutil.copy2(p,out/'data'/p.name)
for name in ['requirements.txt','연구결과.md']:shutil.copy2(old/name,out/name)
for name in ['observation_audit.csv','audit_summary.json']:shutil.copy2(R/'phase1'/name,out/'data'/name)
for name in ['validation.json','app_validation.json']:shutil.copy2(old/name,out/'data'/('previous_'+name))
d=pd.read_parquet(out/'data/grid_analysis.parquet');m=pd.read_parquet(out/'data/grid_maps.parquet')
main=d[(d.size_cm==10)&(d.threshold==0)].copy()
lookup=m[m.size_cm==10].groupby(['quadrat','year','cell']).species.agg(lambda x:sorted(set(x))).to_dict()
states=[];before=[];after=[];new=[];existing=[]
for r in main.itertuples():
 a=set(lookup.get((r.quadrat,r.year,r.cell),[]));b=set(lookup.get((r.quadrat,r.year+1,r.cell),[]));o=a-{r.species};n=b-{r.species};newsp=n-o;existing_sp=n&o
 state=('점유 유지' if not r.lost else '종 식별 불확실' if r.uncertain_end else '신규·기존 타종 함께' if newsp and existing_sp else '타종 신규 기록' if newsp else '기존 타종만 기록' if n else '다각형 식물 기록 없음')
 if r.lost and r.uncertain_start and n:state='종 식별 불확실'
 states.append(state);before.append(' / '.join(sorted(a)));after.append(' / '.join(sorted(b)));new.append(' / '.join(sorted(newsp)));existing.append(' / '.join(sorted(existing_sp)))
main['map_state']=states;main['before_species']=before;main['after_species']=after;main['new_species']=new;main['existing_species']=existing
main.to_parquet(out/'data/transitions_10cm.parquet',index=False)
# Representative: focal taxon with greatest total cover (previously established),
# then quadrat-year closest to median loss rate, with >=50 initially occupied cells.
sp='Bouteloua gracilis';a=main[main.species==sp].groupby(['quadrat','year']).agg(n=('lost','size'),rate=('lost','mean')).reset_index();a=a[a.n>=50].copy();median=float(a.rate.median());a['distance']=(a.rate-median).abs();rep=a.sort_values(['distance','quadrat','year']).iloc[0]
(out/'data/representative.json').write_text(json.dumps({'species':sp,'quadrat':rep.quadrat,'year':int(rep.year),'initial_cells':int(rep.n),'loss_rate':float(rep.rate),'eligible_median':median,'rule':'Highest total polygon cover species; among pairs with >=50 occupied cells, closest to median pair loss rate; ties sorted by quadrat then year.'},ensure_ascii=False,indent=2),encoding='utf8')
# Exhaustive inventory of caption calls, including sidebar and helper functions.
tree=ast.parse((old/'app.py').read_text(encoding='utf8'));rows=[]
for node in ast.walk(tree):
 if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='caption':
  source=ast.get_source_segment((old/'app.py').read_text(encoding='utf8'),node)
  action='본문으로 변경'
  if any(k in source for k in ['설명서에','목장 단위 재표집','분모에 포함']):action='이동'
  if '대상은 다각형' in source:action='이동'
  rows.append({'line':node.lineno,'original':source,'decision':action,'destination':'해당 결과의 본문 또는 방법·검증 페이지. 출처만 작은 주석으로 유지.'})
pd.DataFrame(rows).sort_values('line').to_csv(out/'caption_audit.csv',index=False,encoding='utf-8-sig')
print('Prepared',len(main),'rows; captions',len(rows),'representative',rep.to_dict())

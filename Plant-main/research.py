from pathlib import Path
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
R=Path(__file__).parent
GREEN='#28624D';ORANGE='#BA652D';PURPLE='#796491';BG='#FAFAF6'
COLORS={'점유 유지':GREEN,'타종 신규 기록':ORANGE,'신규·기존 타종 함께':'#AC8235','기존 타종만 기록':'#477C9B','종 식별 불확실':PURPLE,'다각형 식물 기록 없음':'#B8B9AE'}
TREAT={'unun':'계속 비방목','ungz':'방목 시작','gzun':'방목 중단','gzgz':'계속 방목'}
TOP=['Bouteloua gracilis','Buchloe dactyloides','Stipa comata']
def load():return tuple(pd.read_parquet(R/'data'/n) for n in ['grid_analysis.parquet','grid_maps.parquet','transitions_10cm.parquet'])
def read_json(n):return json.loads((R/'data'/n).read_text(encoding='utf8'))
def quad_label(q):
 a,b=q.split('_');return f'목장 {b} · {TREAT[a]} ({q})'
def summary(f,keys):
 a=f.groupby(keys,observed=True).agg(n=('lost','size'),losses=('lost','sum')).reset_index();a['rate']=a.losses/a.n*100;return a
def style(f,h=440):
 f.update_layout(template='plotly_white',paper_bgcolor=BG,plot_bgcolor=BG,font=dict(family='Malgun Gothic, sans-serif',size=15,color='#24332D'),height=h,margin=dict(l=35,r=25,t=30,b=65),legend=dict(orientation='h',y=-.25,x=0));f.update_xaxes(showgrid=False,zeroline=False);f.update_yaxes(gridcolor='#E3E6DD',zeroline=False);return f
def cover_map(m,q,y,sp):
 mm=m[(m.quadrat==q)&(m.year==y)&(m.size_cm==10)];a=mm[mm.species==sp];v=np.zeros(100);v[a.cell.to_numpy(int)]=a.cover*100
 names=mm.groupby('cell').species.agg(lambda x:'<br>'.join(sorted(set(x)))).to_dict();text=np.array([names.get(i,'확인된 종의 다각형 기록 없음') for i in range(100)]).reshape(10,10)
 f=go.Figure(go.Heatmap(z=v.reshape(10,10),x=np.arange(5,100,10),y=np.arange(5,100,10),text=text,zmin=0,zmax=100,colorscale=[[0,'#F0F2EA'],[1,GREEN]],colorbar=dict(title='피복 %',thickness=12),hovertemplate=f'{y} · {sp}<br>x=%{{x}}cm, y=%{{y}}cm<br>피복 %{{z:.1f}}%<br>기록 종:<br>%{{text}}<extra></extra>'))
 style(f,400);f.update_xaxes(title='가로 (cm)',range=[0,100],dtick=20,constrain='domain');f.update_yaxes(title='세로 (cm)',range=[0,100],dtick=20,scaleanchor='x');return f
def change_map(z,sp,q,y,only=False):
 a=z[(z.quadrat==q)&(z.year==y)&(z.species==sp)];a=a[a.a_only] if only else a
 code={s:i+1 for i,s in enumerate(COLORS)};v=np.zeros(100);text=np.array(['비교 대상 밖: 이전 A 점유 조건에 해당하지 않음']*100,dtype=object)
 for r in a.itertuples():
  v[r.cell]=code[r.map_state];text[r.cell]=f'{q} · {y}→{y+1}<br>{sp}<br>{r.map_state}<br>이전: {r.before_species}<br>다음: {r.after_species}<br>신규 타종: {r.new_species}<br>기존 타종: {r.existing_species}<br>식별 불확실 이전/다음: {r.uncertain_start}/{r.uncertain_end}'
 colors=['#ECEDE6']+list(COLORS.values());scale=[]
 for i,c in enumerate(colors):scale.extend([[i/7,c],[(i+1)/7,c]])
 f=go.Figure(go.Heatmap(z=v.reshape(10,10),x=np.arange(5,100,10),y=np.arange(5,100,10),zmin=-.5,zmax=6.5,colorscale=scale,showscale=False,xgap=2,ygap=2,text=text.reshape(10,10),hovertemplate='x=%{x}cm, y=%{y}cm<br>%{text}<extra></extra>'))
 for s,c in COLORS.items():f.add_trace(go.Scatter(x=[None],y=[None],mode='markers',marker=dict(color=c,size=12,symbol='square'),name=s))
 style(f,590);f.update_xaxes(title='가로 (cm)',range=[0,100],dtick=10,constrain='domain');f.update_yaxes(title='세로 (cm)',range=[0,100],dtick=10,scaleanchor='x');return f
def state_counts(z):
 a=z[z.a_only&(z.lost==1)];s=a.groupby('state').size().rename('n').reset_index();s['state']=s.state.replace({'타종 기록':'타종 신규 기록','식별 불확실 포함':'종 식별 불확실'});s['rate']=s.n/len(a)*100 if len(a) else np.nan;return a,s
def state_chart(s):
 f=go.Figure(go.Bar(x=s.rate,y=s.state,orientation='h',marker_color=[COLORS[k] for k in s.state],text=[f'{p:.1f}% ({n}칸)' for p,n in zip(s.rate,s.n)],textposition='auto'));style(f,330);f.update_xaxes(range=[0,100],title='단독 점유 소실 칸 중 비율 (%)');f.update_yaxes(automargin=True);return f
def neighbor_summary(z):
 f=z.copy();f['bin']=pd.cut(f.neighbor_other,[-1e-9,.1,.5,1.000001],labels=['0–10%','10% 초과–50%','50% 초과–100%']);return summary(f,['bin']),f
def matched_grazing(z,obs,years):
 o=obs[(obs.kind=='poly')&obs.observed];pairs=set(zip(o.quadrat,o.year));eligible={}
 for q,y in pairs:
  if (q,y+1) in pairs and years[0]<=y<=years[1]:
   treatment,past=q.split('_');eligible.setdefault((past,y),set()).add(treatment)
 keys={k for k,v in eligible.items() if len(v)==4};f=z[[(r.pasture,r.year) in keys for r in z.itertuples()]];return summary(f,['pasture','treatment'])

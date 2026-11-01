import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from research import *

st.set_page_config(page_title='식물이 사라진 자리에는 무엇이 남을까?',layout='wide',initial_sidebar_state='collapsed')
st.markdown('''<style>
.stApp{background:#FAFAF6;color:#24332D}.block-container{max-width:1120px;padding-top:2rem;padding-bottom:4rem}
h1,h2,h3{color:#244F3E;letter-spacing:-.035em}h1{font-size:clamp(2rem,4.5vw,3.5rem)!important;line-height:1.22!important;max-width:950px;margin:1.2rem 0!important}
h2{margin-top:2.3rem!important;font-size:1.65rem!important}p,li{font-size:1.06rem;line-height:1.8;color:#28362E}.stMarkdown p{max-width:800px}
[data-testid="stCaptionContainer"] p{font-size:.85rem;color:#56635A}[data-testid="stRadio"] [role="radiogroup"]{gap:.6rem 1.1rem;flex-wrap:wrap}
@media(max-width:640px){.block-container{padding:1.2rem 1rem 3rem}h1{font-size:2rem!important}p,li{font-size:1rem}[data-testid="stHorizontalBlock"]{flex-wrap:wrap}[data-testid="stColumn"]{min-width:100%!important}}
</style>''',unsafe_allow_html=True)
@st.cache_data
def dataset():return load()
d,m,t=dataset();rep=read_json('representative.json');obs=pd.read_csv(R/'data/observation_audit.csv');metrics=pd.read_csv(R/'data/model_metrics.csv');meta=read_json('model_validation.json')
page=st.radio('연구 탐색',['연구 소개','공간 변화','소실의 조건','예측 비교','결론','방법과 검증'],horizontal=True,label_visibility='collapsed',key='page')
def plot(f):st.plotly_chart(f,width='stretch',config={'displaylogo':False,'responsive':True})
def species(key):return st.selectbox('살펴볼 식물종 (학명)',TOP+sorted(set(t.species)-set(TOP)),key=key)
def details(f,name):
 with st.expander('수치와 분모 확인'):
  st.dataframe(f,hide_index=True);st.download_button('현재 집계 CSV 내려받기',f.to_csv(index=False).encode('utf-8-sig'),name,mime='text/csv',key=name)
def pair_maps(q,y,sp):
 a,b=st.columns(2)
 with a:st.subheader(f'{y}년');plot(cover_map(m,q,y,sp))
 with b:st.subheader(f'{y+1}년');plot(cover_map(m,q,y+1,sp))
def model_story():
 b,e=metrics.iloc[0],metrics.iloc[1];lo,hi=meta['paired_pasture_bootstrap_AP_delta_95']
 st.write(f'주변 정보를 더했을 때 AP는 **{b.pr_auc:.3f}에서 {e.pr_auc:.3f}**로, F1은 **{b.f1:.3f}에서 {e.f1:.3f}**로 높아졌습니다. 반면 전체 정답률은 {b.accuracy:.1%}에서 {e.accuracy:.1%}로 낮아졌습니다.')
 st.write(f'AP 차이의 목장 단위 재표집 95% 구간은 **{lo:+.3f}–{hi:+.3f}**로 0을 포함합니다. 이번 평가만으로 주변 정보가 예측을 안정적으로 개선했다고 결론 내릴 수 없습니다.')

if page=='연구 소개':
 st.title('식물이 사라진 자리에는 무엇이 남을까?')
 st.write('한곳에 뿌리를 내린 식물도 해마다 차지하는 공간이 달라집니다. 지난해 한 종이 기록된 자리에 다음 해에도 같은 종이 있을까요? 다른 종이 나타났다면, 이전부터 함께 있던 식물일까요?')
 st.write('1997–2010년 미국 콜로라도 초원의 24개 고정 조사구를 비교했습니다. 각 조사구는 가로·세로 1m입니다. 식물의 윤곽을 기록한 도형을 10cm 칸으로 나누어, 같은 칸의 식물 구성이 어떻게 바뀌는지 살펴봅니다.')
 st.subheader('같은 1m², 연속된 두 해')
 st.write(f'아래는 **{rep["species"]}**의 피복입니다. 진할수록 그 식물이 칸 안에서 차지하는 면적이 큽니다. {quad_label(rep["quadrat"])}의 실제 기록입니다.')
 pair_maps(rep['quadrat'],rep['year'],rep['species'])
 st.write('색이 옅어졌다고 식물이 죽었다는 뜻은 아닙니다. 이 연구에서 확인하는 것은 **식물의 기록 변화**입니다. 「공간 변화」에서는 소실된 칸에 어떤 종이 기록됐는지, 「소실의 조건」에서는 주변 식생·방목과의 관계를 비교합니다. 「예측 비교」에서는 주변 정보가 다음 해 예측에 도움이 되는지 평가합니다.')
 with st.expander('이 사례를 고른 기준'):
  st.write(f'전체 합산 피복이 가장 큰 종을 선택했습니다. 그 종이 50칸 이상 기록된 조사구·연도쌍 가운데 소실률이 중앙값({rep["eligible_median"]:.1%})에 가장 가까운 사례입니다. 동률은 조사구 코드·연도순으로 선택했습니다. 변화가 가장 큰 사례를 고르지 않았습니다.')
 st.caption('자료: Chu et al. (2013), Shortgrass Steppe LTER. 출처와 관측 누락은 「방법과 검증」에 수록.')

elif page=='공간 변화':
 st.title('사라진 칸에는 무엇이 기록됐을까?')
 st.write('‘점유’는 그 칸 안에 해당 종의 다각형 기록이 조금이라도 있다는 뜻입니다. 두 해의 지도와 변화 지도를 같은 위치에서 비교합니다. **칸 안의 구성 변화이며, 정확히 같은 위치의 교체 면적은 아닙니다.**')
 with st.expander('다른 종·조사구·연도 살펴보기'):
  sp=species('map_species');qs=sorted(t[t.species==sp].quadrat.unique());q=st.selectbox('조사구',qs,index=qs.index(rep['quadrat']) if rep['quadrat'] in qs else 0,format_func=quad_label)
  ys=sorted(t[(t.species==sp)&(t.quadrat==q)].year.unique());y=st.selectbox('이전 해',ys,index=ys.index(rep['year']) if rep['year'] in ys else 0,format_func=lambda k:f'{k} → {k+1}')
  only=st.checkbox('이전 해 이 종만 기록된 칸으로 한정',value=False)
 f=t[(t.species==sp)&(t.quadrat==q)&(t.year==y)];shown=f[f.a_only] if only else f
 st.write(f'**{sp} · {quad_label(q)} · {y}→{y+1}**');pair_maps(q,y,sp)
 st.subheader('같은 칸의 기록 변화')
 if shown.empty:st.info('선택한 조건에 해당하는 이전 해 점유 칸이 없습니다.')
 else:
  plot(change_map(t,sp,q,y,only));st.write(f'비교 대상 {len(shown)}칸 중 {int(shown.lost.sum())}칸에서 다음 해 선택 종의 기록이 없습니다. 연한 바탕은 비교 대상 밖이며 관측 누락이 아닙니다.')
 st.write('**타종 신규 기록**은 해당 타종이 이전 해 같은 칸에는 없었던 경우입니다. 기존 타종과 신규 타종이 함께 있으면 별도 색으로 표시합니다. 종 식별이 불확실하면 교체로 확정하지 않습니다. **다각형 식물 기록 없음은 맨땅을 뜻하지 않습니다.**')
 st.subheader('전체 기간에서, 이 종만 있던 칸이 사라진 뒤')
 st.write('위의 한 조사구 지도와 달리, 아래는 선택한 종의 **전체 조사구·전체 연도** 요약입니다. 이전 해 다른 종이나 식별 불확실 기록이 없던 칸만 골라 기존 공존을 제외했습니다.')
 a,s=state_counts(t[t.species==sp])
 if len(a)<10:st.info(f'소실 사례가 {len(a)}칸·연도로 적어 비율 비교를 생략합니다.')
 else:
  plot(state_chart(s));st.write(f'분모는 단독 점유 후 소실된 **{len(a)}칸·연도**입니다. 다음 해 타종과 불확실 기록이 겹치면 불확실 범주를 우선했습니다.');details(s,'소실후상태.csv')
 with st.expander('종별·조사구별로 비교'):
  aa=t[t.a_only&(t.lost==1)];ss=aa.groupby(['species','state']).size().rename('n').reset_index();ss['total']=ss.groupby('species').n.transform('sum');ss=ss[ss.total>=10];ss['rate']=ss.n/ss.total*100
  ss['state']=ss.state.replace({'타종 기록':'타종 신규 기록','식별 불확실 포함':'종 식별 불확실'});plot(style(px.bar(ss,x='rate',y='species',color='state',orientation='h',color_discrete_map=COLORS,hover_data=['n','total'],labels={'rate':'소실 사례 중 비율 (%)','species':'식물종','state':'다음 해 기록'},range_x=[0,100]),620))
  st.write('소실 사례가 10개 이상인 종만 비교했습니다.');st.dataframe(a.groupby(['quadrat','state']).size().rename('칸·연도 수').reset_index(),hide_index=True)

elif page=='소실의 조건':
 st.title('어떤 조건에서 점유 기록이 사라질까?')
 with st.expander('비교 대상 변경'):
  sp=species('condition_species');years=st.slider('비교할 시작 연도',1997,2009,(1997,2009));exclude=st.checkbox('종 오분류 경고 조사구 3곳 제외',value=False)
 z=t[(t.species==sp)&t.year.between(*years)];z=z[~z.quadrat.isin(['gzgz_24','gzun_24','ungz_24'])] if exclude else z
 st.write(f'**{sp} · {years[0]}–{years[1]}년에 시작하는 연속 관측쌍**')
 st.write(f'이전 해 점유 **{len(z):,}칸·연도**, 조사구 **{z.quadrat.nunique()}곳**, 목장 **{z.pasture.nunique()}곳**을 비교합니다. 같은 칸을 여러 해 관측한 수이므로 독립 표본 수가 아닙니다.')
 if len(z)<10:st.info('비교에 필요한 점유 기록이 10칸·연도 미만입니다.');st.stop()
 st.subheader('주변에 다른 식물이 많으면 더 자주 사라질까?')
 st.write('주변의 8칸 중 다른 종이 기록된 칸의 비율을 비교했습니다. 가장자리는 관측 가능한 3–5칸만 사용합니다. 소실률은 이전 해 이 종이 있던 칸 중 다음 해 기록이 없는 칸의 비율입니다.')
 a,f=neighbor_summary(z);fig=go.Figure(go.Bar(x=a.bin.astype(str),y=a.rate,marker_color=GREEN,text=[f'{r:.1f}%<br>n={n:,}' for r,n in zip(a.rate,a.n)],textposition='outside',customdata=a[['n','losses']],hovertemplate='%{x}<br>소실 %{customdata[1]} / 이전 점유 %{customdata[0]}<extra></extra>'));style(fig);fig.update_yaxes(title='기록 소실률 (%)',range=[0,min(110,max(20,float(a.rate.max())*1.3))]);fig.update_xaxes(title='이전 해 주변 타종 점유 칸 비율');plot(fig)
 st.write(' / '.join(f'{r.bin}: {r.rate:.1f}%' for r in a.itertuples())+'로 관측됐습니다. 초기 피복이나 조사구 환경 차이를 분리한 결과가 아니므로 직접적인 경쟁의 증거로 해석할 수 없습니다.')
 with st.expander('조사구·연도마다 같은 방향인지 확인'):
  g=summary(f,['quadrat','year','bin']);plot(style(px.box(g,x='bin',y='rate',points='all',hover_data=['quadrat','year','n'],color_discrete_sequence=[GREEN],labels={'bin':'주변 타종 점유 칸 비율','rate':'소실률 (%)'},range_y=[0,100])));st.write('각 점은 조사구·연도·주변 구간 하나입니다. 상자는 관측값의 분포이며 신뢰구간이 아닙니다.')
 details(a,'주변조건.csv')
 st.subheader('방목 조건의 차이는 목장마다 같을까?');b=matched_grazing(z,obs,years)
 if b.empty:st.info('네 처리군을 같은 연도쌍으로 비교할 기록이 없습니다.')
 else:
  fig=go.Figure()
  for pasture,g in b.groupby('pasture'):
   g=g.set_index('treatment').reindex(list(TREAT));fig.add_trace(go.Scatter(x=list(TREAT.values()),y=g.rate,mode='lines+markers',name='목장 '+str(pasture),customdata=g[['n','losses']],hovertemplate='%{x}<br>소실률 %{y:.1f}%<br>소실 %{customdata[1]} / 이전 점유 %{customdata[0]}<extra>%{fullData.name}</extra>'))
  style(fig,480);fig.update_yaxes(title='기록 소실률 (%)',range=[0,100]);plot(fig)
  pivot=b.pivot(index='pasture',columns='treatment',values='rate');diff=(pivot.gzgz-pivot.unun).dropna() if {'gzgz','unun'}<=set(pivot.columns) else pd.Series(dtype=float)
  st.write(f'계속 방목과 계속 비방목을 모두 비교할 수 있는 {len(diff)}개 목장 중, 계속 방목의 소실률이 더 높은 곳은 {int((diff>0).sum())}곳, 낮은 곳은 {int((diff<0).sum())}곳입니다. 목장별 차이를 하나의 관리 효과로 단정하지 않습니다.')
  st.write('선 하나는 같은 목장입니다. 좌우 방향은 시간 흐름이 아닙니다. 네 처리군이 모두 관측된 연도쌍으로 맞췄으며, 선택 종의 기록이 없는 칸을 분모에 새로 더하지 않았습니다.');details(b,'목장별방목.csv')

elif page=='예측 비교':
 st.title('주변 식물의 위치를 알면 예측이 나아질까?')
 st.write('이전 해 한 종만 기록된 칸에서 **다음 해 다른 종이 새로 기록될지** 예측했습니다. 기존 종이 남아 있으면서 다른 종이 더해지는 경우도 포함합니다. 미래에 기존 종이 사라질 칸만 미리 골라 학습하지 않았습니다.')
 left,right=st.columns(2)
 with left:st.subheader('기존 정보만 사용');st.write('현재 피복량, 식물종, 조사구, 연도, 방목 이력으로 예측합니다.')
 with right:st.subheader('주변 식물 정보 추가');st.write('같은 정보에 인접 칸의 타종 점유율과 종별 점유율을 더합니다. 주변에 있는 종이 다음 해 같은 칸에 나타나는지 구분하는 데 도움이 되는지 비교합니다.')
 st.write('두 모델은 같은 로지스틱 회귀를 사용했습니다. 1997–2004년 시작 연도쌍으로 학습하고, 2005–2006년으로 판정 기준을 정한 뒤, **사용하지 않은 2007–2009년의 동일한 400개 기록**에서 비교했습니다. 그중 타종 신규 기록은 91개입니다.')
 st.subheader('성능은 조금 달라졌지만, 개선은 확실하지 않았다')
 st.write('**AP**는 신규 기록이 있을 칸을 높은 점수로 잘 구분하는 정도, **F1**은 신규 기록을 놓치거나 잘못 예측하는 두 오류를 함께 반영한 점수입니다. **정답률**은 전체 기록에서 맞힌 비율입니다. 모두 높을수록 좋지만 서로 다른 측면을 평가합니다.')
 fig=go.Figure()
 for i,r in enumerate(metrics.itertuples()):fig.add_trace(go.Bar(name=r.model,x=['신규 기록 구분 (AP)','오탐·누락 균형 (F1)','전체 정답률'],y=[r.pr_auc,r.f1,r.accuracy],text=[f'{v:.3f}' for v in [r.pr_auc,r.f1,r.accuracy]],textposition='outside',marker_color=GREEN if i else '#90998E'))
 style(fig,460);fig.update_layout(barmode='group');fig.update_yaxes(range=[0,1],title='평가 점수 (0–1)');plot(fig);model_story()
 with st.expander('평가 설계와 원래 수치'):
  st.dataframe(metrics,hide_index=True);st.json(meta);st.write('6개 목장을 같은 방식으로 재표집해 두 모델의 AP 차이를 비교했습니다. 모델을 매번 재학습한 불확실성은 아닙니다. 다음 해 종 식별 불확실 기록은 평가에서 제외되어, 식별 가능한 표본에 한정된 성능입니다. 같은 조사구의 미래 평가이며 새로운 지역에서 검증하지 않았습니다.')

elif page=='결론':
 st.title('무엇을 알게 되었을까?');z=t[t.species==TOP[0]];a,s=state_counts(z);ns=s.set_index('state')
 st.subheader('1. 사라진 뒤의 기록은 한 가지가 아니었다')
 st.write(f'대표종 B. gracilis만 있던 칸에서 기록이 사라진 {len(a)}개 사례 중 타종 신규 기록은 {int(ns.loc["타종 신규 기록","n"])}개, 다각형 식물 기록 없음은 {int(ns.loc["다각형 식물 기록 없음","n"])}개, 식별 불확실은 {int(ns.loc["종 식별 불확실","n"])}개였습니다. 불확실 기록을 모두 교체나 맨땅으로 분류할 수 없습니다.')
 st.subheader('2. 주변 식생과 차이는 있었지만 목장마다 달랐다');bins,_=neighbor_summary(z)
 st.write(f'B. gracilis의 주변 타종 점유율 0–10% 구간에서는 소실률이 {bins.iloc[0].rate:.1f}%, 50% 초과 구간에서는 {bins.iloc[-1].rate:.1f}%였습니다. 방목 조건의 차이는 목장에 따라 반대 방향도 나타났습니다. 종 간 경쟁이나 방목의 인과효과를 입증한 결과는 아닙니다.')
 st.subheader('3. 주변 정보의 추가 예측 가치는 불확실했다');st.write('신규 타종 기록의 구분 정도(AP)와 오탐·누락의 균형(F1)을 비교했습니다.');model_story()
 st.subheader('초지 관측에서 제안할 수 있는 일')
 st.write('총피복량과 함께 같은 칸의 점유 유지, 타종 신규 기록, 종 식별 불확실을 구분해 기록할 것을 제안합니다. 식별 불확실이 큰 곳은 현장 재확인 대상으로 삼을 수 있습니다. 이 자료만으로 방목량을 바꾸거나 특정 종을 제거하는 처방은 제안하지 않습니다.')
 st.subheader('이 연구가 말하지 못하는 것')
 st.write('기록 소실은 개체 사망과 다릅니다. 기록 없음은 실제 부재와 다릅니다. 24개 조사구·6개 목장 밖으로 결과를 일반화하는 데 한계가 있습니다. 1년 사이에 어떤 사건이 먼저 일어났는지, 빈 공간이 몇 년 지속됐는지는 이 분석으로 확인하지 않았습니다.')

else:
 st.title('분석 방법과 검증');st.subheader('자료와 관측 범위')
 st.write('미국 콜로라도 Shortgrass Steppe LTER의 1997–2010년 자료입니다. 324개 조사구·연도 관측과 288개 연속 연도쌍을 사용했습니다. 2000년의 12개 조사구 관측 누락을 빈 칸으로 바꾸지 않았습니다.')
 st.markdown('[원자료 설명서](https://esapubs.org/archive/ecol/E094/128/metadata.php) · [공식 보관본](https://doi.org/10.6084/m9.figshare.3556779.v1) · [자료 논문](https://doi.org/10.1890/13-0121.1)')
 with st.expander('관측 상태표'):st.dataframe(obs[['quadrat','year','kind','observed','file_present','status']],hide_index=True)
 st.subheader('면적과 격자는 서로 다른 질문이다')
 st.write('같은 종의 도형은'+' 합집합으로 중복을 제거하고, 유효성 수정 후 고정된 1m² 경계로 잘랐습니다. 도형 분석은 정확한 위치의 면적 변화, 이 사이트의 기본 10cm 분석은 같은 칸의 구성 변화를 뜻합니다. 작은 경계 이동은 도형에서는 소실이지만 격자에서는 유지일 수 있습니다.')
 st.write('점 기록은 별도 기록이며 면적으로 환산하지 않았습니다. 다만 원자료의 일부 다각형은 점에서 만든 0.25cm² 사각형이므로 이를 실제 측정 면적으로 단정할 수 없습니다. 자동 정렬이나 임의 좌표 오차 보정은 하지 않았습니다.')
 st.subheader('불확실한 기록은 따로 남겼다')
 st.write('속 수준·혼합·Crown·미상 기록은 특정 종에 배정하지 않았습니다. 단독 점유 분석에서는 이전 해 불확실 기록이 있는 칸을 제외하고, 다음 해 불확실 기록을 별도 범주로 둡니다. 전체 변화 지도에서 이전 해 식별 불확실이 있어 타종 신규 여부를 확정할 수 없으면 불확실로 표시합니다. A 기록이 유지되면 유지로 표시하고 불확실 동시 기록은 툴팁에서 확인합니다.')
 st.write('원자료의 종 오분류 경고 대상은 gzgz_24, gzun_24, ungz_24입니다. 설명서에 gzun_24가 중복되어 있어 네 번째 조사구를 임의로 추정하지 않았습니다. 「소실의 조건」에서 이 세 곳을 제외한 결과를 비교할 수 있습니다.')
 st.subheader('칸의 크기를 바꾸면 소실률도 달라질까?');sp=species('sensitivity_species');a=summary(d[d.species==sp],['size_cm','threshold']);a['기준']=a.threshold.map({0.:'교차 면적 > 0',.01:'칸 면적의 1% 이상'})
 fig=px.line(a,x='size_cm',y='rate',color='기준',markers=True,hover_data=['n','losses'],labels={'size_cm':'격자 한 변 (cm)','rate':'기록 소실률 (%)'},color_discrete_sequence=[GREEN,ORANGE]);style(fig);fig.update_yaxes(range=[0,100]);fig.update_xaxes(tickvals=[5,10,20]);plot(fig)
 st.write('각 기준에서 이전 해 점유로 분류된 칸이 분모입니다. 격자가 달라지면 칸 수와 점유 판정도 달라지므로 동일 표본에 대한 반복 실험이 아닙니다. 기본 화면의 공간 변화와 예측은 10cm·양의 교차 면적 기준으로 고정했습니다.');details(a,'격자민감도.csv')
 with st.expander('검증 기록과 분석 설정'):
  st.json(read_json('previous_validation.json'));st.json(read_json('grid_definition.json'));st.write('기존 집계 4,490행의 이전 점유·소실 개수를 대조했습니다. 예측은 시간순 학습·검증·평가를 분리했습니다. 새 지도는 기존 격자 피복표의 종 목록을 재사용하며, 원래 소실률이나 모델을 재학습하지 않았습니다.')
 st.subheader('연구계획서에서 구체화한 부분')
 st.write('신규 점유 예측의 모집단은 이전 해 확인된 한 종만 기록된 모든 칸으로 정했습니다. 다음 해 A 소실을 미리 조건으로 걸지 않았습니다. 예측 목표는 A 유지 여부와 무관한 타종 신규 기록입니다. 장기 공백 지속기간과 인과 추정은 포함하지 않았습니다.')
 st.caption('자료 제공: Shortgrass Steppe LTER, Colorado State University, USDA ARS, U.S. Forest Service Pawnee National Grassland. 지원: NSF DEB-1027319, 0823405.')



"""초원 식물 점유 변화 · 연구 전시형 Streamlit 웹사이트.

핵심 화면은 설명→실제 그래프→해석 순서로 구성한다.
연구 수치는 data/ 내 검증된 Codex 분석 결과에 근거한다.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from research import (
    TOP, TREAT, cover_map, load, matched_grazing, neighbor_summary,
    quad_label, read_json, state_counts, summary,
)
from viz import (
    INK, GREEN, RUST, PAPER, base, compare_prediction, neighbor_bar,
    states_bar, transition_map, grazing_points,
)
from pathlib import Path

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='초원 식물의 공간 변화 | 연구 기록',page_icon='🌱',layout='wide',initial_sidebar_state='collapsed')
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Noto+Sans+KR:wght@400;500;600;700&display=swap');
:root{--paper:#FCFCF8;--ink:#24372C;--line:#D9DED3;--forest:#326B53;}
.stApp{background:var(--paper);color:var(--ink)}
.block-container{max-width:1100px;padding-top:1.4rem;padding-bottom:5.5rem}
html,body,p,li,[data-testid="stMarkdownContainer"] {font-family:'DM Sans','Noto Sans KR',sans-serif!important}
[data-testid="stMarkdownContainer"] p {font-size:1.045rem;line-height:1.88;color:#2C3831;margin:0 0 1.15rem;max-width:900px}
[data-testid="stMarkdownContainer"] h1{font-size:clamp(2.4rem,5vw,4rem)!important;letter-spacing:-.065em!important;line-height:1.23!important;color:#193E30!important;font-weight:700!important;margin:1rem 0 1.2rem!important}
[data-testid="stMarkdownContainer"] h2{font-size:1.75rem!important;letter-spacing:-.045em!important;line-height:1.4!important;color:#254B38!important;margin:2.25rem 0 1rem!important}
[data-testid="stMarkdownContainer"] h3{font-size:1.23rem!important;margin:1.35rem 0 .5rem!important;color:#263D31!important}
[data-testid="stMarkdownContainer"] a{color:#2B6950;text-underline-offset:3px}
[data-testid="stMarkdownContainer"] ul{padding-left:1.4rem}
[data-testid="stMarkdownContainer"] li{font-size:1rem;line-height:1.8;margin-bottom:.3rem}
[data-testid="stRadio"]>label{display:none}
[data-testid="stRadio"] [role="radiogroup"]{gap:0.35rem 1.5rem;flex-wrap:wrap;border-bottom:1px solid var(--line);padding-bottom:.85rem}
[data-testid="stRadio"] [role="radio"]{border-color:#BAC4B9}
[data-testid="stRadio"] label{font-size:.99rem!important}
[data-testid="stPlotlyChart"]{margin:.5rem 0 1.25rem}
[data-testid="stHorizontalBlock"]{align-items:start}
hr{border-color:var(--line)!important;margin:2.7rem 0!important}
[data-testid="stExpander"]{border:1px solid #D8DFD7;border-radius:5px;background:transparent}
[data-testid="stMetric"]{background:transparent;border:none}
[data-testid="stCaptionContainer"] p{font-size:.91rem!important;color:#4B584E!important}
.site-kicker{font-size:1rem;font-weight:600;color:#536E5D;letter-spacing:.02em;margin-top:2.2rem}
.site-lead{font-size:1.22rem;line-height:1.85;color:#2F473A;max-width:800px;margin-bottom:1.2rem}
.site-rule{border-top:1px solid var(--line);margin:2.6rem 0}
.article-insight{border-left:3px solid #326B53;padding:10px 0 10px 20px;margin:1.1rem 0 1.8rem;font-size:1.1rem;line-height:1.85;color:#264536}
.meta-foot{border-top:1px solid var(--line);margin-top:3.5rem;padding-top:1.3rem;font-size:.92rem;color:#4E5A52;line-height:1.7}
@media(max-width:720px){.block-container{padding:1rem 1rem 3rem}[data-testid="stMarkdownContainer"] p{font-size:1rem;line-height:1.8}[data-testid="stMarkdownContainer"] h1{font-size:2.4rem!important}[data-testid="stMarkdownContainer"] h2{font-size:1.5rem!important}[data-testid="stHorizontalBlock"]{flex-wrap:wrap}[data-testid="stColumn"]{min-width:100%!important}}
</style>''',unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_data():
    return load()

try:
    all_grids, all_maps, transitions=get_data()
except Exception as exc:
    st.error('분석 자료를 불러오지 못했습니다. GitHub에 data/ 폴더가 함께 업로드되어 있는지 확인해 주세요.')
    st.exception(exc)
    st.stop()

metrics=pd.read_csv(ROOT/'data/model_metrics.csv')
validation=read_json('model_validation.json')
observed=pd.read_csv(ROOT/'data/observation_audit.csv')
F_SPECIES=TOP[0]


def graph(fig, key=None):
    st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False,'responsive':True,'modeBarButtonsToRemove':['lasso2d','select2d']},key=key)


def ruler():
    st.markdown('<div class="site-rule"></div>',unsafe_allow_html=True)


def note(text):
    st.markdown('<div class="article-insight">'+text+'</div>',unsafe_allow_html=True)


def csv_details(df,filename):
    with st.expander('집계 기준과 수치 확인'):
        st.dataframe(df,hide_index=True,use_container_width=True)
        st.download_button('집계 CSV 내려받기',df.to_csv(index=False).encode('utf-8-sig'),file_name=filename,mime='text/csv')


def make_example():
    """Choose a genuine, visually informative case, not a fabricated or claimed-average case."""
    f=transitions[transitions.species==F_SPECIES]
    a=f.groupby(['quadrat','year'],observed=True).agg(n=('cell','size'),lost=('lost','sum')).reset_index()
    a=a[(a.n>=35)&(a.lost>=5)&(a.lost<=40)]
    if a.empty:
        x=read_json('representative.json')
        return x['quadrat'],int(x['year'])
    # choose middle among cases that actually exhibit change; illustrative, NOT representative of all cases
    a=a.assign(rate=a.lost/a.n)
    median=a.rate.median()
    r=a.assign(dist=abs(a.rate-median)).sort_values(['dist','quadrat','year']).iloc[0]
    return str(r.quadrat),int(r.year)


EX_QUAD,EX_YEAR=make_example()
nav=st.radio('사이트 메뉴',['연구 이야기','공간 지도 탐색','조건과 예측','자료와 방법'],horizontal=True,label_visibility='collapsed')

if nav=='연구 이야기':
    st.markdown('<div class="site-kicker">콜로라도 단초원 · 1997–2010년 공간 관측</div>',unsafe_allow_html=True)
    st.title('식물이 사라진 자리에는 무엇이 남을까?')
    st.markdown('''<div class="site-lead">식물은 움직이지 않지만, 초원에서 식물이 차지하는 공간은 매년 달라진다.
    같은 위치에 어떤 식물이 남았고, 어떤 식물이 새로 기록되었는지 14년간의 관측을 비교했다.</div>''',unsafe_allow_html=True)
    st.write('미국 콜로라도의 **1㎡ 고정 조사구 24곳**에서 기록된 식물의 위치를 가로세로 10cm 칸으로 나누었다. 관측이 이어진 **288개 연도쌍**에 대해 같은 칸의 기록을 비교했다. 한 개체의 생존이나 이동을 추적한 연구는 아니다.')
    ruler()

    st.header('식물이 사라진 칸은 모두 빈 공간이 되었을까?')
    st.write('우선 이전 해에 한 종만 기록된 칸을 찾았다. 이 가운데 다음 해 그 종이 기록되지 않은 경우를 모아, 그 칸에 어떤 식물의 다각형이 남았는지 분류했다.')
    focal=transitions[transitions.species==F_SPECIES]
    loss,s=state_counts(focal)
    counts=dict(zip(s.state,s.n))
    new=int(counts.get('타종 신규 기록',0)); unknown=int(counts.get('종 식별 불확실',0)); no_poly=int(counts.get('다각형 식물 기록 없음',0))
    st.markdown(f'대표종 *Bouteloua gracilis*의 단독 점유가 소실된 **{len(loss)}칸·연도 사례**에서 다른 종의 신규 기록은 **{new}건**, 종 식별이 불확실한 경우는 **{unknown}건**이었다.')
    graph(states_bar(s),'story_state_chart')
    note('다른 종이 새로 기록된 칸도 있었지만, 종을 확실히 구분할 수 없는 사례가 더 많았다. 따라서 모든 소실을 종 교체나 빈 땅으로 분류할 수는 없다.')
    st.write(f'나머지 **{no_poly}건**은 다른 식물의 다각형 기록이 없는 경우다. 이는 조사 자료에 식물이 표시되지 않았다는 뜻이지, 실제로 흙이 완전히 드러났다는 뜻은 아니다.')
    ruler()

    st.header('공간에서 보면 변화가 어떻게 나타날까?')
    st.write('아래는 실제 조사구의 연속된 두 관측 연도를 비교한 것이다. 초록색은 같은 종의 기록이 유지된 칸이고, 주황색 계열은 다른 종의 새로운 기록이 나타난 칸이다. 보라색은 종 식별이 불확실한 칸이다.')
    st.write(f'예시: **{quad_label(EX_QUAD)}**, **{EX_YEAR}→{EX_YEAR+1}년**, *{F_SPECIES}*. 공간 변화가 충분히 관찰되는 사례 중 중간 정도의 소실 비율을 보인 한 쌍이다. 전체 초원의 평균을 대표한다고 해석해서는 안 된다.')
    graph(transition_map(transitions,F_SPECIES,EX_QUAD,EX_YEAR),'story_transition')
    st.write('회색은 이전 해에 선택한 종이 기록되지 않아 비교 대상에서 제외된 칸이다. 각 칸에 마우스를 올리면 이전과 다음 해의 종 목록을 확인할 수 있다.')
    st.write('다른 조사구나 연도를 직접 선택하려면 **「공간 지도 탐색」** 화면을 이용하면 된다.')
    ruler()

    st.header('주변에 다른 식물이 많으면 소실이 잦을까?')
    nsum,_=neighbor_summary(focal)
    graph(neighbor_bar(nsum),'story_neighbor')
    st.write(f'주변 타종 점유율이 가장 낮은 구간에서 기록 소실률은 **{nsum.iloc[0].rate:.1f}%**, 높은 구간에서는 **{nsum.iloc[-1].rate:.1f}%**였다. 다른 종이 많이 기록된 주변에서는 소실률도 높게 관측되었지만, 이 비교만으로 식물 사이의 경쟁이 원인이라고 할 수는 없다.')
    ruler()

    st.header('주변 정보를 더 알면 예측도 나아질까?')
    d=metrics.set_index('model')
    b=d.loc['기준 모델'];e=d.loc['주변 정보 추가']
    st.write('기존 종의 정보만 쓰는 모델과 주변 식생까지 입력한 모델을 같은 시기의 관측자료로 비교했다. 평가에 사용한 것은 학습하지 않은 **400칸·연도 사례**다.')
    graph(compare_prediction(metrics),'story_model')
    st.write(f'주변 정보를 추가하면 **AP {b.pr_auc:.3f} → {e.pr_auc:.3f}**, **F1 {b.f1:.3f} → {e.f1:.3f}**로 조금 높아졌지만, 정답률은 낮아졌다. 평가의 불확실성을 고려하면 예측이 안정적으로 개선되었다고 판단하기 어렵다.')
    note('이번 자료로 확인할 수 있는 것은 공간 점유 기록의 변화와 그에 수반된 차이다. 식물이 실제로 죽은 시점이나 종 간 경쟁의 인과관계까지 확인한 것은 아니다.')
    ruler()

    st.header('이 연구에서 남는 제안')
    st.write('초지의 상태를 기록할 때 전체 피복량만 추적하기보다, **같은 칸에서 유지된 종·새로 기록된 종·식별 불확실 기록**을 구분하는 것이 유용하다. 특히 불확실 기록이 많은 조사구에서는 종 식별을 확인하는 추가 조사가 필요하다. 이 자료만으로 방목량을 조정하거나 특정 종을 제거해야 한다고 제안할 수는 없다.')
    st.write('자료의 출처, 계산 기준, 관측 누락은 **「자료와 방법」**에 정리했다.')

elif nav=='공간 지도 탐색':
    st.title('같은 자리의 두 해를 비교하다')
    st.write('조사구는 가로세로 1m다. 이를 10cm 격자로 나누어 선택한 식물종이 기록된 칸이 다음 관측에서 어떻게 달라졌는지 확인한다. 이 지도는 **식물 개체의 이동 경로가 아니라 관측 기록의 변화**를 보여준다.')
    options=TOP+sorted(set(transitions.species)-set(TOP))
    c1,c2,c3=st.columns([1.5,1.6,1.1])
    with c1: sp=st.selectbox('식물종',options,index=0)
    sub=transitions[transitions.species==sp]
    quads=sorted(sub.quadrat.unique())
    idx=quads.index(EX_QUAD) if EX_QUAD in quads else 0
    with c2: q=st.selectbox('조사구',quads,index=idx,format_func=quad_label)
    yrs=sorted(int(y) for y in sub[sub.quadrat==q].year.unique())
    with c3: y=st.selectbox('연도 비교',yrs,index=(yrs.index(EX_YEAR) if EX_YEAR in yrs else 0),format_func=lambda x:f'{x} → {x+1}')
    with st.expander('비교 기준 자세히'):
        only=st.checkbox('이전 해에 해당 종만 기록된 칸으로 한정',value=False)
        st.write('기본값에서는 이전 해에 선택 종이 기록된 칸을 대상으로 하므로 다른 종과 공존한 칸도 포함된다. 단독 점유를 선택하면 이전 해에 다른 종이나 식별 불확실 다각형이 함께 기록된 칸은 제외된다.')
    sel=sub[(sub.quadrat==q)&(sub.year==y)]
    if only:sel=sel[sel.a_only]
    if sel.empty:
        st.info('선택한 기준을 충족하는 칸이 없습니다. 조건을 변경해 보세요.')
    else:
        lost=int(sel.lost.sum())
        st.markdown(f'**{len(sel)}칸**에서 {sp}의 이전 기록을 확인했고, 다음 해 **{lost}칸**에서는 해당 종이 기록되지 않았다.')
        graph(transition_map(transitions,sp,q,y,only),'explorer_change')
        st.write('지도에서 각 칸의 색은 이전 해에 선택한 종을 기준으로 한 상태다. 회색은 비교 대상에서 제외된 칸이며 관측 누락이나 실제 빈 땅을 뜻하지 않는다.')
        a=sel.groupby('map_state',observed=True).agg(n=('cell','size')).reset_index().sort_values('n',ascending=False)
        with st.expander('이 지도에서 집계된 상태별 칸 수'):
            st.dataframe(a.rename(columns={'map_state':'변화 상태','n':'칸 수'}),hide_index=True,use_container_width=True)
        st.header('실제 피복 기록도 비교해 보기')
        st.write('아래 두 지도는 선택 종이 차지한 면적 비율을 같은 10cm 칸에서 계산한 것이다. 위의 상태 지도와 달리 **해당 종의 피복량만** 표시한다.')
        left,right=st.columns(2)
        with left:
            st.markdown(f'### {y}년')
            graph(cover_map(all_maps,q,y,sp),'cover_before')
        with right:
            st.markdown(f'### {y+1}년')
            graph(cover_map(all_maps,q,y+1,sp),'cover_after')
        st.write('색이 옅어졌다고 식물이 죽었다고 판단할 수는 없다. 이 연구는 연 1회 안팎의 공간 기록을 비교한다.')

elif nav=='조건과 예측':
    st.title('어떤 조건에서 공간이 달라졌을까?')
    st.write('첫 번째 분석에서는 소실률과 주변 식생·방목 조건의 관계를, 두 번째 분석에서는 주변 정보를 추가했을 때 다음 해 새 종의 기록을 더 잘 예측할 수 있는지 비교한다.')
    c1,c2=st.columns([2,3])
    with c1: sp=st.selectbox('분석 식물종',TOP,index=0)
    with c2: yrs=st.slider('비교할 시작 연도',1997,2009,(1997,2009))
    exclude=st.checkbox('종 식별 오류 경고가 있는 조사구 3곳 제외',value=False)
    ss=transitions[(transitions.species==sp)&transitions.year.between(*yrs)]
    if exclude: ss=ss[~ss.quadrat.isin(['gzgz_24','gzun_24','ungz_24'])]
    if len(ss)<10:
        st.warning('해당 조건의 자료가 적어 소실률을 비교하기 어렵다.')
    else:
        st.header('주변 식생과 소실률')
        st.write('주변의 8개 칸 중 다른 종이 기록된 칸의 비율을 계산했다. 소실률은 해당 종이 있었던 칸 중 다음 해 기록이 없어진 비율이다. 같은 위치를 여러 해 관측한 결과이므로 칸·연도 사례들이 서로 독립적이지 않다.')
        nsum,full=neighbor_summary(ss)
        graph(neighbor_bar(nsum),'interactive_neighbor')
        a=nsum.iloc[0];b=nsum.iloc[-1]
        st.write(f'**{sp}**에서 주변 타종 점유율이 낮은 구간의 소실률은 {a.rate:.1f}%, 높은 구간의 소실률은 {b.rate:.1f}%였다. 그러나 이 차이는 초기 피복이나 조사구 환경 차이를 조정한 인과효과가 아니다.')
        csv_details(nsum,'주변_식생_소실률.csv')
        ruler()
        st.header('방목 조건별 차이')
        g=matched_grazing(ss,observed,yrs)
        if g.empty:
            st.write('선택한 기간에는 네 처리군이 모두 관측된 연도쌍이 없어 공정한 비교가 어렵다.')
        else:
            graph(grazing_points(g,TREAT),'interactive_grazing')
            st.write('서로 다른 색의 점은 각 목장을 나타낸다. 가로축의 처리 조건은 시간 흐름이 아니다. 목장마다 소실률 차이의 방향이 달라, 방목이 소실을 일관되게 증가 또는 감소시켰다고 판단하기 어렵다.')
            csv_details(g,'방목_조건_소실률.csv')

    ruler()
    st.header('주변 식물의 위치를 이용한 예측')
    st.write('예측의 대상은 **이전 해 한 종만 기록된 칸에 다음 해 다른 종이 새로 기록되는가**이다. 원래 종이 사라지는 경우만 골라 예측한 것은 아니다.')
    st.write('기준 모델은 초기 피복, 종, 조사구, 연도, 방목 정보를 사용했다. 두 번째 모델은 여기에 주변 8방향의 다른 종 점유 정보를 추가했다. 두 모델은 로지스틱 회귀를 사용하고 같은 평가 표본 400개에서 비교했다.')
    graph(compare_prediction(metrics),'interactive_model')
    d=metrics.set_index('model');bb=d.loc['기준 모델'];ee=d.loc['주변 정보 추가']
    low,high=validation['paired_pasture_bootstrap_AP_delta_95']
    st.write(f'AP는 {bb.pr_auc:.3f}에서 {ee.pr_auc:.3f}, F1은 {bb.f1:.3f}에서 {ee.f1:.3f}로 높아졌지만 정답률은 {bb.accuracy:.1%}에서 {ee.accuracy:.1%}로 낮아졌다. **AP 차이의 목장 단위 재표집 구간({low:+.3f}~{high:+.3f})에는 0이 포함된다.** 따라서 개선이 확실하다고 말할 수 없다.')
    with st.expander('지표와 평가 설계 설명'):
        st.write('AP는 신규 기록이 발생할 사례를 높은 점수로 구분하는 정도다. F1은 신규 기록 탐지의 정밀도와 재현율을 함께 반영한다. 정답률은 전체 예측 가운데 맞힌 비율이다. 세 지표는 서로 다른 성질을 평가한다.')
        st.write('학습: 1997–2004년 시작쌍 / 검증: 2005–2006년 / 최종 평가: 2007–2009년. 400개 평가 사례 중 신규 타종 기록은 91개였다. 동일 장소의 미래 관측을 평가했으므로 새로운 지역에 대한 성능을 검증한 것은 아니다.')
        st.dataframe(metrics,hide_index=True,use_container_width=True)

else:
    st.title('어떻게 분석했는가')
    st.header('관측 자료')
    st.write('미국 콜로라도 Shortgrass Steppe LTER의 식물 다각형 기록을 사용했다. 1997–2010년 24개 고정 1㎡ 조사구 중 관측된 조사구·연도는 324개, 연속 관측 연도쌍은 288개다. 일부 조사구의 2000년 자료가 없는 것은 빈땅이 아니라 **관측 누락**으로 처리했다.')
    st.write('[Chu et al. (2013) 연구](https://doi.org/10.1890/13-0121.1) · [자료 보관본](https://doi.org/10.6084/m9.figshare.3556779.v1) · [메타데이터](https://esapubs.org/archive/ecol/E094/128/metadata.php)')
    st.header('점유와 소실을 어떻게 정의했는가')
    st.write('식물 다각형이 10cm 정사각형과 양의 면적으로 겹치면 그 칸을 해당 종이 점유한 것으로 보았다. 다음 연도 같은 칸에서 같은 종의 기록이 없으면 소실로 표시했다. 여러 종이 함께 기록될 수도 있다. 지도와 통계의 소실은 **개체 사망이나 실제 빈땅을 의미하지 않는다**.')
    st.write('점으로 기록된 식물은 다각형 면적에 직접 더하지 않았다. 속 수준 기록, 혼합종, 미상종의 다각형은 임의로 특정 종에 할당하지 않았으며 식별 불확실 범주로 유지했다.')
    st.header('분석의 범위')
    st.write('공간 변화는 같은 칸에 특정 식물이 기록되었는지를 비교한다. 다른 종의 정확한 침입 시점, 개체의 이동, 종 간 경쟁의 직접적인 인과관계는 확인하지 않았다. 주변 식생과 방목 조건의 비교도 관측된 관련성을 기술한 것이다.')
    st.header('격자 크기를 바꾸면?')
    sp=st.selectbox('민감도 분석 식물종',TOP)
    aa=summary(all_grids[all_grids.species==sp],['size_cm','threshold'])
    fig=go.Figure()
    for threshold,part in aa.groupby('threshold'):
        fig.add_trace(go.Scatter(x=part.size_cm,y=part.rate,mode='lines+markers',
            name=('양의 면적 교차' if threshold==0 else '칸 면적의 1% 이상'),
            hovertemplate='격자 %{x}cm<br>소실률 %{y:.1f}%<extra>%{fullData.name}</extra>'))
    base(fig,365);fig.update_xaxes(title='격자 한 변 길이 (cm)',tickvals=[5,10,20]);fig.update_yaxes(title='기록 소실률 (%)',range=[0,100]);graph(fig,'sensitivity')
    st.write('칸 크기가 달라지면 분모와 점유 판정이 모두 바뀐다. 따라서 각 점은 같은 표본을 반복 측정한 결과가 아니다. 다른 화면의 기본 기준은 10cm 및 양의 교차 면적이다.')
    with st.expander('원자료, 관측 누락 및 분석 검증 기록'):
        st.write('원자료 Shapefile은 저장소에 포함하지 않았고, 제공받은 원본 ZIP의 파일 구성과 DBF 레코드 수를 별도 스크립트로 대조했다. 웹앱은 기존 검증된 가공 Parquet를 이용한다.')
        st.dataframe(observed[['quadrat','year','kind','observed','file_present','status']],hide_index=True,use_container_width=True)
        st.json(read_json('grid_definition.json'))
        st.json(validation)
    st.header('연구 계획과 실제 분석의 차이')
    st.write('원래 계획서의 세 질문을 각각 소실 조건 비교, 단독 점유 소실 후 상태 분류, 주변 정보를 추가한 예측 비교로 구현했다. 다만 공간적·시간적 해상도의 한계로 **공백이 실제로 얼마 동안 유지됐는지**와 종 간 경쟁의 인과효과는 분석하지 않았다.')

st.markdown('''<div class="meta-foot">자료: Shortgrass Steppe LTER, Chu et al. (2013). 계산과 모델은 기존 연구 결과를 재사용했으며 이 웹사이트는 시각화와 설명 구조를 재구성한 것이다. 최초 계획서와 실제 분석의 정의 차이는 「자료와 방법」에 설명했다.</div>''',unsafe_allow_html=True)

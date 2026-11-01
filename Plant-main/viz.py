"""Presentation-only plots. All counts come from the preserved research datasets."""
import numpy as np
import plotly.graph_objects as go

INK = '#24372C'
GREEN = '#326B53'
MOSS = '#9DB6A2'
RUST = '#BC6F44'
VIOLET = '#8B789E'
SAND = '#CCBE9F'
BLUE = '#638A9B'
PAPER = '#FCFCF8'
GRAY = '#DADFD5'

STATUS = {
    '점유 유지': (GREEN, '기존 종 유지'),
    '타종 신규 기록': (RUST, '다른 종 신규 기록'),
    '신규·기존 타종 함께': ('#D19A55', '신규·기존 타종 기록'),
    '기존 타종만 기록': (BLUE, '기존 타종만 기록'),
    '종 식별 불확실': (VIOLET, '종 식별 불확실'),
    '다각형 식물 기록 없음': (SAND, '식물 다각형 기록 없음'),
}

def base(fig, height=410):
    fig.update_layout(
        template='plotly_white', paper_bgcolor=PAPER, plot_bgcolor=PAPER,
        font=dict(family='Arial, Malgun Gothic, sans-serif',size=15,color=INK),
        margin=dict(l=12,r=18,t=28,b=55),height=height,
        hoverlabel=dict(bgcolor='#FFFFFF',font_size=13),
        legend=dict(orientation='h',y=-.22,x=0,title=None),
    )
    fig.update_xaxes(showgrid=False,zeroline=False,linecolor='#B9C1B5')
    fig.update_yaxes(showgrid=True,gridcolor='#E6E9E2',zeroline=False)
    return fig

def states_bar(state_df):
    labels = {'타종 신규 기록':'다른 종이 새로 기록됨',
              '종 식별 불확실':'종을 식별하기 어려움',
              '다각형 식물 기록 없음':'다른 식물 다각형 기록 없음'}
    palette={'타종 신규 기록':RUST,'종 식별 불확실':VIOLET,'다각형 식물 기록 없음':SAND}
    keys=['타종 신규 기록','종 식별 불확실','다각형 식물 기록 없음']
    d=state_df.set_index('state')
    vals=[int(d.loc[k,'n']) if k in d.index else 0 for k in keys]
    total=sum(vals)
    fig=go.Figure(go.Bar(y=[labels[k] for k in keys], x=vals, orientation='h',
        marker_color=[palette[k] for k in keys],
        text=[f'{n}칸 · {100*n/total:.1f}%' if total else '0' for n in vals],
        textposition='outside',cliponaxis=False,
        customdata=[f'{100*n/total:.1f}%' if total else '0%' for n in vals],
        hovertemplate='%{y}<br>%{x}칸 (%{customdata})<extra></extra>'))
    base(fig,300)
    fig.update_layout(margin=dict(l=8,r=65,t=12,b=30),showlegend=False)
    fig.update_yaxes(autorange='reversed',showgrid=False,showline=False,tickfont=dict(size=14))
    fig.update_xaxes(title='소실된 격자 수 (칸·연도)',range=[0,max(vals)*1.35 if vals else 1])
    return fig

def neighbor_bar(d):
    labels=list(d['bin'].astype(str))
    vals=list(d['rate'])
    ns=list(d['n'])
    fig=go.Figure(go.Bar(x=labels,y=vals,marker_color=[MOSS,GREEN,RUST],
        text=[f'{v:.1f}%' for v in vals],textposition='outside',cliponaxis=False,
        customdata=ns,hovertemplate='주변 타종 점유율 %{x}<br>소실률 %{y:.1f}%<br>관측 칸·연도 %{customdata:,}<extra></extra>'))
    base(fig,360)
    fig.update_layout(showlegend=False,margin=dict(l=22,r=25,t=30,b=65))
    fig.update_yaxes(title='다음 관측에서 기록 소실 (%)',range=[0,max(15,max(vals)*1.3 if vals else 15)])
    fig.update_xaxes(title='주변 8방향에서 다른 종이 기록된 칸의 비율')
    return fig

def compare_prediction(metrics):
    d=metrics.set_index('model')
    b=d.loc['기준 모델']; e=d.loc['주변 정보 추가']
    fig=go.Figure()
    for title,rr,clr in [('기존 정보',b,'#A2AAA0'),('주변 정보 포함',e,GREEN)]:
        fig.add_trace(go.Bar(x=['AP','F1','정답률'],y=[rr.pr_auc,rr.f1,rr.accuracy],
           name=title,marker_color=clr,text=[f'{v:.3f}' for v in [rr.pr_auc,rr.f1,rr.accuracy]],
           textposition='outside',cliponaxis=False))
    base(fig,350)
    fig.update_layout(barmode='group',margin=dict(l=16,r=18,t=32,b=62))
    fig.update_yaxes(range=[0,1],title='평가 점수 (0–1)')
    return fig

def grazing_points(g, treatments):
    """Compare unordered treatment categories by pasture (no misleading lines)."""
    fig=go.Figure()
    for pasture,part in g.groupby('pasture',observed=True):
        part=part.set_index('treatment').reindex(list(treatments))
        fig.add_trace(go.Scatter(
            x=list(treatments.values()), y=part.rate,
            mode='markers', marker=dict(size=11),
            name='목장 '+str(pasture),
            customdata=part[['n','losses']].to_numpy(),
            hovertemplate='%{x}<br>소실률 %{y:.1f}%<br>소실 %{customdata[1]} / 이전 점유 %{customdata[0]}<extra>%{fullData.name}</extra>',
        ))
    base(fig,440)
    fig.update_yaxes(title='기록 소실률 (%)',rangemode='tozero')
    fig.update_xaxes(title='방목 처리 조건')
    return fig


def transition_map(t, sp, q, year, only=False):
    """Changes in 10cm quadrat cells; outside is *not* empty ground."""
    d=t[(t.species==sp)&(t.quadrat==q)&(t.year==year)]
    if only: d=d[d.a_only]
    status_keys=list(STATUS)
    keys={k:i+1 for i,k in enumerate(status_keys)}
    z=np.zeros(100,dtype=int)
    text=np.array(['이전 관측에서 선택 종 점유 조건에 해당하지 않음']*100,dtype=object)
    for r in d.itertuples():
        cell=int(r.cell)
        z[cell]=keys.get(r.map_state,0)
        text[cell]=(f'{r.map_state}<br>이전: {r.before_species or "확인된 다각형 기록 없음"}'
                    f'<br>다음: {r.after_species or "확인된 다각형 기록 없음"}'
                    f'<br>새로 기록된 타종: {r.new_species or "없음"}')
    # 0 = outside focus; 1..6 = mutually exclusive map categories.
    cols=[GRAY]+[STATUS[k][0] for k in status_keys]
    scale=[]
    for i,clr in enumerate(cols):
        scale.extend([[i/7,clr],[(i+1)/7,clr]])
    fig=go.Figure(go.Heatmap(
        z=z.reshape(10,10),x=np.arange(5,100,10),y=np.arange(5,100,10),
        text=text.reshape(10,10),zmin=-0.5,zmax=6.5,colorscale=scale,
        showscale=False,xgap=1.4,ygap=1.4,
        hovertemplate='위치 x=%{x}cm, y=%{y}cm<br>%{text}<extra></extra>'))
    for key,(clr,lab) in STATUS.items():
        fig.add_trace(go.Scatter(x=[None],y=[None],mode='markers',
            marker=dict(color=clr,size=11,symbol='square'),name=lab))
    base(fig,535)
    fig.update_layout(margin=dict(l=15,r=12,t=12,b=90),
                      legend=dict(orientation='h',y=-0.15,x=0,font=dict(size=12)))
    fig.update_xaxes(title='가로 위치 (cm)',range=[0,100],dtick=20,constrain='domain')
    fig.update_yaxes(title='세로 위치 (cm)',range=[0,100],dtick=20,scaleanchor='x',showgrid=False)
    return fig

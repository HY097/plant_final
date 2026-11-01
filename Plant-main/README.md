# 식물이 사라진 자리에는 무엇이 남을까?

1997–2010년 미국 콜로라도 단초원 고정 조사구에서 식물의 공간 점유 기록이 다음 해 어떻게 달라졌는지 살펴보는 인터랙티브 연구 웹사이트입니다.

**사용자가 처음 열어 볼 페이지는 `app.py`입니다.** Streamlit에서 연구 이야기·공간 지도·소실의 조건과 예측·분석 방법을 탐색할 수 있습니다. 정적 HTML이 아니므로 GitHub Pages가 아니라 **Streamlit Community Cloud** 등 Python 실행 환경에 배포해야 합니다.

## 무엇을 분석했나

- 24개 고정 1㎡ 조사구의 1997–2010년 자료를 10cm 격자로 변환해 관측이 이어진 연도쌍의 같은 위치를 비교했습니다.
- *Bouteloua gracilis*의 단독 점유 소실 194칸·연도 사례 중 다른 종의 신규 기록 75건, 식별 불확실 94건, 다른 식물 다각형 기록 없음 25건을 분류했습니다.
- 주변 타종 점유 비율과 기존 종의 기록 소실률 사이의 관계를 분석했습니다. 목장별 방목 조건 차이도 검토했지만, 관측된 관계를 직접적인 인과효과로 해석하지 않았습니다.
- 기존 정보만 사용한 모델과 주변 식물 정보를 추가한 모델의 신규 타종 기록 예측 성능을 비교했습니다. AP, F1은 소폭 상승했지만 개선의 불확실성이 큽니다.

**중요:** 기록 소실은 식물 사망이 아닙니다. 다각형 식물 기록 없음은 실제 빈 땅을 의미하지 않습니다. 한 칸에서의 변화를 식물 개체의 이동이나 직접적인 종 교체 과정으로 해석해서는 안 됩니다.

## 실행 방법

Python 3.11–3.13 환경에서 아래 명령어를 실행합니다. `requirements.txt`의 버전 범위 안에서 호환 버전을 설치합니다.

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

브라우저에서 Streamlit이 알려주는 로컬 주소(일반적으로 `http://localhost:8501`)를 엽니다.

## GitHub에 올리는 방법

1. 배포 ZIP의 **내부 파일과 폴더를 압축 해제**하여 GitHub 저장소 최상위 위치에 업로드합니다. ZIP 파일 하나만 업로드하면 Streamlit이 앱을 실행할 수 없습니다.
2. 저장소 최상위에 `app.py`, `research.py`, `viz.py`, `requirements.txt`, `.streamlit/`, `data/`가 모두 있는지 확인합니다.
3. Streamlit Community Cloud에서 저장소를 연결하고 **Main file path**를 `app.py`로 지정합니다.
4. 앱이 공개되면 지도 필터, 그래프, 모바일 레이아웃을 실제 브라우저에서 확인합니다.

`data/`의 `.parquet` 파일은 **필수**입니다. GitHub에 소스 코드만 올리고 자료를 제외하면 웹앱이 실행되지 않습니다.

## 프로젝트 구조

```
app.py                        설명과 탐색 페이지
research.py                   기존 연구의 집계·지도 계산 함수 (보존)
viz.py                        새 그림과 범례·타이포그래피에 맞춘 도표
.streamlit/config.toml        Streamlit 테마 설정
data/                         이전 Codex 실행에서 검증한 가공 자료
scripts/audit_raw_shapefiles.py  원자료 ZIP의 파일·DBF 헤더 점검
source_data/shapefiles.zip    (전체 소스 포함본에만 있음)
tests/test_research.py        집계·파일 해시·그래프 회귀 테스트
tests/test_charts_offline.py  독립적인 CSV·Plotly 사전 점검
CHANGELOG.md                  이전 버전과 비교한 변경 내용
DATA_NOTES.md                 자료 유래와 한계
VALIDATION.md                 수행한 검증과 미검증 항목
```

## 테스트

```bash
python -m unittest discover -s tests -v
```

아래 검사는 Streamlit/Parquet 엔진 없이 CSV와 Plotly만으로 가능한 별도 그래프 검사입니다.

```bash
python -m unittest discover -s tests -p test_charts_offline.py -v
```

원자료 ZIP을 포함한 **전체 소스 포함본**에서 원자료 파일 구성 확인:

```bash
python scripts/audit_raw_shapefiles.py source_data/shapefiles.zip
```

이 원자료 검사 스크립트는 DBF 레코드 헤더와 파일 구성을 검사합니다. **Shapefile에서 가공 Parquet를 독립적으로 재계산하는 스크립트는 아닙니다.** 이전 분석 결과와 새로 제공된 원자료의 기하학적 완전 일치 여부까지 독립 검증했다고 주장하지 않습니다.

## 데이터 출처 및 연구 윤리

- Chu et al. (2013), *Ecology*, DOI: [10.1890/13-0121.1](https://doi.org/10.1890/13-0121.1)
- Shortgrass Steppe LTER 자료: [Figshare](https://doi.org/10.6084/m9.figshare.3556779.v1), [Ecological Archives](https://esapubs.org/archive/ecol/E094/128/metadata.php)
- 원자료 Shapefile은 사용자가 제공한 ZIP을 바탕으로 파일 구성 및 레코드 수를 확인했습니다.
- 가공 Parquet, 모델 지표는 이전 Codex 결과물에서 이어받았습니다. 이번 수정의 중심은 **웹사이트 정보 구조, 시각화, 설명, 탐색 흐름**입니다. 모델을 새로 학습했다고 주장하지 않습니다.
- 별도의 `LICENSE`를 두지 않았습니다. 외부 연구 원자료의 재배포 조건과 코드의 공개 라이선스는 별도로 확인해야 합니다.

코드·페이지 제작에는 AI 보조를 사용했습니다. 최종 결론과 발표 내용은 연구자가 검토해야 합니다.

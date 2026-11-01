"""Streamlit's official testing API. Requires streamlit & parquet dependencies."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

app=Path(__file__).resolve().parents[1]/'app.py'
t=AppTest.from_file(str(app),default_timeout=120).run()
if t.exception:raise AssertionError('First page failed: '+str(t.exception))
for page in ['공간 지도 탐색','조건과 예측','자료와 방법','연구 이야기']:
    t.radio[0].set_value(page).run()
    if t.exception:raise AssertionError(f'{page} failed: {t.exception}')
print('PASS: four page navigation and script execution')

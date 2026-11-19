"""Verification of data isolation, saved-model inference and Streamlit UI."""
import sys,json,time,platform
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd,numpy as np
from src.core import ROOT,clean,analyze

def main():
 start=time.perf_counter();checks={}
 if not (ROOT/'data/train.csv').exists():
  from scripts.train import prepare
  prepare()
 parts={n:pd.read_csv(ROOT/f'data/{n}.csv') for n in ['train','validation','test']}
 for a,b in [('train','validation'),('train','test'),('validation','test')]:
  assert not set(parts[a].text)&set(parts[b].text);checks[f'{a}_{b}_overlap']=0
 assert clean('Ａ <b>좋다</b> https://a.b !!!!')=='A 좋다 !!';checks['preprocessing']=True
 results=analyze(['배우들 연기도 어색하고 스토리도 너무 뻔했음.','영화가 정말 재미있고 훌륭했다.'])
 assert len(results)==2 and all(0<=r['positive_probability']<=1 for r in results)
 assert all(r['aspect_status']=='weak_supervision_experimental' for r in results)
 # Aspect analysis always runs, including sentiment-positive reviews.
 assert all('aspect_probabilities' in r for r in results)
 game=analyze(['게임은 재미있는데 조작이 불편하고 버그가 너무 많아요.'],'game')[0]
 assert game['aspect_status']=='unavailable' and not game['complaints']
 for bad in ['', ' '*10, '가'*5001]:
  try:analyze([bad]);raise AssertionError('invalid accepted')
  except ValueError:pass
 checks['model_inference']=results;checks['game_status']=game;checks['invalid_input_rejected']=True
 from streamlit.testing.v1 import AppTest
 at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run();assert not at.exception
 at.button[0].click().run();assert not at.exception;assert len(at.metric)==3
 checks['streamlit_review_analysis']=True
 at.sidebar.radio[0].set_value('프로젝트 소개').run();assert not at.exception
 checks['streamlit_introduction']=True
 at.sidebar.radio[0].set_value('CSV 대시보드').run();assert not at.exception
 checks['streamlit_dashboard_initial']=True
 at.sidebar.selectbox[0].set_value('게임').run();assert not at.exception
 checks['streamlit_game_warning']=True
 import psutil
 checks['process_rss_mb']=psutil.Process().memory_info().rss/1024**2
 checks['model_files_mb']={p.name:round(p.stat().st_size/1024**2,3) for p in (ROOT/'models').glob('*.joblib')}
 checks['seconds']=time.perf_counter()-start
 (ROOT/'reports/runtime_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(checks,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

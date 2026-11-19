import sys,json,io
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import streamlit as st,pandas as pd
from src.core import ROOT,analyze,sentence_evidence,CATEGORIES
st.set_page_config(page_title='Review Insight AI',page_icon='🎬',layout='wide')
st.markdown('''<style>.stApp{background:#f4f7fb;color:#17253b}h1,h2,h3{letter-spacing:-.04em}div[data-testid="stMetric"]{background:white;padding:22px;border-radius:16px;border:1px solid #e2e8f0}.hero{padding:32px;border-radius:22px;background:linear-gradient(120deg,#12243c,#284d78);color:white;margin-bottom:25px}.hero p{color:#d3dfef}</style><div class="hero"><small>REVIEW INTELLIGENCE / 2026</small><h1>Review Insight AI</h1><p>리뷰 속 감성과 불만을 함께 읽습니다.</p></div>''',unsafe_allow_html=True)
st.sidebar.title('Review Insight')
st.sidebar.caption('202335217 · 김서윤')
page=st.sidebar.radio('워크스페이스',['리뷰 분석','CSV 대시보드','프로젝트 소개'])
domain_label=st.sidebar.selectbox('리뷰 도메인',['영화','게임'])
domain='movie' if domain_label=='영화' else 'game'
st.sidebar.info('감성: 직접 학습한 NSMC 모델\n\n영화 불만: 약한 지도 실험 모델\n\n게임: 도메인 외 실험, 불만 모델 미학습')
if domain=='game': st.warning('게임 전용 학습·평가가 없습니다. 감성 결과는 영화 모델의 도메인 외 예측이며 게임 불만 분류는 제공하지 않습니다.')

def run(texts):
 try:return analyze(texts,domain)
 except Exception as exc:st.error(f'분석할 수 없습니다: {type(exc).__name__}: {exc}');return None

if page=='리뷰 분석':
 st.subheader('한 편의 리뷰, 더 깊은 이해')
 text=st.text_area('리뷰를 입력하세요',value='배우들 연기도 어색하고 스토리도 너무 뻔했음.',height=145,max_chars=5000)
 if st.button('리뷰 분석하기',type='primary'):
  result=run([text])
  if result:
   r=result[0];a,b,c=st.columns(3)
   a.metric('전체 감성',r['sentiment']);b.metric('긍정 모델 확률',f"{r['positive_probability']:.1%}");c.metric('불만 유형',f"{len(r['complaints'])}개")
   st.caption('확률은 통계적으로 보정되지 않은 모델 출력이며 정확도를 보장하지 않습니다.')
   if r['uncertain']:st.info('긍정 확률 40~60%: 해석이 애매한 리뷰입니다.')
   st.subheader('세부 불만 유형 · 실험')
   st.warning('자동 규칙으로 만든 약한 레이블로 학습했습니다. 사람 정답 기준 성능은 미검증이며 결과가 틀릴 수 있습니다.')
   st.write(' · '.join(r['complaints']) or ('감지된 불만 없음' if domain=='movie' else '게임 불만 모델 미학습'))
   if r['aspect_probabilities']:st.bar_chart(pd.Series(r['aspect_probabilities'],name='모델 점수'))
   with st.expander('문장별 모델 재분석 · 실험적 보조 정보'):
    st.caption('문장을 분리해 같은 학습 모델로 재예측합니다. 인과적 설명이나 정확한 근거 추출이 아닙니다. 키워드 매칭을 판단 근거로 표시하지 않습니다.')
    st.json(sentence_evidence(text,domain))
elif page=='CSV 대시보드':
 st.subheader('리뷰를 모아, 문제를 발견하세요')
 st.caption('UTF-8/CP949 CSV · review 또는 text 열 · 최대 1,000개 · 업로드한 내용은 디스크에 저장하지 않습니다.')
 sample=pd.DataFrame({'review':['연기는 좋지만 스토리가 지루하고 결말이 뻔하다.','영상과 음악 모두 훌륭했다.','배우의 연기가 어색해서 몰입하기 어려웠다.']})
 st.download_button('예시 CSV 다운로드',sample.to_csv(index=False).encode('utf-8-sig'),'sample_reviews.csv','text/csv')
 upload=st.file_uploader('CSV 파일',type=['csv'])
 if upload:
  if upload.size>5*1024*1024:st.error('5MB 이하 파일만 가능합니다.');st.stop()
  try:
   blob=upload.getvalue()
   try:df=pd.read_csv(io.BytesIO(blob),encoding='utf-8-sig')
   except UnicodeDecodeError:df=pd.read_csv(io.BytesIO(blob),encoding='cp949')
   col=next((c for c in ['review','text'] if c in df.columns),None)
   if col is None:raise ValueError('review 또는 text 열이 필요합니다.')
   if not 1<=len(df)<=1000:raise ValueError('1~1,000행 CSV만 가능합니다.')
   if df[col].isna().any():raise ValueError('빈 리뷰를 제거해 주세요.')
   if st.button('대량 분석 실행',type='primary'):
    with st.spinner('학습 모델로 분석 중...'):result=run(df[col].astype(str).tolist())
    if result:
     out=pd.DataFrame(result);a,b=st.columns(2)
     with a:st.subheader('전체 감성 비율');st.bar_chart(out.sentiment.value_counts(normalize=True))
     counts=out.complaints.explode().dropna().value_counts()
     with b:st.subheader('주요 불만 빈도');st.bar_chart(counts)
     st.caption('불만 빈도는 약한 지도 모델 예측입니다. 다중 레이블이므로 합계가 리뷰 수를 넘을 수 있습니다.')
     for cat in counts.index:
      with st.expander(f'{cat} · 대표 리뷰'):
       matches=out[out.complaints.map(lambda x:cat in x)]
       for _,row in matches.head(3).iterrows():st.write(row.review)
     out['complaints']=out.complaints.map(lambda x:' | '.join(x));out=out.drop(columns='aspect_probabilities')
     st.dataframe(out,use_container_width=True)
     st.download_button('분석 결과 CSV 다운로드',out.to_csv(index=False).encode('utf-8-sig'),'review_analysis.csv','text/csv')
  except Exception as exc:st.error(str(exc))
else:
 st.subheader('감성에서 개선 포인트까지')
 st.write('영화 관객과 콘텐츠 운영자가 리뷰를 읽을 때 전체 만족도와 부분적 불만을 함께 파악하도록 돕는 머신러닝 프로젝트입니다. 전체 감성이 긍정이어도 불만 모델을 항상 실행합니다.')
 st.info('목표: 감성 F1 ≥ 0.80. 영화 → 게임 단계적 확장. 외부 AI API를 호출하지 않습니다.')
 st.markdown('**현재 한계**: 불만 레이블은 자동 약한 지도이며 사람이 검수한 정답 평가가 필요합니다. 게임 전용 학습, Transformer 실험 완료 여부와 공개 배포 상태는 README를 확인하세요.')
 if (ROOT/'reports/comparison.csv').exists():st.dataframe(pd.read_csv(ROOT/'reports/comparison.csv'))
 if (ROOT/'reports/learning_curves.png').exists():st.image(str(ROOT/'reports/learning_curves.png'))

"""Review Insight: 영화별 집계와 직접 리뷰 분석."""
import sys,json,io
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import pandas as pd,streamlit as st
from src.core import ROOT,analyze,CATEGORIES
from src.catalogue import summarize_reviews
from src.moderation import mask_profanity,masked_clauses
st.set_page_config(page_title='Review Insight',layout='wide',page_icon='🎬')
st.markdown('''<style>.stApp{background:#fff;color:#202b32}h1,h2,h3{letter-spacing:-.04em}div[data-testid="stMetric"]{border-bottom:1px solid #e2e6e8;padding:14px 0}section[data-testid="stSidebar"]{background:#f5f7f7}.block-container{max-width:1200px;padding-top:2.3rem}.caption{color:#68747b;font-size:14px}</style>''',unsafe_allow_html=True)
st.sidebar.title('Review Insight')
page=st.sidebar.radio('메뉴',['영화별 리뷰 분석','리뷰 직접 분석','CSV 대량 분석','분석 모델 정보','프로젝트 소개'])
domain_label=st.sidebar.selectbox('분석 대상',['영화','게임']);domain='movie' if domain_label=='영화' else 'game'
st.sidebar.caption('202335217 · 김서윤')

@st.cache_data
def load_catalogue():return json.loads((ROOT/'web/data/catalogue.json').read_text(encoding='utf-8'))
catalogue=load_catalogue();movies=catalogue['movies']

def sentiment_chart(summary):st.bar_chart(pd.Series(summary['sentiment_ratios'],name='리뷰 비율'))
def frequency_chart(summary):
 items=summary['top_complaints']
 if items:st.bar_chart(pd.Series({i['category']:i['count'] for i in items},name='분류된 리뷰 수'))
 else:st.caption('분류된 불만 유형이 없습니다.')

def detail(m):
 st.header(m['title']);st.caption(f"{m['year']} · 한국 영화")
 a,b,c=st.columns(3);a.metric('수록 리뷰 평점',f"{m['summary']['rating_mean']:.2f} / 10");b.metric('분석 리뷰',f"{m['summary']['review_count']:,}개");c.metric('긍정 리뷰 비율',f"{m['summary']['sentiment_ratios']['긍정']:.1%}")
 st.caption('평점은 이 표본에 포함된 실제 이용자 평점의 평균이며 현재 포털 전체 평점과 다릅니다.')
 left,right=st.columns(2)
 with left:st.subheader('리뷰의 전체적인 분위기');sentiment_chart(m['summary'])
 with right:st.subheader('주요 불만 유형');frequency_chart(m['summary']);st.caption('전체 리뷰가 분모이며 한 리뷰에 여러 유형이 포함될 수 있습니다.')
 st.subheader('자주 등장한 표현');st.write(' · '.join(f"{i['expression']} {i['count']}개" for i in m['summary']['issue_expressions']) or '집계된 표현이 없습니다.');st.caption('부정 예측 절의 문자열 빈도이며 인과적 근거가 아닙니다.')
 st.subheader('대표 리뷰');st.caption('욕설은 자동으로 가립니다. 전체 표본의 대표성을 뜻하지 않습니다.')
 for label in ['긍정','부정','혼합']:
  with st.expander(f'{label}으로 분류한 리뷰'):
   for r in m['summary']['examples'][label][:2]:
    st.write(mask_profanity(r['text']));st.caption(f"원 평점 {r['rating']}/10 · 원문 작성일 미제공");st.link_button('원 자료 보기',r['source_url'])
 with st.expander(f"전체 {m['summary']['review_count']}개 리뷰 보기"):
  label=st.selectbox('리뷰 감성',['전체','긍정','부정','혼합'],key='review_label_'+m['id'])
  selected_rows=[r for r in m['reviews'] if label=='전체' or r['sentiment']==label]
  selected_rows=sorted(selected_rows,key=lambda r:(not 15<=len(r['text'])<=220,r['id']))
  if selected_rows:
   pages=(len(selected_rows)+9)//10;page_number=st.number_input('페이지',min_value=1,max_value=pages,value=1,step=1,key='review_page_'+m['id']+label)
   for r in selected_rows[(page_number-1)*10:page_number*10]:
    st.write(mask_profanity(r['text']));st.caption(f"평점 {r['rating']}/10 · {r['sentiment']}으로 분류")
   st.caption(f'{len(selected_rows)}개 중 페이지 {page_number}/{pages}')
  else:st.caption('해당 감성 리뷰가 없습니다.')
 st.caption('자료: Kim, Lim, Kwon (2022), Mendeley Data V6 · CC BY 4.0 · 원 자료 공개 2022-05-24')
 st.link_button('데이터 출처',catalogue['source']['url'])

if page=='영화별 리뷰 분석':
 st.title('평점과 함께 읽는 영화 리뷰');st.write('한국 영화의 평가를 살펴보고 서로 다른 리뷰를 비교하세요.')
 a,b=st.columns(2);a.metric('한국 영화',f'{len(movies)}편');b.metric('실제 리뷰 표본',f"{sum(m['summary']['review_count'] for m in movies):,}개")
 search=st.text_input('영화 검색',placeholder='영화 제목');sort=st.selectbox('정렬',['수록 리뷰 평점 높은 순','긍정 비율 높은 순','부정 비율 높은 순','리뷰 수 많은 순'])
 rows=[m for m in movies if search.strip() in m['title']]
 key={'수록 리뷰 평점 높은 순':lambda m:m['summary']['rating_mean'],'긍정 비율 높은 순':lambda m:m['summary']['sentiment_ratios']['긍정'],'부정 비율 높은 순':lambda m:m['summary']['sentiment_ratios']['부정'],'리뷰 수 많은 순':lambda m:m['summary']['review_count']}[sort]
 rows=sorted(rows,key=key,reverse=True)
 st.dataframe(pd.DataFrame([{'영화':m['title'],'개봉연도':m['year'],'수록 리뷰 평점':round(m['summary']['rating_mean'],2),'리뷰 수':m['summary']['review_count'],'긍정 비율':f"{m['summary']['sentiment_ratios']['긍정']:.1%}",'부정 비율':f"{m['summary']['sentiment_ratios']['부정']:.1%}",'혼합 비율':f"{m['summary']['sentiment_ratios']['혼합']:.1%}"} for m in rows]),hide_index=True,use_container_width=True)
 st.caption('일부 공개 리뷰 이력에서 추출한 표본으로 전체 관객을 대표하지 않습니다. 평점과 모델 감성은 별개입니다.')
 selected=st.selectbox('영화 상세 보기',[m['title'] for m in rows],index=None,placeholder='영화 선택')
 if selected:detail(next(m for m in rows if m['title']==selected))
 compare=st.multiselect('두 영화 비교',[m['title'] for m in movies],max_selections=2)
 if len(compare)==2:
  st.subheader('주요 불만 유형 비교')
  selected_movies=[next(m for m in movies if m['title']==title) for title in compare]
  compare_df=pd.DataFrame({m['title']:{c['category']:c['ratio'] for c in m['summary']['complaints']} for m in selected_movies});st.bar_chart(compare_df)
  st.caption('각 영화의 전체 분석 리뷰를 분모로 계산한 비율입니다.')
elif page=='리뷰 직접 분석':
 st.title('이 리뷰는 어떤 평가일까요?')
 if domain=='game':st.info('게임 전용 모델이 아닌 영화 모델로 분석합니다. 게임 불만 유형은 제공하지 않습니다.')
 text=st.text_area('리뷰 내용',value='음악은 좋은데 스토리는그닥..',height=150,max_chars=5000)
 if st.button('분석하기',type='primary'):
  try:
   r=analyze([text],domain)[0];a,b,c=st.columns(3);a.metric('전체 감성',r['sentiment']);b.metric('긍정 가능성',f"{r['positive_probability']:.1%}");c.metric('불만 유형',f"{len(r['complaints'])}개")
   if r['uncertain']:st.info('긍정과 부정의 구분이 애매한 리뷰입니다.')
   st.subheader('주요 불만 유형');st.write(' · '.join(r['complaints']) or '분류된 불만 유형이 없습니다.')
   st.subheader('문장별 상세 분석');clauses=pd.DataFrame(masked_clauses(r['clauses'])).rename(columns={'text':'문장','sentiment':'감성','positive_probability':'긍정 가능성'});st.dataframe(clauses,hide_index=True,use_container_width=True)
   st.caption('확률과 분류의 의미는 분석 모델 정보의 기준 및 한계를 확인하세요.')
  except Exception as e:st.error(f'분석할 수 없습니다: {e}')
elif page=='CSV 대량 분석':
 st.title('여러 리뷰를 한눈에');st.caption('review 또는 text 열 · UTF-8/CP949 · 최대 1,000행·5MB')
 sample=pd.DataFrame({'review':['음악은 좋은데 스토리는그닥..','영상과 음악 모두 훌륭했다.']})
 st.download_button('예시 CSV 다운로드',sample.to_csv(index=False).encode('utf-8-sig'),'sample_reviews.csv','text/csv')
 upload=st.file_uploader('CSV 파일',type=['csv'])
 if upload:
  try:
   if upload.size>5*1024*1024:raise ValueError('5MB 이하 파일만 지원합니다.')
   try:df=pd.read_csv(io.BytesIO(upload.getvalue()),encoding='utf-8-sig')
   except UnicodeDecodeError:df=pd.read_csv(io.BytesIO(upload.getvalue()),encoding='cp949')
   column=next((c for c in ['review','text'] if c in df.columns),None)
   if column is None:raise ValueError('review 또는 text 열이 필요합니다.')
   if not 1<=len(df)<=1000:raise ValueError('1~1,000행만 지원합니다.')
   if df[column].isna().any():raise ValueError('빈 리뷰를 제거해 주세요.')
   if st.button('대량 분석 실행',type='primary'):
    results=analyze(df[column].astype(str).tolist(),domain);out=pd.DataFrame(results);a,b=st.columns(2)
    with a:st.subheader('감성 분포');st.bar_chart(out.sentiment.value_counts(normalize=True))
    with b:st.subheader('주요 불만 유형');st.bar_chart(out.complaints.explode().dropna().value_counts())
    for category in CATEGORIES[domain]:
     matched=out[out.complaints.map(lambda labels:category in labels)]
     if not matched.empty:
      with st.expander(f'{category} · 분류 사례'):
       for text in matched.review.head(3):st.write(mask_profanity(text))
    out['complaints']=out.complaints.map(lambda labels:' | '.join(labels));out['review']=out.review.map(mask_profanity);out['clauses']=out.clauses.map(lambda clauses:json.dumps(masked_clauses(clauses),ensure_ascii=False));out=out.drop(columns='aspect_probabilities')
    st.dataframe(out,use_container_width=True);st.download_button('분석 결과 CSV 다운로드',out.to_csv(index=False).encode('utf-8-sig'),'review_analysis.csv','text/csv')
  except Exception as e:st.error(str(e))
elif page=='분석 모델 정보':
 st.title('분석 기준 및 한계');st.dataframe(pd.read_csv(ROOT/'reports/comparison.csv'),hide_index=True)
 st.markdown('''감성은 NSMC로 직접 학습한 이진 모델입니다. F1 0.8688은 혼합 또는 불만 성능이 아닙니다. 긍정 가능성은 보정하지 않은 모델 출력입니다.

혼합은 절별 긍정 가능성 60% 이상과 40% 이하가 함께 나타날 때 표시하는 보조 판정입니다. 문장 전체와 절별 결과는 문맥 차이로 다를 수 있습니다.

불만은 약한 레이블로 학습했으며 독립 사람 정답 평가와 확률 보정은 미완료입니다. 원시 점수를 정확도처럼 표시하지 않습니다. 12개 문맥 대조 점검 중 3개가 기대와 달랐으며 이는 제한된 시험입니다.

영화 평점은 수록된 실제 리뷰 평점의 평균입니다. 현재 포털 전체 평점·인증 관객 평균이 아니며 편의표본이라 전체 관객을 대표하지 않습니다. 빈도 비율의 분모는 전체 분석 리뷰이며 여러 범주가 겹칠 수 있습니다.

Transformer GPU 학습, 게임 전용 모델과 사람 정답 불만 평가는 아직 완료하지 않았습니다.''')
 st.caption('자료: Kim, Lim, Kwon (2022), Mendeley Data V6 · CC BY 4.0');st.link_button('영화 리뷰 출처',catalogue['source']['url']);st.code(catalogue['analysis_signature'],language=None)
else:
 st.title('Review Insight');st.write('영화 리뷰의 전체 감성과 구체적인 불만을 함께 살펴봅니다. 실제 영화별 결과를 비교하거나 직접 리뷰와 CSV를 분석할 수 있습니다.')
 st.write('202335217 김서윤 · 기계학습프로그래밍');st.link_button('공개 서비스','https://030217zerogirl-lang.github.io/review-insight-ai-202335217/');st.link_button('GitHub','https://github.com/030217zerogirl-lang/review-insight-ai-202335217')

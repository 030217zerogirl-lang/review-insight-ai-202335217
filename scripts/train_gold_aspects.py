"""Train/evaluate multi-label models on independently human-reviewed CSV only."""
import sys,json,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd,numpy as np,joblib
from sklearn.pipeline import Pipeline
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score,multilabel_confusion_matrix
from src.core import ROOT,clean,CATEGORIES

def main():
 p=argparse.ArgumentParser();p.add_argument('csv');p.add_argument('--domain',choices=['movie','game'],default='movie');a=p.parse_args()
 df=pd.read_csv(a.csv);cats=CATEGORIES[a.domain]
 required=['text','split','annotator','reviewed',*cats]
 if not set(required)<=set(df):raise ValueError('필수 열: '+str(required))
 if df.annotator.isna().any() or not df.reviewed.astype(str).str.lower().isin(['true','1']).all():raise ValueError('사람 검수 메타데이터가 필요합니다.')
 if df[cats].isna().any().any() or not df[cats].isin([0,1]).all().all():raise ValueError('범주별 0/1을 입력하세요.')
 df['text']=df.text.map(clean)
 if df.text.duplicated().any():raise ValueError('정규화 텍스트 중복을 먼저 제거하세요.')
 if not set(df.split)=={'train','validation','test'}:raise ValueError('고정된 세 분할이 필요합니다.')
 frames={n:df[df.split==n] for n in ['train','validation','test']}
 for n,f in frames.items():
  if ((f[cats].sum()==0)|(f[cats].sum()==len(f))).any():raise ValueError(f'{n}: 카테고리별 양성/음성 지원 수 부족')
 candidates=[]
 for analyzer,ng in [('word',(1,2)),('char',(2,5))]:
  model=Pipeline([('tfidf',TfidfVectorizer(analyzer=analyzer,ngram_range=ng,min_df=1,max_features=60000)),('ovr',OneVsRestClassifier(LogisticRegression(max_iter=300,class_weight='balanced',random_state=42)))])
  model.fit(frames['train'].text,frames['train'][cats]);score=model.predict_proba(frames['validation'].text)
  for threshold in [.3,.5,.7]:candidates.append((f1_score(frames['validation'][cats],score>=threshold,average='micro'),threshold,analyzer,model))
 best_by_model=[max([r for r in candidates if r[2]==name],key=lambda r:r[0]) for name in ['word','char']]
 selected=max(best_by_model,key=lambda r:r[0]);result=[]
 for val,threshold,name,model in best_by_model:
  y=frames['test'][cats];pred=model.predict_proba(frames['test'].text)>=threshold
  result.append({'model':name,'validation_micro_f1':val,'threshold':threshold,'micro_f1':f1_score(y,pred,average='micro'),'macro_f1':f1_score(y,pred,average='macro'),'per_category_f1':dict(zip(cats,map(float,f1_score(y,pred,average=None)))),'positive_support':y.sum().to_dict(),'confusion_matrices':multilabel_confusion_matrix(y,pred).tolist()})
  joblib.dump(model,ROOT/f'models/gold_aspect_{a.domain}_{name}.joblib')
 (ROOT/f'reports/gold_aspect_{a.domain}.json').write_text(json.dumps({'results':result,'selected_by_validation':selected[2],'threshold':selected[1],'deployment':'Not activated automatically: review manifest and inference threshold before deployment.'},ensure_ascii=False,indent=2),encoding='utf-8')
 print(result)
if __name__=='__main__':main()

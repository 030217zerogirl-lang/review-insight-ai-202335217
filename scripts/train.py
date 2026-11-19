"""Run once: deduplicate, freeze splits, select on validation, evaluate held-out test."""
import sys,json,time,platform,hashlib,re,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd,numpy as np,joblib,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression,SGDClassifier
from sklearn.metrics import accuracy_score,precision_recall_fscore_support,confusion_matrix,ConfusionMatrixDisplay,log_loss,f1_score,classification_report
from sklearn.multiclass import OneVsRestClassifier
from src.core import ROOT,clean,CATEGORIES
SEED=42

def save(name,obj):
 (ROOT/'reports'/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def metrics(y,p):
 a,b,c,_=precision_recall_fscore_support(y,p,average='binary',zero_division=0)
 return dict(accuracy=accuracy_score(y,p),precision=a,recall=b,f1=c)
def prepare():
 for folder in ['data','reports','models']:(ROOT/folder).mkdir(exist_ok=True)
 candidates=sorted(ROOT.parent.glob('**/ratings_train.txt'))
 source=next((p for p in candidates if '215141' in str(p)),candidates[0] if candidates else None)
 if source is None:
  source=ROOT/'data/ratings_train.txt'
  import urllib.request
  urllib.request.urlretrieve('https://raw.githubusercontent.com/e9t/nsmc/master/ratings_train.txt',source)
 raw=pd.read_csv(source,sep='\t').dropna(subset=['document','label'])
 raw['text']=raw.document.map(clean)
 examples=raw[['document','text']].loc[raw.document!=raw.text].head(30)
 examples.to_csv(ROOT/'reports/preprocessing_examples.csv',index=False,encoding='utf-8-sig')
 conflicts=raw.groupby('text').label.nunique(); ambiguous=set(conflicts[conflicts>1].index)
 data=raw.loc[~raw.text.isin(ambiguous)&raw.text.ne('')].drop_duplicates('text').copy()
 train,hold=train_test_split(data,test_size=.2,stratify=data.label,random_state=SEED)
 val,test=train_test_split(hold,test_size=.5,stratify=hold.label,random_state=SEED)
 for name,frame in [('train',train),('validation',val),('test',test)]:
  frame[['id','text','label']].to_csv(ROOT/f'data/{name}.csv',index=False)
 save('data_audit.json',{'source':str(source.relative_to(ROOT.parent)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'raw_nonmissing':len(raw),'clean_unique':len(data),'conflicting_texts_removed':len(ambiguous),'split_ratio':[.8,.1,.1],'seed':SEED,'split_counts':{n:{'size':len(f),'class_counts':f.label.value_counts().to_dict()} for n,f in [('train',train),('validation',val),('test',test)]},'note':'Only original NSMC training file used. Official test not used; local fixed holdout is test. Prior coursework used NSMC: provenance disclosed.'})
 return train,val,test

def train_sentiment(train,val,test):
 rows=[];models={}; histories={}
 for name,analyzer,ngrams in [('word_lr','word',(1,2)),('char_lr','char',(2,5))]:
  start=time.perf_counter()
  vector=TfidfVectorizer(analyzer=analyzer,ngram_range=ngrams,min_df=3,max_features=100000,sublinear_tf=True,dtype=np.float32)
  x=vector.fit_transform(train.text);v=vector.transform(val.text)
  best=None
  for C in [.5,2.]:
   clf=LogisticRegression(C=C,max_iter=300,random_state=SEED,solver='liblinear')
   clf.fit(x,train.label)
   score=f1_score(val.label,clf.predict(v))
   if best is None or score>best[0]: best=(score,clf,C)
  pipe=Pipeline([('tfidf',vector),('classifier',best[1])]);models[name]=pipe
  rows.append({'model':name,'validation_f1':best[0],'C':best[2],'training_seconds':time.perf_counter()-start,'train_rows':len(train),'max_features':100000,'analyzer':analyzer,'ngrams':str(ngrams)})
  history=[]
  for fraction in [.1,.35,.7,1.]:
   subset=train if fraction==1 else train_test_split(train,train_size=fraction,stratify=train.label,random_state=SEED)[0]
   pv=TfidfVectorizer(analyzer=analyzer,ngram_range=ngrams,min_df=3,max_features=100000,sublinear_tf=True,dtype=np.float32)
   a=pv.fit_transform(subset.text); pc=LogisticRegression(C=best[2],solver='liblinear',max_iter=300,random_state=SEED).fit(a,subset.label)
   history.append({'train_size':len(subset),'train_f1':f1_score(subset.label,pc.predict(a)),'validation_f1':f1_score(val.label,pc.predict(pv.transform(val.text)))})
  histories[name]=history
  print(name,rows[-1],flush=True)
 selected=max(rows,key=lambda r:r['validation_f1'])['model']
 # Test opened for evaluation only after models/hyperparameters/final selection frozen.
 for row in rows:
  name=row['model'];pipe=models[name];pred=pipe.predict(test.text)
  row.update(metrics(test.label,pred));joblib.dump(pipe,ROOT/f'models/{name}.joblib',compress=3)
  ConfusionMatrixDisplay(confusion_matrix(test.label,pred),display_labels=['Negative','Positive']).plot(cmap='Blues')
  plt.title(name);plt.tight_layout();plt.savefig(ROOT/f'reports/{name}_confusion.png',dpi=140);plt.close()
  errors=test.loc[pred!=test.label,['id','text','label']].copy();errors['prediction']=pred[pred!=test.label]
  errors.head(50).to_csv(ROOT/f'reports/{name}_errors.csv',index=False,encoding='utf-8-sig')
 for name,h in histories.items():
  pd.DataFrame(h).to_csv(ROOT/f'reports/{name}_learning_curve.csv',index=False)
  plt.plot([v['train_size'] for v in h],[v['train_f1'] for v in h],label=f'{name} train')
  plt.plot([v['train_size'] for v in h],[v['validation_f1'] for v in h],label=f'{name} validation')
 plt.xlabel('Training examples');plt.ylabel('F1');plt.legend();plt.tight_layout();plt.savefig(ROOT/'reports/learning_curves.png',dpi=150);plt.close()
 pd.DataFrame(rows).to_csv(ROOT/'reports/comparison.csv',index=False)
 (ROOT/'models/manifest.json').write_text(json.dumps({'sentiment':selected+'.joblib','selection':'highest validation F1; test not used for selection','domain':'movie','game_sentiment':'out_of_domain_unvalidated'},indent=2),encoding='utf-8')
 save('training_environment.json',{'python':sys.version,'platform':platform.platform(),'seed':SEED,'models':rows,'transformer':'not_run_yet'})
 return rows

MOVIE=[r'연기|배우|캐스팅|발연기',r'스토리|전개|줄거리|개연성|결말|시나리오',r'연출|편집|감독|카메라',r'그래픽|영상|시각|씨지|CG|cg|특수효과',r'음악|음향|사운드|ost|OST',r'돈|시간|최악|쓰레기']
NEG=r'별로|어색|지루|뻔|최악|쓰레기|못|없|아쉽|불편|싫|엉망|낭비|실망|부족|유치|망|발연기|구리|안 좋'
def train_aspects(train):
 # Weak labels are generated ONLY from sentiment training partition.
 # No human-gold or aspect test performance is claimed.
 y=np.array([[int(bool(re.search(p,t)) and bool(re.search(NEG,t))) for p in MOVIE] for t in train.text])
 counts=y.sum(axis=0)
 pipe=Pipeline([('tfidf',TfidfVectorizer(analyzer='char',ngram_range=(2,4),min_df=3,max_features=60000,sublinear_tf=True)),('classifier',OneVsRestClassifier(LogisticRegression(C=2,max_iter=250,solver='liblinear',class_weight='balanced',random_state=SEED)))])
 pipe.fit(train.text,y);joblib.dump(pipe,ROOT/'models/aspect_movie.joblib',compress=3)
 save('aspect_training.json',{'label_source':'automated_weak_supervision','human_verified':False,'rows':len(train),'positive_counts':dict(zip(CATEGORIES['movie'],map(int,counts))),'evaluation':'NOT AVAILABLE: no independent human-gold test labels','f1_target':'Set after human-gold annotation and class support audit','threshold':.5,'other_definition':'weak generic dissatisfaction cues; overlaps allowed; not fallback','game':'NOT TRAINED'})
 queue=train.sample(min(300,len(train)),random_state=SEED)[['id','text']].copy()
 for cat in CATEGORIES['movie']: queue[cat]=''
 queue['annotator']='';queue['reviewed']=False
 queue.to_csv(ROOT/'data/annotation_queue.csv',index=False,encoding='utf-8-sig')
 print('Weak-supervised aspect model trained:',counts.tolist(),flush=True)

if __name__=='__main__':
 train,val,test=prepare();train_sentiment(train,val,test);train_aspects(train)


import sys,json,joblib,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.core import ROOT,CATEGORIES,analyze
import pandas as pd
out=ROOT/'web/models';out.mkdir(parents=True,exist_ok=True)
for name in ['char_lr','aspect_movie']:
 model=joblib.load(ROOT/f'models/{name}.joblib');v=model.named_steps['tfidf'];c=model.named_steps['classifier']
 if hasattr(c,'estimators_'):coefs=[e.coef_[0].tolist() for e in c.estimators_];bias=[float(e.intercept_[0]) for e in c.estimators_]
 else:coefs=c.coef_.tolist();bias=c.intercept_.tolist()
 payload={'source':f'models/{name}.joblib','source_sha256':hashlib.sha256((ROOT/f'models/{name}.joblib').read_bytes()).hexdigest(),'analyzer':v.analyzer,'ngram_range':v.ngram_range,'sublinear_tf':v.sublinear_tf,'vocabulary':v.vocabulary_,'idf':v.idf_.tolist(),'coefficients':coefs,'intercepts':bias,'labels':['positive'] if name=='char_lr' else CATEGORIES['movie']}
 # numpy vocabulary integers are not JSON native.
 payload['vocabulary']={k:int(i) for k,i in payload['vocabulary'].items()}
 (out/f'{name}.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
texts=pd.read_csv(ROOT/'data/validation.csv').sample(40,random_state=17).text.tolist()+['배우들 연기도 어색하고 스토리도 너무 뻔했음.','게임은 재미있는데 조작이 불편하고 버그가 너무 많아요.']
(ROOT/'reports/parity_inputs.json').write_text(json.dumps(analyze(texts),ensure_ascii=False),encoding='utf-8')
print('Exported learned weights. No retraining and no rules used for inference.')

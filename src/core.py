"""Shared preprocessing and real model inference. No prediction fallback."""
import html,re,unicodedata,json
from pathlib import Path
import joblib,numpy as np
ROOT=Path(__file__).resolve().parents[1]
CATEGORIES={'movie':['연기 및 캐스팅','스토리 및 전개','연출 및 편집','영상 및 시각효과','음악 및 음향','기타'],'game':['조작감 및 인터페이스','게임성 및 재미','스토리 및 캐릭터','그래픽 및 사운드','버그 및 최적화','가격 및 과금','기타']}
def clean(text):
    text=unicodedata.normalize('NFKC',html.unescape(str(text)))
    text=re.sub(r'<[^>]+>|https?://\S+',' ',text)
    text=re.sub(r'([ㅋㅎㅠㅜ!?])\1{2,}',r'\1\1',text)
    return re.sub(r'\s+',' ',text).strip()
def load_models():
    manifest=json.loads((ROOT/'models/manifest.json').read_text(encoding='utf-8'))
    return joblib.load(ROOT/'models'/manifest['sentiment']),manifest

def analyze(texts,domain='movie'):
    model,manifest=load_models()
    texts=[clean(x) for x in texts]
    if any(not x or len(x)>5000 for x in texts): raise ValueError('리뷰는 1~5,000자로 입력해 주세요.')
    probabilities=model.predict_proba(texts)[:,1]
    aspect_path=ROOT/'models'/f'aspect_{domain}.joblib'
    aspect=joblib.load(aspect_path) if aspect_path.exists() else None
    scores=aspect.predict_proba(texts) if aspect else None
    result=[]
    for i,(text,prob) in enumerate(zip(texts,probabilities)):
        labels=[] if scores is None else [c for c,s in zip(CATEGORIES[domain],scores[i]) if s>=.5]
        result.append({'review':text,'domain':domain,'sentiment':'긍정' if prob>=.5 else '부정','positive_probability':float(prob),'confidence':float(max(prob,1-prob)),'uncertain':bool(.4<=prob<=.6),'complaints':labels,'aspect_status':'weak_supervision_experimental' if aspect else 'unavailable','aspect_probabilities':{} if scores is None else dict(zip(CATEGORIES[domain],map(float,scores[i])))})
    return result

def sentence_evidence(text,domain):
    """Re-score sentences with learned classifier; association, not causal explanation."""
    sentences=[s.strip() for s in re.split(r'(?<=[.!?。])\s*|[\n;]',text) if s.strip()]
    return [{'sentence':r['review'],'categories':r['complaints']} for r in analyze(sentences,domain) if r['complaints']] if sentences else []

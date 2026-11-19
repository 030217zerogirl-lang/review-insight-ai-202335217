"""리뷰 정규화와 저장된 모델을 이용한 감성·불만 분석."""
import html,re,unicodedata,json
from functools import lru_cache
from pathlib import Path
import joblib,numpy as np
ROOT=Path(__file__).resolve().parents[1]
CATEGORIES={'movie':['연기 및 캐스팅','스토리 및 전개','연출 및 편집','영상 및 시각효과','음악 및 음향','기타'],'game':['조작감 및 인터페이스','게임성 및 재미','스토리 및 캐릭터','그래픽 및 사운드','버그 및 최적화','가격 및 과금','기타']}
CLAUSE_POSITIVE=.6
CLAUSE_NEGATIVE=.4

def clean(text):
    text=unicodedata.normalize('NFKC',html.unescape(str(text)))
    text=re.sub(r'<[^>]+>|https?://\S+',' ',text)
    text=re.sub(r'([ㅋㅎㅠㅜ!?])\1{2,}',r'\1\1',text)
    return re.sub(r'\s+',' ',text).strip()

def split_clauses(text):
    """문장부호와 대조 연결어를 이용한 절 분리. 형태소 분석은 수행하지 않는다."""
    parts=re.split(r'(?<=[.!?。])\s+|[\n;]+|(?<=지만)|(?<=는데)|(?<=은데)|(?<=으나)|\s+(?:하지만|그런데|반면에|반면)\s*',text)
    parts=[p.strip(' ,') for p in parts if p.strip(' ,')]
    return parts[:39]+[' '.join(parts[39:])] if len(parts)>40 else parts

@lru_cache(maxsize=1)
def load_models():
    manifest=json.loads((ROOT/'models/manifest.json').read_text(encoding='utf-8'))
    return joblib.load(ROOT/'models'/manifest['sentiment']),manifest

@lru_cache(maxsize=2)
def load_aspect(domain):
    path=ROOT/'models'/f'aspect_{domain}.joblib'
    return joblib.load(path) if path.exists() else None

def analyze(texts,domain='movie'):
    if domain not in CATEGORIES:raise ValueError('지원하지 않는 도메인입니다.')
    texts=[clean(x) for x in texts]
    if any(not x or len(x)>5000 for x in texts):raise ValueError('리뷰는 1~5,000자로 입력해 주세요.')
    if not texts:return []
    model,_=load_models();aspect=load_aspect(domain)
    whole_probabilities=model.predict_proba(texts)[:,1]
    groups=[split_clauses(text) for text in texts]
    flat=[part for group in groups for part in group]
    flat_probs=model.predict_proba(flat)[:,1]
    flat_scores=aspect.predict_proba(flat) if aspect is not None else None
    result=[];offset=0
    for text,whole,parts in zip(texts,whole_probabilities,groups):
        probs=flat_probs[offset:offset+len(parts)]
        mixed=bool(np.any(probs>=CLAUSE_POSITIVE) and np.any(probs<=CLAUSE_NEGATIVE))
        clauses=[{'text':p,'sentiment':'긍정' if q>=CLAUSE_POSITIVE else '부정' if q<=CLAUSE_NEGATIVE else '불확실','positive_probability':float(q)} for p,q in zip(parts,probs)]
        scores=None;source='unavailable'
        if aspect is not None:
            part_scores=flat_scores[offset:offset+len(parts)]
            negative=np.flatnonzero(probs<.5)
            if len(parts)>1 and len(negative):
                scores=part_scores[negative].max(axis=0);source='negative_clauses'
            else:scores=part_scores.max(axis=0);source='no_negative_clause' if not len(negative) else 'whole_review'
        labels=[] if scores is None or source=='no_negative_clause' else [c for c,s in zip(CATEGORIES[domain],scores) if s>=.5]
        result.append({'review':text,'domain':domain,'sentiment':'혼합' if mixed else '긍정' if whole>=.5 else '부정','binary_sentiment':'긍정' if whole>=.5 else '부정','positive_probability':float(whole),'confidence':float(max(whole,1-whole)),'uncertain':bool(not mixed and .4<=whole<=.6),'is_mixed':mixed,'mixed_method':'contrast_clause_model_predictions','clauses':clauses,'complaints':labels,'aspect_status':'weak_supervision_experimental' if aspect is not None else 'unavailable','aspect_source':source,'aspect_probabilities':{} if scores is None else dict(zip(CATEGORIES[domain],map(float,scores)))})
        offset+=len(parts)
    return result

def sentence_evidence(text,domain):
    """절별 예측 결과를 표시하는 보조 정보. 인과적 설명은 아니다."""
    return analyze([text],domain)[0]['clauses']

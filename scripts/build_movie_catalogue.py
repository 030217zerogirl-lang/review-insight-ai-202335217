"""공개 리뷰 이력을 원문 제목으로 연결하고 동일 모델로 영화별 결과를 사전 계산한다."""
from pathlib import Path
import sys,json,hashlib,datetime,collections,concurrent.futures,re
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.core import ROOT,CATEGORIES,clean,analyze
from src.catalogue import summarize_reviews,validate_summary

MOVIES=[('1987',2017),('암살',2015),('택시운전사',2017),('공조',2017),('완벽한 타인',2018),('베테랑',2015),('극한직업',2019),('범죄도시',2017),('부산행',2016),('기생충',2019),('군함도',2017),('신과함께-죄와 벌',2017),('신과함께-인과 연',2018),('마스터',2016),('청년경찰',2017),('더 킹',2017),('검사외전',2016),('변호인',2013),('명량',2014),('엑시트',2019)]
SOURCE='https://data.mendeley.com/datasets/jb5knzh8yv/6'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

def main():
    raw=ROOT/'data/movie_raw';entries=json.loads((raw/'source_manifest.json').read_text(encoding='utf-8'))
    allowed={title for title,_ in MOVIES};records={};removed=collections.Counter();conflicts=set();total=0
    for entry in entries:
        path=raw/(entry['file_id']+'.json')
        if digest(path)!=entry['sha256']:raise ValueError('원문 해시 불일치')
        source=json.loads(path.read_text(encoding='utf-8-sig'))
        for index,row in enumerate(source.get('data',[])):
            total+=1;title=str(row.get('title','')).strip();text=str(row.get('review','')).strip()
            if title not in allowed:continue
            try:rating=int(row['rating'])
            except (KeyError,ValueError,TypeError):removed['invalid_rating']+=1;continue
            if not text or len(clean(text))>5000 or not 1<=rating<=10:removed['invalid_row']+=1;continue
            key=(title,clean(text))
            if key in records:
                removed['duplicate_text']+=1
                if records[key]['rating']!=rating:conflicts.add(key)
                continue
            record_id=hashlib.sha256((title+'\0'+clean(text)+'\0'+str(rating)).encode()).hexdigest()[:20]
            records[key]={'id':record_id,'title':title,'text':text,'rating':rating,'source_file_id':entry['file_id'],'source_row_index':index,'source_url':entry['url'],'review_date':None}
    for key in conflicts:records.pop(key,None)
    removed['conflicting_rating_texts']=len(conflicts)
    rows=list(records.values());rows.sort(key=lambda r:(r['title'],r['id']))
    if any(sum(r['title']==title for r in rows)==0 for title,_ in MOVIES):raise ValueError('원문이 없는 영화가 있습니다.')
    manifest={'schema_version':1,'criteria_version':'ri-clause-v2-p60-n40-aspect50-negative-clause','model_files':{name:digest(ROOT/'models'/name) for name in ['char_lr.joblib','aspect_movie.joblib']},'browser_models':{name:digest(ROOT/'web/models'/name) for name in ['char_lr.json','aspect_movie.json']},'python_engine_sha256':digest(ROOT/'src/core.py'),'browser_engine_sha256':digest(ROOT/'web/engine.mjs'),'positive_clause_threshold':.6,'negative_clause_threshold':.4,'aspect_threshold':.5,'aspect_calibrated':False}
    signature=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest();manifest['analysis_signature']=signature
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for start in range(0,len(rows),80):
        batch=rows[start:start+80];predictions=analyze([r['text'] for r in batch])
        for row,pred in zip(batch,predictions):
            for key in ['sentiment','binary_sentiment','positive_probability','clauses','complaints','uncertain']:row[key]=pred[key]
            row['analysis_signature']=signature
        print('Analyzed',min(start+80,len(rows)),'/',len(rows),flush=True)
    movies=[]
    for i,(title,year) in enumerate(MOVIES):
        film_rows=[r for r in rows if r['title']==title]
        movie={'id':'kr-'+str(i+1).zfill(2),'title':title,'year':year,'country':'대한민국','metadata_source':f'https://en.wikipedia.org/wiki/List_of_South_Korean_films_of_{year}','rating_label':'수록 리뷰 평점','rating_source':'네이버 이용자 개별 평점 · Mendeley 공개 이력 표본','rating_source_url':SOURCE,'rating_scale':10,'rating_scope':'mean of unique text reviews in collected sample; not current portal-wide or verified-ticket audience average','reviews':film_rows,'summary':summarize_reviews(film_rows,CATEGORIES['movie']),'small_sample':len(film_rows)<30,'analysis_signature':signature}
        validate_summary(movie);movies.append(movie)
    pilot=movies[:5]
    write(ROOT/'reports/movie_pilot_validation.json',{'movie_count':5,'passed':all(validate_summary(m) for m in pilot),'review_counts':{m['title']:len(m['reviews']) for m in pilot},'checks':['source-title association','source hash','rating range','deduplication','count and ratio denominators','multi-label independent recount'],'analysis_signature':signature})
    source={'name':'Korean Movie Reviews and Historical Ratings of the Reviewer','authors':['Minseon Kim','Boyoung Lim','Hyuk-Yoon Kwon'],'doi':'10.17632/jb5knzh8yv.6','url':SOURCE,'license':'CC BY 4.0','license_url':'https://creativecommons.org/licenses/by/4.0/','published_at':'2022-05-24','retrieved_at':now,'review_dates':'not supplied in selected source records','source_file_count':len(entries),'raw_history_rows':total,'sampling':'40 deterministic random files plus 80 additional files per cohort among first 1000 API-listed files; five cohorts; convenience sample, not representative of all viewers','changes':'selected 20 Korean titles; removed duplicate normalized text and conflicting rating texts; inferred sentiment with project models; discarded source sentiment scores and user identity metadata','removed':dict(removed),'poster_policy':'no posters included: no redistribution permission verified'}
    catalogue={'schema_version':1,'generated_at':now,'analysis_signature':signature,'model_manifest':manifest,'source':source,'categories':CATEGORIES['movie'],'movies':movies}
    write(ROOT/'web/data/catalogue.json',catalogue);write(ROOT/'web/models/analysis_manifest.json',manifest)
    write(ROOT/'reports/movie_catalogue_validation.json',{'passed':all(validate_summary(m) for m in movies),'movie_count':len(movies),'review_count':len(rows),'small_sample_movies':[m['title'] for m in movies if m['small_sample']],'source_manifest_sha256':digest(raw/'source_manifest.json'),'analysis_signature':signature,'source':source})
    # 화면과 사전 계산이 같은 파이프라인을 쓰는지 표본을 다시 검사한다.
    probes=[m['reviews'][0] for m in movies]
    replay=analyze([r['text'] for r in probes]);assert all(a['sentiment']==b['sentiment'] and a['complaints']==b['complaints'] and abs(a['positive_probability']-b['positive_probability'])<1e-12 for a,b in zip(probes,replay))
    write(ROOT/'reports/movie_live_parity.json',{'passed':True,'cases':len(probes),'analysis_signature':signature,'scope':'Python precomputed vs live inference on one genuine review per movie'})
    write(ROOT/'reports/movie_inference_samples.json',probes)
    print('Validated 5-film pilot and 20-film catalogue:',len(rows),'genuine reviews')
if __name__=='__main__':main()

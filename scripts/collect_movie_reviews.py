from pathlib import Path
import requests,json,random,concurrent.futures,hashlib,time
root=Path(__file__).resolve().parents[1]
frozen=json.loads((root/'docs/movie_source_manifest.json').read_text(encoding='utf-8'))
selected=[{'id':entry['file_id'],'movie_folder':entry['folder'],'content_details':{'download_url':entry['url'],'sha256_hash':entry['sha256']}} for entry in frozen]
raw=root/'data/movie_raw';raw.mkdir(parents=True,exist_ok=True)

def download(f):
 path=raw/(f['id']+'.json')
 if not path.exists():
  for attempt in range(3):
   try:
    response=requests.get(f['content_details']['download_url'],timeout=50);response.raise_for_status();response.json();path.write_bytes(response.content);break
   except Exception:
    if attempt==2:raise
 actual=hashlib.sha256(path.read_bytes()).hexdigest()
 expected=f['content_details']['sha256_hash']
 if actual!=expected:raise ValueError('Download hash mismatch: '+f['id'])
 data=json.loads(path.read_text(encoding='utf-8-sig'))
 return {'file_id':f['id'],'folder':f['movie_folder'],'url':f['content_details']['download_url'],'sha256':actual,'records':len(data.get('data',[]))}
result=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 for i,r in enumerate(pool.map(download,selected),1):
  result.append(r)
  if i%25==0:print('Downloaded',i,'/',len(selected),flush=True)
(root/'data/movie_raw/source_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
from collections import Counter
counts=Counter()
for entry in result:
 data=json.loads((raw/(entry['file_id']+'.json')).read_text(encoding='utf-8-sig'))
 counts.update(x.get('title','') for x in data.get('data',[]) if x.get('review'))
print('SOURCE FILES',len(result),'REVIEW ROWS',sum(counts.values()))
print('TOP TITLES',counts.most_common(75))
(root/'reports/movie_title_availability.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2),encoding='utf-8')

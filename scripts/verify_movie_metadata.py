from pathlib import Path
import requests,re,html,json,concurrent.futures
ROOT=Path(__file__).resolve().parents[1];c=json.loads((ROOT/'web/data/catalogue.json').read_text(encoding='utf-8'))
def page(year):
 url=f'https://en.wikipedia.org/wiki/List_of_South_Korean_films_of_{year}'
 response=requests.get(url,headers={'User-Agent':'ReviewInsight academic metadata verification'},timeout=30);response.raise_for_status()
 text=re.sub(r'<[^>]+>',' ',response.text);text=html.unescape(text);return year,re.sub(r'[^가-힣A-Za-z0-9]','',text),url
pages={}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for year,text,url in pool.map(page,sorted({m['year'] for m in c['movies']})):pages[year]=(text,url)
results=[]
for m in c['movies']:
 query=re.sub(r'[^가-힣A-Za-z0-9]','',m['title']);text,url=pages[m['year']]
 results.append({'title':m['title'],'year':m['year'],'url':url,'title_found_in_year_list':query in text})
(ROOT/'reports/movie_metadata_verification.json').write_text(json.dumps({'method':'HTTP yearly release list; normalized Korean title presence','results':results,'all_verified':all(r['title_found_in_year_list'] for r in results)},ensure_ascii=False,indent=2),encoding='utf-8')
print('Metadata matches',sum(r['title_found_in_year_list'] for r in results),'/',len(results))
for r in results:
 if not r['title_found_in_year_list']:print('Needs cross-check:',r['title'],r['year'])

from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.core import ROOT,CATEGORIES
from src.catalogue import validate_summary,summarize_reviews
c=json.loads((ROOT/'web/data/catalogue.json').read_text(encoding='utf-8'))
assert len(c['movies'])==20
assert all(validate_summary(m) for m in c['movies'])
assert len({m['id'] for m in c['movies']})==20
assert all(m['analysis_signature']==c['analysis_signature'] for m in c['movies'])
assert all(r['analysis_signature']==c['analysis_signature'] and r['source_url'].startswith('https://data.mendeley.com/public-files/') for m in c['movies'] for r in m['reviews'])
assert c['model_manifest']['aspect_calibrated'] is False
assert c['source']['license']=='CC BY 4.0'
pilot=json.loads((ROOT/'reports/movie_pilot_validation.json').read_text(encoding='utf-8'));assert pilot['passed'] and pilot['movie_count']==5
report={'passed':True,'movies':20,'genuine_review_count':sum(m['summary']['review_count'] for m in c['movies']),'movie_review_counts':{m['title']:m['summary']['review_count'] for m in c['movies']},'independent_checks':['real source association','rating arithmetic','sentiment denominators','multi-label counts','unique identities','shared analysis version','licensed data provenance'],'browser_visual_test':False}
(ROOT/'reports/movie_tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))

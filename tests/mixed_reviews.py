import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.core import ROOT,analyze,split_clauses
cases=['음악은 좋은데 스토리는그닥..','음악은 좋다. 스토리는 별로다.','음악과 영상 모두 정말 훌륭하다.','최악이고 지루한 영화다.','그냥 보통이다.']
results=analyze(cases)
assert results[0]['sentiment']=='혼합'
assert results[0]['complaints']==['스토리 및 전개']
assert results[1]['sentiment']=='혼합'
assert results[2]['sentiment']=='긍정' and results[2]['complaints']==[]
assert results[3]['sentiment']=='부정'
assert not results[4]['is_mixed']
assert analyze([])==[]
assert len(split_clauses('좋지만 '*100))<=40
report={'regression_tests_passed':True,'method':'same trained binary model scored on contrast clauses; positive >=0.6 and negative <=0.4 yields mixed; complaints require clause negative prediction','not_a_three_class_model':True,'not_a_gold_evaluation':True,'examples':results}
(ROOT/'reports/mixed_review_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('Mixed-review regression tests passed.')

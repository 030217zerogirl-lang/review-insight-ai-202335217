import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.core import ROOT,analyze
CASES=[('연기가 정말 훌륭하고 감동적이다.',[]),('연기가 너무 어색하고 실망스럽다.',['연기 및 캐스팅']),('음악이 정말 좋다.',[]),('음악이 정말 별로다.',['음악 및 음향']),('스토리는 너무 지루하다.',['스토리 및 전개']),('스토리는 전혀 지루하지 않다.',[]),('음악은 좋은데 스토리는그닥..',['스토리 및 전개']),('영상은 좋지만 음악은 별로다.',['음악 및 음향']),('연기는 나쁘지 않다.',[]),('편집이 엉망이라 집중이 안 된다.',['연출 및 편집']),('재미있고 즐거웠다.',[]),('스토리만 좋고 연기가 별로다.',['연기 및 캐스팅'])]
results=[]
for (text,expected),prediction in zip(CASES,analyze([text for text,_ in CASES])):
 results.append({'synthetic_probe':True,'text':text,'expected_categories_for_probe':expected,'predicted_categories':prediction['complaints'],'matches_probe_expectation':set(expected)==set(prediction['complaints']),'sentiment':prediction['sentiment'],'raw_aspect_scores':prediction['aspect_probabilities']})
report={'purpose':'controlled context/negation probes; not human-gold dataset evaluation','cases':len(results),'mismatches':sum(not r['matches_probe_expectation'] for r in results),'aspect_gold_test_available':False,'calibration_performed':False,'calibration_reason':'No independent gold aspect labels. Weak-label agreement cannot calibrate real correctness.','display_policy':'Do not display raw aspect sigmoid scores as correctness probabilities. Movie graphs show classified review counts and sample-denominator shares.','results':results}
(ROOT/'reports/model_context_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('Context audit:',report['mismatches'],'mismatches /',report['cases'],'synthetic probes; not a population accuracy estimate')

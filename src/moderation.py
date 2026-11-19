"""화면과 내보내기 전용 욕설 가림. 모델 입력과 원문은 보존한다."""
import json,re
from functools import lru_cache
from pathlib import Path
@lru_cache(maxsize=1)
def _rules():
 path=Path(__file__).resolve().parents[1]/'web/data/moderation_rules.json'
 return [re.compile(pattern,re.IGNORECASE) for pattern in json.loads(path.read_text(encoding='utf-8'))['patterns']]
def mask_profanity(value):
 text=str(value)
 for pattern in _rules():text=pattern.sub(lambda match:re.sub(r'[^\s]','*',match.group()),text)
 return text
def masked_clauses(clauses):return [{**clause,'text':mask_profanity(clause['text'])} for clause in clauses]

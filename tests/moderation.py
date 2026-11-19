from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.core import ROOT
from src.moderation import mask_profanity
expected=json.loads((ROOT/'reports/moderation_parity.json').read_text(encoding='utf-8'))
c=json.loads((ROOT/'web/data/catalogue.json').read_text(encoding='utf-8'))
rows={r['id']:r for m in c['movies'] for r in m['reviews']}
for item in expected:assert hashlib.sha256(mask_profanity(rows[item['id']]['text']).encode('utf-8')).hexdigest()==item['masked_sha256']
print('Python/JS mask parity passed:',len(expected),'actual reviews')

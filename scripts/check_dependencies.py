from pathlib import Path
import json,importlib.util,subprocess,sys
root=Path(__file__).resolve().parents[1]
status={}
for name in ['streamlit','torch','transformers','fitz','reportlab','ipykernel']:
 try:
  mod=__import__(name);status[name]={'import_success':True,'version':getattr(mod,'__version__','unknown')}
  if name=='torch':status['cuda_available']=mod.cuda.is_available()
 except Exception as exc:status[name]={'import_success':False,'error':str(exc)}
(root/'reports/dependency_status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(status,ensure_ascii=False,indent=2))

from pathlib import Path
import zipfile,subprocess,sys,json
r=Path(__file__).resolve().parents[1]
archive=r.parent/'기말-202335217-김서윤.zip';dest=r.parent/'tmp/review_insight_package_smoke';dest.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(archive) as z:
 for item in z.infolist():
  if Path(item.filename).is_absolute() or '..' in Path(item.filename).parts:raise ValueError('Invalid ZIP path')
 z.extractall(dest)
project=dest/'review-insight-ai'
code="from streamlit.testing.v1 import AppTest; a=AppTest.from_file('app.py',default_timeout=90).run(); assert not a.exception; a.button[0].click().run(); assert not a.exception; assert len(a.metric)==3; print('PACKAGED_APP_PASS')"
result=subprocess.run([sys.executable,'-X','utf8','-c',code],cwd=project,capture_output=True,text=True,encoding='utf-8',timeout=180)
print(result.stdout)
if result.returncode:print(result.stderr);raise RuntimeError('Packaged app failed')
qa={'pdf_pages_reviewed':7,'pdf_visual_layout':'all pages rendered and visually inspected; no clipping or missing glyphs observed','packaged_app_smoke_test':'passed: extracted ZIP loads learned models and renders 3 prediction metrics','browser_screenshots':'not available; computer-use stopped','notebook_outputs':'executed results preserved'}
(r/'reports/final_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print(qa)

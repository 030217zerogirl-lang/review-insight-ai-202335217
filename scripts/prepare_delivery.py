"""검증된 코드·문서·가중치·소개 자료로 제출 ZIP을 만든다."""
from pathlib import Path
import sys,json,shutil,zipfile,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.core import ROOT
from scripts.build_portfolio import build
workspace=ROOT.parent.parent if ROOT.parent.name=='기말프로젝트_개발용' else ROOT.parent
out=workspace/'기말프로젝트_제출용';release=out/'제출파일/review-insight-ai';release.mkdir(parents=True,exist_ok=True)
files=['README.md','submission.json','requirements.txt','requirements-training.txt','app.py','.gitignore','.streamlit/config.toml']
files += ['scripts/'+name for name in ['train.py','train_transformer.py','train_gold_aspects.py','export_browser.py','build_portfolio.py','build_presentation.py','prepare_delivery.py','collect_movie_reviews.py','build_movie_catalogue.py','audit_model_context.py','verify_movie_metadata.py']]
files += ['tests/'+name for name in ['verify.py','mixed_reviews.py','browser_parity.mjs','static_handlers.mjs','movie_catalogue.py','movie_browser_parity.mjs','movie_ui_draft.mjs','public_deployment.mjs']]
files += ['docs/'+name for name in ['data_sources.md','annotation_guidelines.md','rubric_checklist.md','movie_data_sources.md','movie_source_manifest.json','movie_catalogue_summary.md','manual_screen_check.md']]
reports=['comparison.csv','data_audit.json','training_environment.json','aspect_training.json','learning_curves.png','char_lr_confusion.png','word_lr_confusion.png','char_lr_errors.csv','word_lr_errors.csv','char_lr_learning_curve.csv','word_lr_learning_curve.csv','preprocessing_examples.csv','parity_inputs.json','runtime_checks.json','mixed_review_checks.json','browser_model_parity.json','model_context_audit.json','movie_catalogue_validation.json','movie_pilot_validation.json','movie_live_parity.json','movie_browser_parity.json','movie_tests.json','movie_ui_draft_tests.json','movie_metadata_verification.json','movie_inference_samples.json','deployment.json','presentation_validation.json','submission_smoke.json','movie_platform_progress.json']
files += ['reports/'+name for name in reports]
for folder in ['src','models','notebooks','web','presentation']:
 for p in (ROOT/folder).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc']:
   files.append(p.relative_to(ROOT).as_posix())
for name in sorted(set(files)):
 src=ROOT/name
 if not src.exists():raise FileNotFoundError(src)
 dst=release/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
pdf=build(ROOT,ROOT/'output/pdf/portfolio.pdf');shutil.copy2(pdf,release/'portfolio.pdf')
presentation=out/'발표자료';presentation.mkdir(exist_ok=True)
for p in (ROOT/'presentation').glob('*'):
 if p.is_file():shutil.copy2(p,presentation/p.name)
archive=out/'기말-202335217-김서윤.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in release.rglob('*'):
  if not p.is_file():continue
  if '__pycache__' in p.parts or p.suffix=='.pyc':continue
  if p.stat().st_size>100*1024**2:raise ValueError('100MB 초과: '+str(p))
  if any(part in ['.git','developer_notes','container_tools','__pycache__'] for part in p.relative_to(release).parts):raise ValueError('개발 자료 혼입')
  z.write(p,'review-insight-ai/'+p.relative_to(release).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
import nbformat
nb=nbformat.read(release/'notebooks/01_executed_results.ipynb',as_version=4)
assert any(cell.get('outputs') for cell in nb.cells)
assert not any(o.get('output_type')=='error' for cell in nb.cells for o in cell.get('outputs',[]))
required=['student_id','name','title','github_url','demo_url','data_type','training','models','primary_metric']
assert all(k in json.loads((release/'submission.json').read_text(encoding='utf-8')) for k in required)
assert all(f'## {i}.' in (release/'README.md').read_text(encoding='utf-8') for i in range(10))
manifest={'archive':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'file_count':sum(p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' for p in release.rglob('*')),'movie_count':20,'movie_reviews':1478,'presentation_slides':18,'notebook_outputs_retained':True,'zip_integrity':True,'required_submission_fields':True,'remaining':['three_real_service_screenshots','actual_PC_mobile_browser_and_offline_validation','human_gold_aspect_evaluation','transformer_GPU_training','game_specific_models']}
(out/'제출물_검증.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'제출안내.md').write_text('# 제출 안내\n\n업로드할 파일: 기말-202335217-김서윤.zip\n\n제출파일 폴더는 ZIP과 같은 확인용 원본이고, 발표자료 폴더에는 편집 가능한 PPTX·소개 대본·검토용 PDF가 있다. 교수님 안내에 PPT/발표는 필수로 명시되지 않은 추가 자료다.\n\n중요: 실제 서비스 화면 캡처 3장은 아직 없어 D3 보완이 필요하다. docs/manual_screen_check.md를 참고한다. PC/모바일·오프라인 실제 브라우저 검증과 PowerPoint 앱 렌더링 검증도 미완료다. 정답 없는 불만 F1이나 미실행 Transformer 성능을 기재하지 않았다.\n',encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False,indent=2))

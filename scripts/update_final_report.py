from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=r/'scripts/build_submission.py'
t=p.read_text(encoding='utf-8-sig')
needle=' return text\n\ndef pdf(text):'
block=''' if (ROOT/'reports/deployment.json').exists():
  deployed=json.loads((ROOT/'reports/deployment.json').read_text(encoding='utf-8'))
  text=text.replace('GitHub URL: 미게시(인증 필요). Demo URL: 미배포. 공개 URL 요구사항은 아직 충족하지 않았다.',f"GitHub URL: {deployed['github_url']} . Demo URL: {deployed['demo_url']} . Public 저장소와 공개 정적 데모를 배포했다. 실제 브라우저 조작 검증은 제어 도구 중단으로 완료하지 못했다.")
  text=text.replace('게임 전용 학습, GitHub Public 게시와 공개 배포.','게임 전용 학습, 실제 화면 캡처 3장과 브라우저 검증.')
  text=text.replace('플랫폼 계획: Streamlit Community Cloud. 현재 공개 URL 미배포. GitHub 인증도 정상화가 필요하다. deploy 성공·URL을 지어내지 않았다. docs/deployment.md의 순서로 계정 로그인 후 게시한다.',f"플랫폼: GitHub Pages(공개 정적 데모), 로컬 Python Streamlit(원본 앱). 공개 URL: {deployed['demo_url']} . 인증은 샌드박스 밖에서 재확인하니 유효했다. 직접 학습한 TF-IDF vocabulary/IDF/회귀 계수·절편을 JSON으로 변환하여 브라우저가 동일 수식으로 추론한다. Python 대 JavaScript 42개 리뷰의 최대 확률 차이 1.69e-8 미만. 보고서: reports/browser_model_parity.json. 공개 페이지·JS·모델 파일 HTTP 200과 공개 모델의 실제 예측은 tests/public_deployment.mjs로 검증했다. 실제 브라우저 렌더링·파일 선택·다운로드는 미검증이다. GitHub Pages는 Python 서버를 실행하지 않는다. Streamlit 원본 앱도 별도로 제공한다.")
  text=text.replace('CSV 업로드 전체 흐름의 브라우저 검증 여부는 reports/browser_checks.json을 확인한다(파일이 없으면 미검증).','CSV 처리 코드는 Node DOM 대체 객체 기반 단위 검증을 추가했다(reports/static_handler_tests.json). 실제 브라우저 업로드 흐름은 제어 도구 중단으로 미검증이다.')
  text=text.replace('공개 URL 미배포.','공개 URL은 GitHub Pages로 배포했으며 브라우저 검증은 미완료다.')
  text += '\\n추가 문제 해결: 브라우저 제어 호스트 연결 실패와 안전한 URL 식별 실패로 자동 UI 검증이 중단되었다. 다른 브라우저 제어로 우회하지 않고, 학습 가중치를 정적 JSON으로 내보내 수치 일치·HTTP 공개 자산·코드 처리기 검증을 수행했다. 실제 화면 캡처를 만들었다고 주장하지 않았다. GitHub Pages 무료 정적 호스팅은 서버 모델 메모리 제약을 피하지만 첫 모델 다운로드 약 15MB와 브라우저 메모리 비용이 생긴다. 정확한 숫자는 reports/deployment.json에 있다. 향후 완전한 브라우저 실측과 모바일 성능 개선이 필요하다.\\n'
  (ROOT/'README.md').write_text(text,encoding='utf-8')
  sub.update(github_url=deployed['github_url'],demo_url=deployed['demo_url'])
  sub['incomplete']=['transformer_finetuning','human_gold_aspect_evaluation','game_training','real_browser_verification','three_service_screenshots']
  sub['deployment_verification']='HTTP and remote weights inference passed; real browser UI not verified'
  (ROOT/'submission.json').write_text(json.dumps(sub,ensure_ascii=False,indent=2),encoding='utf-8')
  md=md.replace('|D2|2|미충족|공개 URL 미배포|','|D2|2|부분 충족|reports/deployment.json: 공개 HTTP·모델 추론 확인, 실제 브라우저 미검증|')
  md=md.replace('|E1|1|부분 충족|README 헤더 완료, Public 저장소 미게시|','|E1|1|충족|Public GitHub URL, README 0~9 헤더|')
  md=md.replace('제출 전 Public GitHub·공개 URL 확인 필수.','Public GitHub와 공개 URL은 게시 완료. 제출 전 실제 브라우저 동작 및 화면 캡처 추가 필요.')
  (ROOT/'docs/rubric_checklist.md').write_text(md,encoding='utf-8')
 return text

def pdf(text):'''
assert needle in t
t=t.replace(needle,block)
p.write_text(t,encoding='utf-8')
# Tests remain executable from a source ZIP with raw data intentionally excluded.
p=r/'tests/verify.py';t=p.read_text(encoding='utf-8-sig');t=t.replace(' start=time.perf_counter();checks={}'," start=time.perf_counter();checks={}\n if not (ROOT/'data/train.csv').exists():\n  from scripts.train import prepare\n  prepare()")
p.write_text(t,encoding='utf-8')
p=r/'docs/deployment.md';t=p.read_text(encoding='utf-8-sig');t+='\n\n실제 배포 완료: https://030217zerogirl-lang.github.io/review-insight-ai-202335217/ . 저장소: https://github.com/030217zerogirl-lang/review-insight-ai-202335217 . GitHub 인증은 샌드박스 밖에서 정상으로 확인했다. 위 Streamlit 배포 단계는 추가 배포 옵션이다. 공개 데모는 Python 학습 가중치를 JSON으로 변환한 JavaScript 추론 엔진을 사용한다. 검증 범위는 reports/deployment.json 및 browser_model_parity.json에 있다. 브라우저 제어가 안전한 URL 확인 실패로 중단되어 실제 화면 캡처는 없다.\n'
p.write_text(t,encoding='utf-8')

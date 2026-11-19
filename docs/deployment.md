# 공개 배포 안내

1. 로컬에서 `py -3.12 -m streamlit run app.py`로 확인한다.
2. GitHub에 로그인 후 이 폴더를 Public 저장소로 게시한다. `.gitignore`와 모델 크기를 확인하며 원본 수업 자료·검수 대기 리뷰·환경 비밀값은 커밋하지 않는다.
3. https://share.streamlit.io 에 GitHub 계정으로 로그인하고 저장소·main·app.py를 선택한다. Python 3.12와 requirements.txt를 사용한다.
4. 모델 3개는 joblib 압축 파일을 models/에 포함한다. 라이브러리 버전을 동일하게 유지하며 신뢰할 수 없는 pickle/joblib을 업로드·로드하지 않는다.
5. 실제 공개 주소에서 예측/CSV 다운로드를 확인한 뒤 submission.json의 github_url/demo_url 및 README의 상태를 수정하고 PDF와 ZIP을 재생성한다.

공식 문서: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app . 무료 플랜 자원은 변경될 수 있으므로 https://docs.streamlit.io/deploy/streamlit-community-cloud/status 에서 당일 제한을 확인한다. 본 배포는 Transformer를 메모리에 로드하지 않고 압축 TF-IDF 모델만 사용한다. 정확한 메모리는 reports/runtime_checks.json의 로컬 관측치이며 클라우드 보장을 의미하지 않는다.

현재 GitHub CLI 인증 확인에서 토큰 오류를 관측했다. 게시 및 공개 URL은 완료되지 않았다. 계정 인증 후 배포가 필요하다. 공개 URL 미충족 상태를 숨기지 않는다.


실제 배포 완료: https://030217zerogirl-lang.github.io/review-insight-ai-202335217/ . 저장소: https://github.com/030217zerogirl-lang/review-insight-ai-202335217 . GitHub 인증은 샌드박스 밖에서 정상으로 확인했다. 위 Streamlit 배포 단계는 추가 배포 옵션이다. 공개 데모는 Python 학습 가중치를 JSON으로 변환한 JavaScript 추론 엔진을 사용한다. 검증 범위는 reports/deployment.json 및 browser_model_parity.json에 있다. 브라우저 제어가 안전한 URL 확인 실패로 중단되어 실제 화면 캡처는 없다.

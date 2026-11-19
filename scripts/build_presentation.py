"""실험 결과와 영화별 집계로 편집 가능한 PowerPoint와 소개 대본을 생성한다."""
from pathlib import Path
import json,zipfile,html,textwrap,posixpath,datetime
from xml.etree import ElementTree as ET
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'presentation';OUT.mkdir(exist_ok=True)
C=json.loads((ROOT/'web/data/catalogue.json').read_text(encoding='utf-8'))
A=next(m for m in C['movies'] if m['title']=='택시운전사');B=next(m for m in C['movies'] if m['title']=='공조')
FONT='Malgun Gothic';pdfmetrics.registerFont(TTFont('DeckKR','C:/Windows/Fonts/malgun.ttf'))
W,H=1280,720;EMU=9525
P='http://schemas.openxmlformats.org/presentationml/2006/main';D='http://schemas.openxmlformats.org/drawingml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';PKG='http://schemas.openxmlformats.org/package/2006/relationships'
def e(s):return html.escape(str(s),quote=True)
def unit(n):return str(round(n*EMU))
def wrap(s,width,size):
 lines=[]
 for raw in str(s).split('\n'):
  line=''
  for char in raw:
   if pdfmetrics.stringWidth(line+char,'DeckKR',size)>width*.75 and line:lines.append(line);line=char
   else:line+=char
  lines.append(line)
 return lines
slides=[]
def slide(title,notes,source=''):
 obj={'title':title,'notes':notes,'source':source,'elements':[]};slides.append(obj)
 if title:obj['elements'].append({'kind':'text','x':64,'y':45,'w':1152,'h':95,'text':title,'size':32,'bold':True,'color':'203B43'})
 return obj
def txt(s,text,x=64,y=180,w=1152,h=400,size=23,bold=False,color='26373D'):
 s['elements'].append(dict(kind='text',text=text,x=x,y=y,w=w,h=h,size=size,bold=bold,color=color))
def table(s,rows,x=64,y=180,w=1152,row_h=64,size=19,widths=None):s['elements'].append(dict(kind='table',rows=rows,x=x,y=y,w=w,h=row_h*len(rows),row_h=row_h,size=size,widths=widths))
def image(s,path,x,y,w,h):
 with Image.open(ROOT/path) as im:iw,ih=im.size
 scale=min(w/iw,h/ih);s['elements'].append(dict(kind='image',path=path,x=x+(w-iw*scale)/2,y=y+(h-ih*scale)/2,w=iw*scale,h=ih*scale))
S=slide('', '안녕하세요. 영화 리뷰의 전체 감성과 구체적인 불만을 함께 분석하는 Review Insight를 소개하겠습니다. 구현한 기능과 실제 학습·평가 결과, 그리고 아직 남은 한계를 중심으로 설명하겠습니다.')
txt(S,'Review Insight',64,190,1152,100,52,True,'203B43');txt(S,'영화 리뷰의 감성과 불만을 함께 읽기',68,315,1120,90,28);txt(S,'202335217 김서윤\n기계학습프로그래밍 프로젝트 소개',68,500,1120,100,20,color='68747B')
S=slide('칭찬과 불만이 한 리뷰에 함께 있다','음악은 좋지만 스토리가 아쉽다는 리뷰는 긍정과 부정 중 하나로만 정리하면 정보가 사라집니다. 이 문제를 해결하기 위해 이용자와 운영자가 리뷰를 읽는 상황을 구체적으로 정의했습니다.')
txt(S,'“음악은 좋은데 스토리는그닥..”',64,155,1152,90,32,True)
table(S,[['Who','영화 이용자와 콘텐츠 운영자'],['What','전체 감성과 불만 요소를 함께 파악'],['When','콘텐츠 선택 또는 이용 후 리뷰 정리'],['Why','평점만으로 구체적인 개선점을 알기 어려움']],y=290,row_h=65,widths=[190,962],size=21)
S=slide('영화 비교에서 직접 리뷰 분석까지','서비스는 영화별 분석을 첫 화면으로 제공합니다. 영화 목록에서 작품을 선택하고 평점·감성·불만을 확인한 뒤 두 영화를 비교할 수 있습니다. 마지막으로 새로운 리뷰나 CSV를 입력해 같은 모델로 직접 분석할 수 있습니다.')
txt(S,'영화별 리뷰 분석\n작품 선택 → 평점·감성·불만 확인 → 두 영화 비교\n\n리뷰 직접 분석 · CSV 대량 분석\n새 리뷰를 같은 학습 모델로 분석\n\n분석 모델 정보 · 프로젝트 소개\n분석 기준, 자료 출처와 한계를 따로 확인',y=170,size=25,h=420)
S=slide('학습용 데이터와 영화별 분석 자료를 구분했다','학습에는 정답이 있는 NSMC를 사용했습니다. NSMC에는 영화 제목이 없으므로 영화별 통계에는 사용하지 않았습니다. 영화별 서비스에는 영화 제목과 실제 평점이 있는 Mendeley 공개 리뷰 이력을 별도로 사용했습니다. 이 표본의 평균 평점은 현재 포털의 전체 평점이 아닙니다.','NSMC: https://github.com/e9t/nsmc ; Mendeley: https://doi.org/10.17632/jb5knzh8yv.6')
table(S,[['자료','규모','용도'],['NSMC','정제 후 145,962행','이진 감성 학습·평가'],['Mendeley V6','20편 · 실제 리뷰 1,478개','영화별 사전 분석']],y=175,row_h=78,size=21,widths=[290,425,437])
txt(S,'NSMC: 원본 CC0 1.0 · Mendeley: CC BY 4.0\n600개 이력 파일의 20,770개 항목에서 대상 작품을 추출\n중복·상충 평점 제거 후 표본 평균을 계산',y=460,h=170,size=22)
S=slide('전처리 후 80:10:10으로 고정 분할했다','정규화, 태그·URL 제거, 반복 문장부호 축약, 공백 정리를 구현했습니다. 중복과 상충 정답을 제거한 뒤 seed 42로 층화 분할했습니다. TF-IDF는 학습셋에만 fit했고 검증 F1로 모델을 선택했습니다.','reports/data_audit.json ; reports/preprocessing_examples.csv')
table(S,[['분할','리뷰 수'],['학습','116,769'],['검증','14,596'],['테스트','14,597']],x=64,y=170,w=520,row_h=70,size=22)
txt(S,'NFKC·HTML 엔티티 정규화\n태그·URL 제거\n반복 느낌표·물음표 축약\n공백 정리\n\n분할 텍스트 교집합 0\nrandom seed = 42',x=650,y=180,w=550,h=400,size=23)
S=slide('단어 모델과 문자 모델을 직접 학습했다','단어 모델을 베이스라인으로 두고 문자 n-gram 모델을 비교했습니다. 문자 표현은 띄어쓰기와 어미 변화가 있는 한국어 단문에 대응하려는 선택입니다. 두 모델의 C는 같은 검증셋에서 선택했습니다. Transformer를 학습한 것처럼 설명하지 않겠습니다.','reports/training_environment.json ; reports/comparison.csv')
table(S,[['구분','베이스라인','개선 모델'],['표현','단어 TF-IDF 1~2그램','문자 TF-IDF 2~5그램'],['분류기','Logistic Regression','Logistic Regression'],['선택한 C','2.0','2.0']],y=175,row_h=72,size=21)
txt(S,'max_features 100,000 · min_df 3 · sublinear_tf\n검증 F1로 최종 모델을 선택한 뒤 같은 테스트셋에서 비교',y=515,h=100,size=22)
S=slide('문자 모델의 테스트 F1은 0.8688이었다','목표는 테스트 F1 0.80 이상이었습니다. 단어 모델은 0.8093, 문자 모델은 0.8688로 문자 모델이 약 0.0596 높았습니다. 선택은 테스트가 아니라 검증 F1에 기반했습니다. 이 수치는 긍정 클래스의 이진 감성 성능이며 불만이나 혼합의 성능이 아닙니다.','reports/comparison.csv')
table(S,[['모델','Accuracy','Precision','Recall','F1'],['단어 TF-IDF + LR','0.8163','0.8380','0.7825','0.8093'],['문자 TF-IDF + LR','0.8699','0.8729','0.8648','0.8688']],y=190,row_h=82,size=20,widths=[350,200,200,200,202])
txt(S,'목표 F1 0.80 달성',64,490,1152,80,34,True,'23685B');txt(S,'같은 테스트 14,597행 · 긍정 클래스 기준 · 불만/혼합 성능과 구분',64,590,1152,55,19,color='68747B')
S=slide('문자 표현은 검증 F1에서 더 좋은 결과를 보였다','이 그래프는 epoch별 loss가 아니라 학습 표본 수별 F1 곡선입니다. 각 지점에서 특징 추출기와 모델을 다시 학습했습니다. 데이터가 늘 때 검증 F1은 개선됐지만 학습과 검증 사이의 격차는 남아 있습니다.','reports/learning_curves.png ; reports/*_learning_curve.csv')
image(S,'reports/learning_curves.png',64,155,780,455);txt(S,'학습 표본 수별 곡선\n\n각 지점에서 재학습\n\n학습·검증 격차는 남음\n\nepoch loss 곡선과 구분',865,175,340,420,21)
S=slide('짧은 표현과 복합 문맥에서 오류가 남았다','문자 모델의 혼동행렬입니다. 부정 7,325개 중 6,409개, 긍정 7,272개 중 6,289개를 맞혔습니다. 짧은 표현인 뷁은 부정을 긍정으로 오분류했습니다. 감정과 영화 외 상황이 섞인 문장도 한계가 있었습니다.','reports/char_lr_confusion.png ; reports/char_lr_errors.csv')
image(S,'reports/char_lr_confusion.png',64,155,650,450);txt(S,'실제 오분류 사례\n\n“뷁!!”\n정답 부정 → 예측 긍정\n\n짧은 평가와 복합 문맥은\n추가 검수가 필요',755,180,440,410,23)
S=slide('실제 이용자 평점과 모델 감성은 다른 지표다','영화별 분석에서는 원 자료의 이용자 평점과 모델 감성 비율을 나란히 보여줍니다. 예시로 택시운전사와 공조를 비교할 수 있습니다. 수치는 일부 공개 리뷰 이력의 표본이므로 전체 관객 선호로 일반화하지 않습니다.','web/data/catalogue.json ; https://doi.org/10.17632/jb5knzh8yv.6')
rows=[['영화','표본 평점','리뷰 수','긍정','부정','혼합']]
for m in [A,B]:rows.append([m['title'],f"{m['summary']['rating_mean']:.2f}/10",str(m['summary']['review_count'])]+[f"{m['summary']['sentiment_ratios'][l]:.1%}" for l in ['긍정','부정','혼합']])
table(S,rows,y=190,row_h=85,size=20,widths=[290,190,160,170,170,172]);txt(S,'평점: 원 자료의 실제 개별 점수 평균\n감성: 같은 리뷰 원문에 대한 모델 예측\n현재 포털 전체 평점·인증 관객 평균이 아님',y=490,h=150,size=23)
S=slide('불만 유형은 복수 분류와 표본 분모를 반영했다','한 리뷰에는 연기와 스토리 불만이 함께 있을 수 있습니다. 각 범주의 수는 그 범주로 분류된 리뷰 수이며 비율의 분모는 해당 영화의 분석 리뷰 총개수입니다. 합계가 100퍼센트를 넘을 수 있습니다.','web/data/catalogue.json ; src/catalogue.py')
rows=[['불만 유형',A['title'],B['title']]]
for cat in C['categories']:
 row=[cat]
 for m in [A,B]:
  item=next(i for i in m['summary']['complaints'] if i['category']==cat);row.append(f"{item['count']}개 / {item['ratio']:.1%}")
 rows.append(row)
table(S,rows,y=165,row_h=57,size=19,widths=[432,360,360]);txt(S,'각 영화 전체 리뷰가 분모 · 여러 유형 중복 가능 · 표본에 한정된 모델 분류 빈도',y=605,h=45,size=17,color='68747B')
S=slide('혼합 리뷰는 절별 모델 예측을 조합했다','이 문장은 전체 이진 모델로는 부정에 가깝습니다. 하지만 음악 절은 긍정 가능성 63.46퍼센트, 스토리 절은 6.40퍼센트입니다. 서로 반대되는 절이 함께 있어 혼합으로 표시하고 불만은 스토리만 남깁니다. 별도의 3클래스 모델을 학습한 것은 아닙니다.','reports/mixed_review_checks.json')
txt(S,'“음악은 좋은데 스토리는그닥..”',64,150,1152,80,30,True)
table(S,[['분리한 절','예측','긍정 가능성'],['음악은 좋은데','긍정','63.46%'],['스토리는그닥..','부정','6.40%']],y=265,row_h=68,size=22)
txt(S,'전체 표시: 혼합 · 불만: 스토리 및 전개\n전체 이진 긍정 가능성 12.86%는 혼합 확률이 아님\n절 분리 + 기존 이진 모델 조합이며 3클래스 학습은 미실행',y=510,h=130,size=21)
S=slide('높은 불만 점수를 정확도처럼 보여주지 않았다','불만 레이블은 자동 규칙으로 만든 약한 레이블입니다. 따라서 99.9퍼센트 같은 분류 점수를 실제 정확도라고 해석할 수 없습니다. 제한된 문맥·부정어 대조 12건 중 3건은 기대와 달랐습니다. 독립 사람 정답이 없어 불만 F1과 확률 보정은 수행하지 않았습니다.','reports/model_context_audit.json ; reports/aspect_training.json')
txt(S,'약한 레이블로 학습한 불만 모델\n→ 원시 점수를 신뢰 확률로 강조하지 않음\n\n문맥·부정어 대조 12건 중 3건 기대와 다름\n→ 실제 정답셋 성능이 아닌 제한된 점검\n\n독립 사람 정답 부족\n→ 불만 F1·확률 보정은 미실행',y=170,h=450,size=25)
S=slide('사전 계산과 직접 분석에 같은 가중치를 쓴다','영화 목록과 상세 결과는 미리 계산한 JSON을 읽어 시연 지연을 줄입니다. 직접 입력은 같은 TF-IDF와 회귀 가중치를 브라우저에서 계산합니다. 모델 해시와 분석 기준을 검사합니다. 영화별 실제 리뷰 20건을 비교했을 때 Python과 JavaScript의 최대 확률 차이는 약 5.57 곱하기 10의 마이너스 9승이었습니다. 실제 브라우저 및 오프라인 동작 검증은 완료하지 못했습니다.','reports/movie_browser_parity.json ; web/models/analysis_manifest.json')
txt(S,'영화별 결과: 미리 계산한 JSON 조회\n직접 입력: 같은 학습 가중치를 브라우저에서 계산\n\n모델 해시·분석 기준 버전 확인\n20건 Python/JavaScript 비교: 최대 차이 5.57e-9\n\n공개 서비스: GitHub Pages\n원본 앱: Python Streamlit',y=170,h=410,size=25)
S=slide('개발 과정에서 확인한 점','좋았던 점은 동일 분할 비교와 실제 영화 제목 연결 자료를 확보한 것입니다. 아쉬운 점은 사람 정답이 없어 불만 성능을 검증하지 못한 점과 표본 편향입니다. 흥미로웠던 점은 한 리뷰에 칭찬과 불만이 공존한다는 점, 높은 별점과 문장 감성이 다른 점입니다.')
table(S,[['구분','관찰한 점 1','관찰한 점 2'],['Plus','같은 분할로 모델 성능 비교','실제 제목·평점 연결 자료 확보'],['Minus','불만 사람 정답 평가 부족','편의표본의 선택 편향'],['Interesting','칭찬과 불만이 한 리뷰에 공존','이용자 평점과 문장 감성 차이']],y=180,row_h=96,size=20,widths=[180,486,486])
S=slide('남은 한계를 구분하고 개선 순서를 정했다','혼합 리뷰를 이진 결과로만 보여주던 문제는 절별 재예측을 추가해 보완했습니다. 긍정 문장이 불만으로 표시되는 문제는 부정 절 중심 표시로 줄였습니다. 다만 사례 수정은 정답셋 성능 개선의 증명이 아닙니다. 다음 단계는 사람 정답 구축, Transformer 비교, 실제 화면·모바일·오프라인 시연 점검입니다.')
txt(S,'문제: 혼합 리뷰가 전체 부정으로만 표시\n원인: 리뷰 전체에 대한 이진 예측\n시도·결과: 절별 재예측 → 혼합 표시 사례 통과\n\n다음 개선\n데이터: 두 명의 독립 검수와 불만 정답 구축\n모델: Transformer·혼합 정답·확률 보정 비교\n서비스: 실제 화면·모바일·오프라인 동작 검증',y=170,h=450,size=24)
S=slide('시연 순서','발표 시연은 이 순서로 진행하면 됩니다. 영화 목록에서 공조를 선택하고 수록 리뷰 평점, 감성 비율과 불만을 확인합니다. 택시운전사를 비교에 추가해 두 영화를 비교한 다음 직접 리뷰 분석에서 혼합 사례를 입력합니다. 인터넷이 불안정하면 미리 분석된 결과와 이 자료의 실제 표를 사용하면 됩니다.')
txt(S,'영화 목록 → 공조 상세\n평점 출처 → 감성 분포 → 주요 불만\n택시운전사와 두 영화 비교\n직접 분석에 혼합 리뷰 입력\n\nhttps://030217zerogirl-lang.github.io/\nreview-insight-ai-202335217/',y=170,h=420,size=25)
S=slide('예상 질문과 답변','부록은 질의응답 때만 참고합니다. 교수님 안내 PDF에는 PPT나 발표 의무가 명시되어 있지 않아 이 자료는 추가 소개 자료로 준비했습니다.')
txt(S,'왜 Transformer를 쓰지 않았나?\nCPU에서 실제 학습·비교를 우선했고 GPU 코드는 별도 제공했다.\n\n혼합은 진짜 3클래스 모델인가?\n아니다. 절별 이진 예측을 조합한 보조 판정이다.\n\nF1 0.8688이 불만 성능인가?\n아니다. 이진 감성의 긍정 클래스 F1이다.\n\n게임에서도 검증했나?\n영화 모델의 도메인 외 실험이며 게임 전용 검증은 없다.',y=160,h=470,size=20)

# OOXML 파일과 동일한 텍스트 줄바꿈·좌표의 검토용 PDF를 만든다.
preview=OUT/'Review_Insight_발표.pdf';cv=canvas.Canvas(str(preview),pagesize=(960,540))
images={};files={};relations={};layout_findings=[]
GROUP='<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
def paragraph(text,size,color='26373D',bold=False):
 return '<a:p><a:pPr><a:lnSpc><a:spcPct val="120000"/></a:lnSpc></a:pPr><a:r><a:rPr lang="ko-KR" sz="'+str(round(size*100))+'" b="'+('1' if bold else '0')+'"><a:solidFill><a:srgbClr val="'+color+'"/></a:solidFill><a:latin typeface="Malgun Gothic"/><a:ea typeface="맑은 고딕"/></a:rPr><a:t xml:space="preserve">'+e(text)+'</a:t></a:r><a:endParaRPr lang="ko-KR"/></a:p>'
def relxml(entries):return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="'+PKG+'">'+''.join(f'<Relationship Id="{i}" Type="{R}/{kind}" Target="{e(target)}"/>' for i,kind,target in entries)+'</Relationships>'
def textbox(el,idx):
 lines=wrap(el['text'],el['w'],el['size']);height=len(lines)*el['size']*1.2/0.75
 if height>el['h']+5:layout_findings.append({'slide':slide_index,'text':el['text'][:45],'estimated_height':height,'box_height':el['h']})
 xml=f'<p:sp><p:nvSpPr><p:cNvPr id="{idx}" name="Text {idx}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{unit(el["x"])}" y="{unit(el["y"])}"/><a:ext cx="{unit(el["w"])}" cy="{unit(el["h"])}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="0" rIns="0" tIns="0" bIns="0" anchor="t"><a:noAutofit/></a:bodyPr><a:lstStyle/>'+''.join(paragraph(line,el['size'],el['color'],el['bold']) for line in lines)+'</p:txBody></p:sp>'
 cv.setFillColor(HexColor('#'+el['color']));cv.setFont('DeckKR',el['size'])
 for i,line in enumerate(lines):cv.drawString(el['x']*.75,540-el['y']*.75-el['size']-i*el['size']*1.2,line)
 return xml
for slide_index,s in enumerate(slides,1):
 cv.setFillColor(HexColor('#FFFFFF'));cv.rect(0,0,960,540,fill=1,stroke=0)
 elements='';rels=[('rId1','slideLayout','../slideLayouts/slideLayout1.xml'),('rId2','notesSlide',f'../notesSlides/notesSlide{slide_index}.xml')];idx=2
 for el in s['elements']:
  if el['x']+el['w']>W or el['y']+el['h']>H:raise ValueError('Element outside slide')
  if el['kind']=='text':elements+=textbox(el,idx)
  elif el['kind']=='image':
   path=ROOT/el['path'];media=f'image{len(images)+1}.png';images[media]=path;rid=f'rId{len(rels)+1}';rels.append((rid,'image','../media/'+media))
   elements+=f'<p:pic><p:nvPicPr><p:cNvPr id="{idx}" name="Evidence {idx}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x="{unit(el["x"])}" y="{unit(el["y"])}"/><a:ext cx="{unit(el["w"])}" cy="{unit(el["h"])}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'
   cv.drawImage(str(path),el['x']*.75,540-(el['y']+el['h'])*.75,width=el['w']*.75,height=el['h']*.75)
  else:
   widths=el['widths'] or [el['w']/len(el['rows'][0])]*len(el['rows'][0]);grid=''.join(f'<a:gridCol w="{unit(width)}"/>' for width in widths);rowsxml=''
   for rowindex,row in enumerate(el['rows']):
    cells='';cx=el['x'];cy=el['y']+rowindex*el['row_h']
    for col,value in enumerate(row):
     lines=wrap(value,widths[col]-20,el['size']);fill='EEF3F2' if rowindex==0 else 'FFFFFF'
     cells+='<a:tc><a:txBody><a:bodyPr/><a:lstStyle/>'+''.join(paragraph(line,el['size'],'26373D',rowindex==0) for line in lines)+f'</a:txBody><a:tcPr marL="{unit(10)}" marR="{unit(10)}" marT="{unit(8)}" marB="{unit(5)}"><a:solidFill><a:srgbClr val="{fill}"/></a:solidFill></a:tcPr></a:tc>'
     cv.setFillColor(HexColor('#'+fill));cv.rect(cx*.75,540-(cy+el['row_h'])*.75,widths[col]*.75,el['row_h']*.75,fill=1,stroke=0);cv.setFillColor(HexColor('#26373D'));cv.setFont('DeckKR',el['size'])
     for lineindex,line in enumerate(lines):cv.drawString((cx+10)*.75,540-(cy+8)*.75-el['size']-lineindex*el['size']*1.2,line)
     if len(lines)*el['size']*1.2/0.75>el['row_h']-12:layout_findings.append({'slide':slide_index,'table_cell':str(value),'problem':'estimated row overflow'})
     cx+=widths[col]
    rowsxml+=f'<a:tr h="{unit(el["row_h"])}">'+cells+'</a:tr>'
   elements+=f'<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="{idx}" name="Table {idx}"/><p:cNvGraphicFramePr/><p:nvPr/></p:nvGraphicFramePr><p:xfrm><a:off x="{unit(el["x"])}" y="{unit(el["y"])}"/><a:ext cx="{unit(el["w"])}" cy="{unit(el["h"])}"/></p:xfrm><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table"><a:tbl><a:tblPr firstRow="1" bandRow="1"/><a:tblGrid>{grid}</a:tblGrid>{rowsxml}</a:tbl></a:graphicData></a:graphic></p:graphicFrame>'
  idx+=1
 footer={'kind':'text','text':f'Review Insight · 김서윤                                        {slide_index} / {len(slides)}','x':64,'y':675,'w':1152,'h':28,'size':10,'color':'68747B','bold':False};elements+=textbox(footer,idx)
 files[f'ppt/slides/slide{slide_index}.xml']=f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sld xmlns:a="{D}" xmlns:r="{R}" xmlns:p="{P}"><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree>{GROUP}{elements}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
 files[f'ppt/slides/_rels/slide{slide_index}.xml.rels']=relxml(rels)
 note=s['notes']+('\n\n출처: '+s['source'] if s['source'] else '')
 files[f'ppt/notesSlides/notesSlide{slide_index}.xml']=f'<p:notes xmlns:a="{D}" xmlns:r="{R}" xmlns:p="{P}"><p:cSld><p:spTree>{GROUP}<p:sp><p:nvSpPr><p:cNvPr id="2" name="Speaker notes"/><p:cNvSpPr/><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>{paragraph(note,12)}</p:txBody></p:sp></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>'
 files[f'ppt/notesSlides/_rels/notesSlide{slide_index}.xml.rels']=relxml([('rId1','notesMaster','../notesMasters/notesMaster1.xml'),('rId2','slide',f'../slides/slide{slide_index}.xml')])
 cv.showPage()
cv.save()
if layout_findings:
 (ROOT/'reports/presentation_layout_findings.json').write_text(json.dumps(layout_findings,ensure_ascii=False,indent=2),encoding='utf-8');raise ValueError('Layout needs adjustment: '+str(layout_findings[:4]))
colormap='<p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/>'
files['ppt/presentation.xml']=f'<p:presentation xmlns:a="{D}" xmlns:r="{R}" xmlns:p="{P}"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:notesMasterIdLst><p:notesMasterId r:id="rId2"/></p:notesMasterIdLst><p:sldIdLst>'+''.join(f'<p:sldId id="{255+i}" r:id="rId{i+2}"/>' for i in range(1,len(slides)+1))+f'</p:sldIdLst><p:sldSz cx="{unit(W)}" cy="{unit(H)}" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle/></p:presentation>'
files['ppt/_rels/presentation.xml.rels']=relxml([('rId1','slideMaster','slideMasters/slideMaster1.xml'),('rId2','notesMaster','notesMasters/notesMaster1.xml')]+[(f'rId{i+2}','slide',f'slides/slide{i}.xml') for i in range(1,len(slides)+1)])
files['ppt/slideMasters/slideMaster1.xml']=f'<p:sldMaster xmlns:a="{D}" xmlns:r="{R}" xmlns:p="{P}"><p:cSld><p:spTree>{GROUP}</p:spTree></p:cSld>{colormap}<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>'
files['ppt/slideMasters/_rels/slideMaster1.xml.rels']=relxml([('rId1','slideLayout','../slideLayouts/slideLayout1.xml'),('rId2','theme','../theme/theme1.xml')])
files['ppt/slideLayouts/slideLayout1.xml']=f'<p:sldLayout xmlns:a="{D}" xmlns:r="{R}" xmlns:p="{P}" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree>{GROUP}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'
files['ppt/slideLayouts/_rels/slideLayout1.xml.rels']=relxml([('rId1','slideMaster','../slideMasters/slideMaster1.xml')])
files['ppt/notesMasters/notesMaster1.xml']=f'<p:notesMaster xmlns:a="{D}" xmlns:r="{R}" xmlns:p="{P}"><p:cSld><p:spTree>{GROUP}</p:spTree></p:cSld>{colormap}<p:notesStyle/></p:notesMaster>'
files['ppt/notesMasters/_rels/notesMaster1.xml.rels']=relxml([('rId1','theme','../theme/theme1.xml')])
colors=['203B43','FFFFFF','26373D','F5F7F7','23685B','B7746C','9486A9','5D8874','879E97','68747B','23685B','7B688E'];keys=['dk1','lt1','dk2','lt2','accent1','accent2','accent3','accent4','accent5','accent6','hlink','folHlink']
files['ppt/theme/theme1.xml']=f'<a:theme xmlns:a="{D}" name="Review Insight"><a:themeElements><a:clrScheme name="Review Insight">'+''.join(f'<a:{k}><a:srgbClr val="{v}"/></a:{k}>' for k,v in zip(keys,colors))+'</a:clrScheme><a:fontScheme name="Korean"><a:majorFont><a:latin typeface="Malgun Gothic"/><a:ea typeface="맑은 고딕"/><a:cs typeface="Arial"/></a:majorFont><a:minorFont><a:latin typeface="Malgun Gothic"/><a:ea typeface="맑은 고딕"/><a:cs typeface="Arial"/></a:minorFont></a:fontScheme><a:fmtScheme name="Simple"><a:fillStyleLst>'+('<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'*3)+'</a:fillStyleLst><a:lnStyleLst>'+('<a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln>'*3)+'</a:lnStyleLst><a:effectStyleLst>'+('<a:effectStyle><a:effectLst/></a:effectStyle>'*3)+'</a:effectStyleLst><a:bgFillStyleLst>'+('<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'*3)+'</a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>'
files['_rels/.rels']=f'<Relationships xmlns="{PKG}"><Relationship Id="rId1" Type="{R}/officeDocument" Target="ppt/presentation.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="{R}/extended-properties" Target="docProps/app.xml"/></Relationships>'
files['docProps/core.xml']='<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Review Insight 프로젝트 소개</dc:title><dc:creator>김서윤</dc:creator><dc:description>직접 학습한 한국어 리뷰 모델과 실제 영화별 분석 결과</dc:description></cp:coreProperties>'
files['docProps/app.xml']=f'<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Review Insight</Application><PresentationFormat>On-screen Show (16:9)</PresentationFormat><Slides>{len(slides)}</Slides><Notes>{len(slides)}</Notes></Properties>'
overrides=[('/ppt/presentation.xml','presentationml.presentation.main'),('/ppt/slideMasters/slideMaster1.xml','presentationml.slideMaster'),('/ppt/slideLayouts/slideLayout1.xml','presentationml.slideLayout'),('/ppt/notesMasters/notesMaster1.xml','presentationml.notesMaster'),('/ppt/theme/theme1.xml','theme')]+[(f'/ppt/slides/slide{i}.xml','presentationml.slide') for i in range(1,len(slides)+1)]+[(f'/ppt/notesSlides/notesSlide{i}.xml','presentationml.notesSlide') for i in range(1,len(slides)+1)]
files['[Content_Types].xml']='<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/>'+''.join(f'<Override PartName="{p}" ContentType="application/vnd.openxmlformats-officedocument.{typ}+xml"/>' for p,typ in overrides)+'<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>'
target=OUT/'Review_Insight_프로젝트소개.pptx'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for name,text in files.items():ET.fromstring(text);z.writestr(name,text.encode('utf-8'))
 for name,path in images.items():z.write(path,'ppt/media/'+name)
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None;names=set(z.namelist())
 for name in names:
  if not name.endswith('.rels'):continue
  base='' if name=='_rels/.rels' else posixpath.dirname(posixpath.dirname(name))
  for rel in ET.fromstring(z.read(name)):
   if rel.attrib.get('TargetMode')=='External':continue
   dest=posixpath.normpath(posixpath.join(base,rel.attrib['Target']))
   assert dest in names,(name,dest)
script='# Review Insight 소개 대본\n\n본문 17장, 질의응답 부록 1장. 본문은 약 8~10분을 기준으로 조절한다. 교수님 안내 PDF에 PPT·발표 의무는 명시되어 있지 않아 추가 소개 자료로 준비했다.\n\n'
for i,s in enumerate(slides,1):script+=f"## {i}. {s['title'] or 'Review Insight'}\n\n{s['notes']}\n\n"+(f"출처: {s['source']}\n\n" if s['source'] else '')
(OUT/'발표대본.md').write_text(script,encoding='utf-8')
(ROOT/'reports/presentation_validation.json').write_text(json.dumps({'slides':len(slides),'pptx':str(target.relative_to(ROOT)),'zip_integrity':True,'all_xml_parsed':True,'all_relationships_resolve':True,'editable_tables':True,'notes_present':len(slides),'geometry_overflow_findings':0,'preview_pdf':'presentation/Review_Insight_발표.pdf','render_method':'PDF composed from identical text coordinates, not PowerPoint rendering','opened_in_powerpoint':False,'limitations':'Dedicated presentation runtime unavailable; native OOXML fallback. Actual PowerPoint app rendering not verified.'},ensure_ascii=False,indent=2),encoding='utf-8')
import fitz
pdf=fitz.open(preview);folder=ROOT/'reports/slides_preview';folder.mkdir(exist_ok=True)
for i,page in enumerate(pdf):page.get_pixmap(matrix=fitz.Matrix(1,1)).save(folder/f'slide_{i+1:02}.png')
print('Created',target,'slides=',len(slides))

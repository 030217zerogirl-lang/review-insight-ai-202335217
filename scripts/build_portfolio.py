"""README 내용을 포트폴리오 PDF로 변환한다."""
from pathlib import Path
import re,html
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle,KeepTogether,PageBreak
from reportlab.lib import colors
from PIL import Image as PILImage

def build(root,output):
 root=Path(root);output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 font=next((p for p in [Path('C:/Windows/Fonts/malgun.ttf'),Path('/usr/share/fonts/truetype/nanum/NanumGothic.ttf')] if p.exists()),None)
 if font is None:raise FileNotFoundError('한글 글꼴 malgun.ttf 또는 NanumGothic.ttf가 필요합니다.')
 pdfmetrics.registerFont(TTFont('BodyKR',str(font)))
 body=ParagraphStyle('body',fontName='BodyKR',fontSize=9.5,leading=15,wordWrap='CJK',spaceAfter=6,allowWidows=0,allowOrphans=0)
 small=ParagraphStyle('small',parent=body,fontSize=8,leading=12)
 heading=ParagraphStyle('heading',parent=body,fontSize=14,leading=21,spaceBefore=15,spaceAfter=9,keepWithNext=True,textColor=colors.HexColor('#254d7c'))
 title=ParagraphStyle('title',parent=heading,fontSize=22,leading=30)
 story=[];lines=(root/'README.md').read_text(encoding='utf-8').splitlines();i=0;in_code=False
 def para(s,style=body):return Paragraph(html.escape(s).replace('**','').replace('`',''),style)
 while i<len(lines):
  line=lines[i];i+=1
  if line.startswith('```'):in_code=not in_code;continue
  if not line.strip():continue
  if line.startswith('|'):
   rows=[line]
   while i<len(lines) and lines[i].startswith('|'):rows.append(lines[i]);i+=1
   data=[[para(c.strip(),small) for c in row.strip('|').split('|')] for row in rows if not re.fullmatch(r'[| :\-]+',row)]
   width=505/len(data[0]);table=Table(data,colWidths=[width]*len(data[0]),repeatRows=1,hAlign='LEFT')
   table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eaf0f8')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#d5deeb')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story.extend([table,Spacer(1,10)]);continue
  image=re.match(r'!\[(.*?)\]\((.*?)\)',line)
  if image:
   path=root/image[2]
   if not path.exists():raise FileNotFoundError(path)
   with PILImage.open(path) as im:w,h=im.size
   scale=min(475/w,(560 if 'screenshots' in str(path) else 300)/h)
   story.append(KeepTogether([Image(str(path),width=w*scale,height=h*scale),para(image[1],small),Spacer(1,9)]));continue
  if line.startswith('## 9.'):story.append(PageBreak())
  style=title if line.startswith('# ') else heading if line.startswith('## ') else body
  story.append(para(line.lstrip('# '),style))
 def footer(c,d):c.setFont('BodyKR',8);c.setFillColor(colors.gray);c.drawString(45,25,'Review Insight AI | 202335217 김서윤');c.drawRightString(550,25,str(d.page))
 SimpleDocTemplate(str(output),pagesize=(595.28,841.89),leftMargin=45,rightMargin=45,topMargin=38,bottomMargin=42).build(story,onFirstPage=footer,onLaterPages=footer)
 return output
if __name__=='__main__':
 root=Path(__file__).resolve().parents[1];print(build(root,root/'portfolio.pdf'))

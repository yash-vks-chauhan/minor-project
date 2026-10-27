"""Render local review packages; no network submission occurs."""
from pathlib import Path
import html
import json
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether

REV = Path(__file__).resolve().parents[1]
FONTDIR = Path('/System/Library/Fonts/Supplemental')
for family, filename in [('TNR','Times New Roman.ttf'),('TNR-Bold','Times New Roman Bold.ttf'),('TNR-Italic','Times New Roman Italic.ttf')]:
    pdfmetrics.registerFont(TTFont(family, str(FONTDIR / filename)))
pdfmetrics.registerFontFamily('TNR', normal='TNR', bold='TNR-Bold', italic='TNR-Italic', boldItalic='TNR-Bold')
meta=json.loads((REV/'submissions/author_metadata.json').read_text())
AUTHORS=meta.get('authors_in_submission_order',meta['authors_in_existing_order'])


def markup(text):
    text=html.escape(text)
    return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>',text)


def footer(canvas, doc):
    canvas.saveState();canvas.setFont('TNR',9);canvas.setFillColor(colors.HexColor('#555555'))
    canvas.drawCentredString(A4[0]/2,24,str(doc.page));canvas.restoreState()


def render(source):
    tip='03-tip' in str(source)
    blind='02-weave' in str(source)
    raw=source.read_text(); blocks=raw.strip().split('\n\n')
    title=blocks.pop(0).removeprefix('# ').strip()
    body='\n\n'.join(blocks)
    # Readable word counts include section labels; title and references excluded.
    count=len(re.findall(r'\S+',re.sub(r'[#*]','',body.split('## References')[0])))
    bounds=(800,1500) if blind else (0,700) if tip else (200,300) if '01-ioce' in str(source) else (0,250)
    assert bounds[0] <= count <= bounds[1],(source,count,bounds)
    title_style=ParagraphStyle('title',fontName='TNR-Bold',fontSize=13,leading=16,alignment=TA_CENTER,spaceAfter=14)
    body_style=ParagraphStyle('body',fontName='TNR',fontSize=12 if tip else 11,leading=18 if tip else 14 if blind else 15,
                              alignment=TA_JUSTIFY,spaceBefore=5 if blind else 6,spaceAfter=0,splitLongWords=True)
    heading_style=ParagraphStyle('heading',parent=body_style,fontName='TNR-Bold',keepWithNext=True)
    ref_style=ParagraphStyle('ref',parent=body_style,fontSize=10 if not tip else 12,leading=14 if not tip else 18)
    story=[Paragraph(markup(title),title_style)]
    if tip:
        for author in AUTHORS:
            story.append(Paragraph(markup(author['name']),ParagraphStyle('author',fontName='TNR-Bold',fontSize=11,leading=14)))
            story.append(Paragraph(markup(author['email']),ParagraphStyle('email',fontName='TNR',fontSize=10,leading=12)))
            story.append(Paragraph(markup(meta['affiliation']),ParagraphStyle('aff',fontName='TNR',fontSize=10,leading=12,spaceAfter=6)))
        story.append(Paragraph('EXTENDED ABSTRACT',heading_style))
    in_refs=False
    for block in blocks:
        if block.startswith('## '):
            in_refs=block.startswith('## References')
            story.append(Paragraph(markup(block[3:]),heading_style))
        else:
            story.append(Paragraph(markup(block.replace('\n',' ')),ref_style if in_refs else body_style))
    output=source.with_suffix('.pdf')
    doc=SimpleDocTemplate(str(output),pagesize=A4,rightMargin=54,leftMargin=54,topMargin=48,bottomMargin=43,
                          title=title,author='' if blind else '; '.join(a['name'] for a in AUTHORS),
                          subject='Conference submission draft',creator='Research manuscript preparation')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    text=re.sub(r'(?m)^##?\s+','',raw)
    text=text.replace('**','')
    source.with_suffix('.txt').write_text(text+'\n')
    if not blind and not tip:
        # Online forms provide separate title and abstract fields.
        body_text=re.sub(r'(?m)^##?\s+','',body).replace('**','')
        source.with_name('abstract_body.txt').write_text(body_text+'\n')
    return dict(file=str(output.relative_to(REV)),body_words=count,limits=bounds,blind=blind)


records=[]
for relative in ['01-ioce2027/abstract.md','02-weave2027/extended_abstract_blind.md','03-tip2027/extended_abstract.md','04-urban-eplanning2027/abstract.md']:
    records.append(render(REV/'submissions'/relative))
(REV/'results/submission_format_checks.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records,indent=2))

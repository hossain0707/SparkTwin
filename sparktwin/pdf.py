"""Readable, explicitly non-certifying PDF evidence for analytical scenarios."""
from __future__ import annotations
from datetime import datetime, timezone
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepTogether
from reportlab.pdfbase.pdfmetrics import stringWidth
from xml.sax.saxutils import escape

INK=colors.HexColor('#14283d');ACCENT=colors.HexColor('#127f72');LIGHT=colors.HexColor('#eef4f7')


def report_pdf(assessment: dict, calibration: dict) -> bytes:
    buf=BytesIO()
    pdf=SimpleDocTemplate(buf,pagesize=A4,topMargin=18*mm,bottomMargin=17*mm,leftMargin=19*mm,rightMargin=19*mm,
                          title='SparkTwin Capacity Assessment — Engineering Estimate',author='SparkTwin / Md Najmul Hossain')
    title=ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=19,leading=24,textColor=INK,spaceAfter=9)
    h=ParagraphStyle('heading',fontName='Helvetica-Bold',fontSize=11.5,leading=15,textColor=INK,spaceBefore=15,spaceAfter=8)
    p=ParagraphStyle('body',fontName='Helvetica',fontSize=9.1,leading=14,textColor=INK,spaceAfter=9)
    subtle=ParagraphStyle('small',parent=p,fontSize=8,leading=12,textColor=colors.HexColor('#5d7180'))
    badge=ParagraphStyle('badge',parent=p,fontName='Helvetica-Bold',fontSize=9,textColor=ACCENT)
    f=lambda n: f'{n:,.2f}'
    story=[Paragraph('SparkTwin  /  Capacity Assessment',title),
           Paragraph('ENGINEERING ESTIMATE  •  NOT A CERTIFICATION  •  NOT A MEASURED GPU RUN',badge),
           Paragraph('Created '+datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')+'  |  Version 0.1.0',subtle),Spacer(1,7)]
    s=assessment['scenario']
    story.append(Paragraph(escape(s['name']),h))
    summary=[['Target system',assessment['profile_name']],['Model parameters',f(s['params_b'])+' billion'],
             ['Precision',str(s['weight_bits'])+' bits / weight'],['Context / concurrency',f'{s["context_tokens"]:,} tokens / {s["concurrency"]} sequences'],
             ['Estimated status',assessment['status'].replace('-',' ').title()],
             ['Estimated consumption',f(assessment['total_gib'])+' GiB'],
             ['Unified physical capacity',f(assessment['physical_gib'])+' GiB'],
             ['Estimated headroom',f(assessment['headroom_gib'])+' GiB']]
    tab=Table([[Paragraph(escape(a),p),Paragraph(escape(str(b)),p)] for a,b in summary],colWidths=[67*mm,100*mm],hAlign='LEFT')
    tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT),('ROWBACKGROUNDS',(0,0),(-1,-1),[LIGHT,colors.white]),
                             ('LINEBELOW',(0,0),(-1,-1),.3,colors.HexColor('#ccdade')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                             ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),2)]))
    story.extend([tab,Paragraph('Memory components',h)])
    comps=[('Model weights',assessment['weights_gib']),('KV attention cache',assessment['kv_gib']),
           ('OS + runtime + activation reserve',assessment['reserve_gib']),('Safety margin',assessment['safety_gib'])]
    story.append(Paragraph('  ·  '.join(escape(name)+': <b>'+f(val)+' GiB</b>' for name,val in comps),p))
    story.append(Paragraph('Benchmark calibration',h))
    if calibration['estimate'] is None:
        story.append(Paragraph('No calibrated throughput estimate is available. '+escape(calibration['reason']),p))
    else:
        story.append(Paragraph('Neighbor-based throughput estimate: <b>'+f(calibration['estimate'])+' tokens/s</b>, '+escape(calibration['confidence'])+ ' confidence using '+str(calibration['matches'])+' comparable imported records. Not a measured result for this target scenario.',p))
        story.append(Paragraph('Source labels: '+escape(', '.join(calibration.get('sources',[]))),subtle))
    story.append(Paragraph('Assumptions and limitations',h))
    for item in assessment['assumptions']:
        story.append(Paragraph('• '+escape(item),subtle))
    story.append(Paragraph('This capacity estimate cannot prove that the model will load, serve a given concurrency, achieve a throughput target, satisfy privacy requirements, or pass a security audit. Real deployment benchmarks and hardware validation remain necessary.',p))
    story.append(Paragraph('Independent, unofficial software by Md Najmul Hossain. Not affiliated with or endorsed by NVIDIA.',subtle))
    pdf.build(story)
    return buf.getvalue()

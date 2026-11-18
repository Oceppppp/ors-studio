from __future__ import annotations
import io
import json
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted
from reportlab.lib.units import mm


def flatten(data, prefix=""):
    rows=[]
    if isinstance(data,dict):
        for key,value in data.items():
            name=f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value,(dict,list)):
                rows.extend(flatten(value,name))
            else: rows.append({"Field":name,"Value":value})
    elif isinstance(data,list):
        for i,value in enumerate(data): rows.extend(flatten(value,f"{prefix}[{i}]"))
    else: rows.append({"Field":prefix,"Value":data})
    return rows


def build_excel(analysis):
    import pandas as pd
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine="xlsxwriter",engine_kwargs={"options":{"strings_to_formulas":False,"strings_to_urls":False}}) as writer:
        pd.DataFrame(flatten(analysis.get("input",{}))).to_excel(writer,sheet_name="Input",index=False)
        pd.DataFrame(flatten(analysis.get("output",{}))).to_excel(writer,sheet_name="Results",index=False)
        meta=[{"Field":k,"Value":v} for k,v in analysis.items() if k not in {"input","output"}]
        pd.DataFrame(meta).to_excel(writer,sheet_name="Analysis Info",index=False)
        for sheet in writer.sheets.values():
            sheet.set_column(0,0,34);sheet.set_column(1,1,72);sheet.freeze_panes(1,0)
    buf.seek(0);return buf.getvalue()


def _spreadsheet_safe(value):
    # Prefix untrusted text that spreadsheet programs might interpret as a formula.
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + value
    return value


def build_csv(analysis):
    import pandas as pd
    rows=flatten(analysis.get("output",{}))
    safe_rows=[{key:_spreadsheet_safe(value) for key,value in row.items()} for row in rows]
    df=pd.DataFrame(safe_rows)
    return df.to_csv(index=False).encode("utf-8-sig")


def build_pdf(analysis):
    buf=io.BytesIO();doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=18*mm,bottomMargin=18*mm)
    styles=getSampleStyleSheet();story=[]
    title=escape(str(analysis.get('title','Analysis')))
    module=escape(str(analysis.get('module_key','')))
    status=escape(str(analysis.get('status','')))
    created=escape(str(analysis.get('created_at','')))
    story.extend([Paragraph(f"ORS Analysis Report — {title}",styles['Title']),Spacer(1,8),Paragraph(f"Module: {module} | Status: {status}",styles['Normal']),Paragraph(f"Created: {created}",styles['Normal']),Spacer(1,12)])
    story.append(Paragraph("Results",styles['Heading2']))
    for item in flatten(analysis.get("output",{})):
        value=json.dumps(item["Value"],ensure_ascii=False) if isinstance(item["Value"],(dict,list)) else str(item["Value"])
        story.append(Paragraph(f"<b>{escape(str(item['Field']))}</b>: {escape(value[:1200])}",styles['BodyText']))
    story.extend([Spacer(1,10),Paragraph("Input parameters",styles['Heading2'])])
    inp=json.dumps(analysis.get("input",{}),ensure_ascii=False,indent=2)
    story.append(Preformatted(escape(inp[:12000]),styles['Code']))
    doc.build(story);buf.seek(0);return buf.getvalue()

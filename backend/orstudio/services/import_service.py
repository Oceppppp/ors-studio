from __future__ import annotations
import csv
import io
import math
import zipfile
from datetime import date, datetime
from pathlib import Path
import pandas as pd

MAX_UPLOAD_BYTES=20*1024*1024
MAX_EXPANDED_XLSX_BYTES=100*1024*1024
MAX_XLSX_MEMBERS=20_000
MAX_DATA_CELLS=1_000_000
ALLOWED={".csv",".xlsx"}


def _validate_xlsx_archive(content: bytes) -> None:
    stream=io.BytesIO(content)
    if not zipfile.is_zipfile(stream):
        raise ValueError("The .xlsx file is not a valid Excel workbook")
    stream.seek(0)
    with zipfile.ZipFile(stream) as archive:
        members=archive.infolist()
        if len(members)>MAX_XLSX_MEMBERS:
            raise ValueError("Workbook contains too many internal files")
        expanded=sum(member.file_size for member in members)
        if expanded>MAX_EXPANDED_XLSX_BYTES:
            raise ValueError("Workbook expands beyond the 100 MB safety limit")


def inspect_tabular_file(filename: str, content: bytes) -> dict:
    """Inspect supported input without persisting or fully materializing rows."""
    ext=Path(filename).suffix.lower()
    if ext not in ALLOWED:
        raise ValueError("Only .csv and .xlsx files are supported")
    if not content:
        raise ValueError("Uploaded file is empty")
    if len(content)>MAX_UPLOAD_BYTES:
        raise ValueError("File exceeds the 20 MB upload limit")
    if ext==".csv":
        try:
            content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("CSV must be UTF-8 encoded; save it as CSV UTF-8 and retry") from exc
        return {"filename":filename,"sheets":[]}
    _validate_xlsx_archive(content)
    try:
        workbook=pd.ExcelFile(io.BytesIO(content),engine="openpyxl")
        return {"filename":filename,"sheets":workbook.sheet_names}
    except Exception as exc:
        raise ValueError(f"Could not inspect XLSX workbook: {exc}") from exc


def _json_value(value):
    if value is None: return None
    if isinstance(value,(datetime,date)): return value.isoformat()
    if isinstance(value,float) and (math.isnan(value) or math.isinf(value)): return None
    if pd.isna(value): return None
    if hasattr(value,"item"): value=value.item()
    if isinstance(value,(str,int,float,bool)): return value
    return str(value)


def read_tabular_file(filename: str, content: bytes, sheet_name: str | None = None):
    ext=Path(filename).suffix.lower()
    if ext not in ALLOWED: raise ValueError("Only .csv and .xlsx files are supported")
    if len(content)>MAX_UPLOAD_BYTES: raise ValueError("File exceeds the 20 MB upload limit")
    if not content: raise ValueError("Uploaded file is empty")
    if ext==".csv":
        try:
            text=content.decode("utf-8-sig")
        except UnicodeDecodeError as exc: raise ValueError("CSV must be UTF-8 encoded; save it as CSV UTF-8 and retry") from exc
        try:
            dialect=csv.Sniffer().sniff(text[:4096],delimiters=",;\t|")
        except csv.Error:
            dialect=csv.excel
        df=pd.read_csv(io.StringIO(text),sep=dialect.delimiter)
        selected_sheet=None
    else:
        try:
            _validate_xlsx_archive(content)
            book=pd.ExcelFile(io.BytesIO(content),engine="openpyxl")
            sheets=book.sheet_names
            selected_sheet=sheet_name or sheets[0]
            if selected_sheet not in sheets: raise ValueError(f"Sheet '{selected_sheet}' not found. Available: {', '.join(sheets)}")
            df=pd.read_excel(book,sheet_name=selected_sheet)
        except ValueError: raise
        except Exception as exc: raise ValueError(f"Could not read XLSX workbook: {exc}") from exc
    if df.empty and len(df.columns)==0: raise ValueError("No tabular columns were found")
    if len(df)>100_000: raise ValueError("Dataset exceeds 100,000 rows; split it into smaller files")
    if len(df.columns)>250: raise ValueError("Dataset exceeds 250 columns")
    if len(df)*len(df.columns)>MAX_DATA_CELLS:
        raise ValueError("Dataset exceeds 1,000,000 cells; split it into smaller files")
    columns=[];seen={}
    for i,col in enumerate(df.columns):
        name=str(col).strip() or f"column_{i+1}"
        key=name;count=2
        while key in seen:
            key=f"{name}_{count}";count+=1
        seen[key]=True;columns.append(key)
    df.columns=columns
    rows=[{col:_json_value(row[col]) for col in columns} for _,row in df.iterrows()]
    return {"columns":columns,"rows":rows,"row_count":len(rows),"sheet_name":selected_sheet,"sheets":sheets if ext==".xlsx" else None,"preview":rows[:20],"warnings":_profile(df)}


def _profile(df):
    warnings=[]
    for col in df.columns:
        missing=int(df[col].isna().sum())
        if missing:warnings.append({"column":str(col),"type":"missing_values","count":missing})
        if df[col].nunique(dropna=True) <= 1 and len(df)>1:warnings.append({"column":str(col),"type":"constant_column","count":len(df)})
    return warnings

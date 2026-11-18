import pytest
from orstudio.services.import_service import read_tabular_file, inspect_tabular_file


def test_csv_import_detects_columns_and_nulls():
    result = read_tabular_file("demand.csv", b"Period,Demand\nJan,10\nFeb,\n")
    assert result["columns"] == ["Period", "Demand"]
    assert result["row_count"] == 2
    assert result["rows"][1]["Demand"] is None


def test_unsupported_extension_is_rejected():
    with pytest.raises(ValueError, match="Only .csv and .xlsx"):
        read_tabular_file("data.xls", b"abc")


def test_xlsx_multi_sheet_import_reads_selected_sheet():
    from io import BytesIO
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = 'Demand'
    ws.append(['Period', 'Demand'])
    ws.append(['Jan', 10])
    other = wb.create_sheet('Other')
    other.append(['Code', 'Value'])
    other.append(['A', 7])
    buf = BytesIO(); wb.save(buf)
    result = read_tabular_file('sample.xlsx', buf.getvalue(), 'Demand')
    assert result['sheet_name'] == 'Demand'
    assert result['columns'] == ['Period', 'Demand']
    assert result['rows'][0]['Demand'] == 10


def test_xlsx_extension_with_non_workbook_content_is_rejected():
    with pytest.raises(ValueError, match="valid Excel workbook"):
        read_tabular_file("fake.xlsx", b"not a zip archive")


def test_csv_export_neutralizes_formula_like_text():
    from orstudio.services.export_service import build_csv
    content=build_csv({"output":{"label":"=HYPERLINK(\"https://example.com\")","value":-12}}).decode("utf-8-sig")
    assert "'=HYPERLINK" in content
    # Numeric outputs remain numeric; only untrusted string content is prefixed.
    assert ",-12" in content


def test_inspect_csv_enforces_upload_limit_and_utf8(monkeypatch):
    import orstudio.services.import_service as service
    monkeypatch.setattr(service,"MAX_UPLOAD_BYTES",4)
    with pytest.raises(ValueError,match="20 MB upload limit"):
        inspect_tabular_file("large.csv",b"12345")
    with pytest.raises(ValueError,match="UTF-8"):
        inspect_tabular_file("bad.csv",b"\xff\xfe")

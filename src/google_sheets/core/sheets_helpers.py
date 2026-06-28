"""Shared helpers for Google Sheets tool handlers."""

from typing import Any, Dict, List

from .exceptions import SheetNotFoundError


def resolve_sheet_id(
    sheets_service: Any, spreadsheet_id: str, sheet_name: str
) -> int:
    """Resolve a sheet (tab) name to its numeric sheetId.

    Багато операцій `spreadsheets.batchUpdate` (видалення вкладки, вставка/
    видалення вимірів, форматування) працюють із числовим `sheetId`, а не з
    назвою. Цей хелпер один раз читає метадані таблиці й знаходить потрібний id.
    """
    metadata = (
        sheets_service.spreadsheets()
        .get(spreadsheetId=spreadsheet_id, fields="sheets.properties")
        .execute()
    )

    for sheet in metadata.get("sheets", []):
        props = sheet.get("properties", {})
        if props.get("title") == sheet_name:
            return props["sheetId"]

    available = [
        s.get("properties", {}).get("title")
        for s in metadata.get("sheets", [])
    ]
    raise SheetNotFoundError(
        f"Sheet '{sheet_name}' not found. Available sheets: {available}"
    )


def column_index_to_letter(index: int) -> str:
    """Convert a 0-based column index to its A1 letter (0 -> A, 26 -> AA)."""
    letters = ""
    index += 1  # A1 letters are 1-based
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def list_sheet_properties(
    sheets_service: Any, spreadsheet_id: str
) -> List[Dict[str, Any]]:
    """Return normalized properties for every sheet (tab) in a spreadsheet."""
    metadata = (
        sheets_service.spreadsheets()
        .get(spreadsheetId=spreadsheet_id, fields="sheets.properties")
        .execute()
    )

    sheets: List[Dict[str, Any]] = []
    for sheet in metadata.get("sheets", []):
        props = sheet.get("properties", {})
        grid = props.get("gridProperties", {})
        sheets.append(
            {
                "sheet_id": props.get("sheetId"),
                "title": props.get("title"),
                "index": props.get("index"),
                "sheet_type": props.get("sheetType", "GRID"),
                "row_count": grid.get("rowCount"),
                "column_count": grid.get("columnCount"),
                "hidden": props.get("hidden", False),
            }
        )
    return sheets

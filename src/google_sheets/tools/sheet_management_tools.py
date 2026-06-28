"""Sheet (tab) management tools: create/delete/rename/duplicate/copy sheets,
insert/delete dimensions, and basic cell formatting.

Усі операції тут працюють через Google Sheets API (`spreadsheets` scope), тож
не вимагають розширення дозволів і зберігають принцип найменших привілеїв.
"""

import json
import logging
from typing import Any, Dict, List, NoReturn

from googleapiclient.errors import HttpError
from mcp.types import TextContent, Tool

from ..auth.oauth_manager import GoogleSheetsAuth
from ..core.exceptions import InvalidRangeError, SheetsAPIError
from ..core.sheets_helpers import list_sheet_properties, resolve_sheet_id
from ..core.tool_handler import SheetsToolHandler

logger = logging.getLogger(__name__)


def _handle_http_error(e: HttpError) -> NoReturn:
    """Translate a Google API HttpError into our typed exceptions."""
    if e.resp.status == 400:
        raise InvalidRangeError(f"Invalid request: {e.reason}")
    if e.resp.status == 404:
        raise SheetsAPIError("Spreadsheet or sheet not found", 404)
    raise SheetsAPIError(f"Sheets API error: {e.reason}", e.resp.status)


class ListSheetsHandler(SheetsToolHandler):
    """List all sheets (tabs) inside a spreadsheet."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="list_sheets",
            description="List all sheets (tabs) inside a Google Spreadsheet",
        )
        self.auth = auth

    def get_tool_definition(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "The ID of the spreadsheet",
                    }
                },
                "required": ["spreadsheet_id"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(arguments, ["spreadsheet_id"])
            spreadsheet_id = arguments["spreadsheet_id"]
            sheets_service = self.auth.get_sheets_service()

            sheets = list_sheet_properties(sheets_service, spreadsheet_id)

            return self.format_success_response(
                json.dumps({"total": len(sheets), "sheets": sheets}, indent=2),
                f"Found {len(sheets)} sheet(s)",
            )
        except HttpError as e:
            _handle_http_error(e)
        except Exception as e:
            return self.format_error_response(e)


class CreateSheetHandler(SheetsToolHandler):
    """Create a new sheet (tab) inside a spreadsheet."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="create_sheet",
            description="Create a new sheet (tab) inside a Google Spreadsheet",
        )
        self.auth = auth

    def get_tool_definition(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "The ID of the spreadsheet",
                    },
                    "title": {
                        "type": "string",
                        "description": "Title of the new sheet (tab)",
                    },
                    "index": {
                        "type": "integer",
                        "description": "Optional 0-based position for the new sheet",
                    },
                    "row_count": {
                        "type": "integer",
                        "description": "Optional number of rows (default 1000)",
                    },
                    "column_count": {
                        "type": "integer",
                        "description": "Optional number of columns (default 26)",
                    },
                },
                "required": ["spreadsheet_id", "title"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(arguments, ["spreadsheet_id", "title"])
            spreadsheet_id = arguments["spreadsheet_id"]

            properties: Dict[str, Any] = {"title": arguments["title"]}
            if "index" in arguments:
                properties["index"] = arguments["index"]
            grid: Dict[str, Any] = {}
            if "row_count" in arguments:
                grid["rowCount"] = arguments["row_count"]
            if "column_count" in arguments:
                grid["columnCount"] = arguments["column_count"]
            if grid:
                properties["gridProperties"] = grid

            sheets_service = self.auth.get_sheets_service()
            result = (
                sheets_service.spreadsheets()
                .batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={"requests": [{"addSheet": {"properties": properties}}]},
                )
                .execute()
            )

            new_props = (
                result.get("replies", [{}])[0]
                .get("addSheet", {})
                .get("properties", {})
            )

            return self.format_success_response(
                json.dumps(
                    {
                        "sheet_id": new_props.get("sheetId"),
                        "title": new_props.get("title"),
                        "index": new_props.get("index"),
                    },
                    indent=2,
                ),
                f"Created sheet '{arguments['title']}'",
            )
        except HttpError as e:
            _handle_http_error(e)
        except Exception as e:
            return self.format_error_response(e)


class DeleteSheetHandler(SheetsToolHandler):
    """Delete a sheet (tab) from a spreadsheet."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="delete_sheet",
            description="Delete a sheet (tab) from a Google Spreadsheet",
        )
        self.auth = auth

    def get_tool_definition(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "The ID of the spreadsheet",
                    },
                    "sheet_name": {
                        "type": "string",
                        "description": "Name of the sheet (tab) to delete",
                    },
                },
                "required": ["spreadsheet_id", "sheet_name"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(arguments, ["spreadsheet_id", "sheet_name"])
            spreadsheet_id = arguments["spreadsheet_id"]
            sheet_name = arguments["sheet_name"]
            sheets_service = self.auth.get_sheets_service()

            sheet_id = resolve_sheet_id(sheets_service, spreadsheet_id, sheet_name)

            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": [{"deleteSheet": {"sheetId": sheet_id}}]},
            ).execute()

            return self.format_success_response(
                json.dumps({"deleted_sheet": sheet_name, "sheet_id": sheet_id}),
                f"Deleted sheet '{sheet_name}'",
            )
        except HttpError as e:
            _handle_http_error(e)
        except Exception as e:
            return self.format_error_response(e)


class RenameSheetHandler(SheetsToolHandler):
    """Rename a sheet (tab) within a spreadsheet."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="rename_sheet",
            description="Rename a sheet (tab) within a Google Spreadsheet",
        )
        self.auth = auth

    def get_tool_definition(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "The ID of the spreadsheet",
                    },
                    "sheet_name": {
                        "type": "string",
                        "description": "Current name of the sheet (tab)",
                    },
                    "new_name": {
                        "type": "string",
                        "description": "New name for the sheet (tab)",
                    },
                },
                "required": ["spreadsheet_id", "sheet_name", "new_name"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(
                arguments, ["spreadsheet_id", "sheet_name", "new_name"]
            )
            spreadsheet_id = arguments["spreadsheet_id"]
            sheet_name = arguments["sheet_name"]
            new_name = arguments["new_name"]
            sheets_service = self.auth.get_sheets_service()

            sheet_id = resolve_sheet_id(sheets_service, spreadsheet_id, sheet_name)

            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={
                    "requests": [
                        {
                            "updateSheetProperties": {
                                "properties": {
                                    "sheetId": sheet_id,
                                    "title": new_name,
                                },
                                "fields": "title",
                            }
                        }
                    ]
                },
            ).execute()

            return self.format_success_response(
                json.dumps({"old_name": sheet_name, "new_name": new_name}),
                f"Renamed sheet '{sheet_name}' to '{new_name}'",
            )
        except HttpError as e:
            _handle_http_error(e)
        except Exception as e:
            return self.format_error_response(e)


class DuplicateSheetHandler(SheetsToolHandler):
    """Duplicate a sheet (tab) within the same spreadsheet."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="duplicate_sheet",
            description="Duplicate a sheet (tab) within the same spreadsheet",
        )
        self.auth = auth

    def get_tool_definition(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "The ID of the spreadsheet",
                    },
                    "sheet_name": {
                        "type": "string",
                        "description": "Name of the sheet (tab) to duplicate",
                    },
                    "new_name": {
                        "type": "string",
                        "description": "Optional name for the duplicated sheet",
                    },
                    "insert_index": {
                        "type": "integer",
                        "description": "Optional 0-based position for the new sheet",
                    },
                },
                "required": ["spreadsheet_id", "sheet_name"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(arguments, ["spreadsheet_id", "sheet_name"])
            spreadsheet_id = arguments["spreadsheet_id"]
            sheet_name = arguments["sheet_name"]
            sheets_service = self.auth.get_sheets_service()

            sheet_id = resolve_sheet_id(sheets_service, spreadsheet_id, sheet_name)

            duplicate_req: Dict[str, Any] = {"sourceSheetId": sheet_id}
            if "new_name" in arguments:
                duplicate_req["newSheetName"] = arguments["new_name"]
            if "insert_index" in arguments:
                duplicate_req["insertSheetIndex"] = arguments["insert_index"]

            result = (
                sheets_service.spreadsheets()
                .batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={"requests": [{"duplicateSheet": duplicate_req}]},
                )
                .execute()
            )

            new_props = (
                result.get("replies", [{}])[0]
                .get("duplicateSheet", {})
                .get("properties", {})
            )

            return self.format_success_response(
                json.dumps(
                    {
                        "source_sheet": sheet_name,
                        "new_sheet_id": new_props.get("sheetId"),
                        "new_title": new_props.get("title"),
                    },
                    indent=2,
                ),
                f"Duplicated sheet '{sheet_name}'",
            )
        except HttpError as e:
            _handle_http_error(e)
        except Exception as e:
            return self.format_error_response(e)


class CopySheetToHandler(SheetsToolHandler):
    """Copy a sheet (tab) from one spreadsheet to another."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="copy_sheet_to",
            description="Copy a sheet (tab) from one spreadsheet into another",
        )
        self.auth = auth

    def get_tool_definition(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "source_spreadsheet_id": {
                        "type": "string",
                        "description": "ID of the source spreadsheet",
                    },
                    "source_sheet_name": {
                        "type": "string",
                        "description": "Name of the sheet (tab) to copy",
                    },
                    "destination_spreadsheet_id": {
                        "type": "string",
                        "description": "ID of the destination spreadsheet",
                    },
                },
                "required": [
                    "source_spreadsheet_id",
                    "source_sheet_name",
                    "destination_spreadsheet_id",
                ],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(
                arguments,
                [
                    "source_spreadsheet_id",
                    "source_sheet_name",
                    "destination_spreadsheet_id",
                ],
            )
            source_id = arguments["source_spreadsheet_id"]
            source_sheet = arguments["source_sheet_name"]
            dest_id = arguments["destination_spreadsheet_id"]
            sheets_service = self.auth.get_sheets_service()

            sheet_id = resolve_sheet_id(sheets_service, source_id, source_sheet)

            result = (
                sheets_service.spreadsheets()
                .sheets()
                .copyTo(
                    spreadsheetId=source_id,
                    sheetId=sheet_id,
                    body={"destinationSpreadsheetId": dest_id},
                )
                .execute()
            )

            return self.format_success_response(
                json.dumps(
                    {
                        "source_sheet": source_sheet,
                        "destination_spreadsheet_id": dest_id,
                        "new_sheet_id": result.get("sheetId"),
                        "new_title": result.get("title"),
                    },
                    indent=2,
                ),
                f"Copied sheet '{source_sheet}' to spreadsheet {dest_id}",
            )
        except HttpError as e:
            _handle_http_error(e)
        except Exception as e:
            return self.format_error_response(e)


class InsertDimensionHandler(SheetsToolHandler):
    """Insert empty rows or columns into a sheet."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="insert_dimension",
            description="Insert empty rows or columns into a sheet (tab)",
        )
        self.auth = auth

    def get_tool_definition(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "The ID of the spreadsheet",
                    },
                    "sheet_name": {
                        "type": "string",
                        "description": "Name of the sheet (tab)",
                    },
                    "dimension": {
                        "type": "string",
                        "description": "Whether to insert ROWS or COLUMNS",
                        "enum": ["ROWS", "COLUMNS"],
                    },
                    "start_index": {
                        "type": "integer",
                        "description": "0-based start index (inclusive) to insert at",
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of rows/columns to insert",
                        "default": 1,
                    },
                    "inherit_from_before": {
                        "type": "boolean",
                        "description": "Inherit formatting from the preceding row/column",
                        "default": False,
                    },
                },
                "required": ["spreadsheet_id", "sheet_name", "dimension", "start_index"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(
                arguments,
                ["spreadsheet_id", "sheet_name", "dimension", "start_index"],
            )
            spreadsheet_id = arguments["spreadsheet_id"]
            sheet_name = arguments["sheet_name"]
            dimension = arguments["dimension"]
            start_index = arguments["start_index"]
            count = arguments.get("count", 1)
            inherit = arguments.get("inherit_from_before", False)
            sheets_service = self.auth.get_sheets_service()

            sheet_id = resolve_sheet_id(sheets_service, spreadsheet_id, sheet_name)

            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={
                    "requests": [
                        {
                            "insertDimension": {
                                "range": {
                                    "sheetId": sheet_id,
                                    "dimension": dimension,
                                    "startIndex": start_index,
                                    "endIndex": start_index + count,
                                },
                                "inheritFromBefore": inherit,
                            }
                        }
                    ]
                },
            ).execute()

            return self.format_success_response(
                json.dumps(
                    {
                        "sheet": sheet_name,
                        "dimension": dimension,
                        "inserted": count,
                        "at_index": start_index,
                    }
                ),
                f"Inserted {count} {dimension.lower()} into '{sheet_name}'",
            )
        except HttpError as e:
            _handle_http_error(e)
        except Exception as e:
            return self.format_error_response(e)


class DeleteDimensionHandler(SheetsToolHandler):
    """Delete rows or columns from a sheet."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="delete_dimension",
            description="Delete rows or columns from a sheet (tab)",
        )
        self.auth = auth

    def get_tool_definition(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "The ID of the spreadsheet",
                    },
                    "sheet_name": {
                        "type": "string",
                        "description": "Name of the sheet (tab)",
                    },
                    "dimension": {
                        "type": "string",
                        "description": "Whether to delete ROWS or COLUMNS",
                        "enum": ["ROWS", "COLUMNS"],
                    },
                    "start_index": {
                        "type": "integer",
                        "description": "0-based start index (inclusive) to delete from",
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of rows/columns to delete",
                        "default": 1,
                    },
                },
                "required": ["spreadsheet_id", "sheet_name", "dimension", "start_index"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(
                arguments,
                ["spreadsheet_id", "sheet_name", "dimension", "start_index"],
            )
            spreadsheet_id = arguments["spreadsheet_id"]
            sheet_name = arguments["sheet_name"]
            dimension = arguments["dimension"]
            start_index = arguments["start_index"]
            count = arguments.get("count", 1)
            sheets_service = self.auth.get_sheets_service()

            sheet_id = resolve_sheet_id(sheets_service, spreadsheet_id, sheet_name)

            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={
                    "requests": [
                        {
                            "deleteDimension": {
                                "range": {
                                    "sheetId": sheet_id,
                                    "dimension": dimension,
                                    "startIndex": start_index,
                                    "endIndex": start_index + count,
                                }
                            }
                        }
                    ]
                },
            ).execute()

            return self.format_success_response(
                json.dumps(
                    {
                        "sheet": sheet_name,
                        "dimension": dimension,
                        "deleted": count,
                        "at_index": start_index,
                    }
                ),
                f"Deleted {count} {dimension.lower()} from '{sheet_name}'",
            )
        except HttpError as e:
            _handle_http_error(e)
        except Exception as e:
            return self.format_error_response(e)


def _hex_to_color(hex_color: str) -> Dict[str, float]:
    """Convert '#RRGGBB' (or 'RRGGBB') to a Sheets API color object."""
    value = hex_color.lstrip("#")
    if len(value) != 6:
        raise InvalidRangeError(
            f"Invalid hex color '{hex_color}', expected format #RRGGBB"
        )
    try:
        r = int(value[0:2], 16) / 255.0
        g = int(value[2:4], 16) / 255.0
        b = int(value[4:6], 16) / 255.0
    except ValueError:
        raise InvalidRangeError(f"Invalid hex color '{hex_color}'")
    return {"red": r, "green": g, "blue": b}


class FormatCellsHandler(SheetsToolHandler):
    """Apply basic formatting (bold/italic/colors/number format) to a range."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="format_cells",
            description=(
                "Apply basic formatting (bold, italic, font size, background and "
                "text color, number format, alignment) to a range of cells"
            ),
        )
        self.auth = auth

    def get_tool_definition(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "The ID of the spreadsheet",
                    },
                    "sheet_name": {
                        "type": "string",
                        "description": "Name of the sheet (tab)",
                    },
                    "start_row": {
                        "type": "integer",
                        "description": "0-based start row index (inclusive)",
                    },
                    "end_row": {
                        "type": "integer",
                        "description": "0-based end row index (exclusive)",
                    },
                    "start_column": {
                        "type": "integer",
                        "description": "0-based start column index (inclusive)",
                    },
                    "end_column": {
                        "type": "integer",
                        "description": "0-based end column index (exclusive)",
                    },
                    "bold": {"type": "boolean", "description": "Make text bold"},
                    "italic": {"type": "boolean", "description": "Make text italic"},
                    "font_size": {
                        "type": "integer",
                        "description": "Font size in points",
                    },
                    "background_color": {
                        "type": "string",
                        "description": "Cell background color as hex, e.g. '#FFEB3B'",
                    },
                    "text_color": {
                        "type": "string",
                        "description": "Text color as hex, e.g. '#000000'",
                    },
                    "number_format": {
                        "type": "string",
                        "description": (
                            "Number format pattern, e.g. '$#,##0.00', '0.00%', "
                            "'yyyy-mm-dd'"
                        ),
                    },
                    "number_format_type": {
                        "type": "string",
                        "description": "Number format type (default NUMBER)",
                        "enum": [
                            "NUMBER",
                            "CURRENCY",
                            "PERCENT",
                            "DATE",
                            "TIME",
                            "DATE_TIME",
                            "TEXT",
                            "SCIENTIFIC",
                        ],
                        "default": "NUMBER",
                    },
                    "horizontal_alignment": {
                        "type": "string",
                        "enum": ["LEFT", "CENTER", "RIGHT"],
                        "description": "Horizontal text alignment",
                    },
                },
                "required": [
                    "spreadsheet_id",
                    "sheet_name",
                    "start_row",
                    "end_row",
                    "start_column",
                    "end_column",
                ],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(
                arguments,
                [
                    "spreadsheet_id",
                    "sheet_name",
                    "start_row",
                    "end_row",
                    "start_column",
                    "end_column",
                ],
            )
            spreadsheet_id = arguments["spreadsheet_id"]
            sheet_name = arguments["sheet_name"]
            sheets_service = self.auth.get_sheets_service()

            sheet_id = resolve_sheet_id(sheets_service, spreadsheet_id, sheet_name)

            # Build the cell format and the fields mask incrementally so we only
            # touch the attributes the caller actually specified.
            cell_format: Dict[str, Any] = {}
            fields: List[str] = []

            text_format: Dict[str, Any] = {}
            if "bold" in arguments:
                text_format["bold"] = arguments["bold"]
                fields.append("userEnteredFormat.textFormat.bold")
            if "italic" in arguments:
                text_format["italic"] = arguments["italic"]
                fields.append("userEnteredFormat.textFormat.italic")
            if "font_size" in arguments:
                text_format["fontSize"] = arguments["font_size"]
                fields.append("userEnteredFormat.textFormat.fontSize")
            if "text_color" in arguments:
                text_format["foregroundColor"] = _hex_to_color(arguments["text_color"])
                fields.append("userEnteredFormat.textFormat.foregroundColor")
            if text_format:
                cell_format["textFormat"] = text_format

            if "background_color" in arguments:
                cell_format["backgroundColor"] = _hex_to_color(
                    arguments["background_color"]
                )
                fields.append("userEnteredFormat.backgroundColor")

            if "number_format" in arguments:
                cell_format["numberFormat"] = {
                    "type": arguments.get("number_format_type", "NUMBER"),
                    "pattern": arguments["number_format"],
                }
                fields.append("userEnteredFormat.numberFormat")

            if "horizontal_alignment" in arguments:
                cell_format["horizontalAlignment"] = arguments["horizontal_alignment"]
                fields.append("userEnteredFormat.horizontalAlignment")

            if not fields:
                raise InvalidRangeError(
                    "No formatting options provided. Specify at least one of: "
                    "bold, italic, font_size, background_color, text_color, "
                    "number_format, horizontal_alignment."
                )

            request = {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": arguments["start_row"],
                        "endRowIndex": arguments["end_row"],
                        "startColumnIndex": arguments["start_column"],
                        "endColumnIndex": arguments["end_column"],
                    },
                    "cell": {"userEnteredFormat": cell_format},
                    "fields": ",".join(fields),
                }
            }

            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": [request]},
            ).execute()

            return self.format_success_response(
                json.dumps({"sheet": sheet_name, "applied": fields}, indent=2),
                f"Applied formatting to '{sheet_name}'",
            )
        except HttpError as e:
            _handle_http_error(e)
        except Exception as e:
            return self.format_error_response(e)


class SortRangeHandler(SheetsToolHandler):
    """Sort a range of cells by one or more columns."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="sort_range",
            description="Sort a range of cells by one or more columns",
        )
        self.auth = auth

    def get_tool_definition(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "The ID of the spreadsheet",
                    },
                    "sheet_name": {
                        "type": "string",
                        "description": "Name of the sheet (tab)",
                    },
                    "start_row": {
                        "type": "integer",
                        "description": "0-based start row index (inclusive)",
                    },
                    "end_row": {
                        "type": "integer",
                        "description": "0-based end row index (exclusive)",
                    },
                    "start_column": {
                        "type": "integer",
                        "description": "0-based start column index (inclusive)",
                    },
                    "end_column": {
                        "type": "integer",
                        "description": "0-based end column index (exclusive)",
                    },
                    "sort_specs": {
                        "type": "array",
                        "description": "Ordered list of sort columns",
                        "items": {
                            "type": "object",
                            "properties": {
                                "column_index": {
                                    "type": "integer",
                                    "description": "0-based column index to sort by "
                                    "(absolute within the sheet)",
                                },
                                "order": {
                                    "type": "string",
                                    "enum": ["ASCENDING", "DESCENDING"],
                                    "default": "ASCENDING",
                                },
                            },
                            "required": ["column_index"],
                        },
                    },
                },
                "required": [
                    "spreadsheet_id",
                    "sheet_name",
                    "start_row",
                    "end_row",
                    "start_column",
                    "end_column",
                    "sort_specs",
                ],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(
                arguments,
                [
                    "spreadsheet_id",
                    "sheet_name",
                    "start_row",
                    "end_row",
                    "start_column",
                    "end_column",
                    "sort_specs",
                ],
            )
            spreadsheet_id = arguments["spreadsheet_id"]
            sheet_name = arguments["sheet_name"]
            sheets_service = self.auth.get_sheets_service()

            sheet_id = resolve_sheet_id(sheets_service, spreadsheet_id, sheet_name)

            sort_specs = [
                {
                    "dimensionIndex": spec["column_index"],
                    "sortOrder": spec.get("order", "ASCENDING"),
                }
                for spec in arguments["sort_specs"]
            ]

            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={
                    "requests": [
                        {
                            "sortRange": {
                                "range": {
                                    "sheetId": sheet_id,
                                    "startRowIndex": arguments["start_row"],
                                    "endRowIndex": arguments["end_row"],
                                    "startColumnIndex": arguments["start_column"],
                                    "endColumnIndex": arguments["end_column"],
                                },
                                "sortSpecs": sort_specs,
                            }
                        }
                    ]
                },
            ).execute()

            return self.format_success_response(
                json.dumps(
                    {"sheet": sheet_name, "sort_specs": sort_specs}, indent=2
                ),
                f"Sorted range in '{sheet_name}'",
            )
        except HttpError as e:
            _handle_http_error(e)
        except Exception as e:
            return self.format_error_response(e)


class SetDataValidationHandler(SheetsToolHandler):
    """Set a dropdown (list) data-validation rule on a range."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="set_data_validation",
            description="Set a dropdown (one-of-list) data-validation rule on a range",
        )
        self.auth = auth

    def get_tool_definition(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "The ID of the spreadsheet",
                    },
                    "sheet_name": {
                        "type": "string",
                        "description": "Name of the sheet (tab)",
                    },
                    "start_row": {
                        "type": "integer",
                        "description": "0-based start row index (inclusive)",
                    },
                    "end_row": {
                        "type": "integer",
                        "description": "0-based end row index (exclusive)",
                    },
                    "start_column": {
                        "type": "integer",
                        "description": "0-based start column index (inclusive)",
                    },
                    "end_column": {
                        "type": "integer",
                        "description": "0-based end column index (exclusive)",
                    },
                    "values": {
                        "type": "array",
                        "description": "Allowed dropdown values",
                        "items": {"type": "string"},
                    },
                    "strict": {
                        "type": "boolean",
                        "description": "Reject values not in the list (default true)",
                        "default": True,
                    },
                    "show_dropdown": {
                        "type": "boolean",
                        "description": "Show the dropdown arrow in cells",
                        "default": True,
                    },
                },
                "required": [
                    "spreadsheet_id",
                    "sheet_name",
                    "start_row",
                    "end_row",
                    "start_column",
                    "end_column",
                    "values",
                ],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(
                arguments,
                [
                    "spreadsheet_id",
                    "sheet_name",
                    "start_row",
                    "end_row",
                    "start_column",
                    "end_column",
                    "values",
                ],
            )
            spreadsheet_id = arguments["spreadsheet_id"]
            sheet_name = arguments["sheet_name"]
            sheets_service = self.auth.get_sheets_service()

            sheet_id = resolve_sheet_id(sheets_service, spreadsheet_id, sheet_name)

            condition_values = [{"userEnteredValue": v} for v in arguments["values"]]

            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={
                    "requests": [
                        {
                            "setDataValidation": {
                                "range": {
                                    "sheetId": sheet_id,
                                    "startRowIndex": arguments["start_row"],
                                    "endRowIndex": arguments["end_row"],
                                    "startColumnIndex": arguments["start_column"],
                                    "endColumnIndex": arguments["end_column"],
                                },
                                "rule": {
                                    "condition": {
                                        "type": "ONE_OF_LIST",
                                        "values": condition_values,
                                    },
                                    "strict": arguments.get("strict", True),
                                    "showCustomUi": arguments.get(
                                        "show_dropdown", True
                                    ),
                                },
                            }
                        }
                    ]
                },
            ).execute()

            return self.format_success_response(
                json.dumps(
                    {"sheet": sheet_name, "values": arguments["values"]}, indent=2
                ),
                f"Set dropdown validation on '{sheet_name}'",
            )
        except HttpError as e:
            _handle_http_error(e)
        except Exception as e:
            return self.format_error_response(e)


class AddConditionalFormatHandler(SheetsToolHandler):
    """Add a conditional formatting rule (boolean condition) to a range."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="add_conditional_format",
            description=(
                "Add a conditional formatting rule to a range: when a condition is "
                "met, apply a background and/or text color"
            ),
        )
        self.auth = auth

    def get_tool_definition(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "The ID of the spreadsheet",
                    },
                    "sheet_name": {
                        "type": "string",
                        "description": "Name of the sheet (tab)",
                    },
                    "start_row": {"type": "integer", "description": "0-based start row (inclusive)"},
                    "end_row": {"type": "integer", "description": "0-based end row (exclusive)"},
                    "start_column": {"type": "integer", "description": "0-based start column (inclusive)"},
                    "end_column": {"type": "integer", "description": "0-based end column (exclusive)"},
                    "condition_type": {
                        "type": "string",
                        "description": "Boolean condition type",
                        "enum": [
                            "NUMBER_GREATER",
                            "NUMBER_GREATER_THAN_EQ",
                            "NUMBER_LESS",
                            "NUMBER_LESS_THAN_EQ",
                            "NUMBER_EQ",
                            "NUMBER_NOT_EQ",
                            "NUMBER_BETWEEN",
                            "TEXT_CONTAINS",
                            "TEXT_NOT_CONTAINS",
                            "TEXT_STARTS_WITH",
                            "TEXT_ENDS_WITH",
                            "TEXT_EQ",
                            "BLANK",
                            "NOT_BLANK",
                            "CUSTOM_FORMULA",
                        ],
                    },
                    "values": {
                        "type": "array",
                        "description": "Condition argument(s), e.g. ['100'] or "
                        "['10','20'] for NUMBER_BETWEEN; omit for BLANK/NOT_BLANK",
                        "items": {"type": "string"},
                    },
                    "background_color": {
                        "type": "string",
                        "description": "Background color to apply as hex, e.g. '#FF0000'",
                    },
                    "text_color": {
                        "type": "string",
                        "description": "Text color to apply as hex, e.g. '#FFFFFF'",
                    },
                    "bold": {"type": "boolean", "description": "Make matching text bold"},
                },
                "required": [
                    "spreadsheet_id",
                    "sheet_name",
                    "start_row",
                    "end_row",
                    "start_column",
                    "end_column",
                    "condition_type",
                ],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(
                arguments,
                [
                    "spreadsheet_id",
                    "sheet_name",
                    "start_row",
                    "end_row",
                    "start_column",
                    "end_column",
                    "condition_type",
                ],
            )
            spreadsheet_id = arguments["spreadsheet_id"]
            sheet_name = arguments["sheet_name"]
            sheets_service = self.auth.get_sheets_service()

            sheet_id = resolve_sheet_id(sheets_service, spreadsheet_id, sheet_name)

            condition: Dict[str, Any] = {"type": arguments["condition_type"]}
            if arguments.get("values"):
                condition["values"] = [
                    {"userEnteredValue": v} for v in arguments["values"]
                ]

            # Build the format applied when the condition holds.
            cell_format: Dict[str, Any] = {}
            if "background_color" in arguments:
                cell_format["backgroundColor"] = _hex_to_color(
                    arguments["background_color"]
                )
            text_format: Dict[str, Any] = {}
            if "text_color" in arguments:
                text_format["foregroundColor"] = _hex_to_color(arguments["text_color"])
            if "bold" in arguments:
                text_format["bold"] = arguments["bold"]
            if text_format:
                cell_format["textFormat"] = text_format

            if not cell_format:
                raise InvalidRangeError(
                    "No format provided. Specify at least one of: "
                    "background_color, text_color, bold."
                )

            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={
                    "requests": [
                        {
                            "addConditionalFormatRule": {
                                "index": 0,
                                "rule": {
                                    "ranges": [
                                        {
                                            "sheetId": sheet_id,
                                            "startRowIndex": arguments["start_row"],
                                            "endRowIndex": arguments["end_row"],
                                            "startColumnIndex": arguments[
                                                "start_column"
                                            ],
                                            "endColumnIndex": arguments["end_column"],
                                        }
                                    ],
                                    "booleanRule": {
                                        "condition": condition,
                                        "format": cell_format,
                                    },
                                },
                            }
                        }
                    ]
                },
            ).execute()

            return self.format_success_response(
                json.dumps(
                    {
                        "sheet": sheet_name,
                        "condition": arguments["condition_type"],
                    },
                    indent=2,
                ),
                f"Added conditional format rule to '{sheet_name}'",
            )
        except HttpError as e:
            _handle_http_error(e)
        except Exception as e:
            return self.format_error_response(e)


# Registry of all sheet-management tool handlers
SHEET_MANAGEMENT_HANDLERS = [
    ListSheetsHandler,
    CreateSheetHandler,
    DeleteSheetHandler,
    RenameSheetHandler,
    DuplicateSheetHandler,
    CopySheetToHandler,
    InsertDimensionHandler,
    DeleteDimensionHandler,
    FormatCellsHandler,
    SortRangeHandler,
    SetDataValidationHandler,
    AddConditionalFormatHandler,
]

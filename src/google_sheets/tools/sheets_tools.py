"""Google Sheets API tools for data manipulation and sheet management."""

import json
import logging
from typing import Any, Dict, List, Optional

from googleapiclient.errors import HttpError
from mcp.types import TextContent, Tool

from ..auth.oauth_manager import GoogleSheetsAuth
from ..core.exceptions import InvalidRangeError, SheetsAPIError
from ..core.sheets_helpers import (
    column_index_to_letter,
    list_sheet_properties,
    resolve_sheet_id,
)
from ..core.tool_handler import SheetsToolHandler

logger = logging.getLogger(__name__)


class ReadRangeHandler(SheetsToolHandler):
    """Handler for reading data from spreadsheet ranges."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="read_range",
            description="Read data from a specified range in a Google Sheet",
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
                    "range": {
                        "type": "string",
                        "description": "The A1 notation range to read (e.g., 'Sheet1!A1:C10' or 'A1:C10')",
                    },
                    "value_render_option": {
                        "type": "string",
                        "description": "How values should be represented",
                        "enum": ["FORMATTED_VALUE", "UNFORMATTED_VALUE", "FORMULA"],
                        "default": "FORMATTED_VALUE",
                    },
                    "date_time_render_option": {
                        "type": "string",
                        "description": "How dates should be represented",
                        "enum": ["SERIAL_NUMBER", "FORMATTED_STRING"],
                        "default": "FORMATTED_STRING",
                    },
                },
                "required": ["spreadsheet_id", "range"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute the read range operation."""
        try:
            self.validate_arguments(arguments, ["spreadsheet_id", "range"])

            spreadsheet_id = arguments["spreadsheet_id"]
            range_name = arguments["range"]
            value_render_option = arguments.get(
                "value_render_option", "FORMATTED_VALUE"
            )
            date_time_render_option = arguments.get(
                "date_time_render_option", "FORMATTED_STRING"
            )

            sheets_service = self.auth.get_sheets_service()

            result = (
                sheets_service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueRenderOption=value_render_option,
                    dateTimeRenderOption=date_time_render_option,
                )
                .execute()
            )

            values = result.get("values", [])

            if not values:
                return self.format_success_response(
                    "No data found in the specified range."
                )

            response_data = {
                "range": result.get("range"),
                "major_dimension": result.get("majorDimension", "ROWS"),
                "row_count": len(values),
                "column_count": max(len(row) for row in values) if values else 0,
                "values": values,
            }

            return self.format_success_response(
                json.dumps(response_data, indent=2),
                f"Read {len(values)} rows from range {range_name}",
            )

        except HttpError as e:
            if e.resp.status == 400:
                raise InvalidRangeError(f"Invalid range: {range_name}")
            elif e.resp.status == 404:
                raise SheetsAPIError("Spreadsheet not found", 404)
            else:
                raise SheetsAPIError(f"Sheets API error: {e.reason}", e.resp.status)
        except Exception as e:
            return self.format_error_response(e)


class WriteRangeHandler(SheetsToolHandler):
    """Handler for writing data to spreadsheet ranges."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="write_range",
            description="Write data to a specified range in a Google Sheet",
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
                    "range": {
                        "type": "string",
                        "description": "The A1 notation range to write to (e.g., 'Sheet1!A1:C10')",
                    },
                    "values": {
                        "type": "array",
                        "description": "2D array of values to write",
                        "items": {"type": "array", "items": {"type": "string"}},
                    },
                    "value_input_option": {
                        "type": "string",
                        "description": "How input data should be interpreted",
                        "enum": ["RAW", "USER_ENTERED"],
                        "default": "USER_ENTERED",
                    },
                },
                "required": ["spreadsheet_id", "range", "values"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute the write range operation."""
        try:
            self.validate_arguments(arguments, ["spreadsheet_id", "range", "values"])

            spreadsheet_id = arguments["spreadsheet_id"]
            range_name = arguments["range"]
            values = arguments["values"]
            value_input_option = arguments.get("value_input_option", "USER_ENTERED")

            sheets_service = self.auth.get_sheets_service()

            body = {"values": values}

            result = (
                sheets_service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute()
            )

            response_data = {
                "updated_range": result.get("updatedRange"),
                "updated_rows": result.get("updatedRows"),
                "updated_columns": result.get("updatedColumns"),
                "updated_cells": result.get("updatedCells"),
            }

            return self.format_success_response(
                json.dumps(response_data, indent=2),
                f"Successfully updated {result.get('updatedCells', 0)} cells in range {range_name}",
            )

        except HttpError as e:
            if e.resp.status == 400:
                raise InvalidRangeError(f"Invalid range or data: {range_name}")
            elif e.resp.status == 404:
                raise SheetsAPIError("Spreadsheet not found", 404)
            else:
                raise SheetsAPIError(f"Sheets API error: {e.reason}", e.resp.status)
        except Exception as e:
            return self.format_error_response(e)


class AppendDataHandler(SheetsToolHandler):
    """Handler for appending data to a spreadsheet."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="append_data",
            description="Append rows of data to the end of a Google Sheet",
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
                    "range": {
                        "type": "string",
                        "description": "The A1 notation range indicating the sheet and columns (e.g., 'Sheet1!A:C')",
                    },
                    "values": {
                        "type": "array",
                        "description": "2D array of values to append",
                        "items": {"type": "array", "items": {"type": "string"}},
                    },
                    "value_input_option": {
                        "type": "string",
                        "description": "How input data should be interpreted",
                        "enum": ["RAW", "USER_ENTERED"],
                        "default": "USER_ENTERED",
                    },
                    "insert_data_option": {
                        "type": "string",
                        "description": "How data should be inserted",
                        "enum": ["OVERWRITE", "INSERT_ROWS"],
                        "default": "INSERT_ROWS",
                    },
                },
                "required": ["spreadsheet_id", "range", "values"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute the append data operation."""
        try:
            self.validate_arguments(arguments, ["spreadsheet_id", "range", "values"])

            spreadsheet_id = arguments["spreadsheet_id"]
            range_name = arguments["range"]
            values = arguments["values"]
            value_input_option = arguments.get("value_input_option", "USER_ENTERED")
            insert_data_option = arguments.get("insert_data_option", "INSERT_ROWS")

            sheets_service = self.auth.get_sheets_service()

            body = {"values": values}

            result = (
                sheets_service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    insertDataOption=insert_data_option,
                    body=body,
                )
                .execute()
            )

            response_data = {
                "spreadsheet_id": result.get("spreadsheetId"),
                "table_range": result.get("tableRange"),
                "updates": result.get("updates", {}),
            }

            return self.format_success_response(
                json.dumps(response_data, indent=2),
                f"Successfully appended {len(values)} rows to {range_name}",
            )

        except HttpError as e:
            if e.resp.status == 400:
                raise InvalidRangeError(f"Invalid range or data: {range_name}")
            elif e.resp.status == 404:
                raise SheetsAPIError("Spreadsheet not found", 404)
            else:
                raise SheetsAPIError(f"Sheets API error: {e.reason}", e.resp.status)
        except Exception as e:
            return self.format_error_response(e)


class ClearRangeHandler(SheetsToolHandler):
    """Handler for clearing data from spreadsheet ranges."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="clear_range",
            description="Clear data from a specified range in a Google Sheet",
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
                    "range": {
                        "type": "string",
                        "description": "The A1 notation range to clear (e.g., 'Sheet1!A1:C10')",
                    },
                },
                "required": ["spreadsheet_id", "range"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute the clear range operation."""
        try:
            self.validate_arguments(arguments, ["spreadsheet_id", "range"])

            spreadsheet_id = arguments["spreadsheet_id"]
            range_name = arguments["range"]

            sheets_service = self.auth.get_sheets_service()

            result = (
                sheets_service.spreadsheets()
                .values()
                .clear(spreadsheetId=spreadsheet_id, range=range_name, body={})
                .execute()
            )

            response_data = {
                "cleared_range": result.get("clearedRange"),
                "spreadsheet_id": result.get("spreadsheetId"),
            }

            return self.format_success_response(
                json.dumps(response_data, indent=2),
                f"Successfully cleared range {range_name}",
            )

        except HttpError as e:
            if e.resp.status == 400:
                raise InvalidRangeError(f"Invalid range: {range_name}")
            elif e.resp.status == 404:
                raise SheetsAPIError("Spreadsheet not found", 404)
            else:
                raise SheetsAPIError(f"Sheets API error: {e.reason}", e.resp.status)
        except Exception as e:
            return self.format_error_response(e)


class CreateSpreadsheetHandler(SheetsToolHandler):
    """Handler for creating a brand new spreadsheet.

    Створюємо через Sheets API (`spreadsheets().create`), а не Drive, тож
    лишаємось у межах скоупу `spreadsheets` (принцип найменших привілеїв).
    """

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="create_spreadsheet",
            description="Create a new Google Spreadsheet (optionally with named sheets)",
        )
        self.auth = auth

    def get_tool_definition(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the new spreadsheet",
                    },
                    "sheet_titles": {
                        "type": "array",
                        "description": "Optional list of sheet (tab) titles to create",
                        "items": {"type": "string"},
                    },
                },
                "required": ["title"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(arguments, ["title"])
            title = arguments["title"]
            sheet_titles = arguments.get("sheet_titles") or []

            body: Dict[str, Any] = {"properties": {"title": title}}
            if sheet_titles:
                body["sheets"] = [
                    {"properties": {"title": t}} for t in sheet_titles
                ]

            sheets_service = self.auth.get_sheets_service()
            result = (
                sheets_service.spreadsheets()
                .create(body=body, fields="spreadsheetId,spreadsheetUrl,sheets.properties")
                .execute()
            )

            sheets_list = [
                s.get("properties", {}).get("title")
                for s in result.get("sheets", [])
            ]

            return self.format_success_response(
                json.dumps(
                    {
                        "spreadsheet_id": result.get("spreadsheetId"),
                        "spreadsheet_url": result.get("spreadsheetUrl"),
                        "sheets": sheets_list,
                    },
                    indent=2,
                ),
                f"Created spreadsheet '{title}'",
            )
        except HttpError as e:
            raise SheetsAPIError(f"Sheets API error: {e.reason}", e.resp.status)
        except Exception as e:
            return self.format_error_response(e)


class BatchGetValuesHandler(SheetsToolHandler):
    """Handler for reading multiple ranges in a single API call."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="batch_get_values",
            description="Read several ranges from a spreadsheet in a single request",
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
                    "ranges": {
                        "type": "array",
                        "description": "List of A1 ranges to read (e.g. ['Sheet1!A1:B2', 'Sheet2!C:C'])",
                        "items": {"type": "string"},
                    },
                    "value_render_option": {
                        "type": "string",
                        "enum": ["FORMATTED_VALUE", "UNFORMATTED_VALUE", "FORMULA"],
                        "default": "FORMATTED_VALUE",
                    },
                },
                "required": ["spreadsheet_id", "ranges"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(arguments, ["spreadsheet_id", "ranges"])
            spreadsheet_id = arguments["spreadsheet_id"]
            ranges = arguments["ranges"]
            value_render_option = arguments.get(
                "value_render_option", "FORMATTED_VALUE"
            )

            sheets_service = self.auth.get_sheets_service()
            result = (
                sheets_service.spreadsheets()
                .values()
                .batchGet(
                    spreadsheetId=spreadsheet_id,
                    ranges=ranges,
                    valueRenderOption=value_render_option,
                )
                .execute()
            )

            value_ranges = [
                {
                    "range": vr.get("range"),
                    "values": vr.get("values", []),
                }
                for vr in result.get("valueRanges", [])
            ]

            return self.format_success_response(
                json.dumps({"value_ranges": value_ranges}, indent=2),
                f"Read {len(value_ranges)} range(s)",
            )
        except HttpError as e:
            if e.resp.status == 400:
                raise InvalidRangeError("Invalid range(s) provided")
            if e.resp.status == 404:
                raise SheetsAPIError("Spreadsheet not found", 404)
            raise SheetsAPIError(f"Sheets API error: {e.reason}", e.resp.status)
        except Exception as e:
            return self.format_error_response(e)


class BatchUpdateValuesHandler(SheetsToolHandler):
    """Handler for writing multiple ranges in a single API call."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="batch_update_values",
            description="Write several ranges to a spreadsheet in a single request",
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
                    "data": {
                        "type": "array",
                        "description": "List of {range, values} objects to write",
                        "items": {
                            "type": "object",
                            "properties": {
                                "range": {
                                    "type": "string",
                                    "description": "A1 range (e.g. 'Sheet1!A1:B2')",
                                },
                                "values": {
                                    "type": "array",
                                    "description": "2D array of values",
                                    "items": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                            },
                            "required": ["range", "values"],
                        },
                    },
                    "value_input_option": {
                        "type": "string",
                        "enum": ["RAW", "USER_ENTERED"],
                        "default": "USER_ENTERED",
                    },
                },
                "required": ["spreadsheet_id", "data"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(arguments, ["spreadsheet_id", "data"])
            spreadsheet_id = arguments["spreadsheet_id"]
            data = arguments["data"]
            value_input_option = arguments.get("value_input_option", "USER_ENTERED")

            body = {
                "valueInputOption": value_input_option,
                "data": [
                    {"range": item["range"], "values": item["values"]}
                    for item in data
                ],
            }

            sheets_service = self.auth.get_sheets_service()
            result = (
                sheets_service.spreadsheets()
                .values()
                .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
                .execute()
            )

            return self.format_success_response(
                json.dumps(
                    {
                        "total_updated_cells": result.get("totalUpdatedCells"),
                        "total_updated_rows": result.get("totalUpdatedRows"),
                        "total_updated_ranges": len(result.get("responses", [])),
                    },
                    indent=2,
                ),
                f"Updated {result.get('totalUpdatedCells', 0)} cells across "
                f"{len(data)} range(s)",
            )
        except HttpError as e:
            if e.resp.status == 400:
                raise InvalidRangeError("Invalid range(s) or data provided")
            if e.resp.status == 404:
                raise SheetsAPIError("Spreadsheet not found", 404)
            raise SheetsAPIError(f"Sheets API error: {e.reason}", e.resp.status)
        except Exception as e:
            return self.format_error_response(e)


class FindReplaceHandler(SheetsToolHandler):
    """Handler for find/replace across a spreadsheet or a single sheet."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="find_replace",
            description="Find and replace text across a spreadsheet or a single sheet",
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
                    "find": {
                        "type": "string",
                        "description": "Text or pattern to search for",
                    },
                    "replacement": {
                        "type": "string",
                        "description": "Text to replace matches with",
                    },
                    "sheet_name": {
                        "type": "string",
                        "description": "Optional sheet (tab) to limit the operation to; "
                        "omit to search all sheets",
                    },
                    "match_case": {
                        "type": "boolean",
                        "description": "Whether the search is case-sensitive",
                        "default": False,
                    },
                    "match_entire_cell": {
                        "type": "boolean",
                        "description": "Match the entire cell content only",
                        "default": False,
                    },
                    "search_by_regex": {
                        "type": "boolean",
                        "description": "Treat 'find' as a regular expression",
                        "default": False,
                    },
                },
                "required": ["spreadsheet_id", "find", "replacement"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(
                arguments, ["spreadsheet_id", "find", "replacement"]
            )
            spreadsheet_id = arguments["spreadsheet_id"]
            sheets_service = self.auth.get_sheets_service()

            find_replace: Dict[str, Any] = {
                "find": arguments["find"],
                "replacement": arguments["replacement"],
                "matchCase": arguments.get("match_case", False),
                "matchEntireCell": arguments.get("match_entire_cell", False),
                "searchByRegex": arguments.get("search_by_regex", False),
            }

            if arguments.get("sheet_name"):
                sheet_id = resolve_sheet_id(
                    sheets_service, spreadsheet_id, arguments["sheet_name"]
                )
                find_replace["sheetId"] = sheet_id
            else:
                find_replace["allSheets"] = True

            result = (
                sheets_service.spreadsheets()
                .batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={"requests": [{"findReplace": find_replace}]},
                )
                .execute()
            )

            reply = result.get("replies", [{}])[0].get("findReplace", {})

            return self.format_success_response(
                json.dumps(
                    {
                        "values_changed": reply.get("valuesChanged", 0),
                        "rows_changed": reply.get("rowsChanged", 0),
                        "sheets_changed": reply.get("sheetsChanged", 0),
                        "occurrences_changed": reply.get("occurrencesChanged", 0),
                    },
                    indent=2,
                ),
                f"Replaced {reply.get('occurrencesChanged', 0)} occurrence(s)",
            )
        except HttpError as e:
            if e.resp.status == 400:
                raise InvalidRangeError("Invalid find/replace request")
            if e.resp.status == 404:
                raise SheetsAPIError("Spreadsheet not found", 404)
            raise SheetsAPIError(f"Sheets API error: {e.reason}", e.resp.status)
        except Exception as e:
            return self.format_error_response(e)


class RenameSpreadsheetHandler(SheetsToolHandler):
    """Handler for renaming the spreadsheet (file) itself.

    Через `updateSpreadsheetProperties` у Sheets API, тож без Drive write —
    лишаємось у межах скоупу `spreadsheets`.
    """

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="rename_spreadsheet",
            description="Rename the spreadsheet (the whole file) itself",
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
                    "new_title": {
                        "type": "string",
                        "description": "New title for the spreadsheet",
                    },
                },
                "required": ["spreadsheet_id", "new_title"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(arguments, ["spreadsheet_id", "new_title"])
            spreadsheet_id = arguments["spreadsheet_id"]
            new_title = arguments["new_title"]

            sheets_service = self.auth.get_sheets_service()
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={
                    "requests": [
                        {
                            "updateSpreadsheetProperties": {
                                "properties": {"title": new_title},
                                "fields": "title",
                            }
                        }
                    ]
                },
            ).execute()

            return self.format_success_response(
                json.dumps({"spreadsheet_id": spreadsheet_id, "new_title": new_title}),
                f"Renamed spreadsheet to '{new_title}'",
            )
        except HttpError as e:
            if e.resp.status == 404:
                raise SheetsAPIError("Spreadsheet not found", 404)
            raise SheetsAPIError(f"Sheets API error: {e.reason}", e.resp.status)
        except Exception as e:
            return self.format_error_response(e)


class GetSheetFormulasHandler(SheetsToolHandler):
    """Handler for reading formulas (not computed values) from a range."""

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="get_sheet_formulas",
            description="Read the formulas (not the computed values) from a range",
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
                    "range": {
                        "type": "string",
                        "description": "A1 range to read formulas from (e.g. 'Sheet1!A1:C10')",
                    },
                },
                "required": ["spreadsheet_id", "range"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(arguments, ["spreadsheet_id", "range"])
            spreadsheet_id = arguments["spreadsheet_id"]
            range_name = arguments["range"]

            sheets_service = self.auth.get_sheets_service()
            result = (
                sheets_service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueRenderOption="FORMULA",
                )
                .execute()
            )

            values = result.get("values", [])
            if not values:
                return self.format_success_response(
                    "No formulas or data found in the specified range."
                )

            return self.format_success_response(
                json.dumps(
                    {
                        "range": result.get("range"),
                        "row_count": len(values),
                        "formulas": values,
                    },
                    indent=2,
                ),
                f"Read formulas from {range_name}",
            )
        except HttpError as e:
            if e.resp.status == 400:
                raise InvalidRangeError(f"Invalid range: {range_name}")
            if e.resp.status == 404:
                raise SheetsAPIError("Spreadsheet not found", 404)
            raise SheetsAPIError(f"Sheets API error: {e.reason}", e.resp.status)
        except Exception as e:
            return self.format_error_response(e)


class FindCellsHandler(SheetsToolHandler):
    """Handler for finding cells by value WITHOUT modifying anything.

    На відміну від `find_replace`, це read-only пошук: повертає координати
    комірок та їх значення, нічого не змінюючи.
    """

    def __init__(self, auth: GoogleSheetsAuth) -> None:
        super().__init__(
            name="find_cells",
            description="Find cells matching a query (read-only) across a sheet or "
            "the whole spreadsheet",
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
                    "query": {
                        "type": "string",
                        "description": "Text to search for inside cell values",
                    },
                    "sheet_name": {
                        "type": "string",
                        "description": "Optional sheet (tab) to limit the search to; "
                        "omit to search all sheets",
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Whether the search is case-sensitive",
                        "default": False,
                    },
                    "match_entire_cell": {
                        "type": "boolean",
                        "description": "Match the entire cell content only",
                        "default": False,
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of matches to return",
                        "default": 50,
                    },
                },
                "required": ["spreadsheet_id", "query"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            self.validate_arguments(arguments, ["spreadsheet_id", "query"])
            spreadsheet_id = arguments["spreadsheet_id"]
            query = arguments["query"]
            case_sensitive = arguments.get("case_sensitive", False)
            match_entire_cell = arguments.get("match_entire_cell", False)
            max_results = arguments.get("max_results", 50)

            sheets_service = self.auth.get_sheets_service()

            # Determine which sheets to scan.
            if arguments.get("sheet_name"):
                target_sheets = [arguments["sheet_name"]]
            else:
                target_sheets = [
                    s["title"]
                    for s in list_sheet_properties(sheets_service, spreadsheet_id)
                ]

            needle = query if case_sensitive else query.lower()
            matches: List[Dict[str, Any]] = []

            for sheet_title in target_sheets:
                result = (
                    sheets_service.spreadsheets()
                    .values()
                    .get(
                        spreadsheetId=spreadsheet_id,
                        range=sheet_title,
                        valueRenderOption="FORMATTED_VALUE",
                    )
                    .execute()
                )
                rows = result.get("values", [])
                for row_idx, row in enumerate(rows):
                    for col_idx, cell in enumerate(row):
                        haystack = str(cell)
                        compare = haystack if case_sensitive else haystack.lower()
                        found = (
                            compare == needle
                            if match_entire_cell
                            else needle in compare
                        )
                        if found:
                            col_letter = column_index_to_letter(col_idx)
                            matches.append(
                                {
                                    "sheet": sheet_title,
                                    "cell": f"{col_letter}{row_idx + 1}",
                                    "value": haystack,
                                }
                            )
                            if len(matches) >= max_results:
                                break
                    if len(matches) >= max_results:
                        break
                if len(matches) >= max_results:
                    break

            return self.format_success_response(
                json.dumps(
                    {"total_matches": len(matches), "matches": matches}, indent=2
                ),
                f"Found {len(matches)} matching cell(s)",
            )
        except HttpError as e:
            if e.resp.status == 404:
                raise SheetsAPIError("Spreadsheet not found", 404)
            raise SheetsAPIError(f"Sheets API error: {e.reason}", e.resp.status)
        except Exception as e:
            return self.format_error_response(e)


# Registry of all sheets tool handlers
SHEETS_HANDLERS = [
    ReadRangeHandler,
    WriteRangeHandler,
    AppendDataHandler,
    ClearRangeHandler,
    CreateSpreadsheetHandler,
    BatchGetValuesHandler,
    BatchUpdateValuesHandler,
    FindReplaceHandler,
    RenameSpreadsheetHandler,
    GetSheetFormulasHandler,
    FindCellsHandler,
]

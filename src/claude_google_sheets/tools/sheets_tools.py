"""Google Sheets API tools for data manipulation and sheet management."""

import json
import logging
from typing import Any, Dict, List, Optional

from googleapiclient.errors import HttpError
from mcp.types import TextContent, Tool

from ..auth.oauth_manager import GoogleSheetsAuth
from ..core.exceptions import InvalidRangeError, SheetsAPIError
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


# Registry of all sheets tool handlers
SHEETS_HANDLERS = [
    ReadRangeHandler,
    WriteRangeHandler,
    AppendDataHandler,
    ClearRangeHandler,
]

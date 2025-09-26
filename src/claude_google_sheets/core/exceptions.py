"""Exception classes for Google Sheets MCP server."""

from typing import Optional


class GoogleSheetsMCPError(Exception):
    """Base exception for Google Sheets MCP operations."""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class AuthenticationError(GoogleSheetsMCPError):
    """Raised when authentication fails."""
    pass


class ConfigurationError(GoogleSheetsMCPError):
    """Raised when configuration is invalid."""
    pass


class SheetsAPIError(GoogleSheetsMCPError):
    """Raised when Google Sheets API calls fail."""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[str] = None) -> None:
        super().__init__(message, details)
        self.status_code = status_code


class DriveAPIError(GoogleSheetsMCPError):
    """Raised when Google Drive API calls fail."""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[str] = None) -> None:
        super().__init__(message, details)
        self.status_code = status_code


class SpreadsheetNotFoundError(GoogleSheetsMCPError):
    """Raised when a spreadsheet cannot be found."""
    pass


class SheetNotFoundError(GoogleSheetsMCPError):
    """Raised when a sheet within a spreadsheet cannot be found."""
    pass


class InvalidRangeError(GoogleSheetsMCPError):
    """Raised when an invalid cell range is specified."""
    pass
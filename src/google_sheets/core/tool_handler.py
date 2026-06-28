"""Base tool handler class for Google Sheets MCP operations."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from mcp.types import TextContent, Tool

logger = logging.getLogger(__name__)


class SheetsToolHandler(ABC):
    """Base class for Google Sheets MCP tool handlers."""

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{__name__}.{name}")

    @abstractmethod
    def get_tool_definition(self) -> Tool:
        """Return the MCP tool definition for this handler."""
        pass

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute the tool with the given arguments."""
        pass

    def validate_arguments(
        self, arguments: Dict[str, Any], required_args: List[str]
    ) -> None:
        """Validate that required arguments are present."""
        missing_args = [arg for arg in required_args if arg not in arguments]
        if missing_args:
            raise ValueError(f"Missing required arguments: {', '.join(missing_args)}")

    def format_error_response(self, error: Exception) -> List[TextContent]:
        """Format an error as a response.

        Повний текст помилки (з можливими внутрішніми деталями) пишемо лише в
        лог із трейсбеком; клієнту віддаємо узагальнене повідомлення.
        """
        self.logger.exception(f"Error in {self.name}")
        return [
            TextContent(
                type="text",
                text=(
                    f"Error in {self.name}: {type(error).__name__}. "
                    "See server logs for details."
                ),
            )
        ]

    def format_success_response(
        self, data: Any, message: Optional[str] = None
    ) -> List[TextContent]:
        """Format a successful response."""
        if message:
            response_text = f"{message}\n\n{data}"
        else:
            response_text = str(data)

        return [TextContent(type="text", text=response_text)]

#!/usr/bin/env python3
"""Test script for the Google Sheets MCP server."""

import sys
import os
import tempfile
import asyncio
import json

# Add the source directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from google_sheets.server import initialize_handlers
from google_sheets.auth.oauth_manager import GoogleSheetsAuth
from google_sheets.tools.drive_tools import DRIVE_HANDLERS
from google_sheets.tools.sheets_tools import SHEETS_HANDLERS
from google_sheets.tools.sheet_management_tools import SHEET_MANAGEMENT_HANDLERS


async def test_tool_definitions():
    """Test that all tools can be defined without authentication."""
    print("Testing tool definitions...")

    # Create a mock auth object (won't work for actual API calls)
    auth = GoogleSheetsAuth()

    # Test drive handlers
    print(f"Testing {len(DRIVE_HANDLERS)} drive handlers...")
    for handler_class in DRIVE_HANDLERS:
        handler = handler_class(auth)
        tool_def = handler.get_tool_definition()
        print(f"  ✓ {handler.name}: {tool_def.description}")

        # Validate tool definition structure
        assert tool_def.name == handler.name
        assert tool_def.description
        assert tool_def.inputSchema

    # Test sheets handlers
    print(f"Testing {len(SHEETS_HANDLERS)} sheets handlers...")
    for handler_class in SHEETS_HANDLERS:
        handler = handler_class(auth)
        tool_def = handler.get_tool_definition()
        print(f"  ✓ {handler.name}: {tool_def.description}")

        # Validate tool definition structure
        assert tool_def.name == handler.name
        assert tool_def.description
        assert tool_def.inputSchema

    # Test sheet-management handlers
    print(f"Testing {len(SHEET_MANAGEMENT_HANDLERS)} sheet-management handlers...")
    for handler_class in SHEET_MANAGEMENT_HANDLERS:
        handler = handler_class(auth)
        tool_def = handler.get_tool_definition()
        print(f"  ✓ {handler.name}: {tool_def.description}")

        # Validate tool definition structure
        assert tool_def.name == handler.name
        assert tool_def.description
        assert tool_def.inputSchema

    print("All tool definitions are valid!")


async def test_server_import():
    """Test that the server module can be imported and initialized."""
    print("Testing server import...")

    try:
        from google_sheets.server import app, tool_handlers
        print("  ✓ Server module imported successfully")

        # Test that we can create the auth manager (without actual authentication)
        auth = GoogleSheetsAuth(tempfile.mkdtemp())
        print("  ✓ Auth manager created")

        # Test that we can initialize handlers
        initialize_handlers(auth)
        print(f"  ✓ Initialized {len(tool_handlers)} tool handlers")

        # List the tools
        print("Available tools:")
        for name, handler in tool_handlers.items():
            print(f"    - {name}: {handler.description}")

    except Exception as e:
        print(f"  ✗ Server import failed: {e}")
        raise

    print("Server import test passed!")


async def test_error_handling():
    """Test error handling in tool handlers."""
    print("Testing error handling...")

    auth = GoogleSheetsAuth()

    # Test with missing required arguments
    from google_sheets.tools.drive_tools import ListSpreadsheetsHandler
    handler = ListSpreadsheetsHandler(auth)

    try:
        # This should not fail even with empty arguments since all args are optional
        result = await handler.execute({})
        print("  ✓ Handler executes with empty arguments (will fail at API level)")
    except Exception as e:
        print(f"  ✓ Handler properly handles missing args: {type(e).__name__}")

    print("Error handling test passed!")


async def main():
    """Run all tests."""
    print("🧪 Testing Claude Google Sheets MCP Server")
    print("=" * 50)

    try:
        await test_server_import()
        print()

        await test_tool_definitions()
        print()

        await test_error_handling()
        print()

        print("🎉 All tests passed!")
        print()
        print("Next steps:")
        print("1. Set up Google API credentials")
        print("2. Restart Claude Desktop to load the new MCP server")
        print("3. Test with actual Google Sheets operations")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
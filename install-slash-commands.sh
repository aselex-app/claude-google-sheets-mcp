#!/bin/bash

# Install Google Sheets slash commands for Claude CLI

CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
SLASH_COMMANDS_SOURCE="$(pwd)/slash-commands"

echo "Installing Google Sheets slash commands..."

# Check if Claude config directory exists
if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
    echo "Error: Claude Desktop not found at $CLAUDE_CONFIG_DIR"
    echo "Please install Claude Desktop first"
    exit 1
fi

# Create slash commands directory if it doesn't exist
SLASH_COMMANDS_DIR="$CLAUDE_CONFIG_DIR/slash-commands"
mkdir -p "$SLASH_COMMANDS_DIR"

# Copy slash commands
echo "Copying slash commands..."
for cmd in "$SLASH_COMMANDS_SOURCE"/*; do
    if [ -f "$cmd" ]; then
        cmd_name=$(basename "$cmd")
        cp "$cmd" "$SLASH_COMMANDS_DIR/"
        echo "  ✓ Installed /$cmd_name"
    fi
done

echo ""
echo "✅ Installation complete!"
echo ""
echo "Available slash commands:"
echo "  /list-sheets     - List all your Google Sheets"
echo "  /read-sheet      - Read data from a sheet"
echo "  /write-sheet     - Write data to a sheet"
echo "  /append-sheet    - Append data to a sheet"
echo "  /search-sheets   - Search for sheets"
echo "  /sheet-info      - Get sheet information"
echo "  /find-sheet      - Find sheet by name"
echo "  /clear-range     - Clear data from range"
echo ""
echo "📚 Documentation: See SLASH_COMMANDS.md for detailed usage"
echo ""
echo "🔄 Restart Claude Desktop to activate the new commands"
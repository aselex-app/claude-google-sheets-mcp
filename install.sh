#!/bin/bash

# Installation script for Claude Google Sheets MCP Server (macOS/Linux)

set -e

# Default credentials directory
CREDENTIALS_DIR="${CREDENTIALS_DIR:-$HOME/.config/google-sheets-mcp}"

echo "🚀 Installing Claude Google Sheets MCP Server..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
if [[ "$(printf '%s\n' "3.11" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.11" ]]; then
    echo "❌ Python 3.11+ required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version check passed: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -e .

# Create credentials directory
echo "📁 Creating credentials directory: $CREDENTIALS_DIR"
mkdir -p "$CREDENTIALS_DIR"
chmod 700 "$CREDENTIALS_DIR"

# Detect Claude Desktop config location
if [[ "$OSTYPE" == "darwin"* ]]; then
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
else
    CLAUDE_CONFIG_DIR="$HOME/.config/claude"
fi

CLAUDE_CONFIG_PATH="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Set up Google API credentials in: $CREDENTIALS_DIR"
echo "2. Add to Claude Desktop configuration at: $CLAUDE_CONFIG_PATH"
echo ""
echo "📝 Example configuration:"
cat << EOF
{
  "mcpServers": {
    "google-sheets": {
      "command": "$(pwd)/venv/bin/python",
      "args": [
        "-m",
        "claude_google_sheets.server",
        "--credentials-dir",
        "$CREDENTIALS_DIR"
      ]
    }
  }
}
EOF
echo ""
echo "3. 🔄 Restart Claude Desktop"
echo "4. 🧪 Test with: python test_server.py"

# Ask about slash commands installation
echo ""
read -p "📝 Install slash commands? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    if [ -d "$CLAUDE_CONFIG_DIR" ]; then
        ./install-slash-commands.sh
    else
        echo "⚠️  Claude Desktop directory not found. Install Claude Desktop first."
        echo "   You can run ./install-slash-commands.sh later."
    fi
fi

echo ""
echo "🎉 Setup complete! Restart Claude Desktop to use the new MCP server."
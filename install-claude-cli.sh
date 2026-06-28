#!/bin/bash

# Automated installation script for Claude Google Sheets MCP Server in Claude CLI
# This script handles everything: installation, configuration, authentication, and slash commands

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CREDENTIALS_DIR="${CREDENTIALS_DIR:-$HOME/.config/google-sheets-mcp}"

echo "🚀 Claude Google Sheets MCP Server - Automated Claude CLI Integration"
echo "================================================================================"

# Function to detect Claude CLI config location
detect_claude_config() {
    local config_paths=(
        "$HOME/.config/claude/claude_cli_config.json"
        "$HOME/.claude/claude_cli_config.json"
        "$HOME/Library/Application Support/Claude/claude_cli_config.json"
    )

    for path in "${config_paths[@]}"; do
        if [ -f "$path" ] || [ -d "$(dirname "$path")" ]; then
            echo "$path"
            return 0
        fi
    done

    # Default fallback
    echo "$HOME/.config/claude/claude_cli_config.json"
}

# Function to check if claude CLI is installed
check_claude_cli() {
    if ! command -v claude &> /dev/null; then
        echo "❌ Claude CLI not found. Please install Claude CLI first:"
        echo "   Visit: https://claude.ai/cli"
        exit 1
    fi

    echo "✅ Claude CLI found: $(claude --version)"
}

# Function to install Python dependencies
install_dependencies() {
    echo "📦 Installing Python dependencies..."

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
    source venv/bin/activate
    pip install --upgrade pip
    pip install -e .

    # Create credentials directory
    mkdir -p "$CREDENTIALS_DIR"
    chmod 700 "$CREDENTIALS_DIR"

    echo "✅ Dependencies installed successfully"
}

# Function to configure Claude CLI MCP server
configure_claude_cli() {
    local claude_config_path="$(detect_claude_config)"
    local claude_config_dir="$(dirname "$claude_config_path")"

    echo "📝 Configuring Claude CLI MCP server..."
    echo "   Config location: $claude_config_path"

    # Create config directory if it doesn't exist
    mkdir -p "$claude_config_dir"

    # Backup existing config if it exists
    if [ -f "$claude_config_path" ]; then
        cp "$claude_config_path" "${claude_config_path}.backup.$(date +%Y%m%d_%H%M%S)"
        echo "✅ Backed up existing config"
    fi

    # Merge configuration using Python.
    #
    # ВАЖЛИВО: дані (шлях до конфіга, шлях до python) передаються через
    # змінні оточення, а наявний конфіг читається всередині Python із файлу.
    # Жодні значення НЕ інтерполюються у тіло скрипта — це унеможливлює
    # ін'єкцію коду через вміст конфіга чи спецсимволи у шляхах.
    CLAUDE_CONFIG_PATH="$claude_config_path" \
    MCP_PYTHON="$SCRIPT_DIR/venv/bin/python" \
    python3 - <<'EOF'
import json
import os
import sys

config_path = os.environ["CLAUDE_CONFIG_PATH"]
mcp_python = os.environ["MCP_PYTHON"]

try:
    if os.path.exists(config_path):
        with open(config_path) as f:
            existing = json.load(f)
    else:
        existing = {}

    if not isinstance(existing, dict):
        raise ValueError("Existing config is not a JSON object")

    existing.setdefault("mcpServers", {})
    existing["mcpServers"]["google-sheets"] = {
        "command": mcp_python,
        "args": ["-m", "google_sheets.server"],
    }

    with open(config_path, "w") as f:
        json.dump(existing, f, indent=2)

    print("✅ Claude CLI configuration updated")

except Exception as e:
    print(f"❌ Failed to update config: {e}")
    sys.exit(1)
EOF
}

# Function to install slash commands
install_slash_commands() {
    echo "📝 Installing slash commands..."

    # Detect Claude CLI slash commands directory
    local slash_commands_dir="$HOME/.claude/slash-commands"

    # Try alternative locations
    if [ ! -d "$(dirname "$slash_commands_dir")" ]; then
        slash_commands_dir="$HOME/.config/claude/slash-commands"
    fi

    mkdir -p "$slash_commands_dir"

    # Copy slash commands
    local commands_copied=0
    if [ -d "$SCRIPT_DIR/slash-commands" ]; then
        for cmd in "$SCRIPT_DIR/slash-commands"/*; do
            if [ -f "$cmd" ]; then
                cmd_name=$(basename "$cmd")
                cp "$cmd" "$slash_commands_dir/"
                echo "  ✓ Installed /$cmd_name"
                ((commands_copied++))
            fi
        done
    fi

    if [ $commands_copied -eq 0 ]; then
        echo "⚠️  No slash commands found to install"
    else
        echo "✅ Installed $commands_copied slash commands"
    fi
}

# Function to run authentication setup
setup_authentication() {
    echo "🔐 Setting up authentication..."

    source venv/bin/activate

    if python3 -m google_sheets.server --setup; then
        echo "✅ Authentication setup completed"
        return 0
    else
        echo "⚠️  Authentication setup was skipped or failed"
        echo "   You can run it later with: google-sheets-mcp --setup"
        return 1
    fi
}

# Function to test the installation
test_installation() {
    echo "🧪 Testing installation..."

    source venv/bin/activate

    # Test server startup (dry run)
    if python3 test_server.py > /dev/null 2>&1; then
        echo "✅ Server test passed"
    else
        echo "⚠️  Server test failed - this may be due to authentication"
        echo "   Run: google-sheets-mcp --setup"
    fi
}

# Show help
show_help() {
    cat << EOF
Claude Google Sheets MCP Server - Automated Installation

USAGE:
    ./install-claude-cli.sh [OPTIONS]

OPTIONS:
    --auto, -y    Run in automatic mode (skip prompts)
    --help, -h    Show this help message

DESCRIPTION:
    This script automates the complete installation and setup of the Google Sheets
    MCP server for Claude CLI, including:

    • Python dependencies installation
    • Claude CLI MCP server configuration
    • Slash commands installation (/list-sheets, /read-sheet, etc.)
    • Interactive authentication setup (OAuth/Service Account/ADC)
    • Installation testing and validation

EXAMPLES:
    ./install-claude-cli.sh           # Interactive installation
    ./install-claude-cli.sh --auto    # Automatic installation (skip auth setup)

For more information, see README.md
EOF
}

# Main installation flow
main() {
    # Handle help option
    if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
        show_help
        exit 0
    fi

    echo
    echo "This script will:"
    echo "  1. ✅ Install Python dependencies"
    echo "  2. ⚙️  Configure Claude CLI MCP server"
    echo "  3. 📝 Install slash commands"
    echo "  4. 🔐 Set up authentication (interactive)"
    echo "  5. 🧪 Test the installation"
    echo

    # Check for non-interactive mode
    if [[ "$1" == "--auto" ]] || [[ "$1" == "-y" ]]; then
        echo "🔄 Running in automatic mode..."
    else
        read -p "Continue with automatic installation? (Y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            echo "Installation cancelled."
            exit 0
        fi
    fi

    # Step 1: Check Claude CLI
    check_claude_cli

    # Step 2: Install dependencies
    install_dependencies

    # Step 3: Configure Claude CLI
    configure_claude_cli

    # Step 4: Install slash commands
    install_slash_commands

    # Step 5: Authentication setup (optional)
    echo
    if [[ "$1" == "--auto" ]] || [[ "$1" == "-y" ]]; then
        echo "⏭️  Skipping authentication setup in automatic mode"
        echo "   Run later with: google-sheets-mcp --setup"
    else
        read -p "🔐 Run authentication setup now? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            setup_authentication
        else
            echo "⏭️  Skipping authentication setup"
            echo "   You can run it later with: google-sheets-mcp --setup"
        fi
    fi

    # Step 6: Test installation
    test_installation

    echo
    echo "🎉 Installation Complete!"
    echo
    echo "📋 What was installed:"
    echo "  ✅ Google Sheets MCP Server"
    echo "  ✅ Claude CLI configuration"
    echo "  ✅ Slash commands (/list-sheets, /read-sheet, etc.)"
    if [ -f "$CREDENTIALS_DIR/token.json" ] || [ -f "$CREDENTIALS_DIR/service-account.json" ]; then
        echo "  ✅ Authentication configured"
    else
        echo "  ⚠️  Authentication not configured (run: google-sheets-mcp --setup)"
    fi
    echo
    echo "🚀 Ready to use! Try these commands:"
    echo "  • List my spreadsheets"
    echo "  • /list-sheets"
    echo "  • Read data from my Budget sheet"
    echo
    echo "📚 Documentation: README.md and SLASH_COMMANDS.md"
}

# Run main function
main "$@"
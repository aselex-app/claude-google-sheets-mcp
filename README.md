# Claude Google Sheets MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

A comprehensive Model Context Protocol (MCP) server for Google Sheets integration with Claude. This server provides intuitive access to Google Sheets operations, including spreadsheet discovery, data manipulation, and formatting - specifically optimized for Claude CLI.

## ✨ Features

### 🔍 **Spreadsheet Discovery**
- **List all spreadsheets** in your Google Drive
- **Advanced search** with filters (name, owner, date, sharing status)
- **Detailed metadata** about any spreadsheet
- **Find sheets by name** with partial matching

### 📊 **Data Operations**
- **Read data** from any range with multiple format options
- **Write data** to specific ranges with type inference
- **Append rows** safely without overwriting existing data
- **Clear ranges** with confirmation safeguards

### 🚀 **Claude CLI Optimized**
- **Natural language commands** - "List my budget spreadsheets"
- **Slash commands** for power users - `/list-sheets`, `/read-sheet`, etc.
- **Interactive workflows** with guided prompts
- **Rich formatted responses** with direct web links

### 🔐 **Robust Authentication**
- **Multiple auth methods**: OAuth 2.0, Service Account, Application Default
- **Automatic token refresh** and secure caching
- **Reuses existing Google Workspace credentials**
- **No credential storage** in the MCP server

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Claude Desktop installed
- Google Cloud Project with Sheets and Drive APIs enabled
- Google API credentials (OAuth or Service Account)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ryanrobson/claude-google-sheets-mcp.git
   cd claude-google-sheets-mcp
   ```

2. **Install the server**:
   ```bash
   ./install.sh
   ```

3. **Set up Google API credentials** (see [Authentication](#authentication) section)

4. **Add to Claude Desktop configuration**:
   ```json
   {
     "mcpServers": {
       "google-sheets": {
         "command": "/path/to/claude-google-sheets-mcp/venv/bin/python",
         "args": [
           "-m",
           "claude_google_sheets.server",
           "--credentials-dir",
           "/path/to/your/credentials"
         ]
       }
     }
   }
   ```

5. **Install slash commands** (optional but recommended):
   ```bash
   ./install-slash-commands.sh
   ```

6. **Restart Claude Desktop**

## 📖 Usage

### Natural Language Commands

Once configured, interact with Google Sheets using natural language:

```
List all my spreadsheets
Read data from range A1:C10 in my Budget spreadsheet
Write this sales data to my Q4 Results sheet
Search for spreadsheets containing 'project' in the name
Get information about my expense tracking sheet
```

### Slash Commands (Power User)

For faster access to common operations:

- **`/list-sheets`** - List all your Google Sheets
- **`/read-sheet`** - Read data from a sheet range
- **`/write-sheet`** - Write data to a sheet range
- **`/append-sheet`** - Append new rows to a sheet
- **`/search-sheets`** - Search sheets with advanced filters
- **`/sheet-info`** - Get detailed sheet information
- **`/find-sheet`** - Find sheet by name
- **`/clear-range`** - Clear data from range (with confirmation)

📚 **See [SLASH_COMMANDS.md](SLASH_COMMANDS.md) for detailed usage guide**

## 🔐 Authentication

### Option 1: OAuth 2.0 (Recommended for personal use)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sheets API and Google Drive API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download `credentials.json` to your credentials directory

### Option 2: Service Account (Recommended for server/team use)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a service account
3. Download the service account key as `service-account.json`
4. Share your spreadsheets with the service account email

### Option 3: Application Default Credentials

Use `gcloud auth application-default login` if you have Google Cloud SDK installed.

## 🛠️ Available Tools

The MCP server exposes these tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_spreadsheets` | List all Google Sheets | max_results, query, include_shared |
| `search_spreadsheets` | Advanced spreadsheet search | name_contains, owner_email, created_after, etc. |
| `get_spreadsheet_info` | Get detailed metadata | spreadsheet_id |
| `read_range` | Read data from range | spreadsheet_id, range, value_render_option |
| `write_range` | Write data to range | spreadsheet_id, range, values, value_input_option |
| `append_data` | Append rows to sheet | spreadsheet_id, range, values |
| `clear_range` | Clear data from range | spreadsheet_id, range |

## 🏗️ Architecture

```
claude-google-sheets-mcp/
├── src/claude_google_sheets/
│   ├── auth/                 # Authentication management
│   ├── tools/               # MCP tool implementations
│   ├── core/                # Base classes and utilities
│   └── server.py            # Main MCP server
├── slash-commands/          # Claude CLI slash commands
├── tests/                   # Test suite
└── docs/                    # Documentation
```

## 🧪 Development

### Setup Development Environment

```bash
git clone https://github.com/ryanrobson/claude-google-sheets-mcp.git
cd claude-google-sheets-mcp
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Run Tests

```bash
python test_server.py
```

### Code Quality

```bash
black src/
isort src/
flake8 src/
mypy src/
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `python test_server.py`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📋 Roadmap

- [ ] **Formatting tools** - Cell formatting, colors, borders
- [ ] **Chart creation** - Generate charts from data
- [ ] **Batch operations** - Multiple operations in single request
- [ ] **Sheet management** - Create, delete, rename sheets
- [ ] **Collaboration features** - Comments, suggestions
- [ ] **Advanced formulas** - Formula manipulation and analysis
- [ ] **Export/Import** - CSV, Excel, PDF export
- [ ] **Webhook support** - Real-time change notifications

## 🔒 Security & Privacy

- **No data storage**: This server doesn't store your spreadsheet data
- **Credential security**: Uses Google's official authentication libraries
- **Minimal permissions**: Requests only necessary API scopes
- **Local processing**: All operations performed locally
- **Audit trail**: All API calls logged for debugging

See [SECURITY.md](SECURITY.md) for detailed security information.

## 📊 Comparison with Other Solutions

| Feature | This MCP Server | Google Sheets API | Other MCP Servers |
|---------|----------------|-------------------|-------------------|
| Spreadsheet Discovery | ✅ Full Drive integration | ❌ Requires sheet IDs | ❌ Limited or none |
| Claude CLI Optimized | ✅ Purpose-built | ❌ Generic API | ⚠️ Basic integration |
| Slash Commands | ✅ 8 commands included | ❌ None | ❌ None |
| Authentication Options | ✅ Multiple methods | ✅ Standard OAuth | ⚠️ Varies |
| Error Handling | ✅ User-friendly | ❌ Technical errors | ⚠️ Varies |
| Interactive Workflows | ✅ Guided prompts | ❌ None | ❌ None |

## 🆘 Troubleshooting

### Common Issues

**"Spreadsheet not found"**
- Use `/list-sheets` to see available spreadsheets
- Check spreadsheet sharing permissions
- Verify the spreadsheet ID is correct

**"Authentication failed"**
- Check your credentials file exists and is valid
- Ensure APIs are enabled in Google Cloud Console
- Verify the credentials directory path

**"Invalid range"**
- Use A1 notation (e.g., "A1:C10", "Sheet1!A1:C10")
- Check that the range exists in the spreadsheet
- Include sheet name if the spreadsheet has multiple tabs

### Getting Help

1. Check the [Issues](https://github.com/ryanrobson/claude-google-sheets-mcp/issues) page
2. Review [SLASH_COMMANDS.md](SLASH_COMMANDS.md) for usage examples
3. Enable debug logging: `--debug` flag
4. Join discussions in the repository

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Anthropic** for Claude and the Model Context Protocol
- **Google** for the Sheets and Drive APIs
- **MCP Community** for tools and inspiration
- **Contributors** who help improve this project

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/ryanrobson/claude-google-sheets-mcp/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ryanrobson/claude-google-sheets-mcp/discussions)
- 📖 **Documentation**: [Wiki](https://github.com/ryanrobson/claude-google-sheets-mcp/wiki)

---

**Made with ❤️ for the Claude and MCP community**
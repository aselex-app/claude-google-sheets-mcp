# Claude Google Sheets MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

A comprehensive Model Context Protocol (MCP) server for Google Sheets integration with Claude. This server provides intuitive access to **26 tools** covering spreadsheet discovery, data manipulation, sheet (tab) management, batch operations, and formatting — specifically optimized for Claude CLI.

**🚀 One-command installation with full Claude CLI automation!**

## ✨ Features

### 🔍 **Spreadsheet Discovery**
- **List all spreadsheets** in your Google Drive
- **Advanced search** with filters (name, owner, date, sharing status)
- **Detailed metadata** about any spreadsheet
- **Find cells by value** inside a spreadsheet (read-only)

### 📊 **Data Operations**
- **Read data** from any range with multiple format options
- **Read formulas** (not just computed values)
- **Write data** to specific ranges with type inference
- **Append rows** safely without overwriting existing data
- **Clear ranges** with confirmation safeguards
- **Batch read / write** multiple ranges in a single request
- **Find & replace** across a sheet or the whole spreadsheet

### 🗂️ **Spreadsheet & Sheet Management**
- **Create spreadsheets** (optionally with named tabs)
- **Rename** a spreadsheet (the whole file)
- **Create / delete / rename / duplicate** sheets (tabs)
- **Copy a sheet** into another spreadsheet
- **Insert / delete** rows and columns

### 🎨 **Formatting & Structure**
- **Format cells** — bold, italic, font size, colors, number format, alignment
- **Conditional formatting** — colour cells when a condition is met
- **Data validation** — dropdown (one-of-list) rules
- **Sort ranges** by one or more columns

### 🚀 **Fully Automated Setup**
- **One-command installation** - Complete Claude CLI integration in minutes
- **Automatic configuration** - No manual JSON editing required
- **8 slash commands included** - `/list-sheets`, `/read-sheet`, `/write-sheet`, etc.
- **Universal authentication** - Works with any Google account type
- **Smart detection** - Automatically finds and configures Claude CLI

### 🔐 **Universal Authentication**
- **Works with any Google account type**: Personal, GCP, Google Workspace/GSuite
- **Interactive setup wizard** for guided authentication configuration
- **Multiple auth methods**: OAuth 2.0, Service Account, Application Default Credentials
- **Automatic token refresh** and secure caching
- **Smart account detection** and permission checking

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Claude CLI installed
- A Google account (personal, GCP, or Google Workspace/GSuite)

### Installation

#### 🔥 **One-Command Setup (Recommended)**

For completely automated installation including Claude CLI configuration, slash commands, and authentication setup:

```bash
git clone https://github.com/aselex-app/google-sheets-mcp.git
cd google-sheets-mcp
./install-claude-cli.sh
```

This script will:
- ✅ Install all dependencies
- ⚙️ Automatically configure Claude CLI
- 📝 Install all 8 slash commands
- 🔐 Guide you through authentication setup
- 🧪 Test the installation

#### **Manual Installation**

If you prefer step-by-step control:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/aselex-app/google-sheets-mcp.git
   cd google-sheets-mcp
   ```

2. **Install the server**:
   ```bash
   ./install.sh
   ```

3. **Run the interactive setup wizard**:
   ```bash
   source venv/bin/activate
   google-sheets-mcp --setup
   ```

4. **Add to Claude CLI configuration** (manual):
   ```json
   {
     "mcpServers": {
       "google-sheets": {
         "command": "/path/to/google-sheets-mcp/venv/bin/python",
         "args": [
           "-m",
           "google_sheets.server"
         ]
       }
     }
   }
   ```

5. **Install slash commands** (optional):
   ```bash
   ./install-slash-commands.sh
   ```

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

The Google Sheets MCP server supports **all Google account types** and provides an interactive setup wizard to guide you through the authentication process.

### Requested OAuth Scopes (Least Privilege)

This server follows the **principle of least privilege** and requests only the
minimum scopes needed to work with spreadsheets:

| Scope | Why it's needed |
|-------|-----------------|
| `openid`, `userinfo.email` | Identify the authenticated account |
| `…/auth/spreadsheets` | **Read and write** any spreadsheet you have access to |
| `…/auth/drive.metadata.readonly` | List/search spreadsheets and read their metadata |

> ⚠️ This server **does not** request the broad `…/auth/drive` scope. It can
> read and write your spreadsheets, but it **cannot** read, modify, or delete
> any other (non-spreadsheet) files in your Google Drive. The consent screen
> will reflect exactly these limited permissions.

### Quick Setup (Recommended)

Run the interactive setup wizard:

```bash
google-sheets-mcp --setup
```

The wizard will:
- Detect your account type (Personal, Google Workspace, or GCP)
- Guide you through the appropriate authentication method
- Test your configuration to ensure everything works
- Provide troubleshooting tips if needed

### Authentication Methods

#### 🔐 OAuth 2.0 (Best for personal use)
- Access your personal Google Sheets
- Requires one-time Google Cloud project setup
- Interactive browser-based authentication
- Automatic token refresh

#### 🤖 Service Account (Best for automation/server use)
- Non-interactive authentication for scripts
- Requires sharing sheets with service account email
- Ideal for team/organization deployments

#### 🌐 Application Default Credentials (Best for GCP users)
- Uses existing `gcloud` authentication
- Perfect if you're already using Google Cloud Platform
- Quick setup with: `gcloud auth application-default login --scopes="https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive.metadata.readonly"`

### Manual Setup (Advanced)

If you prefer manual configuration, see the setup wizard prompts for detailed instructions, or place your credentials in `~/.config/google-sheets-mcp/`:

- **OAuth**: `credentials.json` (from Google Cloud Console)
- **Service Account**: `service-account.json` (service account key)
- **Application Default**: Use `gcloud auth application-default login`

## 🛠️ Available Tools

The MCP server exposes **26 tools**. **Bold** parameters are required; the rest
are optional. All tools work within the least-privilege scopes (`spreadsheets` +
`drive.metadata.readonly`) — no full Drive access is ever required.

> 💡 **Tip for ranges & indices:** ranges use A1 notation (e.g. `Sheet1!A1:C10`).
> Row/column **indices are 0-based**, and end indices are **exclusive** (a header
> on the first row is `start_row=0, end_row=1`).

### 🔍 Discovery (Drive)

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_spreadsheets` | List Google Sheets in your Drive | max_results, query, include_shared |
| `search_spreadsheets` | Advanced spreadsheet search | name_contains, owner_email, created_after, modified_after, shared_only, max_results |
| `get_spreadsheet_info` | Get detailed metadata (sheets, sizes, owners) | **spreadsheet_id** |

### 📊 Data operations (Sheets)

| Tool | Description | Parameters |
|------|-------------|------------|
| `read_range` | Read data from a range | **spreadsheet_id**, **range**, value_render_option, date_time_render_option |
| `write_range` | Write data to a range (overwrites) | **spreadsheet_id**, **range**, **values**, value_input_option |
| `append_data` | Append rows to the end of a sheet | **spreadsheet_id**, **range**, **values**, value_input_option, insert_data_option |
| `clear_range` | Clear data from a range | **spreadsheet_id**, **range** |
| `batch_get_values` | Read several ranges in one request | **spreadsheet_id**, **ranges**, value_render_option |
| `batch_update_values` | Write several ranges in one request | **spreadsheet_id**, **data** (list of `{range, values}`), value_input_option |
| `get_sheet_formulas` | Read the formulas (not computed values) | **spreadsheet_id**, **range** |
| `find_cells` | Find cells matching a query (read-only) | **spreadsheet_id**, **query**, sheet_name, case_sensitive, match_entire_cell, max_results |
| `find_replace` | Find & replace text (mutates data) | **spreadsheet_id**, **find**, **replacement**, sheet_name, match_case, match_entire_cell, search_by_regex |

### 🗂️ Spreadsheet & sheet (tab) management

| Tool | Description | Parameters |
|------|-------------|------------|
| `create_spreadsheet` | Create a new spreadsheet | **title**, sheet_titles |
| `rename_spreadsheet` | Rename the whole file | **spreadsheet_id**, **new_title** |
| `list_sheets` | List all tabs inside a spreadsheet | **spreadsheet_id** |
| `create_sheet` | Create a new tab | **spreadsheet_id**, **title**, index, row_count, column_count |
| `delete_sheet` | Delete a tab | **spreadsheet_id**, **sheet_name** |
| `rename_sheet` | Rename a tab | **spreadsheet_id**, **sheet_name**, **new_name** |
| `duplicate_sheet` | Duplicate a tab within the file | **spreadsheet_id**, **sheet_name**, new_name, insert_index |
| `copy_sheet_to` | Copy a tab into another spreadsheet | **source_spreadsheet_id**, **source_sheet_name**, **destination_spreadsheet_id** |
| `insert_dimension` | Insert rows or columns | **spreadsheet_id**, **sheet_name**, **dimension** (`ROWS`/`COLUMNS`), **start_index**, count, inherit_from_before |
| `delete_dimension` | Delete rows or columns | **spreadsheet_id**, **sheet_name**, **dimension** (`ROWS`/`COLUMNS`), **start_index**, count |

### 🎨 Formatting & structure

| Tool | Description | Parameters |
|------|-------------|------------|
| `format_cells` | Bold/italic/size/colors/number format/alignment | **spreadsheet_id**, **sheet_name**, **start_row**, **end_row**, **start_column**, **end_column**, bold, italic, font_size, background_color, text_color, number_format, number_format_type, horizontal_alignment |
| `add_conditional_format` | Colour cells when a condition is met | **spreadsheet_id**, **sheet_name**, **start_row**, **end_row**, **start_column**, **end_column**, **condition_type**, values, background_color, text_color, bold |
| `set_data_validation` | Dropdown (one-of-list) validation rule | **spreadsheet_id**, **sheet_name**, **start_row**, **end_row**, **start_column**, **end_column**, **values**, strict, show_dropdown |
| `sort_range` | Sort a range by one or more columns | **spreadsheet_id**, **sheet_name**, **start_row**, **end_row**, **start_column**, **end_column**, **sort_specs** (list of `{column_index, order}`) |

> Colors are hex strings (`#RRGGBB`). `number_format` is a pattern such as
> `$#,##0.00`, `0.00%`, or `yyyy-mm-dd`.

## 🏗️ Architecture

```
google-sheets-mcp/
├── src/google_sheets/
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
git clone https://github.com/aselex-app/google-sheets-mcp.git
cd google-sheets-mcp
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

- [x] **Formatting tools** — cell formatting, colors, conditional formatting
- [x] **Batch operations** — multiple ranges in a single request
- [x] **Sheet management** — create, delete, rename, duplicate, copy sheets
- [x] **Data validation** — dropdown rules
- [x] **Sorting** — sort ranges by columns
- [x] **Formula reading** — read formulas, not just values
- [ ] **Chart creation** — generate charts from data
- [ ] **Native Tables API** — typed tables with column types
- [ ] **Collaboration features** — comments, suggestions
- [ ] **Export/Import** — CSV, Excel, PDF export
- [ ] **Webhook support** — real-time change notifications

## 🔒 Security & Privacy

- **No data storage**: This server doesn't store your spreadsheet data
- **Credential security**: Uses Google's official authentication libraries; the
  credentials directory is created with `0700` and `token.json` is written with
  `0600` (owner-only) permissions
- **Least privilege**: Requests only `spreadsheets` (read/write) and
  `drive.metadata.readonly` — never full Drive access
- **Local processing**: All operations performed locally
- **Log hygiene**: Spreadsheet cell data (`values`) is redacted from logs, and
  internal error details are kept in server logs rather than returned to clients
- **Input safety**: User-supplied search terms are escaped before being placed
  into Google Drive queries

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

**"Authentication failed"**
- Run the setup wizard: `google-sheets-mcp --setup`
- For GCP users: Use `gcloud auth application-default login` with proper scopes
- Check that Google Sheets and Drive APIs are enabled in your Google Cloud project

**"Spreadsheet not found"**
- Use `/list-sheets` to see available spreadsheets
- Check spreadsheet sharing permissions (especially for service accounts)
- Verify the spreadsheet ID is correct

**"Invalid range"**
- Use A1 notation (e.g., "A1:C10", "Sheet1!A1:C10")
- Check that the range exists in the spreadsheet
- Include sheet name if the spreadsheet has multiple tabs

**"Insufficient permissions"**
- For Application Default Credentials, ensure you have the right scopes:
  ```bash
  gcloud auth application-default login --scopes="https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive.metadata.readonly"
  ```
- For service accounts, ensure the service account email has been granted access to your spreadsheets

### Getting Help

1. Check the [Issues](https://github.com/aselex-app/google-sheets-mcp/issues) page
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

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/aselex-app/google-sheets-mcp/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/aselex-app/google-sheets-mcp/discussions)
- 📖 **Documentation**: [Wiki](https://github.com/aselex-app/google-sheets-mcp/wiki)

---

**Made with ❤️ for the Claude and MCP community**
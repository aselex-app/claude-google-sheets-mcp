# Usage Examples

This document provides practical examples of using the Claude Google Sheets MCP Server.

## 🚀 Getting Started Examples

### First Time Setup

```bash
# Clone and install
git clone https://github.com/ryanrobson/claude-google-sheets-mcp.git
cd claude-google-sheets-mcp
./install.sh

# Install slash commands
./install-slash-commands.sh

# Test the installation
python test_server.py
```

## 📋 Natural Language Examples

### Basic Operations

**List all spreadsheets:**
```
User: List all my Google Sheets
Claude: I'll list all your Google Sheets for you.
[Shows list of spreadsheets with names, IDs, and last modified dates]
```

**Read data from a sheet:**
```
User: Read data from range A1:C10 in my Budget spreadsheet
Claude: I'll read the data from range A1:C10 in your Budget spreadsheet.
[Shows formatted table with the data]
```

**Write data to a sheet:**
```
User: Write this sales data to my Q4 Results sheet:
Product,Sales,Profit
Widget A,1000,200
Widget B,1500,300

Claude: I'll write this sales data to your Q4 Results sheet.
Which range should I write to?
User: A1:C3
Claude: [Confirms and writes the data]
```

### Advanced Operations

**Search for specific sheets:**
```
User: Find all spreadsheets with "project" in the name that were modified this month
Claude: I'll search for spreadsheets containing "project" modified this month.
[Shows filtered results]
```

**Get detailed sheet information:**
```
User: Tell me about my expense tracking spreadsheet
Claude: I'll get detailed information about your expense tracking spreadsheet.
[Shows metadata, sheets, structure, etc.]
```

## ⚡ Slash Command Examples

### Basic Commands

**List sheets:**
```
/list-sheets
```
*Output: Shows all your Google Sheets with details*

**Read data:**
```
/read-sheet
Which spreadsheet? Budget 2024
Which range? A1:E20
```
*Output: Formatted table with the data*

**Write data:**
```
/write-sheet
Which spreadsheet? Sales Log
Which range? A1:C3
Data to write: [paste your data]
```
*Output: Confirmation of successful write*

### Advanced Commands

**Search sheets:**
```
/search-sheets
Search criteria: name contains "budget"
```
*Output: All sheets with "budget" in the name*

**Sheet information:**
```
/sheet-info
Spreadsheet ID or name: Expense Tracker
```
*Output: Detailed metadata and structure*

**Append data:**
```
/append-sheet
Which spreadsheet? Daily Sales
Which columns? A:D
Data to append: [new sales records]
```
*Output: Confirmation with new row numbers*

## 🔄 Workflow Examples

### Daily Sales Tracking

1. **Morning - Check yesterday's data:**
   ```
   /read-sheet
   Spreadsheet: Daily Sales
   Range: A:E
   ```

2. **Add new sales:**
   ```
   /append-sheet
   Spreadsheet: Daily Sales
   Columns: A:E
   Data: 2024-09-26,Widget A,5,100,500
   ```

3. **Generate weekly report:**
   ```
   User: Create a summary of this week's sales from my Daily Sales sheet
   ```

### Budget Management

1. **Review current budget:**
   ```
   /sheet-info
   Spreadsheet: Budget 2024
   ```

2. **Update expenses:**
   ```
   /write-sheet
   Spreadsheet: Budget 2024
   Range: Expenses!B15:D15
   Data: Groceries,150,Food
   ```

3. **Check totals:**
   ```
   /read-sheet
   Spreadsheet: Budget 2024
   Range: Summary!A1:C10
   ```

### Project Tracking

1. **Find project sheets:**
   ```
   /search-sheets
   Criteria: name contains "Project Alpha"
   ```

2. **Update task status:**
   ```
   User: Mark task #5 as completed in my Project Alpha timeline
   ```

3. **Generate status report:**
   ```
   User: Create a summary of all incomplete tasks from Project Alpha
   ```

## 🎯 Common Use Cases

### Data Entry

**Scenario**: Adding daily sales data
```bash
# Using natural language
User: Add today's sales data to my sales tracking sheet:
Date: 2024-09-26
Product: Widget Pro
Quantity: 10
Price: 50
Total: 500

# Using slash command
/append-sheet
# Follow prompts to add the data
```

### Data Analysis

**Scenario**: Analyzing monthly expenses
```bash
# Read expense data
/read-sheet
Spreadsheet: Monthly Expenses
Range: A1:F100

# Then ask Claude to analyze
User: Analyze this expense data and show me spending trends by category
```

### Report Generation

**Scenario**: Creating weekly reports
```bash
# Get data from multiple ranges
User: Get my weekly sales data from ranges A1:E7 and summary from G1:I5, then create a weekly report

# Alternative with slash commands
/read-sheet  # Get sales data
/read-sheet  # Get summary data
# Then: "Create a weekly report from this data"
```

## 🔧 Troubleshooting Examples

### Authentication Issues

```bash
# Test authentication
python -c "
from src.claude_google_sheets.auth.oauth_manager import GoogleSheetsAuth
auth = GoogleSheetsAuth('/path/to/credentials')
print(auth.get_user_info())
"
```

### Finding Sheet IDs

```bash
# List all sheets to find IDs
/list-sheets

# Or search by name
/find-sheet
Name: Budget
```

### Debugging API Calls

```bash
# Run with debug logging
python -m claude_google_sheets.server --debug --credentials-dir /path/to/creds
```

## 📊 Data Format Examples

### CSV-style Data Input

```
Product,Sales,Date
Widget A,1000,2024-09-26
Widget B,1500,2024-09-26
Widget C,800,2024-09-26
```

### Table Format

```
| Name     | Department | Salary |
|----------|------------|--------|
| John Doe | Engineering| 75000  |
| Jane Smith| Marketing | 65000  |
```

### Formula Examples

```bash
# Writing formulas
/write-sheet
Range: D2:D10
Data: =B2*C2  # Will be interpreted as formulas
```

## 🔒 Security Examples

### Safe Credential Setup

```bash
# Create secure credential directory
mkdir -p ~/.config/google-sheets-mcp
chmod 700 ~/.config/google-sheets-mcp

# Place credentials securely
cp credentials.json ~/.config/google-sheets-mcp/
chmod 600 ~/.config/google-sheets-mcp/credentials.json
```

### Environment Variables

```bash
# Set up environment
export GOOGLE_CREDENTIALS_DIR="~/.config/google-sheets-mcp"
export GOOGLE_APPLICATION_CREDENTIALS="~/.config/google-sheets-mcp/service-account.json"
```

## 📚 Integration Examples

### With Other MCP Servers

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "/path/to/claude-google-sheets-mcp/venv/bin/python",
      "args": ["-m", "claude_google_sheets.server", "--credentials-dir", "/path/to/creds"]
    },
    "weather": {
      "command": "weather-mcp-server"
    }
  }
}
```

**Workflow**: Get weather data and log it to sheets
```
User: Get today's weather and add it to my weather tracking spreadsheet
```

### Automation Scripts

```python
# Python script example
import asyncio
from claude_google_sheets.tools.sheets_tools import AppendDataHandler
from claude_google_sheets.auth.oauth_manager import GoogleSheetsAuth

async def daily_backup():
    auth = GoogleSheetsAuth("/path/to/creds")
    handler = AppendDataHandler(auth)

    # Add daily backup entry
    await handler.execute({
        "spreadsheet_id": "your-sheet-id",
        "range": "Backups!A:C",
        "values": [["2024-09-26", "Daily Backup", "Completed"]]
    })

asyncio.run(daily_backup())
```

## 🎉 Fun Examples

### Game Score Tracking

```bash
/append-sheet
Spreadsheet: Board Game Scores
Columns: A:D
Data: 2024-09-26,Settlers of Catan,Alice,12
```

### Recipe Ingredient Lists

```bash
/write-sheet
Spreadsheet: Recipe Book
Range: Pancakes!A1:C10
Data:
Ingredient,Amount,Unit
Flour,2,cups
Eggs,2,whole
Milk,1.5,cups
```

### Workout Tracking

```bash
User: Log today's workout in my fitness tracker:
Exercise: Push-ups
Sets: 3
Reps: 15
Date: 2024-09-26
```

---

*These examples demonstrate the flexibility and power of the Claude Google Sheets MCP Server. Start with simple operations and gradually explore more advanced features!*
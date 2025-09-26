# Google Sheets Slash Commands

This document describes all available slash commands for working with Google Sheets through Claude CLI. These commands provide quick access to common spreadsheet operations.

## 📋 Available Commands

### `/list-sheets`
**Purpose**: List all Google Sheets in your Google Drive
**Usage**: `/list-sheets`

Lists your spreadsheets with:
- Sheet names and IDs
- Last modified dates
- Owners and sharing status
- Direct web links
- Sorted by most recent (limit 20)

**Example**:
```
/list-sheets
```

---

### `/read-sheet`
**Purpose**: Read data from a Google Sheet range
**Usage**: `/read-sheet`

Interactive command that asks for:
1. Spreadsheet ID or name
2. Range in A1 notation (e.g., "A1:C10", "Sheet1!A1:C10")

Returns formatted data with row/column counts and readable table format.

**Example**:
```
/read-sheet
# Then provide: "Budget 2024" and "A1:E20"
```

---

### `/write-sheet`
**Purpose**: Write data to a specific range in a Google Sheet
**Usage**: `/write-sheet`

Interactive command for:
1. Target spreadsheet (ID or name)
2. Range to write to
3. Data to write (table/CSV format)

Includes confirmation before writing and shows preview of changes.

**Example**:
```
/write-sheet
# Then provide spreadsheet, range, and data
```

---

### `/append-sheet`
**Purpose**: Append new rows to the end of a Google Sheet
**Usage**: `/append-sheet`

Perfect for adding records to existing data tables:
1. Target spreadsheet (ID or name)
2. Column range (e.g., "A:C", "Sheet1!A:D")
3. Data to append as new rows

Safely adds data without overwriting existing content.

**Example**:
```
/append-sheet
# Then provide: "Sales Log", "A:E", and new sales data
```

---

### `/search-sheets`
**Purpose**: Search for spreadsheets using advanced filters
**Usage**: `/search-sheets`

Search by:
- Name contains text
- Owner email address
- Created after date (YYYY-MM-DD)
- Modified after date (YYYY-MM-DD)
- Only shared spreadsheets

**Example**:
```
/search-sheets
# Then specify: "Find sheets with 'budget' in the name"
```

---

### `/sheet-info`
**Purpose**: Get detailed information about a specific spreadsheet
**Usage**: `/sheet-info`

Provides comprehensive details:
- Basic metadata (name, dates, size)
- Owner and sharing information
- All sheets/tabs with properties
- Grid dimensions and structure
- Direct web links

**Example**:
```
/sheet-info
# Then provide: spreadsheet ID or name
```

---

### `/find-sheet`
**Purpose**: Find a specific sheet by name
**Usage**: `/find-sheet`

Quick way to locate a sheet when you know the name but need the ID:
- Searches by partial name matches
- Shows multiple results if needed
- Provides basic info for selection

**Example**:
```
/find-sheet
# Then provide: "Budget" (finds all sheets with "Budget" in name)
```

---

### `/clear-range`
**Purpose**: Clear data from a specific range
**Usage**: `/clear-range`

⚠️ **DESTRUCTIVE OPERATION** - Use with caution:
1. Target spreadsheet (ID or name)
2. Range to clear (A1 notation)
3. Confirmation required

Permanently removes data from the specified range.

**Example**:
```
/clear-range
# Then provide: spreadsheet and range (with confirmation)
```

---

## 🚀 Quick Start Examples

### Common Workflows:

1. **Find and read your budget sheet**:
   ```
   /find-sheet
   # Enter: "Budget"
   # Then: /read-sheet
   # Enter: [selected sheet ID] and "A1:Z100"
   ```

2. **Add new expense to tracking sheet**:
   ```
   /append-sheet
   # Enter: "Expense Tracker", "A:E"
   # Provide: new expense data
   ```

3. **Search for recent project sheets**:
   ```
   /search-sheets
   # Enter: modified_after: "2024-01-01"
   # And: name_contains: "Project"
   ```

## 📝 Tips for Effective Use

### Range Notation:
- `A1:C10` - Specific range
- `A:C` - Entire columns A through C
- `1:5` - Entire rows 1 through 5
- `Sheet1!A1:C10` - Range in specific sheet

### Best Practices:
1. **Always confirm** before writing or clearing data
2. **Use sheet names** when possible (more readable than IDs)
3. **Preview data** before large operations
4. **Start with small ranges** to test operations
5. **Keep backups** of important data

### Authentication:
- Commands use your existing Google Workspace credentials
- Reuses authentication from `/tmp/mcp-gsuite/`
- Supports multiple auth methods (OAuth, Service Account, etc.)

## 🔧 Advanced Usage

### Combining Commands:
1. Use `/list-sheets` to browse available sheets
2. Use `/find-sheet` to locate specific sheets by name
3. Use `/sheet-info` to understand sheet structure
4. Use `/read-sheet` to examine data before modifications
5. Use `/write-sheet` or `/append-sheet` for data updates

### Error Handling:
- Commands provide clear error messages
- Invalid ranges are caught before execution
- Authentication issues are reported with solutions
- Missing sheets are handled gracefully

## 🛠️ Troubleshooting

### Common Issues:

1. **"Spreadsheet not found"**
   - Use `/list-sheets` to see available sheets
   - Check spelling of sheet names
   - Verify you have access to the sheet

2. **"Invalid range"**
   - Use A1 notation (e.g., "A1:C10")
   - Include sheet name if multiple tabs
   - Check that range exists in the sheet

3. **"Authentication failed"**
   - Ensure Google credentials are set up
   - Check `/tmp/mcp-gsuite/` directory
   - Restart Claude Desktop if needed

### Getting Help:
- Each command provides interactive guidance
- Error messages include specific solutions
- Commands confirm operations before execution

---

*These slash commands are powered by the Claude Google Sheets MCP server and provide seamless integration with your Google Workspace through Claude CLI.*
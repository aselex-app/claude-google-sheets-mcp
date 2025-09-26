---
name: Slash Command Request
about: Request a new slash command for Claude CLI
title: '[SLASH] '
labels: ['enhancement', 'slash-command']
assignees: ''
---

## ⚡ Slash Command Request

### 📝 Command Name
What should the slash command be called?
*Example: `/format-currency` or `/create-pivot-table`*

### 🎯 Purpose
What should this slash command do?

### 🔄 User Interaction
Describe the expected user workflow:

1. User types `/your-command`
2. Claude asks for: [parameter 1, parameter 2, etc.]
3. User provides: [example inputs]
4. Claude performs: [action]
5. User sees: [expected output]

### 📊 Example Usage
Provide a realistic example of how this command would be used:

```
User: /format-currency
Claude: Which spreadsheet would you like to format? (ID or name)
User: Budget 2024
Claude: Which range should I format as currency?
User: B2:B100
Claude: Formatting range B2:B100 as currency in "Budget 2024"...
✅ Successfully formatted 99 cells as currency ($)
```

### 🛠️ Underlying MCP Tools
Which existing MCP tools would this slash command use?
- [ ] `list_spreadsheets`
- [ ] `search_spreadsheets`
- [ ] `get_spreadsheet_info`
- [ ] `read_range`
- [ ] `write_range`
- [ ] `append_data`
- [ ] `clear_range`
- [ ] New tool needed: [describe]

### 🔒 Safety Considerations
Does this command need any safety features?
- [ ] Confirmation before destructive actions
- [ ] Preview of changes before applying
- [ ] Backup recommendations
- [ ] Data validation
- [ ] Permission checks

### 📋 Similar Commands
Are there similar existing commands? How would this be different?

### 🎁 User Benefit
How would this improve the user experience compared to natural language commands?

### ✅ Checklist
- [ ] I have searched existing slash commands to avoid duplicates
- [ ] I have provided a clear example of the user workflow
- [ ] I have considered safety and security implications
- [ ] The command name follows existing naming conventions
- [ ] This would provide value over natural language commands
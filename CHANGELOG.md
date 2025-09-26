# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Claude Google Sheets MCP Server
- Full Google Sheets API integration with 7 core tools
- Google Drive API integration for spreadsheet discovery
- 8 slash commands for Claude CLI
- Multiple authentication methods (OAuth, Service Account, Application Default)
- Comprehensive documentation and examples
- Cross-platform installation scripts
- Security and privacy documentation
- CI/CD pipeline with GitHub Actions

### Tools Added
- `list_spreadsheets` - List all Google Sheets in Drive
- `search_spreadsheets` - Advanced spreadsheet search with filters
- `get_spreadsheet_info` - Detailed spreadsheet metadata
- `read_range` - Read data from sheet ranges
- `write_range` - Write data to sheet ranges
- `append_data` - Append rows to sheets
- `clear_range` - Clear data from ranges

### Slash Commands Added
- `/list-sheets` - Quick spreadsheet listing
- `/read-sheet` - Interactive data reading
- `/write-sheet` - Interactive data writing
- `/append-sheet` - Safe data appending
- `/search-sheets` - Advanced spreadsheet search
- `/sheet-info` - Detailed sheet information
- `/find-sheet` - Find sheets by name
- `/clear-range` - Safe data clearing

## [0.1.0] - 2024-09-26

### Added
- Initial project setup
- Core MCP server implementation
- Basic authentication system
- Initial tool implementations
- Project documentation

### Security
- Implemented secure credential handling
- Added input validation and sanitization
- Secure token management
- Minimal API permission requests

---

## Release Notes Template

### [X.Y.Z] - YYYY-MM-DD

### Added
- New features and tools

### Changed
- Modifications to existing functionality

### Deprecated
- Features that will be removed in future versions

### Removed
- Features removed in this version

### Fixed
- Bug fixes

### Security
- Security improvements and vulnerability fixes
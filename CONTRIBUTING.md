# Contributing to Claude Google Sheets MCP Server

Thank you for your interest in contributing! This document provides guidelines for contributing to the Claude Google Sheets MCP Server project.

## 🚀 Quick Start for Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/claude-google-sheets-mcp.git
   cd claude-google-sheets-mcp
   ```
3. **Set up development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
5. **Make your changes and test**
6. **Submit a pull request**

## 🎯 Ways to Contribute

### 🐛 Bug Reports
- Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md)
- Include steps to reproduce, expected vs actual behavior
- Provide environment details (Python version, OS, etc.)
- Include relevant logs with `--debug` flag enabled

### ✨ Feature Requests
- Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md)
- Describe the problem you're solving
- Explain your proposed solution
- Consider implementation complexity and compatibility

### 📝 Documentation
- Fix typos, improve clarity, add examples
- Update README.md, SLASH_COMMANDS.md, or code docstrings
- Create tutorials or guides
- Improve API documentation

### 🔧 Code Contributions
- New MCP tools or slash commands
- Performance improvements
- Security enhancements
- Bug fixes
- Test coverage improvements

## 🏗️ Development Guidelines

### Code Style

We use Python's standard tools for code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Code Standards

- **Python 3.11+** - Use modern Python features
- **Type hints** - All functions should have type annotations
- **Docstrings** - Use Google-style docstrings
- **Error handling** - Graceful error handling with user-friendly messages
- **Logging** - Use the standard logging module
- **Security** - Follow security best practices for credential handling

### Project Structure

```
src/claude_google_sheets/
├── auth/                    # Authentication management
│   ├── __init__.py
│   └── oauth_manager.py     # Google OAuth handling
├── tools/                   # MCP tool implementations
│   ├── __init__.py
│   ├── drive_tools.py       # Google Drive operations
│   └── sheets_tools.py      # Google Sheets operations
├── core/                    # Base classes and utilities
│   ├── __init__.py
│   ├── exceptions.py        # Custom exception classes
│   └── tool_handler.py      # Base tool handler class
└── server.py               # Main MCP server
```

### Adding New Tools

1. **Create tool handler class** in appropriate module:
   ```python
   class YourToolHandler(SheetsToolHandler):
       def __init__(self, auth: GoogleSheetsAuth) -> None:
           super().__init__(
               name="your_tool_name",
               description="What your tool does"
           )
           self.auth = auth

       def get_tool_definition(self) -> Tool:
           # Define the MCP tool schema
           pass

       async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
           # Implement the tool logic
           pass
   ```

2. **Add to the handler registry** in the appropriate `HANDLERS` list

3. **Write tests** for your new tool

4. **Update documentation** - Add to README.md and create slash command if applicable

### Testing

- **Unit tests** - Test individual components
- **Integration tests** - Test with real Google Sheets API (optional)
- **Error handling** - Test error conditions and edge cases

Run tests:
```bash
python test_server.py
```

### Adding Slash Commands

1. **Create command file** in `slash-commands/` directory
2. **Follow existing patterns** - Interactive, user-friendly prompts
3. **Include safety checks** - Confirmations for destructive operations
4. **Update documentation** - Add to SLASH_COMMANDS.md
5. **Test the command** with Claude CLI

## 🧪 Testing Your Changes

### Local Testing

1. **Install your changes**:
   ```bash
   pip install -e .
   ```

2. **Run the test suite**:
   ```bash
   python test_server.py
   ```

3. **Test with Claude Desktop**:
   - Update your Claude Desktop config to point to your development version
   - Restart Claude Desktop
   - Test your changes with actual Google Sheets

### Test Checklist

- [ ] Code passes all existing tests
- [ ] New functionality has tests
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Slash commands work correctly (if applicable)
- [ ] Error handling is robust
- [ ] Security considerations addressed

## 📋 Pull Request Process

### Before Submitting

1. **Update your branch** with the latest main:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run quality checks**:
   ```bash
   black src/ tests/
   isort src/ tests/
   flake8 src/ tests/
   mypy src/
   python test_server.py
   ```

3. **Update documentation** if needed

### PR Guidelines

- **Clear title** - Summarize what the PR does
- **Detailed description** - Explain the problem and solution
- **Link issues** - Reference any related issues
- **Screenshots** - Include for UI/UX changes
- **Breaking changes** - Clearly mark any breaking changes

### PR Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] I have tested this with Claude CLI
- [ ] New and existing unit tests pass locally with my changes

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
```

## 🏷️ Issue Labels

We use these labels to organize issues and PRs:

- **`bug`** - Something isn't working
- **`enhancement`** - New feature or request
- **`documentation`** - Improvements or additions to documentation
- **`good first issue`** - Good for newcomers
- **`help wanted`** - Extra attention is needed
- **`security`** - Security-related issues
- **`performance`** - Performance improvements
- **`slash-command`** - Related to slash commands
- **`api`** - Google Sheets/Drive API related
- **`auth`** - Authentication related

## 🔒 Security

- **Never commit credentials** - Use `.gitignore` and environment variables
- **Validate inputs** - Sanitize and validate all user inputs
- **Follow least privilege** - Request minimal API permissions
- **Report security issues** privately via email to the maintainers

## 🌟 Recognition

Contributors will be:
- **Listed in README.md** acknowledgments
- **Mentioned in release notes** for significant contributions
- **Given contributor status** for ongoing contributions

## 📞 Getting Help

- **GitHub Discussions** - General questions and ideas
- **GitHub Issues** - Bug reports and feature requests
- **Code review** - Ask for help in PR comments
- **Discord** - Join the MCP community Discord (link in README)

## 📚 Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Google Drive API Documentation](https://developers.google.com/drive/api)
- [Claude Desktop Documentation](https://docs.anthropic.com/claude/desktop)

## 🎉 First-Time Contributors

Welcome! Here are some good first issues to start with:

- Documentation improvements
- Adding examples to README
- Writing tests for existing functionality
- Improving error messages
- Adding input validation

Look for issues labeled `good first issue` to get started.

Thank you for contributing to the Claude Google Sheets MCP Server! 🚀
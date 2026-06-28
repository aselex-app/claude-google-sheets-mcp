# Security Policy

## 🔒 Security Overview

The Claude Google Sheets MCP Server is designed with security and privacy as core principles. This document outlines our security practices, supported versions, and how to report security vulnerabilities.

## 🛡️ Security Features

### Data Protection
- **No data storage**: The MCP server never stores your spreadsheet data locally
- **No credential storage**: Credentials are handled by Google's official libraries
- **Local processing**: All operations are performed locally on your machine
- **Minimal permissions**: Requests only necessary Google API scopes
- **Secure communication**: All API calls use HTTPS/TLS encryption

### Authentication Security
- **Official Google libraries**: Uses Google's official Python client libraries
- **OAuth 2.0 standards**: Implements standard OAuth 2.0 flows
- **Token management**: Secure token storage and automatic refresh
- **Multiple auth methods**: Supports OAuth, Service Account, and Application Default Credentials
- **Scope limitation**: Requests minimal required API permissions

### API Security
- **Input validation**: All user inputs are validated and sanitized
- **Error handling**: Prevents information leakage through error messages
- **Rate limiting**: Respects Google API rate limits
- **Audit logging**: All API calls are logged for debugging (no sensitive data)

## 🔑 Required Permissions

The MCP server requests these Google API scopes:

```python
SHEETS_SCOPES = [
    "openid",                                           # Basic authentication
    "https://www.googleapis.com/auth/userinfo.email",   # User identification
    "https://www.googleapis.com/auth/spreadsheets",     # Google Sheets access
    "https://www.googleapis.com/auth/drive",            # Google Drive access
    "https://www.googleapis.com/auth/drive.file",       # File-specific access
    "https://www.googleapis.com/auth/drive.readonly",   # Read-only Drive access
]
```

### Scope Justification
- **`spreadsheets`**: Required for reading/writing sheet data
- **`drive`**: Needed to list and search for spreadsheets
- **`drive.file`**: Allows access to files created by the application
- **`drive.readonly`**: Enables read-only operations on existing files
- **`userinfo.email`**: Used for authentication verification only

## 🔐 Credential Management

### Recommended Practices
1. **Use Service Accounts** for production/team environments
2. **Use OAuth 2.0** for personal development
3. **Store credentials securely** outside the project directory
4. **Never commit credentials** to version control
5. **Rotate credentials regularly** according to your security policy

### Credential Storage Locations
```bash
# Recommended credential directory structure
~/.config/google-sheets-mcp/
├── credentials.json         # OAuth client secrets
├── token.json              # OAuth access tokens (auto-generated)
└── service-account.json    # Service account key (if used)
```

### Environment Variables
```bash
# Alternative: Use environment variables
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
export GOOGLE_CREDENTIALS_DIR="/path/to/credentials"
```

## 🚨 Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | ✅ Yes             |
| < 0.1   | ❌ No              |

## 🔍 Security Vulnerabilities

### Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

To report a security vulnerability, please email:
- **Email**: [security@example.com] (replace with actual email)
- **Subject**: "Security Vulnerability in Claude Google Sheets MCP"

Include the following information:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Any suggested fixes or mitigations

### Response Timeline
- **Initial Response**: Within 48 hours
- **Investigation**: Within 7 days
- **Fix Development**: Within 30 days (depending on severity)
- **Public Disclosure**: After fix is released

### Vulnerability Assessment Criteria

#### Critical (CVSS 9.0-10.0)
- Remote code execution
- Credential theft
- Data exfiltration at scale

#### High (CVSS 7.0-8.9)
- Privilege escalation
- Authentication bypass
- Sensitive data exposure

#### Medium (CVSS 4.0-6.9)
- Information disclosure
- Denial of service
- Input validation issues

#### Low (CVSS 0.1-3.9)
- Configuration issues
- Non-exploitable bugs
- Minor information leaks

## 🛠️ Security Best Practices for Users

### Installation Security
```bash
# Verify package integrity
pip install google-sheets-mcp --verify-ssl

# Use virtual environments
python -m venv mcp-env
source mcp-env/bin/activate

# Keep dependencies updated
pip install --upgrade google-sheets-mcp
```

### Configuration Security
```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "/full/path/to/python",
      "args": [
        "-m", "google_sheets.server",
        "--credentials-dir", "/secure/path/to/credentials"
      ]
    }
  }
}
```

### Operational Security
1. **Regular updates**: Keep the MCP server updated
2. **Monitor access**: Review Google account activity regularly
3. **Limit sharing**: Don't share credentials or tokens
4. **Secure systems**: Keep your operating system and Python updated
5. **Network security**: Use secure networks for API calls

## 🔒 Privacy Considerations

### Data Handling
- **No telemetry**: The server doesn't send usage data anywhere
- **Local processing**: All operations happen on your local machine
- **Google's privacy**: Subject to Google's privacy policy for API usage
- **Logging**: Only technical logs, no user data

### User Rights
- **Data portability**: Your data remains in your Google account
- **Access control**: You control all access permissions
- **Deletion rights**: Uninstall removes all local components
- **Transparency**: Open source code for full transparency

## 🔧 Security Configuration

### Enable Debug Logging (for security investigation)
```bash
python -m google_sheets.server --debug --credentials-dir /path/to/creds
```

### Restrict File Permissions
```bash
# Secure credential files
chmod 600 ~/.config/google-sheets-mcp/credentials.json
chmod 600 ~/.config/google-sheets-mcp/token.json
chmod 600 ~/.config/google-sheets-mcp/service-account.json

# Secure credential directory
chmod 700 ~/.config/google-sheets-mcp/
```

### Network Security
```bash
# Verify TLS connections (for advanced users)
export PYTHONHTTPSVERIFY=1
export SSL_CERT_FILE=$(python -m certifi)
```

## 🚨 Incident Response

### If You Suspect a Security Issue
1. **Immediately revoke** Google API credentials
2. **Change passwords** for affected Google accounts
3. **Check access logs** in Google Cloud Console
4. **Report the incident** using our security contact
5. **Document everything** for investigation

### Google Account Security
- Enable 2FA on your Google account
- Review authorized applications regularly
- Monitor account activity
- Use strong, unique passwords

## 📋 Security Checklist

### For Users
- [ ] Credentials stored securely outside project directory
- [ ] File permissions set correctly (600 for files, 700 for directories)
- [ ] Google account has 2FA enabled
- [ ] Regular review of authorized applications
- [ ] MCP server kept up to date
- [ ] Using latest Python version

### For Developers
- [ ] Code follows secure coding practices
- [ ] Input validation implemented
- [ ] Error handling doesn't leak information
- [ ] Dependencies regularly updated
- [ ] Security tests included
- [ ] Credentials never committed to git

## 📚 Security Resources

- [Google Cloud Security Best Practices](https://cloud.google.com/security/best-practices)
- [OAuth 2.0 Security Best Practices](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)
- [Python Security Guide](https://python-security.readthedocs.io/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## 🔄 Security Updates

Security updates will be:
- **Announced** in GitHub releases
- **Documented** in CHANGELOG.md
- **Tagged** with severity level
- **Backported** to supported versions when possible

Subscribe to [GitHub releases](https://github.com/ryanrobson/google-sheets-mcp/releases) to stay informed about security updates.

---

**Last Updated**: 2024-09-26
**Next Review**: 2024-12-26
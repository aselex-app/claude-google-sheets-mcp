# Installation script for Claude Google Sheets MCP Server (Windows)

param(
    [string]$CredentialsDir = "$env:USERPROFILE\.config\google-sheets-mcp"
)

Write-Host "Installing Claude Google Sheets MCP Server for Windows..." -ForegroundColor Green

# Check Python version
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.1[1-9]") {
    Write-Host "✓ Python version check passed: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python 3.11+ required. Found: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment and install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
pip install -e .

# Create credentials directory
if (!(Test-Path $CredentialsDir)) {
    Write-Host "Creating credentials directory: $CredentialsDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $CredentialsDir -Force | Out-Null
}

# Get Claude Desktop config path
$claudeConfigDir = "$env:APPDATA\Claude"
$claudeConfigPath = "$claudeConfigDir\claude_desktop_config.json"

Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Set up Google API credentials in: $CredentialsDir"
Write-Host "2. Add to Claude Desktop configuration at: $claudeConfigPath"
Write-Host ""
Write-Host "Example configuration:" -ForegroundColor Cyan
Write-Host @"
{
  "mcpServers": {
    "google-sheets": {
      "command": "$((Get-Location).Path)\venv\Scripts\python.exe",
      "args": [
        "-m",
        "claude_google_sheets.server",
        "--credentials-dir",
        "$CredentialsDir"
      ]
    }
  }
}
"@
Write-Host ""
Write-Host "3. Restart Claude Desktop"
Write-Host "4. Test with: python test_server.py"

# Optionally install slash commands
$installSlash = Read-Host "Install slash commands? (Y/n)"
if ($installSlash -ne "n" -and $installSlash -ne "N") {
    if (Test-Path "$claudeConfigDir") {
        $slashDir = "$claudeConfigDir\slash-commands"
        if (!(Test-Path $slashDir)) {
            New-Item -ItemType Directory -Path $slashDir -Force | Out-Null
        }

        Write-Host "Installing slash commands..." -ForegroundColor Yellow
        Copy-Item "slash-commands\*" -Destination $slashDir -Force
        Write-Host "✓ Slash commands installed to: $slashDir" -ForegroundColor Green
    } else {
        Write-Host "Claude Desktop not found. Install Claude Desktop first." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎉 Setup complete! Restart Claude Desktop to use the new MCP server." -ForegroundColor Green
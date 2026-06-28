"""Interactive setup wizard for Google Sheets MCP server."""

import json
import logging
import os
import subprocess
import sys
import webbrowser
from typing import Optional

import click

from .auth.oauth_manager import DEFAULT_CREDENTIALS_DIR, GoogleSheetsAuth


class SetupWizard:
    """Interactive setup wizard for Google Sheets authentication."""

    def __init__(self, credentials_dir: Optional[str] = None):
        self.credentials_dir = credentials_dir or DEFAULT_CREDENTIALS_DIR
        os.makedirs(self.credentials_dir, exist_ok=True)

    def run(self) -> bool:
        """Run the interactive setup wizard."""
        click.echo("🔧 Google Sheets MCP Server Setup Wizard")
        click.echo("=" * 50)
        click.echo()

        # Check if already set up
        if self._check_existing_setup():
            if not click.confirm("Authentication is already configured. Reconfigure?"):
                return True

        click.echo("This wizard will help you set up authentication for Google Sheets.")
        click.echo()

        # Determine setup method
        setup_method = self._choose_setup_method()

        if setup_method == "oauth":
            return self._setup_oauth()
        elif setup_method == "service_account":
            return self._setup_service_account()
        elif setup_method == "default":
            return self._setup_default_credentials()
        else:
            click.echo("❌ Setup cancelled.")
            return False

    def _check_existing_setup(self) -> bool:
        """Check if authentication is already configured."""
        try:
            auth = GoogleSheetsAuth(self.credentials_dir)
            auth.authenticate()
            click.echo("✅ Authentication is already configured and working!")
            return True
        except Exception as e:
            # Очікувано на першому запуску (креденшіалів ще немає) — не шумимо в
            # консоль, але лишаємо слід для діагностики.
            logging.getLogger(__name__).debug(
                f"No working auth found during setup check: {e}"
            )
            return False

    def _choose_setup_method(self) -> str:
        """Let user choose authentication method."""
        click.echo("Choose your authentication method:")
        click.echo()
        click.echo("1. 🔐 OAuth 2.0 (Recommended for personal use)")
        click.echo("   - Access your personal Google Sheets")
        click.echo("   - Requires Google Cloud project setup")
        click.echo()
        click.echo("2. 🤖 Service Account (For automation/server use)")
        click.echo("   - Non-interactive authentication")
        click.echo("   - Requires sharing sheets with service account")
        click.echo()
        click.echo("3. 🌐 Application Default Credentials (If using GCP)")
        click.echo("   - Uses gcloud authentication")
        click.echo("   - May have limited permissions")
        click.echo()

        while True:
            choice = click.prompt("Select option (1-3)", type=int)
            if choice == 1:
                return "oauth"
            elif choice == 2:
                return "service_account"
            elif choice == 3:
                return "default"
            else:
                click.echo("❌ Invalid choice. Please select 1, 2, or 3.")

    def _setup_oauth(self) -> bool:
        """Set up OAuth 2.0 authentication."""
        click.echo()
        click.echo("🔐 Setting up OAuth 2.0 Authentication")
        click.echo("-" * 40)
        click.echo()

        credentials_path = os.path.join(self.credentials_dir, "credentials.json")

        if os.path.exists(credentials_path):
            click.echo(f"✅ OAuth credentials found at {credentials_path}")
        else:
            click.echo("📋 You need to create OAuth 2.0 credentials:")
            click.echo()
            click.echo("1. Go to Google Cloud Console")
            click.echo("2. Create a new project or select existing")
            click.echo("3. Enable Google Sheets API and Google Drive API")
            click.echo("4. Create OAuth 2.0 credentials (Desktop application)")
            click.echo("5. Download credentials.json")
            click.echo()

            if click.confirm("Open Google Cloud Console now?"):
                webbrowser.open("https://console.cloud.google.com/")

            click.echo()
            click.echo(f"📁 Save your credentials.json file to: {credentials_path}")

            while not os.path.exists(credentials_path):
                click.pause("Press any key after saving credentials.json...")
                if not os.path.exists(credentials_path):
                    click.echo(f"❌ File not found at {credentials_path}")
                    if not click.confirm("Try again?"):
                        return False

        # Test OAuth flow
        click.echo()
        click.echo("🔓 Testing OAuth authentication...")

        try:
            auth = GoogleSheetsAuth(self.credentials_dir)
            auth.authenticate()

            click.echo("✅ OAuth authentication successful!")

            # Try to get user info
            try:
                user_info = auth.get_user_info()
                email = user_info.get("email", "Unknown")
                click.echo(f"📧 Authenticated as: {email}")
            except Exception:
                click.echo("📧 Authentication successful (user info not available)")

            return True

        except Exception as e:
            click.echo(f"❌ OAuth setup failed: {str(e)}")
            return False

    def _setup_service_account(self) -> bool:
        """Set up service account authentication."""
        click.echo()
        click.echo("🤖 Setting up Service Account Authentication")
        click.echo("-" * 45)
        click.echo()

        service_account_path = os.path.join(
            self.credentials_dir, "service-account.json"
        )

        if os.path.exists(service_account_path):
            click.echo(f"✅ Service account found at {service_account_path}")
        else:
            click.echo("📋 You need to create a service account:")
            click.echo()
            click.echo("1. Go to Google Cloud Console")
            click.echo("2. Create a service account")
            click.echo("3. Download the service account key")
            click.echo("4. Share your spreadsheets with the service account email")
            click.echo()

            if click.confirm("Open Google Cloud Console now?"):
                webbrowser.open("https://console.cloud.google.com/iam-admin/serviceaccounts")

            click.echo()
            click.echo(f"📁 Save your service account key as: {service_account_path}")

            while not os.path.exists(service_account_path):
                click.pause("Press any key after saving service-account.json...")
                if not os.path.exists(service_account_path):
                    click.echo(f"❌ File not found at {service_account_path}")
                    if not click.confirm("Try again?"):
                        return False

        # Test service account
        click.echo()
        click.echo("🔓 Testing service account authentication...")

        try:
            auth = GoogleSheetsAuth(self.credentials_dir)
            auth.authenticate()

            click.echo("✅ Service account authentication successful!")

            # Show service account email
            try:
                with open(service_account_path) as f:
                    sa_data = json.load(f)
                    sa_email = sa_data.get("client_email", "Unknown")
                    click.echo(f"📧 Service account: {sa_email}")
                    click.echo()
                    click.echo(
                        f"💡 Remember to share your spreadsheets with: {sa_email}"
                    )
            except Exception:
                pass

            return True

        except Exception as e:
            click.echo(f"❌ Service account setup failed: {str(e)}")
            return False

    def _setup_default_credentials(self) -> bool:
        """Set up application default credentials."""
        click.echo()
        click.echo("🌐 Setting up Application Default Credentials")
        click.echo("-" * 45)
        click.echo()

        click.echo("This will use your existing gcloud authentication.")
        click.echo()

        # Check if gcloud is available. subprocess з list-аргументами не запускає
        # shell, тож немає ризику shell-ін'єкції; також не залежимо від $PATH-трюків.
        def _run_gcloud(cmd_args: list) -> subprocess.CompletedProcess:
            return subprocess.run(
                ["gcloud", *cmd_args],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        try:
            if _run_gcloud(["--version"]).returncode != 0:
                raise FileNotFoundError
        except (FileNotFoundError, OSError):
            click.echo("❌ gcloud CLI not found. Please install Google Cloud SDK.")
            return False

        # Check if authenticated
        auth_check = _run_gcloud(
            ["auth", "list", "--filter=status:ACTIVE", "--format=value(account)"]
        )
        if auth_check.returncode != 0:
            click.echo("❌ No active gcloud authentication found.")
            click.echo("Run: gcloud auth login")
            return False

        click.echo("🔓 Testing application default credentials...")

        try:
            auth = GoogleSheetsAuth(self.credentials_dir)
            auth.authenticate()

            click.echo("✅ Application default credentials working!")

            # Check permissions
            permissions = auth.check_permissions()
            available_perms = [k for k, v in permissions.items() if v]

            if available_perms:
                click.echo(f"📊 Available permissions: {', '.join(available_perms)}")
            else:
                click.echo("⚠️  Limited permissions detected.")
                click.echo("You may need to enable Google Sheets/Drive APIs in your GCP project.")

            return True

        except Exception as e:
            click.echo(f"❌ Default credentials failed: {str(e)}")
            click.echo("You may need to run: gcloud auth application-default login")
            return False


@click.command()
@click.option(
    "--credentials-dir",
    default=None,
    help="Directory to store credentials",
    type=click.Path(),
)
def setup_command(credentials_dir: Optional[str]):
    """Run the interactive setup wizard."""
    wizard = SetupWizard(credentials_dir)
    success = wizard.run()

    if success:
        click.echo()
        click.echo("🎉 Setup completed successfully!")
        click.echo()
        click.echo("You can now use the Google Sheets MCP server:")
        click.echo("  google-sheets-mcp")
        click.echo()
        click.echo("Or in Claude CLI:")
        click.echo("  'List my recent spreadsheets'")
        sys.exit(0)
    else:
        click.echo()
        click.echo("❌ Setup failed. Please try again.")
        sys.exit(1)


if __name__ == "__main__":
    setup_command()
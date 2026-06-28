"""OAuth2 authentication manager for Google Sheets and Drive APIs."""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from ..core.exceptions import AuthenticationError, ConfigurationError

logger = logging.getLogger(__name__)

# Required Google API scopes for Sheets and Drive access.
#
# Принцип найменших привілеїв: сервер працює лише з таблицями, тож йому НЕ
# потрібен повний доступ до Drive. `drive.metadata.readonly` достатньо для
# list/search/get_spreadsheet_info (читання метаданих файлів), а `spreadsheets`
# покриває читання/запис самих даних таблиць.
SHEETS_SCOPES = [
    # Basic authentication
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    # Google Sheets API (read/write cell data)
    "https://www.googleapis.com/auth/spreadsheets",
    # Google Drive API — лише метадані для пошуку/переліку таблиць
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]

# Default credentials directory
DEFAULT_CREDENTIALS_DIR = os.path.expanduser("~/.config/google-sheets-mcp")


def _write_secret_file(path: str, content: str) -> None:
    """Записати чутливий файл (токен) з правами 0600 — лише власник."""
    # O_CREAT з режимом 0600 застосовує права лише при створенні файлу,
    # тож на наявному файлі додатково виставляємо chmod.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
    finally:
        try:
            os.chmod(path, 0o600)
        except OSError as e:
            logger.warning(f"Could not set permissions on {path}: {e}")


class GoogleSheetsAuth:
    """Manages authentication for Google Sheets and Drive APIs."""

    def __init__(self, credentials_dir: Optional[str] = None) -> None:
        self.credentials_dir = credentials_dir or os.getenv(
            "GOOGLE_CREDENTIALS_DIR", DEFAULT_CREDENTIALS_DIR
        )
        # Ensure credentials directory exists with owner-only permissions (0700).
        os.makedirs(self.credentials_dir, mode=0o700, exist_ok=True)
        # makedirs не змінює права вже наявного каталогу — підстраховуємось.
        try:
            os.chmod(self.credentials_dir, 0o700)
        except OSError as e:
            logger.warning(f"Could not set permissions on credentials dir: {e}")
        self.credentials: Optional[Credentials] = None
        self._services: Dict[str, Any] = {}

    def authenticate(self) -> Credentials:
        """Authenticate using available methods and return credentials."""
        if self.credentials and self.credentials.valid:
            return self.credentials

        # Track authentication attempts for better error reporting
        auth_attempts = []

        # Method 1: Try existing OAuth token file
        try:
            self.credentials = self._load_oauth_token()
            if self.credentials:
                logger.info("Successfully authenticated using cached OAuth token")
                return self.credentials
            auth_attempts.append("OAuth token: Not found or invalid")
        except Exception as e:
            auth_attempts.append(f"OAuth token: {str(e)}")

        # Method 2: Try service account credentials
        try:
            self.credentials = self._load_service_account()
            if self.credentials:
                logger.info("Successfully authenticated using service account")
                return self.credentials
            auth_attempts.append("Service account: Not found or invalid")
        except Exception as e:
            auth_attempts.append(f"Service account: {str(e)}")

        # Method 3: Try application default credentials
        try:
            self.credentials = self._load_default_credentials()
            if self.credentials:
                logger.info(
                    "Successfully authenticated using application default credentials"
                )
                return self.credentials
            auth_attempts.append("Application default credentials: Not available")
        except Exception as e:
            auth_attempts.append(f"Application default credentials: {str(e)}")

        # Method 4: Interactive OAuth flow
        try:
            self.credentials = self._run_oauth_flow()
            if self.credentials:
                logger.info("Successfully authenticated using interactive OAuth flow")
                return self.credentials
            auth_attempts.append("Interactive OAuth: Failed or not configured")
        except Exception as e:
            auth_attempts.append(f"Interactive OAuth: {str(e)}")

        # If all methods failed, provide helpful error message
        error_message = (
            "No valid authentication method found. Attempted:\n"
            + "\n".join(f"  - {attempt}" for attempt in auth_attempts)
            + "\n\nTo set up authentication, run: google-sheets-mcp --setup"
        )
        raise AuthenticationError(error_message)

    def _load_oauth_token(self) -> Optional[Credentials]:
        """Load OAuth token from saved file."""
        token_path = os.path.join(self.credentials_dir, "token.json")
        if not os.path.exists(token_path):
            return None

        try:
            creds = Credentials.from_authorized_user_file(token_path, SHEETS_SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Save refreshed token with owner-only permissions
                _write_secret_file(token_path, creds.to_json())
            return creds if creds and creds.valid else None
        except Exception as e:
            logger.warning(f"Failed to load OAuth token: {e}")
            return None

    def _load_service_account(self) -> Optional[Credentials]:
        """Load service account credentials."""
        service_account_path = os.path.join(
            self.credentials_dir, "service-account.json"
        )
        if not os.path.exists(service_account_path):
            return None

        try:
            from google.oauth2 import service_account

            creds = service_account.Credentials.from_service_account_file(
                service_account_path, scopes=SHEETS_SCOPES
            )
            return creds
        except Exception as e:
            logger.warning(f"Failed to load service account credentials: {e}")
            return None

    def _load_default_credentials(self) -> Optional[Credentials]:
        """Load application default credentials with proper scopes.

        Свідомо НЕ робимо fallback на `google.auth.default()` без scopes:
        такі креденшіали мають невизначені/неконтрольовані права, що суперечить
        принципу найменших привілеїв і ускладнює діагностику. Якщо ADC не
        вдається отримати з потрібними scopes — повертаємо None.
        """
        try:
            creds, project = google.auth.default(scopes=SHEETS_SCOPES)
            logger.debug(f"Loaded default credentials for project: {project}")
            return creds
        except Exception as e:
            logger.warning(f"Failed to load default credentials with scopes: {e}")
            return None

    def _run_oauth_flow(self) -> Optional[Credentials]:
        """Run interactive OAuth flow."""
        credentials_path = os.path.join(self.credentials_dir, "credentials.json")

        if not os.path.exists(credentials_path):
            logger.warning(
                f"No OAuth credentials file found at {credentials_path}. "
                "Run 'google-sheets-mcp --setup' to configure authentication."
            )
            return None

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SHEETS_SCOPES
            )

            # Try to run local server, fall back to manual flow if needed
            try:
                creds = flow.run_local_server(port=0, open_browser=True)
            except Exception:
                logger.info("Local server auth failed, trying manual flow...")
                creds = flow.run_console()

            # Save token for future use with owner-only permissions
            token_path = os.path.join(self.credentials_dir, "token.json")
            _write_secret_file(token_path, creds.to_json())

            logger.info(f"OAuth token saved to {token_path}")
            return creds
        except Exception as e:
            logger.warning(f"Interactive OAuth flow failed: {e}")
            return None

    def get_service(self, service_name: str, version: str = "v4") -> Any:
        """Get a Google API service instance."""
        service_key = f"{service_name}_{version}"
        if service_key in self._services:
            return self._services[service_key]

        if not self.credentials:
            self.authenticate()

        if not self.credentials:
            raise AuthenticationError("No valid credentials available")

        try:
            service = build(service_name, version, credentials=self.credentials)
            self._services[service_key] = service
            return service
        except Exception as e:
            raise AuthenticationError(
                f"Failed to build {service_name} service: {str(e)}"
            ) from e

    def get_sheets_service(self):
        """Get Google Sheets API service."""
        return self.get_service("sheets", "v4")

    def get_drive_service(self):
        """Get Google Drive API service."""
        return self.get_service("drive", "v3")

    def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information."""
        if not self.credentials:
            self.authenticate()

        try:
            service = self.get_service("oauth2", "v2")
            user_info = service.userinfo().get().execute()
            return user_info
        except Exception as e:
            raise AuthenticationError(f"Failed to get user info: {str(e)}") from e

    def detect_account_type(self) -> str:
        """Detect the type of Google account being used."""
        try:
            user_info = self.get_user_info()
            email = user_info.get("email", "")

            if email.endswith("@gmail.com"):
                return "personal"
            elif email.endswith("@googlemail.com"):
                return "personal"
            elif "." in email and not email.endswith(".gserviceaccount.com"):
                return "workspace"
            elif email.endswith(".gserviceaccount.com"):
                return "service_account"
            else:
                return "unknown"
        except Exception as e:
            # If we can't get user info, try to detect from credentials type
            logger.debug(f"Could not fetch user info for account detection: {e}")
            if hasattr(self.credentials, "service_account_email"):
                return "service_account"
            elif hasattr(self.credentials, "refresh_token"):
                return "oauth"
            else:
                return "unknown"

    def check_permissions(self) -> Dict[str, bool]:
        """Check what permissions are available with current credentials."""
        permissions = {
            "drive_read": False,
            "drive_write": False,
            "sheets_read": False,
            "sheets_write": False,
        }

        try:
            # Test Drive API access (read-only: ми тримаємо лише
            # drive.metadata.readonly, тож drive_write свідомо лишається False).
            drive_service = self.get_drive_service()
            try:
                drive_service.files().list(pageSize=1).execute()
                permissions["drive_read"] = True
            except Exception as e:
                logger.debug(f"Drive read permission check failed: {e}")

            # Sheets: точно перевірити запис без конкретного sheet ID не можна.
            # Якщо сервіс будується і Drive-метадані доступні — вважаємо, що
            # scope `spreadsheets` (read+write) активний.
            self.get_sheets_service()
            if permissions["drive_read"]:
                permissions["sheets_read"] = True
                permissions["sheets_write"] = True

        except Exception as e:
            logger.debug(f"Permission check failed: {e}")

        return permissions

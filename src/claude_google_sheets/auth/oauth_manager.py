"""OAuth2 authentication manager for Google Sheets and Drive APIs."""

import json
import logging
import os
from typing import Dict, List, Optional, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.auth

from ..core.exceptions import AuthenticationError, ConfigurationError

logger = logging.getLogger(__name__)

# Required Google API scopes for Sheets and Drive access
SHEETS_SCOPES = [
    # Basic authentication
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",

    # Google Sheets API
    "https://www.googleapis.com/auth/spreadsheets",

    # Google Drive API (for listing and managing spreadsheets)
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
]


class GoogleSheetsAuth:
    """Manages authentication for Google Sheets and Drive APIs."""

    def __init__(self, credentials_dir: Optional[str] = None) -> None:
        self.credentials_dir = credentials_dir or os.getenv("GOOGLE_CREDENTIALS_DIR", ".")
        self.credentials: Optional[Credentials] = None
        self._services: Dict[str, Any] = {}

    def authenticate(self) -> Credentials:
        """Authenticate using available methods and return credentials."""
        if self.credentials and self.credentials.valid:
            return self.credentials

        # Try different authentication methods in order
        try:
            # Method 1: Try existing OAuth token file
            self.credentials = self._load_oauth_token()
            if self.credentials:
                logger.info("Successfully authenticated using cached OAuth token")
                return self.credentials

            # Method 2: Try service account credentials
            self.credentials = self._load_service_account()
            if self.credentials:
                logger.info("Successfully authenticated using service account")
                return self.credentials

            # Method 3: Try application default credentials
            self.credentials = self._load_default_credentials()
            if self.credentials:
                logger.info("Successfully authenticated using application default credentials")
                return self.credentials

            # Method 4: Interactive OAuth flow
            self.credentials = self._run_oauth_flow()
            if self.credentials:
                logger.info("Successfully authenticated using interactive OAuth flow")
                return self.credentials

            raise AuthenticationError("No valid authentication method found")

        except Exception as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}") from e

    def _load_oauth_token(self) -> Optional[Credentials]:
        """Load OAuth token from saved file."""
        token_path = os.path.join(self.credentials_dir, "token.json")
        if not os.path.exists(token_path):
            return None

        try:
            creds = Credentials.from_authorized_user_file(token_path, SHEETS_SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Save refreshed token
                with open(token_path, 'w') as token_file:
                    token_file.write(creds.to_json())
            return creds if creds and creds.valid else None
        except Exception as e:
            logger.warning(f"Failed to load OAuth token: {e}")
            return None

    def _load_service_account(self) -> Optional[Credentials]:
        """Load service account credentials."""
        service_account_path = os.path.join(self.credentials_dir, "service-account.json")
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
        """Load application default credentials."""
        try:
            creds, _ = google.auth.default(scopes=SHEETS_SCOPES)
            return creds
        except Exception as e:
            logger.warning(f"Failed to load default credentials: {e}")
            return None

    def _run_oauth_flow(self) -> Optional[Credentials]:
        """Run interactive OAuth flow."""
        credentials_path = os.path.join(self.credentials_dir, "credentials.json")
        if not os.path.exists(credentials_path):
            logger.warning("No OAuth credentials file found for interactive flow")
            return None

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SHEETS_SCOPES
            )
            creds = flow.run_local_server(port=0)

            # Save token for future use
            token_path = os.path.join(self.credentials_dir, "token.json")
            with open(token_path, 'w') as token_file:
                token_file.write(creds.to_json())

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
            raise AuthenticationError(f"Failed to build {service_name} service: {str(e)}") from e

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
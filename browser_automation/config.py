"""Configuration management for browser automation."""
import os
from dataclasses import dataclass
from typing import Optional

from pydantic import SecretStr


@dataclass
class AppConfig:
    """Application configuration."""

    openai_api_key: Optional[SecretStr]
    chromium_path: str
    base_url: str
    auth_username: Optional[SecretStr]
    auth_password: Optional[SecretStr]
    headless: bool = False
    model: str = "gpt-4o-mini"


class ConfigLoader:
    """Loads configuration from environment variables."""

    @staticmethod
    def from_env() -> AppConfig:
        """Load configuration from environment variables."""
        openai_key = os.getenv("OPENAI_API_KEY")
        auth_username = os.getenv("AUTH_USERNAME")
        auth_password = os.getenv("AUTH_PASSWORD")

        return AppConfig(
            openai_api_key=SecretStr(openai_key) if openai_key else None,
            chromium_path=os.getenv("CHROMIUM_PATH", "/Applications/Chromium.app/Contents/MacOS/Chromium"),
            base_url=os.getenv("BASE_URL", ""),
            auth_username=SecretStr(auth_username) if auth_username else None,
            auth_password=SecretStr(auth_password) if auth_password else None,
            headless=False,
            model="gpt-4o-mini"
        )


class ConfigValidator:
    """Validates configuration."""

    @staticmethod
    def validate(config: AppConfig) -> None:
        """Validate that required configuration is present.

        Args:
            config: The configuration to validate

        Raises:
            ValueError: If required configuration is missing
        """
        errors = []

        if not config.openai_api_key:
            errors.append("OPENAI_API_KEY environment variable is required")

        if not config.base_url:
            errors.append("BASE_URL environment variable is required")

        if not config.auth_username:
            errors.append("AUTH_USERNAME environment variable is required")

        if not config.auth_password:
            errors.append("AUTH_PASSWORD environment variable is required")

        if errors:
            error_message = "Configuration errors:\n" + "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_message)

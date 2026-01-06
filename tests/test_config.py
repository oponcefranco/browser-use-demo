"""Tests for configuration validation."""

import pytest
from pydantic import SecretStr
from task import AppConfig, validate_config


class TestAppConfig:
    """Test AppConfig dataclass."""

    def test_config_creation_with_all_fields(self):
        """Test creating config with all required fields."""
        config = AppConfig(
            openai_api_key=SecretStr("test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass"),
            headless=False,
            model="gpt-4o-mini"
        )
        assert config.openai_api_key.get_secret_value() == "test-key"
        assert config.chromium_path == "/path/to/chromium"
        assert config.base_url == "https://test.com"
        assert config.auth_username.get_secret_value() == "testuser"
        assert config.auth_password.get_secret_value() == "testpass"
        assert config.headless is False
        assert config.model == "gpt-4o-mini"

    def test_config_default_values(self):
        """Test config default values."""
        config = AppConfig(
            openai_api_key=SecretStr("test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass")
        )
        assert config.headless is False
        assert config.model == "gpt-4o-mini"


class TestValidateConfig:
    """Test configuration validation."""

    def test_valid_config_passes(self):
        """Test that valid configuration passes validation."""
        config = AppConfig(
            openai_api_key=SecretStr("test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass")
        )
        # Should not raise any exception
        validate_config(config)

    def test_missing_openai_api_key(self):
        """Test that missing OpenAI API key raises ValueError."""
        config = AppConfig(
            openai_api_key=None,
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass")
        )
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            validate_config(config)

    def test_missing_base_url(self):
        """Test that missing BASE_URL raises ValueError."""
        config = AppConfig(
            openai_api_key=SecretStr("test-key"),
            chromium_path="/path/to/chromium",
            base_url="",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass")
        )
        with pytest.raises(ValueError, match="BASE_URL"):
            validate_config(config)

    def test_missing_username(self):
        """Test that missing username raises ValueError."""
        config = AppConfig(
            openai_api_key=SecretStr("test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=None,
            auth_password=SecretStr("testpass")
        )
        with pytest.raises(ValueError, match="AUTH_USERNAME"):
            validate_config(config)

    def test_missing_password(self):
        """Test that missing password raises ValueError."""
        config = AppConfig(
            openai_api_key=SecretStr("test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=None
        )
        with pytest.raises(ValueError, match="AUTH_PASSWORD"):
            validate_config(config)

    def test_multiple_missing_fields(self):
        """Test that multiple missing fields are all reported."""
        config = AppConfig(
            openai_api_key=None,
            chromium_path="/path/to/chromium",
            base_url="",
            auth_username=None,
            auth_password=None
        )
        with pytest.raises(ValueError) as exc_info:
            validate_config(config)

        error_message = str(exc_info.value)
        assert "OPENAI_API_KEY" in error_message
        assert "BASE_URL" in error_message
        assert "AUTH_USERNAME" in error_message
        assert "AUTH_PASSWORD" in error_message

"""Tests for configuration validation."""

import os
import pytest
from unittest.mock import patch
from pydantic import SecretStr
from browser_automation.config import AppConfig, ConfigValidator, ConfigLoader


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
        assert config.openai_api_key is not None
        assert config.openai_api_key.get_secret_value() == "test-key"
        assert config.chromium_path == "/path/to/chromium"
        assert config.base_url == "https://test.com"
        assert config.auth_username is not None
        assert config.auth_username.get_secret_value() == "testuser"
        assert config.auth_password is not None
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
        ConfigValidator.validate(config)

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
            ConfigValidator.validate(config)

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
            ConfigValidator.validate(config)

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
            ConfigValidator.validate(config)

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
            ConfigValidator.validate(config)

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
            ConfigValidator.validate(config)

        error_message = str(exc_info.value)
        assert "OPENAI_API_KEY" in error_message
        assert "BASE_URL" in error_message
        assert "AUTH_USERNAME" in error_message
        assert "AUTH_PASSWORD" in error_message


class TestConfigLoader:
    """Test configuration loading from environment."""

    def test_load_from_env_all_variables_present(self):
        """Test loading config when all environment variables are set."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test-key-123",
            "CHROMIUM_PATH": "/custom/path/chromium",
            "BASE_URL": "https://test.example.com",
            "AUTH_USERNAME": "testuser",
            "AUTH_PASSWORD": "testpass"
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConfigLoader.from_env()

            assert config.openai_api_key is not None
            assert config.openai_api_key.get_secret_value() == "sk-test-key-123"
            assert config.chromium_path == "/custom/path/chromium"
            assert config.base_url == "https://test.example.com"
            assert config.auth_username is not None
            assert config.auth_username.get_secret_value() == "testuser"
            assert config.auth_password is not None
            assert config.auth_password.get_secret_value() == "testpass"

    def test_load_from_env_missing_openai_key(self):
        """Test loading config without OPENAI_API_KEY."""
        env_vars = {
            "CHROMIUM_PATH": "/path/chromium",
            "BASE_URL": "https://test.com",
            "AUTH_USERNAME": "user",
            "AUTH_PASSWORD": "pass"
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConfigLoader.from_env()
            assert config.openai_api_key is None

    def test_load_from_env_missing_credentials(self):
        """Test loading config without authentication credentials."""
        env_vars = {
            "OPENAI_API_KEY": "sk-key",
            "CHROMIUM_PATH": "/path/chromium",
            "BASE_URL": "https://test.com"
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConfigLoader.from_env()
            assert config.auth_username is None
            assert config.auth_password is None

    def test_load_from_env_default_chromium_path(self):
        """Test that default chromium path is used when not provided."""
        env_vars = {
            "OPENAI_API_KEY": "sk-key",
            "BASE_URL": "https://test.com",
            "AUTH_USERNAME": "user",
            "AUTH_PASSWORD": "pass"
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConfigLoader.from_env()
            # Should use default macOS Chromium path
            assert config.chromium_path == "/Applications/Chromium.app/Contents/MacOS/Chromium"

    def test_load_from_env_empty_base_url(self):
        """Test loading config with empty BASE_URL."""
        env_vars = {
            "OPENAI_API_KEY": "sk-key",
            "CHROMIUM_PATH": "/path/chromium",
            "AUTH_USERNAME": "user",
            "AUTH_PASSWORD": "pass"
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConfigLoader.from_env()
            assert config.base_url == ""

    def test_load_from_env_default_values(self):
        """Test that default values are set correctly."""
        env_vars = {
            "OPENAI_API_KEY": "sk-key",
            "BASE_URL": "https://test.com",
            "AUTH_USERNAME": "user",
            "AUTH_PASSWORD": "pass"
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConfigLoader.from_env()
            assert config.headless is False
            assert config.model == "gpt-4o-mini"

    def test_load_from_env_custom_chromium_path(self):
        """Test loading config with custom chromium path."""
        custom_path = "/usr/local/bin/chromium"
        env_vars = {
            "OPENAI_API_KEY": "sk-key",
            "CHROMIUM_PATH": custom_path,
            "BASE_URL": "https://test.com",
            "AUTH_USERNAME": "user",
            "AUTH_PASSWORD": "pass"
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConfigLoader.from_env()
            assert config.chromium_path == custom_path

    def test_load_from_env_secret_types(self):
        """Test that sensitive values are loaded as SecretStr."""
        env_vars = {
            "OPENAI_API_KEY": "sk-key",
            "BASE_URL": "https://test.com",
            "AUTH_USERNAME": "user",
            "AUTH_PASSWORD": "pass"
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConfigLoader.from_env()

            assert isinstance(config.openai_api_key, SecretStr)
            assert isinstance(config.auth_username, SecretStr)
            assert isinstance(config.auth_password, SecretStr)

    def test_load_from_env_empty_environment(self):
        """Test loading config from completely empty environment."""
        with patch.dict(os.environ, {}, clear=True):
            config = ConfigLoader.from_env()

            assert config.openai_api_key is None
            assert config.auth_username is None
            assert config.auth_password is None
            assert config.base_url == ""
            assert config.chromium_path == "/Applications/Chromium.app/Contents/MacOS/Chromium"
            assert config.headless is False
            assert config.model == "gpt-4o-mini"

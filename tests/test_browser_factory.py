"""Tests for browser factory."""

from unittest.mock import Mock, patch, MagicMock
import pytest
from pydantic import SecretStr

from browser_automation.browser_factory import BrowserFactory
from browser_automation.config import AppConfig


class TestBrowserFactory:
    """Test BrowserFactory class."""

    def test_create_browser_with_default_headless(self):
        """Test creating browser with headless=False."""
        config = AppConfig(
            openai_api_key=SecretStr("test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass"),
            headless=False
        )

        with patch('browser_automation.browser_factory.Browser') as mock_browser_class:
            mock_browser_instance = Mock()
            mock_browser_class.return_value = mock_browser_instance

            browser = BrowserFactory.create_browser(config)

            # Verify Browser was called
            assert mock_browser_class.called
            call_args = mock_browser_class.call_args

            # Verify config was passed with correct headless setting
            assert call_args.kwargs['config'].headless is False
            assert call_args.kwargs['config'].browser_binary_path == "/path/to/chromium"
            assert browser == mock_browser_instance

    def test_create_browser_with_headless_enabled(self):
        """Test creating browser with headless=True."""
        config = AppConfig(
            openai_api_key=SecretStr("test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass"),
            headless=True
        )

        with patch('browser_automation.browser_factory.Browser') as mock_browser_class:
            mock_browser_instance = Mock()
            mock_browser_class.return_value = mock_browser_instance

            browser = BrowserFactory.create_browser(config)

            assert mock_browser_class.called
            call_args = mock_browser_class.call_args
            assert call_args.kwargs['config'].headless is True
            assert browser == mock_browser_instance

    def test_create_browser_with_custom_chromium_path(self):
        """Test creating browser with custom chromium path."""
        custom_path = "/custom/path/to/chromium"
        config = AppConfig(
            openai_api_key=SecretStr("test-key"),
            chromium_path=custom_path,
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass")
        )

        with patch('browser_automation.browser_factory.Browser') as mock_browser_class:
            mock_browser_instance = Mock()
            mock_browser_class.return_value = mock_browser_instance

            BrowserFactory.create_browser(config)

            call_args = mock_browser_class.call_args
            assert call_args.kwargs['config'].browser_binary_path == custom_path

    def test_create_browser_without_chromium_path(self):
        """Test creating browser without chromium path (empty string)."""
        config = AppConfig(
            openai_api_key=SecretStr("test-key"),
            chromium_path="",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass")
        )

        with patch('browser_automation.browser_factory.Browser') as mock_browser_class:
            mock_browser_instance = Mock()
            mock_browser_class.return_value = mock_browser_instance

            BrowserFactory.create_browser(config)

            call_args = mock_browser_class.call_args
            # When chromium_path is empty, browser_binary_path should not be set
            assert not hasattr(call_args.kwargs['config'], 'browser_binary_path') or \
                   call_args.kwargs['config'].browser_binary_path is None

    def test_create_browser_logs_configuration(self):
        """Test that browser creation logs the configuration."""
        config = AppConfig(
            openai_api_key=SecretStr("test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass"),
            headless=True
        )

        with patch('browser_automation.browser_factory.Browser'), \
             patch('browser_automation.browser_factory.logger') as mock_logger:

            BrowserFactory.create_browser(config)

            # Verify logging occurred
            mock_logger.info.assert_called_once()
            log_message = mock_logger.info.call_args[0][0]
            assert "headless=True" in log_message

    def test_create_context_from_browser(self):
        """Test creating browser context from browser instance."""
        mock_browser = Mock()

        with patch('browser_automation.browser_factory.BrowserContext') as mock_context_class:
            mock_context_instance = Mock()
            mock_context_class.return_value = mock_context_instance

            context = BrowserFactory.create_context(mock_browser)

            # Verify BrowserContext was called with correct arguments
            mock_context_class.assert_called_once()
            call_kwargs = mock_context_class.call_args.kwargs
            assert call_kwargs['browser'] == mock_browser
            assert 'config' in call_kwargs
            assert context == mock_context_instance

    def test_create_context_uses_default_config(self):
        """Test that create_context uses BrowserContextConfig."""
        mock_browser = Mock()

        with patch('browser_automation.browser_factory.BrowserContext') as mock_context_class, \
             patch('browser_automation.browser_factory.BrowserContextConfig') as mock_config_class:

            mock_config_instance = Mock()
            mock_config_class.return_value = mock_config_instance

            BrowserFactory.create_context(mock_browser)

            # Verify BrowserContextConfig was instantiated
            mock_config_class.assert_called_once_with()
            # Verify it was passed to BrowserContext
            call_kwargs = mock_context_class.call_args.kwargs
            assert call_kwargs['config'] == mock_config_instance

    def test_browser_factory_methods_are_static(self):
        """Test that BrowserFactory methods can be called without instantiation."""
        # This is a design test - verify we don't need to instantiate the factory
        assert callable(BrowserFactory.create_browser)
        assert callable(BrowserFactory.create_context)

        # Verify these are static methods (can be called on the class)
        config = AppConfig(
            openai_api_key=SecretStr("test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass")
        )

        with patch('browser_automation.browser_factory.Browser'):
            # Should not raise any errors about needing self
            BrowserFactory.create_browser(config)

    def test_create_browser_with_all_config_options(self):
        """Test creating browser with all configuration options set."""
        config = AppConfig(
            openai_api_key=SecretStr("sk-test-key-123"),
            chromium_path="/usr/bin/chromium",
            base_url="https://example.com/login",
            auth_username=SecretStr("admin"),
            auth_password=SecretStr("secure-pass-123"),
            headless=True,
            model="gpt-4o"
        )

        with patch('browser_automation.browser_factory.Browser') as mock_browser_class:
            mock_browser = Mock()
            mock_browser_class.return_value = mock_browser

            result = BrowserFactory.create_browser(config)

            # Verify the browser was created
            assert result == mock_browser
            assert mock_browser_class.called

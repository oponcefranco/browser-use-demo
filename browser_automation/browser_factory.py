"""Factory for creating browser instances."""
import logging

from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext, BrowserContextConfig

from browser_automation.config import AppConfig

logger = logging.getLogger(__name__)


class BrowserFactory:
    """Creates and configures browser instances."""

    @staticmethod
    def create_browser(config: AppConfig) -> Browser:
        """Create a configured browser instance.

        Args:
            config: Application configuration

        Returns:
            Configured Browser instance
        """
        logger.info(f"Configuring browser (headless={config.headless})")

        browser_config = BrowserConfig(headless=config.headless)

        # Only set browser_binary_path if chromium_path is provided
        if config.chromium_path:
            browser_config.browser_binary_path = config.chromium_path

        return Browser(config=browser_config)

    @staticmethod
    def create_context(browser: Browser) -> BrowserContext:
        """Create a browser context.

        Args:
            browser: Browser instance

        Returns:
            BrowserContext instance
        """
        return BrowserContext(
            browser=browser,
            config=BrowserContextConfig()
        )

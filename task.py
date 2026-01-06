"""
Navigate to provided URL and perform task
------------------------------------------
"""

import os
import sys
import logging
import argparse
from dataclasses import dataclass
from typing import Any

from browser_use.browser.context import BrowserContextConfig, BrowserContext
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from langchain_openai import ChatOpenAI
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use import Agent, Controller


# ============ Configuration Section ============
@dataclass
class AppConfig:

    openai_api_key: SecretStr | None
    chromium_path: str
    base_url: str
    auth_username: SecretStr | None
    auth_password: SecretStr | None
    headless: bool = False
    model: str = "gpt-4o-mini"


# Customize these settings
_openai_key = os.getenv("OPENAI_API_KEY")
_auth_username = os.getenv("AUTH_USERNAME")
_auth_password = os.getenv("AUTH_PASSWORD")
_base_url = os.getenv("BASE_URL", "")

config = AppConfig(
    openai_api_key=SecretStr(_openai_key) if _openai_key is not None else None,
    chromium_path=os.getenv("CHROMIUM_PATH", "/Applications/Chromium.app/Contents/MacOS/Chromium"),
    headless=False,
    base_url=_base_url,
    auth_username=SecretStr(_auth_username) if _auth_username is not None else None,
    auth_password=SecretStr(_auth_password) if _auth_password is not None else None
)


def validate_config(config: AppConfig) -> None:
    """Validate that required configuration is present."""
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


def create_agent(browser_config: AppConfig) -> tuple[Agent, BrowserContext]:
    logger.info(f"Initializing agent with model: {browser_config.model}")

    llm = ChatOpenAI(model=browser_config.model, api_key=browser_config.openai_api_key)

    logger.info(f"Configuring browser (headless={browser_config.headless})")

    # Only set browser_binary_path if chromium_path is provided
    if browser_config.chromium_path:
        browser = Browser(
            config=BrowserConfig(
                headless=browser_config.headless,
                browser_binary_path=browser_config.chromium_path,
            )
        )
    else:
        browser = Browser(
            config=BrowserConfig(
                headless=browser_config.headless,
            )
        )

    # Create browser context with default config
    browser_context = BrowserContext(browser=browser, config=BrowserContextConfig())
    controller = Controller()

    # Create the agent with detailed instructions
    username = browser_config.auth_username.get_secret_value() if browser_config.auth_username else ""
    password = browser_config.auth_password.get_secret_value() if browser_config.auth_password else ""

    agent = Agent(
        task=f"""Navigate to the login page and authenticate.

                Here are the specific steps:

                - Go to {browser_config.base_url}
                - See the header (h2) text that says "Test login" (look for attribute: 'id="login"')
                - Find input to Enter Username (look for attribute: 'name="username"')
                    * username value is "{username}"
                - Find input to Enter Password (look for attribute: 'name="password"')
                    * password value is "{password}"
                - Successful login will display the following text, "Logged In Successfully"
                - The "Log out" button should be present and visible

                Important:
                - Wait for each element to load before interacting
                """,
        llm=llm,
        max_actions_per_step=5,
        controller=controller,
        browser_context=browser_context
    )

    return agent, browser_context


async def navigate(agent: Agent, browser_context: BrowserContext) -> Any:
    """Execute the navigation task with the agent."""
    try:
        logger.info("Starting agent navigation task...")
        result = await agent.run(max_steps=25)
        logger.info("Navigation task completed successfully!")
        return result
    except Exception as e:
        logger.error(f"Error during navigation: {str(e)}", exc_info=True)
        raise
    finally:
        # Always close the browser, even if there's an error
        logger.info("Closing browser...")
        await browser_context.close()
        logger.info("Browser closed successfully")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='AI-powered browser automation demo using browser-use framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python task.py                          # Run with default settings from .env
  python task.py --headless               # Run in headless mode
  python task.py --url https://example.com  # Override BASE_URL
  python task.py --headless --url https://example.com  # Combine options

Environment Variables:
  See .env.example for all available configuration options.
        """
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (no visible window)'
    )
    parser.add_argument(
        '--url',
        type=str,
        help='Override BASE_URL from environment variables'
    )
    parser.add_argument(
        '--model',
        type=str,
        help='Override OpenAI model (default: gpt-4o-mini)'
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the browser automation task."""
    try:
        # Parse command-line arguments
        args = parse_arguments()

        # Apply CLI overrides to config
        if args.headless:
            config.headless = True
            logger.info("Headless mode enabled via CLI argument")

        if args.url:
            config.base_url = args.url
            logger.info(f"BASE_URL overridden via CLI: {args.url}")

        if args.model:
            config.model = args.model
            logger.info(f"Model overridden via CLI: {args.model}")

        logger.info("Starting browser automation task...")
        validate_config(config)
        logger.info("Configuration validated successfully")

        agent, browser_context = create_agent(config)
        asyncio.run(navigate(agent, browser_context))

        logger.info("Task completed successfully!")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

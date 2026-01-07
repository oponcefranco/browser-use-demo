"""
Navigate to provided URL and perform task
------------------------------------------
Main entry point for browser automation.
"""
import sys
import logging
import asyncio

from dotenv import load_dotenv

from browser_automation.config import ConfigLoader, ConfigValidator
from browser_automation.browser_factory import BrowserFactory
from browser_automation.agent_factory import AgentFactory
from browser_automation.tasks.login_task import LoginTask
from browser_automation.tasks.base import TaskCredentials
from browser_automation.runner import TaskRunner
from cli import CLI

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point for the browser automation task."""
    try:
        # Parse CLI arguments
        args = CLI.parse_arguments()

        # Load configuration
        config = ConfigLoader.from_env()

        # Apply CLI overrides
        if args.headless:
            config.headless = True
            logger.info("Headless mode enabled via CLI argument")

        if args.url:
            config.base_url = args.url
            logger.info(f"BASE_URL overridden via CLI: {args.url}")

        if args.model:
            config.model = args.model
            logger.info(f"Model overridden via CLI: {args.model}")

        # Validate configuration
        logger.info("Starting browser automation task...")
        ConfigValidator.validate(config)
        logger.info("Configuration validated successfully")

        # Create browser and context
        browser = BrowserFactory.create_browser(config)
        browser_context = BrowserFactory.create_context(browser)

        # Create task
        # Note: Config validation ensures these are not None
        assert config.auth_username is not None, "auth_username should be validated"
        assert config.auth_password is not None, "auth_password should be validated"

        credentials = TaskCredentials(
            username=config.auth_username.get_secret_value(),
            password=config.auth_password.get_secret_value()
        )
        task = LoginTask(url=config.base_url, credentials=credentials)

        # Create agent
        agent = AgentFactory.create_agent(
            config=config,
            task=task,
            browser_context=browser_context
        )

        # Run task
        asyncio.run(TaskRunner.run(agent, browser_context))

        logger.info("Task completed successfully!")

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

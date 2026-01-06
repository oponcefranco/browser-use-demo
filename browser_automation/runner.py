"""Task execution orchestration."""
import logging
from typing import Any

from browser_use import Agent
from browser_use.browser.context import BrowserContext

logger = logging.getLogger(__name__)


class TaskRunner:
    """Executes browser automation tasks."""

    @staticmethod
    async def run(
        agent: Agent,
        browser_context: BrowserContext,
        max_steps: int = 25
    ) -> Any:
        """Execute the task with the given agent.

        Args:
            agent: The AI agent to run
            browser_context: Browser context for the agent
            max_steps: Maximum number of steps to execute (default: 25)

        Returns:
            Result of the task execution

        Raises:
            Exception: If an error occurs during task execution
        """
        try:
            logger.info("Starting agent navigation task...")
            result = await agent.run(max_steps=max_steps)
            logger.info("Navigation task completed successfully!")
            return result
        except Exception as e:
            logger.error(f"Error during navigation: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info("Closing browser...")
            await browser_context.close()
            logger.info("Browser closed successfully")

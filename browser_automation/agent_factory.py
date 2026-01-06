"""Factory for creating AI agents."""
import logging

from langchain_openai import ChatOpenAI
from browser_use import Agent, Controller
from browser_use.browser.context import BrowserContext

from browser_automation.config import AppConfig
from browser_automation.tasks.base import Task

logger = logging.getLogger(__name__)


class AgentFactory:
    """Creates and configures AI agents."""

    @staticmethod
    def create_agent(
        config: AppConfig,
        task: Task,
        browser_context: BrowserContext,
        max_actions_per_step: int = 5
    ) -> Agent:
        """Create an AI agent configured for the given task.

        Args:
            config: Application configuration
            task: The task to be performed
            browser_context: Browser context for the agent
            max_actions_per_step: Maximum actions per step (default: 5)

        Returns:
            Configured Agent instance
        """
        logger.info(f"Initializing agent with model: {config.model}")

        llm = ChatOpenAI(
            model=config.model,
            api_key=config.openai_api_key
        )

        controller = Controller()

        return Agent(
            task=task.get_instructions(),
            llm=llm,
            max_actions_per_step=max_actions_per_step,
            controller=controller,
            browser_context=browser_context
        )

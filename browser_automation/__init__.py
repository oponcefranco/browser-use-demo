"""Browser automation package."""
from browser_automation.config import AppConfig, ConfigLoader, ConfigValidator
from browser_automation.browser_factory import BrowserFactory
from browser_automation.agent_factory import AgentFactory
from browser_automation.runner import TaskRunner
from browser_automation.tasks.base import Task, TaskCredentials
from browser_automation.tasks.login_task import LoginTask

__all__ = [
    "AppConfig",
    "ConfigLoader",
    "ConfigValidator",
    "BrowserFactory",
    "AgentFactory",
    "TaskRunner",
    "Task",
    "TaskCredentials",
    "LoginTask",
]

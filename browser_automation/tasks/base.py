"""Base task definition."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TaskCredentials:
    """Credentials for authentication tasks."""

    username: str
    password: str


class Task(ABC):
    """Abstract base class for browser automation tasks."""

    @abstractmethod
    def get_instructions(self) -> str:
        """Return the task instructions for the AI agent.

        Returns:
            Task instructions as a string
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the task name.

        Returns:
            Task name
        """
        pass

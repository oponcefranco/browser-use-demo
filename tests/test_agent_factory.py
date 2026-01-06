"""Tests for agent factory."""

from unittest.mock import Mock, patch, MagicMock
import pytest
from pydantic import SecretStr

from browser_automation.agent_factory import AgentFactory
from browser_automation.config import AppConfig
from browser_automation.tasks.base import Task


class MockTask(Task):
    """Mock task for testing."""

    def __init__(self, instructions: str = "Test instructions"):
        self._instructions = instructions

    def get_instructions(self) -> str:
        return self._instructions

    @property
    def name(self) -> str:
        return "mock_task"


class TestAgentFactory:
    """Test AgentFactory class."""

    def test_create_agent_with_default_max_actions(self):
        """Test creating agent with default max_actions_per_step."""
        config = AppConfig(
            openai_api_key=SecretStr("sk-test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass"),
            model="gpt-4o-mini"
        )
        task = MockTask()
        mock_browser_context = Mock()

        with patch('browser_automation.agent_factory.ChatOpenAI') as mock_llm_class, \
             patch('browser_automation.agent_factory.Controller') as mock_controller_class, \
             patch('browser_automation.agent_factory.Agent') as mock_agent_class:

            mock_llm = Mock()
            mock_llm_class.return_value = mock_llm
            mock_controller = Mock()
            mock_controller_class.return_value = mock_controller
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent

            agent = AgentFactory.create_agent(config, task, mock_browser_context)

            # Verify ChatOpenAI was created with correct config
            mock_llm_class.assert_called_once_with(
                model="gpt-4o-mini",
                api_key=config.openai_api_key
            )

            # Verify Controller was created
            mock_controller_class.assert_called_once_with()

            # Verify Agent was created with correct parameters
            mock_agent_class.assert_called_once_with(
                task=task.get_instructions(),
                llm=mock_llm,
                max_actions_per_step=5,
                controller=mock_controller,
                browser_context=mock_browser_context
            )

            assert agent == mock_agent

    def test_create_agent_with_custom_max_actions(self):
        """Test creating agent with custom max_actions_per_step."""
        config = AppConfig(
            openai_api_key=SecretStr("sk-test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass"),
            model="gpt-4o"
        )
        task = MockTask()
        mock_browser_context = Mock()
        custom_max_actions = 10

        with patch('browser_automation.agent_factory.ChatOpenAI'), \
             patch('browser_automation.agent_factory.Controller'), \
             patch('browser_automation.agent_factory.Agent') as mock_agent_class:

            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent

            AgentFactory.create_agent(
                config,
                task,
                mock_browser_context,
                max_actions_per_step=custom_max_actions
            )

            # Verify Agent was called with custom max_actions_per_step
            call_kwargs = mock_agent_class.call_args.kwargs
            assert call_kwargs['max_actions_per_step'] == custom_max_actions

    def test_create_agent_with_gpt4o_model(self):
        """Test creating agent with gpt-4o model."""
        config = AppConfig(
            openai_api_key=SecretStr("sk-test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass"),
            model="gpt-4o"
        )
        task = MockTask()
        mock_browser_context = Mock()

        with patch('browser_automation.agent_factory.ChatOpenAI') as mock_llm_class, \
             patch('browser_automation.agent_factory.Controller'), \
             patch('browser_automation.agent_factory.Agent'):

            AgentFactory.create_agent(config, task, mock_browser_context)

            # Verify ChatOpenAI was called with gpt-4o model
            call_kwargs = mock_llm_class.call_args.kwargs
            assert call_kwargs['model'] == "gpt-4o"

    def test_create_agent_with_different_api_keys(self):
        """Test creating agent with different API keys."""
        api_keys = [
            "sk-test-key-1",
            "sk-test-key-2",
            "sk-another-key"
        ]

        for api_key in api_keys:
            config = AppConfig(
                openai_api_key=SecretStr(api_key),
                chromium_path="/path/to/chromium",
                base_url="https://test.com",
                auth_username=SecretStr("testuser"),
                auth_password=SecretStr("testpass")
            )
            task = MockTask()
            mock_browser_context = Mock()

            with patch('browser_automation.agent_factory.ChatOpenAI') as mock_llm_class, \
                 patch('browser_automation.agent_factory.Controller'), \
                 patch('browser_automation.agent_factory.Agent'):

                AgentFactory.create_agent(config, task, mock_browser_context)

                # Verify correct API key was passed
                call_kwargs = mock_llm_class.call_args.kwargs
                assert call_kwargs['api_key'].get_secret_value() == api_key

    def test_create_agent_uses_task_instructions(self):
        """Test that agent is created with task's instructions."""
        config = AppConfig(
            openai_api_key=SecretStr("sk-test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass")
        )

        custom_instructions = "Navigate to login page and authenticate"
        task = MockTask(instructions=custom_instructions)
        mock_browser_context = Mock()

        with patch('browser_automation.agent_factory.ChatOpenAI'), \
             patch('browser_automation.agent_factory.Controller'), \
             patch('browser_automation.agent_factory.Agent') as mock_agent_class:

            AgentFactory.create_agent(config, task, mock_browser_context)

            # Verify Agent was called with task instructions
            call_kwargs = mock_agent_class.call_args.kwargs
            assert call_kwargs['task'] == custom_instructions

    def test_create_agent_logs_model_info(self):
        """Test that agent creation logs the model being used."""
        config = AppConfig(
            openai_api_key=SecretStr("sk-test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass"),
            model="gpt-4o"
        )
        task = MockTask()
        mock_browser_context = Mock()

        with patch('browser_automation.agent_factory.ChatOpenAI'), \
             patch('browser_automation.agent_factory.Controller'), \
             patch('browser_automation.agent_factory.Agent'), \
             patch('browser_automation.agent_factory.logger') as mock_logger:

            AgentFactory.create_agent(config, task, mock_browser_context)

            # Verify logging occurred
            mock_logger.info.assert_called_once()
            log_message = mock_logger.info.call_args[0][0]
            assert "gpt-4o" in log_message

    def test_create_agent_with_browser_context(self):
        """Test that agent is created with the provided browser context."""
        config = AppConfig(
            openai_api_key=SecretStr("sk-test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass")
        )
        task = MockTask()
        mock_browser_context = Mock()
        mock_browser_context.id = "test-context-123"

        with patch('browser_automation.agent_factory.ChatOpenAI'), \
             patch('browser_automation.agent_factory.Controller'), \
             patch('browser_automation.agent_factory.Agent') as mock_agent_class:

            AgentFactory.create_agent(config, task, mock_browser_context)

            # Verify Agent was called with the browser context
            call_kwargs = mock_agent_class.call_args.kwargs
            assert call_kwargs['browser_context'] == mock_browser_context
            assert call_kwargs['browser_context'].id == "test-context-123"

    def test_create_agent_controller_initialization(self):
        """Test that Controller is properly initialized."""
        config = AppConfig(
            openai_api_key=SecretStr("sk-test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass")
        )
        task = MockTask()
        mock_browser_context = Mock()

        with patch('browser_automation.agent_factory.ChatOpenAI'), \
             patch('browser_automation.agent_factory.Controller') as mock_controller_class, \
             patch('browser_automation.agent_factory.Agent') as mock_agent_class:

            mock_controller = Mock()
            mock_controller_class.return_value = mock_controller

            AgentFactory.create_agent(config, task, mock_browser_context)

            # Verify Controller was instantiated
            mock_controller_class.assert_called_once_with()

            # Verify Controller was passed to Agent
            call_kwargs = mock_agent_class.call_args.kwargs
            assert call_kwargs['controller'] == mock_controller

    def test_agent_factory_method_is_static(self):
        """Test that AgentFactory method can be called without instantiation."""
        # Verify this is a static method (can be called on the class)
        assert callable(AgentFactory.create_agent)

        config = AppConfig(
            openai_api_key=SecretStr("sk-test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("testuser"),
            auth_password=SecretStr("testpass")
        )
        task = MockTask()
        mock_browser_context = Mock()

        with patch('browser_automation.agent_factory.ChatOpenAI'), \
             patch('browser_automation.agent_factory.Controller'), \
             patch('browser_automation.agent_factory.Agent'):
            # Should not raise any errors about needing self
            AgentFactory.create_agent(config, task, mock_browser_context)

    def test_create_agent_with_all_parameters(self):
        """Test creating agent with all parameters specified."""
        config = AppConfig(
            openai_api_key=SecretStr("sk-production-key"),
            chromium_path="/usr/local/bin/chromium",
            base_url="https://production.example.com",
            auth_username=SecretStr("admin"),
            auth_password=SecretStr("secure-password"),
            headless=True,
            model="gpt-4o"
        )
        task = MockTask(instructions="Complete production task")
        mock_browser_context = Mock()
        max_actions = 15

        with patch('browser_automation.agent_factory.ChatOpenAI') as mock_llm_class, \
             patch('browser_automation.agent_factory.Controller') as mock_controller_class, \
             patch('browser_automation.agent_factory.Agent') as mock_agent_class:

            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent

            result = AgentFactory.create_agent(
                config=config,
                task=task,
                browser_context=mock_browser_context,
                max_actions_per_step=max_actions
            )

            # Verify all components were created correctly
            assert mock_llm_class.called
            assert mock_controller_class.called
            assert mock_agent_class.called
            assert result == mock_agent

            # Verify Agent was called with all correct parameters
            call_kwargs = mock_agent_class.call_args.kwargs
            assert call_kwargs['task'] == "Complete production task"
            assert call_kwargs['max_actions_per_step'] == max_actions
            assert call_kwargs['browser_context'] == mock_browser_context

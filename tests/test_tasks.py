"""Tests for task classes."""

import pytest
from abc import ABC

from browser_automation.tasks.base import Task, TaskCredentials
from browser_automation.tasks.login_task import LoginTask


class TestTaskCredentials:
    """Test TaskCredentials dataclass."""

    def test_create_credentials(self):
        """Test creating credentials with username and password."""
        credentials = TaskCredentials(
            username="testuser",
            password="testpass123"
        )
        assert credentials.username == "testuser"
        assert credentials.password == "testpass123"

    def test_credentials_are_stored_as_strings(self):
        """Test that credentials are stored as plain strings."""
        credentials = TaskCredentials(
            username="admin",
            password="secure-password"
        )
        assert isinstance(credentials.username, str)
        assert isinstance(credentials.password, str)

    def test_credentials_with_special_characters(self):
        """Test credentials with special characters."""
        special_password = "p@ssw0rd!#$%^&*()"
        credentials = TaskCredentials(
            username="user@example.com",
            password=special_password
        )
        assert credentials.username == "user@example.com"
        assert credentials.password == special_password

    def test_credentials_equality(self):
        """Test that credentials with same values are equal."""
        creds1 = TaskCredentials(username="user", password="pass")
        creds2 = TaskCredentials(username="user", password="pass")
        assert creds1 == creds2

    def test_credentials_inequality(self):
        """Test that credentials with different values are not equal."""
        creds1 = TaskCredentials(username="user1", password="pass")
        creds2 = TaskCredentials(username="user2", password="pass")
        assert creds1 != creds2


class ConcreteTask(Task):
    """Concrete implementation of Task for testing."""

    def __init__(self, task_name: str = "test_task", instructions: str = "Test instructions"):
        self._name = task_name
        self._instructions = instructions

    def get_instructions(self) -> str:
        return self._instructions

    @property
    def name(self) -> str:
        return self._name


class TestTaskBaseClass:
    """Test Task abstract base class."""

    def test_task_is_abstract(self):
        """Test that Task is an abstract base class."""
        assert issubclass(Task, ABC)

    def test_cannot_instantiate_task_directly(self):
        """Test that Task cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Task()

    def test_concrete_task_can_be_instantiated(self):
        """Test that concrete Task implementation can be instantiated."""
        task = ConcreteTask()
        assert isinstance(task, Task)

    def test_get_instructions_is_abstract(self):
        """Test that get_instructions must be implemented."""
        task = ConcreteTask(instructions="Do something")
        instructions = task.get_instructions()
        assert instructions == "Do something"

    def test_name_property_is_abstract(self):
        """Test that name property must be implemented."""
        task = ConcreteTask(task_name="my_task")
        assert task.name == "my_task"

    def test_task_subclass_requires_both_methods(self):
        """Test that Task subclass must implement both abstract methods."""
        # This should fail to instantiate if methods are missing
        class IncompleteTask(Task):
            pass

        with pytest.raises(TypeError):
            IncompleteTask()


class TestLoginTask:
    """Test LoginTask implementation."""

    def test_create_login_task(self):
        """Test creating a login task."""
        url = "https://example.com/login"
        credentials = TaskCredentials(username="user", password="pass")

        task = LoginTask(url=url, credentials=credentials)

        assert task.url == url
        assert task.credentials == credentials

    def test_login_task_name(self):
        """Test that login task has correct name."""
        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url="https://test.com", credentials=credentials)

        assert task.name == "login"

    def test_get_instructions_contains_url(self):
        """Test that instructions contain the target URL."""
        url = "https://example.com/login"
        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url=url, credentials=credentials)

        instructions = task.get_instructions()

        assert url in instructions

    def test_get_instructions_contains_username(self):
        """Test that instructions contain the username."""
        username = "testuser123"
        credentials = TaskCredentials(username=username, password="pass")
        task = LoginTask(url="https://test.com", credentials=credentials)

        instructions = task.get_instructions()

        assert username in instructions

    def test_get_instructions_contains_password(self):
        """Test that instructions contain the password."""
        password = "secretpass456"
        credentials = TaskCredentials(username="user", password=password)
        task = LoginTask(url="https://test.com", credentials=credentials)

        instructions = task.get_instructions()

        assert password in instructions

    def test_get_instructions_has_objective_section(self):
        """Test that instructions include OBJECTIVE section."""
        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url="https://test.com", credentials=credentials)

        instructions = task.get_instructions()

        assert "OBJECTIVE" in instructions

    def test_get_instructions_has_required_actions(self):
        """Test that instructions include REQUIRED ACTIONS section."""
        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url="https://test.com", credentials=credentials)

        instructions = task.get_instructions()

        assert "REQUIRED ACTIONS" in instructions

    def test_get_instructions_has_success_criteria(self):
        """Test that instructions include SUCCESS CRITERIA section."""
        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url="https://test.com", credentials=credentials)

        instructions = task.get_instructions()

        assert "SUCCESS CRITERIA" in instructions

    def test_get_instructions_mentions_navigate_step(self):
        """Test that instructions mention navigation step."""
        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url="https://test.com", credentials=credentials)

        instructions = task.get_instructions()

        assert "Navigate" in instructions or "navigate" in instructions

    def test_get_instructions_mentions_username_field(self):
        """Test that instructions mention username field."""
        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url="https://test.com", credentials=credentials)

        instructions = task.get_instructions()

        assert 'name="username"' in instructions

    def test_get_instructions_mentions_password_field(self):
        """Test that instructions mention password field."""
        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url="https://test.com", credentials=credentials)

        instructions = task.get_instructions()

        assert 'name="password"' in instructions

    def test_get_instructions_mentions_login_header(self):
        """Test that instructions mention the login header."""
        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url="https://test.com", credentials=credentials)

        instructions = task.get_instructions()

        assert "Test login" in instructions
        assert 'id="login"' in instructions

    def test_get_instructions_mentions_success_message(self):
        """Test that instructions mention success verification."""
        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url="https://test.com", credentials=credentials)

        instructions = task.get_instructions()

        assert "Logged In Successfully" in instructions

    def test_get_instructions_mentions_logout_button(self):
        """Test that instructions mention logout button verification."""
        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url="https://test.com", credentials=credentials)

        instructions = task.get_instructions()

        assert "Log out" in instructions

    def test_get_instructions_is_formatted_string(self):
        """Test that get_instructions returns a formatted string."""
        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url="https://test.com", credentials=credentials)

        instructions = task.get_instructions()

        assert isinstance(instructions, str)
        assert len(instructions) > 100  # Should be a substantial instruction set

    def test_login_task_with_different_urls(self):
        """Test login task with various URLs."""
        urls = [
            "https://example.com/login",
            "https://app.staging.example.com/auth",
            "http://localhost:8080/login",
            "https://secure-site.com/signin"
        ]

        credentials = TaskCredentials(username="user", password="pass")

        for url in urls:
            task = LoginTask(url=url, credentials=credentials)
            instructions = task.get_instructions()
            assert url in instructions
            assert task.url == url

    def test_login_task_with_complex_credentials(self):
        """Test login task with complex usernames and passwords."""
        test_cases = [
            ("admin@example.com", "P@ssw0rd123!"),
            ("user.name+tag@example.co.uk", "complex-pass-123"),
            ("test_user", "simple"),
        ]

        for username, password in test_cases:
            credentials = TaskCredentials(username=username, password=password)
            task = LoginTask(url="https://test.com", credentials=credentials)

            instructions = task.get_instructions()
            assert username in instructions
            assert password in instructions

    def test_login_task_preserves_credentials(self):
        """Test that login task preserves original credentials."""
        original_username = "original_user"
        original_password = "original_pass"
        credentials = TaskCredentials(
            username=original_username,
            password=original_password
        )

        task = LoginTask(url="https://test.com", credentials=credentials)

        # Credentials should not be modified
        assert task.credentials.username == original_username
        assert task.credentials.password == original_password

    def test_login_task_is_task_subclass(self):
        """Test that LoginTask is a subclass of Task."""
        assert issubclass(LoginTask, Task)

        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url="https://test.com", credentials=credentials)

        assert isinstance(task, Task)

    def test_login_task_implements_all_abstract_methods(self):
        """Test that LoginTask implements all required abstract methods."""
        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url="https://test.com", credentials=credentials)

        # Should not raise AttributeError
        assert hasattr(task, 'get_instructions')
        assert hasattr(task, 'name')
        assert callable(task.get_instructions)

        # Should return proper values
        instructions = task.get_instructions()
        name = task.name

        assert isinstance(instructions, str)
        assert isinstance(name, str)

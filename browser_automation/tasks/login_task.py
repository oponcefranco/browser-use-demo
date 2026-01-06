"""Login task implementation."""
from browser_automation.tasks.base import Task, TaskCredentials


class LoginTask(Task):
    """Task for performing login automation."""

    def __init__(self, url: str, credentials: TaskCredentials):
        """Initialize login task.

        Args:
            url: The URL to navigate to
            credentials: Authentication credentials
        """
        self.url = url
        self.credentials = credentials

    @property
    def name(self) -> str:
        """Return the task name."""
        return "login"

    def get_instructions(self) -> str:
        """Generate login task instructions.

        Returns:
            Formatted task instructions for the AI agent
        """
        return f"""Your task is to navigate to a login page and successfully authenticate using the provided credentials.

                OBJECTIVE:
                Complete the login process and verify successful authentication.

                REQUIRED ACTIONS (execute in order):

                1. Navigate to the login page:
                   - URL: {self.url}
                   - Wait for the page to fully load

                2. Verify you're on the correct page:
                   - Locate the header element with text "Test login"
                   - This header is an <h2> element with attribute id="login"
                   - If you cannot find this header, report an error

                3. Enter username:
                   - Locate the username input field (attribute: name="username")
                   - Clear any existing text in the field
                   - Enter the username: "{self.credentials.username}"
                   - Verify the text was entered correctly

                4. Enter password:
                   - Locate the password input field (attribute: name="password")
                   - Clear any existing text in the field
                   - Enter the password: "{self.credentials.password}"
                   - Verify the text was entered correctly

                5. Submit the login form:
                   - Locate and click the submit/login button
                   - Wait for the page to process the login request

                6. Verify successful authentication:
                   - Confirm the text "Logged In Successfully" is displayed on the page
                   - Confirm the "Log out" button is present and visible
                   - Both conditions must be met to consider the login successful

                SUCCESS CRITERIA:
                The task is complete when BOTH of the following are true:
                - The message "Logged In Successfully" is visible on the page
                - The "Log out" button is present and visible

                IMPORTANT GUIDELINES:
                - Wait for each element to be visible and interactive before attempting to interact with it
                - If any element cannot be found within a reasonable time, report which step failed
                - Do not proceed to the next step until the current step is successfully completed
                - If the login fails (success message not shown), report the failure
                """

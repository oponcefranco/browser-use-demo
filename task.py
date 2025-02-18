"""
Navigate to provided URL and perform task
------------------------------------------
"""

import os
import sys
from dataclasses import dataclass

from browser_use.browser.context import BrowserContextConfig, BrowserContext
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()

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
config = AppConfig(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    chromium_path="/Applications/Chromium.app/Contents/MacOS/Chromium",
    headless=False,
    base_url=os.getenv("BASE_URL"),
    auth_username=os.getenv("AUTH_USERNAME"),
    auth_password=os.getenv("AUTH_PASSWORD")
)

cookie = [{
    "name": "jwt",
    "value": os.getenv("JWT_TOKEN"),
    "domain": os.getenv('DOMAIN'),
    "path": "/"
}]


def create_agent(browser_config: AppConfig) -> Agent:

    llm = ChatOpenAI(model=browser_config.model, api_key=browser_config.openai_api_key)

    browser = Browser(
        config=BrowserConfig(
            headless=browser_config.headless,
            chrome_instance_path=browser_config.chromium_path,
        )
    )

    file_path = os.path.join(os.path.dirname(__file__), 'cookie.txt')
    cookie_file = ''.join(map(str, cookie))
    browser_context = BrowserContext(browser=browser, config=BrowserContextConfig(cookies_file=file_path))

    controller = Controller()

    # Create the agent with detailed instructions
    return Agent(
        task=f"""Navigate to the provide URL and use top navigation menu to select Create Account.

                Here are the specific steps:

                1. Go to {browser_config.base_url} 
                3. See the header text at the top of the page that says "Home" (look for attribute: 'data-qa="header_nav_home"')
                4. From top navigation menu, click on "Account" link (look for attribute: 'data-qa="account_header"') 
                5. Click on "Create account" dropdown option (look for attribute: 'data-qa="create_account_menu_button"')
                6. Find input to Enter First and Last Name (look for attribute: 'data-qa="create_account_name_input"')
                7. Find input to Enter email (look for attribute: 'data-qa="create_account_email_input"')
                    * email must have a domain '@goattest.com'
                    * name of email starts with "qauto" + unix timestamp
                7. Find input to Enter Password (look for attribute: 'data-qa="create_account_password_input"')
                    * new password must be "testing123

                Important:
                - Wait for each element to load before interacting
                """,
        llm=llm,
        max_actions_per_step=5,
        controller=controller,
        browser_context=browser_context
    )


async def navigate(agent: Agent):
    try:
        await agent.run(max_steps=25)
        # print("Navigation successful!")
    except Exception as e:
        print(f"Error navigating to destination: {str(e)}")


def main():
    agent = create_agent(config)
    asyncio.run(navigate(agent))

if __name__ == "__main__":
    main()

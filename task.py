"""
Navigate to CMS (staging) and navigate to Search Feeds
----------------------------------------
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
    chrome_path: str
    title: str
    subtitle: str
    description: str
    headless: bool = False
    model: str = "gpt-4o-mini"
    base_url: str = ""


# Customize these settings
config = AppConfig(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    chrome_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    title="TEST TITLE 1-2-3",
    subtitle="TEST SUBTITLE 1-2-3",
    description="This is a sample description, lorem ipsum.",
    headless=False,
)


def create_agent(browser_config: AppConfig) -> Agent:

    llm = ChatOpenAI(model=browser_config.model, api_key=browser_config.openai_api_key)

    browser = Browser(
        config=BrowserConfig(
            headless=browser_config.headless,
            chrome_instance_path=browser_config.chrome_path,
        )
    )

    file_path = os.path.join(os.path.dirname(__file__), 'cookie.txt')
    context = BrowserContext(browser=browser, config=BrowserContextConfig(cookies_file=file_path))

    controller = Controller()

    # Create the agent with detailed instructions
    return Agent(
        task=f"""Navigate to the provide URL and use top navigation menu to select Articles, select Search, and click on search-home-feed-alias link.

        Here are the specific steps:

        1. Go to {browser_config.base_url}. See the text input field at the top of the page that says "Collection"
        2. Look for the text input field at the top of the page that says "What's happening?"
        3. Click the input field and type exactly this message:
        4. Find and click the "Post" button (look for attributes: 'button' and 'data-testid="tweetButton"')
        5. Do not click on the '+' button which will add another tweet.

        6. Navigate to
        7. Before replying, understand the context of the tweet by scrolling down and reading the comments.
        8. Reply to the tweet under 50 characters.

        Important:
        - Wait for each element to load before interacting
        - Make sure the message is typed exactly as shown
        - Verify the post button is clickable before clicking
        - Do not click on the '+' button which will add another tweet
        """,
        llm=llm,
        controller=controller,
        browser=browser,
    )


async def navigate(agent: Agent):

    try:
        await agent.run(max_steps=100)
        agent.create_history_gif()
        print("Navigation successful!")
    except Exception as e:
        print(f"Error navigating to destination: {str(e)}")


def main():
    agent = create_agent(config)
    asyncio.run(navigate(agent))

if __name__ == "__main__":
    main()

# twitter/browser_manager.py

from dataclasses import dataclass, field
from typing import Optional, List
from playwright.sync_api import sync_playwright
from .utils.logger import logger

@dataclass
class BrowserConfig:
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    viewport: dict = field(default_factory=lambda: {"width": 1920, "height": 1080})
    locale: str = "en-US"
    args: Optional[List[str]] = None

class BrowserManager:
    def __init__(self, headless: bool = True, config: Optional[BrowserConfig] = None):
        self.headless = headless
        self.config = config or BrowserConfig()
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def __enter__(self):
        try:
            self.playwright = sync_playwright().start()
            launch_args = {
                "headless": self.headless,
                "args": self.config.args or ["--disable-blink-features=AutomationControlled"]
            }
            self.browser = self.playwright.chromium.launch(**launch_args)
            self.context = self.browser.new_context(
                user_agent=self.config.user_agent,
                viewport=self.config.viewport,
                locale=self.config.locale
            )
            self.page = self.context.new_page()
            logger.debug("Browser initialized successfully")
            return self
        except Exception as e:
            logger.error(f"Browser initialization failed: {str(e)}")
            self._cleanup()
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()
        logger.debug("Browser resources cleaned up")

    def _cleanup(self):
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
# twitter/scraper.py
import random
from time import sleep
from typing import List, Optional
from playwright.sync_api import Page
from .browser_manager import BrowserManager, BrowserConfig
from .instance_manager import InstanceManager
from .parsers.tweet_parser import TweetParser
from .models.schemas import TweetSchema
from .utils.logger import logger

class TweetScraper:
    def __init__(self, headless: bool = True):
        self.config = BrowserConfig()
        self.headless = headless
        self.instance_manager = None
        self.browser_manager = None

    def scrape_tweets(self, query: str, limit: int = 10, verbose: bool = False) -> List[TweetSchema]:
        try:
            with BrowserManager(headless=self.headless, config=self.config) as browser:
                self.instance_manager = InstanceManager(browser.page)
                instance = self.instance_manager.get_working_instance()
                
                current_url = f"{instance}/search?f=tweets&q={query}"
                browser.page.goto(current_url, timeout=60000)
                
                tweets = []
                retry_count = 0
                max_retries = 3
                consecutive_failures = 0
                
                while len(tweets) < limit and retry_count < max_retries:
                    try:
                        # Simulasi interaksi manusia
                        self._simulate_human_interaction(browser.page, verbose)
                        
                        # Ekstrak elemen tweet
                        tweet_elements = browser.page.locator("div.timeline-item").all()
                        
                        # Handle hasil kosong
                        if not tweet_elements:
                            logger.warning("No tweets found, rotating instance...")
                            instance = self.instance_manager.get_working_instance()
                            current_url = f"{instance}/search?f=tweets&q={query}"
                            browser.page.goto(current_url, timeout=60000)
                            retry_count += 1
                            continue
                            
                        # Proses tweet
                        new_tweets = []
                        for idx, element in enumerate(tweet_elements):
                            if len(tweets) + len(new_tweets) >= limit:
                                break
                                
                            try:
                                html = element.inner_html()
                                parsed = TweetParser.parse(html)
                                if parsed and self._validate_tweet(parsed):
                                    new_tweets.append(parsed)
                                    
                                    if verbose:
                                        logger.info(f"Collected {len(tweets)+len(new_tweets)}/{limit} tweets")
                                
                            except Exception as e:
                                logger.error(f"Error processing tweet {idx}: {str(e)}")
                                consecutive_failures += 1
                                if consecutive_failures > 5:
                                    raise RuntimeError("Too many consecutive tweet processing failures")
                                
                        tweets.extend(new_tweets)
                        
                        # Handle paginasi
                        if not self._handle_pagination(browser.page):
                            logger.info("Reached end of pages")
                            break
                            
                        retry_count = 0
                        consecutive_failures = 0
                        
                    except Exception as e:
                        logger.error(f"Page error: {str(e)}")
                        retry_count += 1
                        instance = self.instance_manager.get_working_instance()
                        current_url = f"{instance}/search?f=tweets&q={query}"
                        browser.page.goto(current_url, timeout=60000)
                        sleep(10)
                
                return tweets[:limit]
                
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            return []
        
    def _simulate_human_interaction(self, page: Page, verbose: bool):
        """Simulate realistic human scrolling behavior"""
        try:
            # Random initial delay
            sleep(random.uniform(1, 3))
            
            # Scroll in random chunks with variable speed
            scrolls = random.randint(3, 6)
            if verbose:
                logger.info(f"Simulating human scrolling ({scrolls} times)")
            
            viewport_height = page.viewport_size["height"]
            current_scroll = 0
            
            for _ in range(scrolls):
                # Random scroll distance (30-80% of viewport height)
                scroll_distance = random.randint(
                    int(viewport_height * 0.3), 
                    int(viewport_height * 0.8)
                )
                
                # Smooth scroll with random duration
                page.evaluate(f"""
                    window.scrollBy({{
                        top: {scroll_distance},
                        left: 0,
                        behavior: 'smooth'
                    }});
                """)
                
                # Random scroll duration between 0.5-2 seconds
                sleep(random.uniform(0.5, 2))
                
                # Random pause after scroll
                sleep(random.uniform(0.5, 1.5))
                
                current_scroll += scroll_distance

            # Final scroll to trigger lazy loading
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            sleep(1)
            
        except Exception as e:
            logger.warning(f"Interaction simulation failed: {str(e)}")

    def _get_next_page_url(self, page: Page) -> Optional[str]:
        """Click next page button and return new URL"""
        try:
            if page.locator("div.show-more").count() > 0:
                with page.expect_navigation():
                    page.locator("div.show-more a").first.click()
                sleep(random.uniform(1, 3))  # Wait for content load
                return page.url
        except Exception as e:
            logger.warning(f"Failed to navigate to next page: {str(e)}")
            return None
        
    def _handle_pagination(self, page: Page) -> bool:
        """Handle paginasi dan return status keberhasilan"""
        try:
            # Coba klik tombol "Show More"
            if page.locator("div.show-more:visible").count() > 0:
                with page.expect_navigation(timeout=10000):
                    page.locator("div.show-more a").first.click()
                sleep(random.uniform(1, 2))
                return True
            
            # Scroll untuk trigger lazy loading
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            sleep(2)
            
            # Cek apakah muncul tombol baru setelah scroll
            if page.locator("div.show-more:visible").count() > 0:
                with page.expect_navigation(timeout=10000):
                    page.locator("div.show-more a").first.click()
                sleep(random.uniform(1, 2))
                return True
                
            return False
            
        except Exception as e:
            logger.warning(f"Pagination failed: {str(e)}")
            return False

    def _validate_tweet(self, tweet: TweetSchema) -> bool:
        """Validasi akhir untuk tweet"""
        return all([
            tweet.user.username not in ["unknown_user", ""],
            len(tweet.content or "") >= 10,
            tweet.link and tweet.link.startswith("https://twitter.com/"),
            tweet.timestamp is not None,
            isinstance(tweet.stats.comments, int),
            isinstance(tweet.stats.retweets, int)
        ])
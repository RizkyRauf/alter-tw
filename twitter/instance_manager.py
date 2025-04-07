# twitter/instance_manager.py

import random
from time import sleep
from typing import List, Optional
from .settings import NIITTER_INSTANCES
from .utils.logger import logger

class InstanceManager:
    def __init__(self, page, instances: Optional[List[str]] = None):
        self.page = page
        self.instances = instances or NIITTER_INSTANCES
        self.current_instance = None
        self.max_retries = 3

    def _test_instance(self, instance: str) -> bool:
        try:
            logger.info(f"Testing instance: {instance}")
            self.page.goto(f"{instance}/search?q=test", timeout=30000)
            sleep(random.uniform(1, 3))
            return self.page.locator("div.timeline-item").count() > 2
        except Exception as e:
            logger.warning(f"Instance test failed: {str(e)[:80]}...")
            return False

    def get_working_instance(self) -> str:
        for _ in range(self.max_retries):
            for instance in random.sample(self.instances, len(self.instances)):
                if self._test_instance(instance):
                    self.current_instance = instance
                    logger.info(f"Selected instance: {instance}")
                    return instance
            logger.warning("No working instances found, retrying...")
            sleep(7)
        
        raise ConnectionError("No available instances after multiple retries")
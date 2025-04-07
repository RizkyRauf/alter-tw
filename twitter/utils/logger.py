# twitter/utils/logger.py

import logging
import sys

class CustomLogger:
    def __init__(self, name: str = "NitterScraper"):
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self):
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(f"⚠️ {message}")

    def error(self, message: str):
        self.logger.error(f"🚨 {message}")

    def critical(self, message: str):
        self.logger.critical(f"🔥 {message}")

logger = CustomLogger().logger
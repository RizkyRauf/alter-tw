# twitter/parser/user_parser.py

from bs4 import BeautifulSoup
from typing import Optional
from ..models.schemas import UserSchema
from ..utils.logger import logger

class UserParser:
    @staticmethod
    def parse(soup: BeautifulSoup) -> UserSchema:
        try:
            return UserSchema(
                username=UserParser._parse_username(soup),
                fullname=UserParser._parse_fullname(soup),
                verified=UserParser._parse_verified_status(soup)
            )
        except Exception as e:
            logger.error(f"User parsing error: {str(e)}")
            return UserSchema(username="unknown", fullname="Unknown User")

    @staticmethod
    def _parse_username(soup) -> str:
        # Prioritas ambil dari username di tweet header
        username_element = soup.select_one("div.tweet-header a.username")
        if username_element:
            return username_element.text.strip().lstrip('@').lower()
            
        # Fallback ke selector lama
        username_element = soup.select_one("a.username")
        return username_element.text.strip().lstrip('@').lower() if username_element else "unknown_user"

    @staticmethod
    def _parse_fullname(soup) -> str:
        fullname_element = soup.select_one("a.fullname")
        return fullname_element.get_text(strip=True) if fullname_element else "Unknown User"

    @staticmethod
    def _parse_verified_status(soup) -> bool:
        verified_element = soup.select_one("a.fullname span.verified-icon")
        return bool(verified_element)
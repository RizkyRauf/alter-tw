# twitter/parser/media_parser.py

from typing import List
from bs4 import BeautifulSoup
from urllib.parse import unquote
from ..models.schemas import MediaSchema
from ..utils.logger import logger

class MediaParser:
    @staticmethod
    def parse(soup: BeautifulSoup) -> MediaSchema:
        try:
            return MediaSchema(
                images=MediaParser._parse_images(soup),
                videos=MediaParser._parse_videos(soup),
                gifs=MediaParser._parse_gifs(soup)
            )
        except Exception as e:
            logger.error(f"Media parsing error: {str(e)}")
            return MediaSchema(images=[], videos=[], gifs=[])

    @staticmethod
    def _clean_url(url: str) -> str:
        """Remove URL parameters and decode"""
        try:
            return unquote(url.split('?')[0])
        except Exception as e:
            logger.warning(f"URL cleaning failed: {str(e)}")
            return url

    @staticmethod
    def _parse_images(soup) -> List[str]:
        images = []
        for img in soup.select("div.attachments img[src*='/pic/']"):
            try:
                src = img.get("src", "")
                if "/pic/" in src:
                    # Bersihkan URL
                    clean_url = unquote(src.split('?')[0].split("/pic")[1])
                    images.append(f"https://pbs.twimg.com{clean_url}")
            except Exception as e:
                logger.warning(f"Image parsing error: {str(e)}")
        return images

    @staticmethod
    def _parse_videos(soup) -> List[str]:
        videos = []
        for video in soup.select("video:not(.gif)"):
            try:
                data_url = video.get("data-url", "")
                if data_url:
                    decoded_url = unquote(data_url.split("/pic")[1].split("?")[0])
                    videos.append(f"https://pbs.twimg.com{decoded_url}")
            except Exception as e:
                logger.warning(f"Video parsing error: {str(e)}")
        return videos

    @staticmethod
    def _parse_gifs(soup) -> List[str]:
        gifs = []
        for gif in soup.select("video.gif"):
            try:
                data_url = gif.get("data-url", "")
                if data_url:
                    decoded_url = unquote(data_url.split("/pic")[1].split("?")[0])
                    gifs.append(f"https://pbs.twimg.com{decoded_url}")
            except Exception as e:
                logger.warning(f"GIF parsing error: {str(e)}")
        return gifs
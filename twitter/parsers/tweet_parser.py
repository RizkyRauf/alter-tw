from bs4 import BeautifulSoup
import re
import datetime
from typing import Optional, List
from ..models.schemas import TweetSchema, TweetStats, UserSchema, MediaSchema
from .user_parser import UserParser
from .media_parser import MediaParser
from ..utils.logger import logger

class TweetParser:
    
    @staticmethod
    def parse(html: str) -> Optional[TweetSchema]:
        """Main parser dengan error handling komprehensif"""
        try:
            soup = BeautifulSoup(html, "html.parser")
            if not soup.find("div", class_="tweet-body"):
                return None
                
            is_retweet = bool(soup.select_one("div.retweet-header"))
            
            return (
                TweetParser._parse_retweet(soup)
                if is_retweet
                else TweetParser._parse_regular_tweet(soup)
            )
            
        except Exception as e:
            logger.error(f"Tweet parsing failed: {str(e)}", exc_info=True)
            return None

    @staticmethod
    def _parse_regular_tweet(soup: BeautifulSoup) -> Optional[TweetSchema]:
        """Parse tweet biasa dengan validasi ketat"""
        try:
            content = TweetParser._parse_content(soup)
            if not content:
                return None
                
            return TweetSchema(
                user=UserParser.parse(soup),
                content=content,
                hashtags=TweetParser._parse_hashtags(soup),
                mentions=TweetParser._parse_mentions(soup),
                replying_to=TweetParser._parse_replying_to(soup),
                timestamp=TweetParser._parse_timestamp(soup),
                stats=TweetParser._parse_stats(soup),
                media=MediaParser.parse(soup),
                link=TweetParser._parse_link(soup),
                is_retweet=False,
                retweeter=None
            )
        except Exception as e:
            logger.warning(f"Failed to parse regular tweet: {str(e)}")
            return None

    @staticmethod
    def _parse_retweet(soup: BeautifulSoup) -> Optional[TweetSchema]:
        """Parse retweet dengan penanganan khusus"""
        try:
            retweeter = None
            retweet_header = soup.select_one("div.retweet-header")
            
            if retweet_header:
                retweet_text = retweet_header.get_text(strip=True)
                match = re.search(r"([A-Za-z0-9_]+)\s+retweeted", retweet_text)
                if match:
                    retweeter = match.group(1)

            content = TweetParser._parse_content(soup)
            if not content:
                return None
                
            return TweetSchema(
                user=UserParser.parse(soup),
                content=content,
                hashtags=TweetParser._parse_hashtags(soup),
                mentions=TweetParser._parse_mentions(soup),
                replying_to=TweetParser._parse_replying_to(soup),
                timestamp=TweetParser._parse_timestamp(soup),
                stats=TweetParser._parse_stats(soup),
                media=MediaParser.parse(soup),
                link=TweetParser._parse_link(soup),
                is_retweet=True,
                retweeter=retweeter
            )
        except Exception as e:
            logger.warning(f"Failed to parse retweet: {str(e)}")
            return None

    @staticmethod
    def _parse_content(soup: BeautifulSoup) -> Optional[str]:
        """Ekstrak konten dengan null safety dan pembersihan"""
        try:
            content_div = soup.select_one("div.tweet-content")
            if not content_div:
                return None
                
            # Hapus elemen yang tidak diperlukan
            for elem in content_div.select(".mention, .hashtag, .ellipsis, .hidden, .rt-quote"):
                elem.decompose()
                
            return content_div.get_text(" ", strip=True).replace("\n", " ").strip()
        except Exception as e:
            logger.warning(f"Content parsing error: {str(e)}")
            return None

    @staticmethod
    def _parse_hashtags(soup: BeautifulSoup) -> List[str]:
        """Ekstrak hashtag dari konten dan link"""
        hashtags = set()
        
        # Dari teks konten
        content = TweetParser._parse_content(soup) or ""
        hashtags.update(re.findall(r"#(\w+)", content))
        
        # Dari link hashtag
        for a in soup.select("a[href*='/search?q=%23']"):
            href = a.get("href", "")
            match = re.search(r"%23(\w+)", href)
            if match:
                hashtags.add(match.group(1).lower())
                
        return sorted([ht for ht in hashtags if len(ht) > 1])

    @staticmethod
    def _parse_mentions(soup: BeautifulSoup) -> List[str]:
        """Ekstrak mention dari konten dan link"""
        mentions = set()
        
        # Dari teks konten
        content = TweetParser._parse_content(soup) or ""
        mentions.update(re.findall(r"@(\w+)", content))
        
        # Dari link mention
        for a in soup.select("a.mention"):
            username = a.get("href", "").lstrip("/")
            if username:
                mentions.add(username.lower())
                
        return sorted(mentions)

    @staticmethod
    def _parse_replying_to(soup: BeautifulSoup) -> List[str]:
        """Ekstrak akun yang di-reply dengan validasi"""
        replying_to = []
        replying_div = soup.find("div", class_="replying-to")
        
        if replying_div:
            # Dari teks
            replying_text = replying_div.get_text(strip=True)
            replying_to.extend(re.findall(r"@(\w+)", replying_text))
            
            # Dari link
            replying_to.extend([
                a["href"].lstrip("/").lower()
                for a in replying_div.find_all("a")
                if a.has_attr("href")
            ])
            
        return list(set(filter(None, replying_to)))

    @staticmethod
    def _parse_timestamp(soup: BeautifulSoup) -> Optional[datetime.datetime]:
        """Parse timestamp dengan berbagai format"""
        try:
            date_element = soup.select_one("span.tweet-date a")
            if not date_element or not date_element.has_attr("title"):
                return None
                
            return TweetParser._parse_date(date_element["title"])
        except Exception as e:
            logger.warning(f"Timestamp parsing error: {str(e)}")
            return None

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime.datetime]:
        """Handle berbagai format tanggal Nitter"""
        try:
            # Format absolut: "Apr 5, 2025 · 3:00 PM UTC"
            if "·" in date_str:
                return datetime.datetime.strptime(
                    date_str, 
                    "%b %d, %Y · %I:%M %p UTC"
                ).replace(tzinfo=datetime.timezone.utc)
            
            # Format relatif: "14m", "2h", "3d"
            match = re.match(r"(\d+)([mhd])", date_str)
            if not match:
                return None
                
            num, unit = match.groups()
            num = int(num)
            
            delta = datetime.timedelta(
                minutes=num if unit == 'm' else 0,
                hours=num if unit == 'h' else 0,
                days=num if unit == 'd' else 0
            )
            return datetime.datetime.now(datetime.timezone.utc) - delta
            
        except Exception as e:
            logger.warning(f"Date parsing failed: {date_str} - {str(e)}")
            return None

    @staticmethod
    def _parse_stats(soup: BeautifulSoup) -> TweetStats:
        """Parse statistik dengan validasi tipe data"""
        stats = TweetStats()
        
        for item in soup.select("span.tweet-stat"):
            try:
                icon = item.select_one("span[class^='icon-']")
                value_div = item.select_one("div")
                
                if not icon or not value_div:
                    continue
                    
                icon_type = icon["class"][0].split("icon-")[-1]
                value = int(value_div.text.strip().replace(",", "")) if value_div.text.strip() else 0
                
                if icon_type == "comment":
                    stats.comments = value
                elif icon_type == "retweet":
                    stats.retweets = value
                elif icon_type == "quote":
                    stats.quotes = value
                elif icon_type == "heart":
                    stats.likes = value
                    
            except (ValueError, KeyError, AttributeError) as e:
                logger.debug(f"Invalid stat item: {str(e)}")
                
        return stats

    @staticmethod
    def _parse_link(soup: BeautifulSoup) -> Optional[str]:
        """Ekstrak link tweet dengan validasi"""
        try:
            link_element = soup.select_one("a.tweet-link")
            if link_element and link_element.has_attr("href"):
                return f"https://twitter.com{link_element['href']}"
            return None
        except Exception as e:
            logger.warning(f"Link parsing error: {str(e)}")
            return None
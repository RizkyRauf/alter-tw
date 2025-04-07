from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class UserSchema:
    username: str
    fullname: str
    verified: bool = field(default=False)

@dataclass
class MediaSchema:
    images: List[str] = field(default_factory=list)
    videos: List[str] = field(default_factory=list)
    gifs: List[str] = field(default_factory=list)

@dataclass
class TweetStats:
    comments: int = 0
    retweets: int = 0
    quotes: int = 0
    likes: int = 0

@dataclass
class TweetSchema:
    user: UserSchema
    content: str
    hashtags: List[str]
    mentions: List[str]
    replying_to: List[str]
    timestamp: Optional[datetime]
    stats: TweetStats
    media: MediaSchema
    link: str
    is_retweet: bool = False
    retweeter: Optional[str] = None
# File: cli.py
import argparse
from termcolor import colored
from typing import List
from twitter import TweetScraper
from twitter.models.schemas import TweetSchema
from twitter.utils.logger import logger
from twitter.utils.helpers import EnhancedJSONEncoder

def display_results(tweets: List[TweetSchema]):
    """Display formatted scraping results"""
    print(f"\n{colored('=== Hasil Scraping ===', 'cyan', attrs=['bold'])}")
    for idx, tweet in enumerate(tweets, 1):
        user = tweet.user
        stats = tweet.stats
        
        print(f"\n{colored(f'Tweet #{idx}', 'yellow', attrs=['bold'])}")
        print(f"{colored('• Pengguna:', 'green')} {user.fullname} (@{user.username})")
        print(f"{colored('• Verifikasi:', 'green')} {'✅' if user.verified else '❌'}")
        print(f"{colored('• Waktu:', 'blue')} {tweet.timestamp.strftime('%Y-%m-%d %H:%M UTC') if tweet.timestamp else 'N/A'}")
        print(f"{colored('• Konten:', 'magenta')}\n{tweet.content}")
        
        print(f"{colored('• Statistik:', 'cyan')} "
              f"💬 {stats.comments} | "
              f"🔁 {stats.retweets} | "
              f"💬 {stats.quotes} | "
              f"💖 {stats.likes}")
        
        print(f"{colored('• Media:', 'cyan')} "
              f"🖼 {len(tweet.media.images)} | "
              f"🎥 {len(tweet.media.videos)} | "
              f"🎞 {len(tweet.media.gifs)}")
        
        print(f"{colored('• Link:', 'blue')} {tweet.link}")
        print("-" * 80)

def main():
    """Command Line Interface for Twitter Scraper"""
    parser = argparse.ArgumentParser(
        description="Nitter Scraper - Ekstrak Data Twitter Tanpa API",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "query",
        help="Kata kunci atau hashtag untuk pencarian"
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=20,
        help="Jumlah maksimum tweet yang akan diambil"
    )
    parser.add_argument(
        "-o", "--output",
        help="Simpan hasil ke file JSON"
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="Tampilkan browser selama proses scraping"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Tampilkan log detail proses scraping"
    )
    
    args = parser.parse_args()
    
    try:
        scraper = TweetScraper(headless=not args.visible)
        tweets = scraper.scrape_tweets(
            query=args.query,
            limit=args.limit,
            verbose=args.verbose
        )
        
        if args.output:
            import json
            with open(args.output, "w") as f:
                json.dump(
                    tweets,
                    f,
                    indent=2,
                    cls=EnhancedJSONEncoder,
                    ensure_ascii=False
                )
            print(f"\n{colored('✔ Hasil disimpan di:', 'green')} {args.output}")
        
        display_results(tweets)
        print(f"\n{colored(f'Berhasil mengumpulkan {len(tweets)} tweet!', 'green')}")
        
    except Exception as e:
        logger.error(f"{colored('❌ Error:', 'red')} {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
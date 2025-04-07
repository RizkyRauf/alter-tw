# File: main_test.py
import json
from datetime import datetime
from twitter import TweetScraper
from twitter.utils.logger import logger
from twitter.utils.helpers import EnhancedJSONEncoder

def test_scraping():
    """Fungsi testing untuk scraping tweet"""
    try:
        # Konfigurasi testing
        test_config = {
            "query": "jokowi",
            "limit": 30,
            "visible_browser": True,
            "output_file": "test_results.json",
            "verbose": True
        }
        
        logger.info("Memulai proses testing...")
        start_time = datetime.now()
        
        scraper = TweetScraper(headless=not test_config["visible_browser"])
        results = scraper.scrape_tweets(
            query=test_config["query"],
            limit=test_config["limit"],
            verbose=test_config["verbose"]
        )
        
        # Simpan hasil dalam format JSON
        with open(test_config["output_file"], "w") as f:
            json.dump(
                results,
                f,
                indent=2,
                cls=EnhancedJSONEncoder,
                ensure_ascii=False
            )
        
        # Analisis hasil
        duration = datetime.now() - start_time
        stats = {
            "total_tweets": len(results),
            "duration": str(duration),
            "avg_tweets_per_second": len(results) / duration.total_seconds(),
            "users": len({t.user.username for t in results}),
            "avg_hashtags": sum(len(t.hashtags) for t in results) / len(results),
            "success_rate": f"{(len(results)/test_config['limit']*100):.1f}%"
        }
        
        print("\n=== Hasil Testing ===")
        for k, v in stats.items():
            print(f"{k.replace('_', ' ').title():<25}: {v}")
            
        print(f"\nFile hasil disimpan di: {test_config['output_file']}")
        
    except Exception as e:
        logger.error(f"Testing gagal: {str(e)}")
        exit(1)

if __name__ == "__main__":
    test_scraping()
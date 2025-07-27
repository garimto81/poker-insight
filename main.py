#!/usr/bin/env python3
"""
메인 크롤러 실행 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from datetime import datetime
from crawlers.pokerscout_crawler import PokerScoutCrawler
from crawlers.pokernews_crawler import PokerNewsCrawler
from config.settings import Config

# 로깅 설정
os.makedirs(Config.LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_crawlers():
    """모든 크롤러 실행"""
    logger.info("=== Starting daily crawl ===")
    start_time = datetime.now()
    
    # PokerScout 크롤링
    try:
        logger.info("Running PokerScout crawler...")
        scout_crawler = PokerScoutCrawler()
        scout_crawler.run()
    except Exception as e:
        logger.error(f"PokerScout crawler failed: {str(e)}")
    
    # PokerNews 크롤링
    try:
        logger.info("Running PokerNews crawler...")
        news_crawler = PokerNewsCrawler()
        news_crawler.run()
    except Exception as e:
        logger.error(f"PokerNews crawler failed: {str(e)}")
    
    end_time = datetime.now()
    duration = (end_time - start_time).seconds
    logger.info(f"=== Daily crawl completed in {duration} seconds ===")

if __name__ == "__main__":
    run_crawlers()
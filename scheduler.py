#!/usr/bin/env python3
"""
일일 자동 실행 스케줄러
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import schedule
import time
import logging
from datetime import datetime
from main import run_crawlers
from config.settings import Config

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def scheduled_crawl():
    """스케줄된 크롤링 작업"""
    logger.info(f"Scheduled crawl triggered at {datetime.now()}")
    run_crawlers()

def run_scheduler():
    """스케줄러 실행"""
    # 매일 오전 6시에 실행 (UTC 기준)
    schedule.every().day.at("06:00").do(scheduled_crawl)
    
    # 추가 실행 시간 설정 가능
    # schedule.every().day.at("18:00").do(scheduled_crawl)  # 오후 6시 추가 실행
    
    logger.info("Scheduler started. Waiting for scheduled tasks...")
    logger.info(f"Next run scheduled at: {schedule.next_run()}")
    
    # 시작 시 한 번 실행 (옵션)
    logger.info("Running initial crawl...")
    run_crawlers()
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}")
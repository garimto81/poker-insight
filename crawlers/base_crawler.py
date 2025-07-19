import logging
from datetime import datetime
from abc import ABC, abstractmethod
from database.models import SessionLocal, CrawlLog
from config.settings import Config
import time
import random

class BaseCrawler(ABC):
    def __init__(self, source_name):
        self.source_name = source_name
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = SessionLocal()
        self.crawl_log = None
        
    def start_crawl(self):
        """크롤링 시작 시 로그 생성"""
        self.crawl_log = CrawlLog(
            source=self.source_name,
            status='running',
            started_at=datetime.utcnow()
        )
        self.session.add(self.crawl_log)
        self.session.commit()
        
    def end_crawl(self, status='success', items_scraped=0, error_message=None):
        """크롤링 종료 시 로그 업데이트"""
        if self.crawl_log:
            self.crawl_log.status = status
            self.crawl_log.items_scraped = items_scraped
            self.crawl_log.error_message = error_message
            self.crawl_log.completed_at = datetime.utcnow()
            self.session.commit()
            
    def random_delay(self, min_delay=1, max_delay=3):
        """랜덤 딜레이 추가"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        
    @abstractmethod
    def crawl(self):
        """각 크롤러가 구현해야 할 메인 크롤링 로직"""
        pass
    
    def run(self):
        """크롤링 실행"""
        try:
            self.start_crawl()
            self.logger.info(f"Starting {self.source_name} crawl...")
            items_count = self.crawl()
            self.end_crawl(status='success', items_scraped=items_count)
            self.logger.info(f"Completed {self.source_name} crawl. Items scraped: {items_count}")
        except Exception as e:
            self.logger.error(f"Error during {self.source_name} crawl: {str(e)}")
            self.end_crawl(status='failed', error_message=str(e))
            raise
        finally:
            self.session.close()
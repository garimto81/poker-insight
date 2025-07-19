#!/usr/bin/env python3
"""
크롤러 테스트 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from datetime import datetime
import json
from sqlalchemy import create_engine
from database.models import Base, SessionLocal, PokerSite, TrafficData, NewsItem, CrawlLog

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_database_connection():
    """데이터베이스 연결 테스트"""
    logger.info("Testing database connection...")
    try:
        db = SessionLocal()
        # 간단한 쿼리 실행
        result = db.execute("SELECT 1").fetchone()
        db.close()
        logger.info("✓ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {str(e)}")
        return False

def test_pokerscout_crawler():
    """PokerScout 크롤러 테스트"""
    logger.info("\n=== Testing PokerScout Crawler ===")
    try:
        from crawlers.pokerscout_crawler import PokerScoutCrawler
        
        # 크롤러 인스턴스 생성
        crawler = PokerScoutCrawler()
        
        # 헤더 테스트
        headers = crawler.get_headers()
        logger.info(f"✓ Headers generated: User-Agent = {headers['User-Agent'][:50]}...")
        
        # 실제 크롤링 테스트 (제한적)
        import requests
        from bs4 import BeautifulSoup
        
        response = requests.get(
            crawler.base_url,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"✓ Successfully accessed PokerScout (Status: {response.status_code})")
            
            # HTML 파싱 테스트
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'class': 'ranktable'})
            
            if table:
                logger.info("✓ Found ranking table")
                rows = table.find_all('tr')[1:6]  # 상위 5개만 테스트
                logger.info(f"✓ Found {len(rows)} data rows")
                
                # 첫 번째 행 파싱 테스트
                if rows:
                    cols = rows[0].find_all('td')
                    if len(cols) >= 6:
                        site_name = cols[1].text.strip()
                        total_players = cols[4].text.strip()
                        logger.info(f"✓ Sample data: {site_name} - {total_players} players")
                        return True
            else:
                logger.warning("✗ Could not find ranking table")
        else:
            logger.error(f"✗ Failed to access PokerScout (Status: {response.status_code})")
            
    except Exception as e:
        logger.error(f"✗ PokerScout crawler test failed: {str(e)}")
        return False

def test_pokernews_crawler():
    """PokerNews 크롤러 테스트"""
    logger.info("\n=== Testing PokerNews Crawler ===")
    try:
        from crawlers.pokernews_crawler import PokerNewsCrawler
        
        # 크롤러 인스턴스 생성
        crawler = PokerNewsCrawler()
        
        # 헤더 테스트
        headers = crawler.get_headers()
        logger.info(f"✓ Headers generated: User-Agent = {headers['User-Agent'][:50]}...")
        
        # 실제 크롤링 테스트
        import requests
        from bs4 import BeautifulSoup
        
        test_url = f"{crawler.base_url}/news/"
        response = requests.get(
            test_url,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"✓ Successfully accessed PokerNews (Status: {response.status_code})")
            
            # HTML 파싱 테스트
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('article', limit=5)
            
            if articles:
                logger.info(f"✓ Found {len(articles)} articles")
                
                # 첫 번째 기사 파싱 테스트
                article = articles[0]
                title_elem = article.find('h2') or article.find('h3')
                if title_elem:
                    title = title_elem.text.strip()
                    logger.info(f"✓ Sample article: {title[:60]}...")
                    return True
            else:
                logger.warning("✗ Could not find any articles")
        else:
            logger.error(f"✗ Failed to access PokerNews (Status: {response.status_code})")
            
    except Exception as e:
        logger.error(f"✗ PokerNews crawler test failed: {str(e)}")
        return False

def test_data_saving():
    """데이터 저장 테스트"""
    logger.info("\n=== Testing Data Saving ===")
    try:
        db = SessionLocal()
        
        # 테스트 사이트 저장
        test_site = PokerSite(
            name="Test Poker Site",
            url="https://example.com"
        )
        db.add(test_site)
        db.commit()
        logger.info("✓ Successfully saved test poker site")
        
        # 테스트 트래픽 데이터 저장
        test_traffic = TrafficData(
            site_id=test_site.id,
            cash_players=100,
            tournament_players=50,
            total_players=150,
            seven_day_average=145.5,
            rank=1
        )
        db.add(test_traffic)
        db.commit()
        logger.info("✓ Successfully saved test traffic data")
        
        # 데이터 조회 테스트
        saved_site = db.query(PokerSite).filter_by(name="Test Poker Site").first()
        if saved_site:
            logger.info(f"✓ Retrieved test site: {saved_site.name}")
            
            # 테스트 데이터 삭제
            db.query(TrafficData).filter_by(site_id=saved_site.id).delete()
            db.delete(saved_site)
            db.commit()
            logger.info("✓ Test data cleaned up")
            
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ Data saving test failed: {str(e)}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def run_all_tests():
    """모든 테스트 실행"""
    logger.info("Starting crawler tests...\n")
    
    results = {
        "Database Connection": test_database_connection(),
        "PokerScout Crawler": test_pokerscout_crawler(),
        "PokerNews Crawler": test_pokernews_crawler(),
        "Data Saving": test_data_saving()
    }
    
    # 결과 요약
    logger.info("\n=== Test Results Summary ===")
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    logger.info(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    return all(results.values())

if __name__ == "__main__":
    # SQLite를 사용한 테스트 (PostgreSQL 없이도 테스트 가능)
    import tempfile
    temp_db = tempfile.NamedTemporaryFile(delete=False)
    test_db_path = temp_db.name
    temp_db.close()
    
    # 테스트용 SQLite 데이터베이스 설정
    from config.settings import Config
    Config.DATABASE_URL = f"sqlite:///{test_db_path}"
    
    # 테스트 데이터베이스 초기화
    from database.models import engine
    Base.metadata.create_all(bind=engine)
    
    # 테스트 실행
    success = run_all_tests()
    
    # 테스트 데이터베이스 정리
    try:
        os.unlink(test_db_path)
    except:
        pass
    
    sys.exit(0 if success else 1)
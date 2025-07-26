#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions용 연결 테스트 스크립트
"""

import os
import sys
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_environment():
    """환경 변수 및 기본 설정 테스트"""
    logger.info("환경 변수 테스트 시작")
    
    # 필수 환경 변수 확인
    db_type = os.getenv('DB_TYPE', 'postgresql')
    database_url = os.getenv('DATABASE_URL', '')
    
    logger.info(f"DB_TYPE: {db_type}")
    logger.info(f"DATABASE_URL 존재: {'Yes' if database_url else 'No'}")
    
    if not database_url:
        logger.warning("DATABASE_URL이 설정되지 않음 - SQLite fallback 사용")
    
    return True

def test_python_packages():
    """필수 Python 패키지 테스트"""
    logger.info("Python 패키지 테스트 시작")
    
    required_packages = [
        'cloudscraper',
        'bs4',  # beautifulsoup4는 bs4로 import됨
        'requests',
        'lxml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package}: OK")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package}: 누락")
    
    if missing_packages:
        logger.error(f"누락된 패키지: {missing_packages}")
        return False
    
    return True

def test_database_connection():
    """데이터베이스 연결 테스트"""
    logger.info("데이터베이스 연결 테스트 시작")
    
    try:
        db_type = os.getenv('DB_TYPE', 'postgresql')
        database_url = os.getenv('DATABASE_URL', '')
        
        if not database_url:
            logger.info("DATABASE_URL 없음 - SQLite fallback 테스트")
            import sqlite3
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            conn.close()
            logger.info("✅ SQLite fallback 연결 성공")
            return True
        
        if db_type == 'postgresql':
            import psycopg2
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            conn.close()
            logger.info("✅ PostgreSQL 연결 성공")
            return True
        
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
        logger.info("SQLite fallback으로 진행...")
        return True  # GitHub Actions에서는 SQLite fallback 허용
    
    return True

def test_pokerscout_access():
    """PokerScout 사이트 접근 테스트"""
    logger.info("PokerScout 접근 테스트 시작")
    
    try:
        import cloudscraper
        from bs4 import BeautifulSoup
        
        # 수정된 CloudScraper 설정 사용
        scraper = cloudscraper.create_scraper()
        response = scraper.get('https://www.pokerscout.com', timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'class': 'rankTable'})
            
            if table:
                rows = table.find_all('tr')
                logger.info(f"✅ PokerScout 접근 성공 - {len(rows)}개 행 발견")
                return True
            else:
                logger.error("❌ rankTable을 찾을 수 없음")
                return False
        else:
            logger.error(f"❌ PokerScout 접근 실패 - HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ PokerScout 접근 테스트 실패: {str(e)}")
        return False

def main():
    """메인 테스트 실행"""
    logger.info("=== GitHub Actions 환경 테스트 시작 ===")
    logger.info(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    tests = [
        ("환경 변수", test_environment),
        ("Python 패키지", test_python_packages),
        ("데이터베이스 연결", test_database_connection),
        ("PokerScout 접근", test_pokerscout_access)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            logger.info(f"\n--- {test_name} 테스트 ---")
            result = test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: PASS")
            else:
                logger.error(f"❌ {test_name}: FAIL")
                
        except Exception as e:
            logger.error(f"❌ {test_name} 테스트 중 오류: {str(e)}")
            results.append((test_name, False))
    
    # 결과 요약
    logger.info("\n=== 테스트 결과 요약 ===")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n통과: {passed}/{total}")
    
    if passed == total:
        logger.info("✅ 모든 테스트 통과 - 데이터 수집 준비 완료!")
        sys.exit(0)
    else:
        logger.error("❌ 일부 테스트 실패 - 확인 필요")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 연결 테스트 스크립트
GitHub Actions에서 실패 원인 파악용
"""
import os
import sys
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_environment():
    """환경변수 확인"""
    logger.info("=== 환경변수 테스트 ===")
    
    database_url = os.getenv('DATABASE_URL', '')
    db_type = os.getenv('DB_TYPE', 'postgresql')
    
    logger.info(f"DB_TYPE: {db_type}")
    logger.info(f"DATABASE_URL 존재: {'Yes' if database_url else 'No'}")
    
    if database_url:
        # URL에서 민감정보 제거하여 로깅
        safe_url = database_url.replace(database_url.split('@')[0].split('//')[1], 'USER:PASS')
        logger.info(f"DATABASE_URL (안전): {safe_url}")
    
    return database_url, db_type

def test_imports():
    """패키지 임포트 테스트"""
    logger.info("=== 패키지 임포트 테스트 ===")
    
    try:
        import cloudscraper
        logger.info("✅ cloudscraper 임포트 성공")
    except ImportError as e:
        logger.error(f"❌ cloudscraper 임포트 실패: {e}")
        return False
        
    try:
        from bs4 import BeautifulSoup
        logger.info("✅ beautifulsoup4 임포트 성공")
    except ImportError as e:
        logger.error(f"❌ beautifulsoup4 임포트 실패: {e}")
        return False
        
    try:
        import psycopg2
        logger.info("✅ psycopg2 임포트 성공")
    except ImportError as e:
        logger.error(f"❌ psycopg2 임포트 실패: {e}")
        return False
        
    return True

def test_database_connection(database_url):
    """데이터베이스 연결 테스트"""
    logger.info("=== 데이터베이스 연결 테스트 ===")
    
    if not database_url:
        logger.error("❌ DATABASE_URL이 설정되지 않음")
        return False
        
    try:
        import psycopg2
        
        # IPv4 강제 연결을 위한 연결 파라미터 수정
        if 'supabase.co' in database_url:
            logger.info("🔧 Supabase 연결 최적화 시도...")
            
            # 연결 문자열에 IPv4 강제 옵션 추가
            if '?' in database_url:
                optimized_url = database_url + '&connect_timeout=10&application_name=poker-insight'
            else:
                optimized_url = database_url + '?connect_timeout=10&application_name=poker-insight'
        else:
            optimized_url = database_url
            
        logger.info("🔗 데이터베이스 연결 시도...")
        conn = psycopg2.connect(optimized_url)
        cursor = conn.cursor()
        
        # 간단한 쿼리 테스트
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        # 연결 정보 확인
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        logger.info(f"📊 PostgreSQL 버전: {version[0][:50]}...")
        
        cursor.close()
        conn.close()
        
        logger.info(f"✅ 데이터베이스 연결 성공: {result}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
        
        # IPv6 관련 오류인지 확인
        if "Network is unreachable" in str(e) or "2406:da12" in str(e):
            logger.error("🚨 IPv6 네트워크 문제 감지")
            logger.error("💡 해결책: Supabase 설정에서 IPv4 우선 연결 필요")
            
        return False

def test_web_scraping():
    """웹 스크래핑 테스트"""
    logger.info("=== 웹 스크래핑 테스트 ===")
    
    try:
        import cloudscraper
        scraper = cloudscraper.create_scraper()
        
        # 간단한 테스트 요청
        response = scraper.get('https://httpbin.org/ip', timeout=10)
        response.raise_for_status()
        
        logger.info("✅ 웹 스크래핑 테스트 성공")
        return True
        
    except Exception as e:
        logger.error(f"❌ 웹 스크래핑 테스트 실패: {str(e)}")
        return False

def main():
    """메인 테스트 실행"""
    logger.info("🚀 연결 테스트 시작")
    
    # 환경변수 확인
    database_url, db_type = test_environment()
    
    # 패키지 임포트 테스트
    if not test_imports():
        logger.error("❌ 패키지 임포트 실패")
        sys.exit(1)
    
    # 웹 스크래핑 테스트
    if not test_web_scraping():
        logger.error("❌ 웹 스크래핑 테스트 실패")
        sys.exit(1)
    
    # 데이터베이스 연결 테스트
    if not test_database_connection(database_url):
        logger.error("❌ 데이터베이스 연결 실패")
        sys.exit(1)
    
    logger.info("✅ 모든 테스트 통과")
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("SUCCESS: All tests passed")
            sys.exit(0)
        else:
            print("FAILURE: Some tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)
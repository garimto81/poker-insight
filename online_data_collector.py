#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
온라인 기반 포커 데이터 수집기
- GitHub Actions에서 매일 자동 실행
- 온라인 데이터베이스 연동 (PostgreSQL/MySQL)
- Discord/Slack 알림
- 웹 대시보드 자동 업데이트
"""
import os
import sys
import json
import logging
import requests
from datetime import datetime, timedelta
import cloudscraper
from bs4 import BeautifulSoup
import re

# 환경변수에 따른 데이터베이스 설정
DB_TYPE = os.getenv('DB_TYPE', 'postgresql')  # postgresql, mysql, sqlite  
DATABASE_URL = os.getenv('DATABASE_URL', '')

if DB_TYPE == 'postgresql':
    import psycopg2
    from psycopg2.extras import RealDictCursor
elif DB_TYPE == 'mysql':
    import pymysql
else:
    import sqlite3

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('online_collection.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class OnlineDataCollector:
    def __init__(self):
        self.db_url = DATABASE_URL
        # DATABASE_URL이 없으면 자동으로 SQLite 사용
        self.use_sqlite_fallback = not bool(DATABASE_URL)
        # 정확한 데이터를 위해 올바른 CloudScraper 설정 사용 (방법 1)
        self.scraper = cloudscraper.create_scraper()
        # PokerScout의 모든 사이트를 수집하므로 특정 타겟 제한 없음
        self.gg_poker_sites = ['GGNetwork', 'GGPoker ON', 'GG Poker', 'GGPoker']  # GG POKER 식별용
        self.setup_database()
        
    def get_db_connection(self):
        """데이터베이스 연결"""
        try:
            # SQLite fallback이 활성화된 경우
            if self.use_sqlite_fallback:
                logger.info("Using SQLite fallback mode")
                import sqlite3
                return sqlite3.connect('github_actions_fallback.db')
            
            if DB_TYPE == 'postgresql':
                if not self.db_url:
                    raise ValueError("DATABASE_URL is not set")
                
                # Supabase 연결 최적화
                if 'supabase.co' in self.db_url:
                    logger.info("Optimizing Supabase connection...")
                    if '?' in self.db_url:
                        optimized_url = self.db_url + '&connect_timeout=10&application_name=poker-insight'
                    else:
                        optimized_url = self.db_url + '?connect_timeout=10&application_name=poker-insight'
                    return psycopg2.connect(optimized_url)
                else:
                    return psycopg2.connect(self.db_url)
            elif DB_TYPE == 'mysql':
                if not self.db_url:
                    raise ValueError("DATABASE_URL is not set")
                return pymysql.connect(self.db_url)
            else:
                return sqlite3.connect('online_poker_data.db')
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            logger.error(f"DB_TYPE: {DB_TYPE}")
            logger.error(f"DATABASE_URL exists: {'Yes' if self.db_url else 'No'}")
            
            # IPv6 네트워크 문제 감지 시 SQLite로 fallback
            if "Network is unreachable" in str(e) and 'supabase.co' in str(self.db_url):
                logger.warning("Supabase IPv6 network issue detected")
                logger.warning("Switching to SQLite fallback automatically...")
                
                self.use_sqlite_fallback = True
                try:
                    import sqlite3
                    conn = sqlite3.connect('github_actions_fallback.db')
                    logger.info("SQLite fallback enabled successfully")
                    return conn
                except Exception as fallback_error:
                    logger.error(f"SQLite fallback also failed: {fallback_error}")
                    raise fallback_error
            
            # 연결 문자열에서 민감정보 제거하여 로깅
            if self.db_url:
                try:
                    safe_url = self.db_url.split('@')[1] if '@' in self.db_url else 'invalid_format'
                    logger.error(f"DB Host: {safe_url}")
                except:
                    logger.error("Failed to parse DB URL")
            raise
    
    def setup_database(self):
        """데이터베이스 테이블 설정"""
        logger.info("Setting up online database...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # PostgreSQL/MySQL용 SQL (SQLite fallback이 아닌 경우)
            if not self.use_sqlite_fallback and DB_TYPE in ['postgresql', 'mysql']:
                sql_commands = [
                    """
                    CREATE TABLE IF NOT EXISTS daily_traffic (
                        id SERIAL PRIMARY KEY,
                        site_name VARCHAR(100) NOT NULL,
                        collection_date DATE NOT NULL,
                        collection_time TIME NOT NULL,
                        players_online INTEGER NOT NULL,
                        cash_players INTEGER NOT NULL,
                        peak_24h INTEGER,
                        seven_day_avg INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(site_name, collection_date, collection_time)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS collection_stats (
                        id SERIAL PRIMARY KEY,
                        collection_date DATE NOT NULL,
                        collection_time TIME NOT NULL,
                        total_sites INTEGER,
                        gg_poker_sites INTEGER,
                        total_players INTEGER,
                        success BOOLEAN DEFAULT TRUE,
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS poker_events (
                        id SERIAL PRIMARY KEY,
                        event_date DATE NOT NULL,
                        event_title VARCHAR(500) NOT NULL,
                        event_type VARCHAR(50) NOT NULL,
                        affected_sites TEXT,
                        impact_level VARCHAR(20),
                        description TEXT,
                        news_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                ]
            else:
                # SQLite용 SQL (로컬 테스트용)
                sql_commands = [
                    """
                    CREATE TABLE IF NOT EXISTS daily_traffic (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        site_name TEXT NOT NULL,
                        collection_date DATE NOT NULL,
                        collection_time TIME NOT NULL,
                        players_online INTEGER NOT NULL,
                        cash_players INTEGER NOT NULL,
                        peak_24h INTEGER,
                        seven_day_avg INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(site_name, collection_date, collection_time)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS collection_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        collection_date DATE NOT NULL,
                        collection_time TIME NOT NULL,
                        total_sites INTEGER,
                        gg_poker_sites INTEGER,
                        total_players INTEGER,
                        success BOOLEAN DEFAULT TRUE,
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS poker_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_date DATE NOT NULL,
                        event_title TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        affected_sites TEXT,
                        impact_level TEXT,
                        description TEXT,
                        news_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                ]
            
            for sql in sql_commands:
                cursor.execute(sql)
            
            conn.commit()
            conn.close()
            logger.info("Database setup complete")
            
        except Exception as e:
            logger.error(f"Database setup failed: {str(e)}")
            raise
    
    def crawl_pokerscout_data(self):
        """PokerScout 크롤링 - 수정된 올바른 로직"""
        logger.info("Starting PokerScout online crawling...")
        
        try:
            # 올바른 CloudScraper 사용 (성공한 로직과 동일)
            response = self.scraper.get('https://www.pokerscout.com', timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'class': 'rankTable'})
            
            if not table:
                logger.error("Could not find PokerScout table")
                return []
            
            collected_data = []
            rows = table.find_all('tr')[1:]  # Skip header
            logger.info(f"Found rows: {len(rows)}")
            
            for i, row in enumerate(rows):
                try:
                    # 광고 행 건너뛰기 - 중요!
                    if 'cus_top_traffic_coin' in row.get('class', []):
                        logger.info(f"Row {i+1}: Skipping ad row")
                        continue
                    
                    # 사이트명 추출
                    brand_title = row.find('span', {'class': 'brand-title'})
                    if not brand_title:
                        continue
                    
                    site_name = brand_title.get_text(strip=True)
                    if not site_name or len(site_name) < 2:
                        continue
                    
                    # Players Online 추출 (성공한 로직과 정확히 동일)
                    players_online = 0
                    online_td = row.find('td', {'id': 'online'})
                    if online_td:
                        online_span = online_td.find('span')
                        if online_span:
                            online_text = online_span.get_text(strip=True).replace(',', '')
                            if online_text.isdigit():
                                players_online = int(online_text)
                    
                    # Cash Players 추출 (성공한 로직과 정확히 동일)
                    cash_players = 0
                    cash_td = row.find('td', {'id': 'cash'})
                    if cash_td:
                        cash_text = cash_td.get_text(strip=True).replace(',', '')
                        if cash_text.isdigit():
                            cash_players = int(cash_text)
                    
                    # 24H Peak 추출
                    peak_24h = 0
                    peak_td = row.find('td', {'id': 'peak'})
                    if peak_td:
                        peak_text = peak_td.get_text(strip=True).replace(',', '')
                        if peak_text.isdigit():
                            peak_24h = int(peak_text)
                    
                    # 7 Day Average 추출
                    seven_day_avg = 0
                    avg_td = row.find('td', {'id': 'avg'})
                    if avg_td:
                        avg_text = avg_td.get_text(strip=True).replace(',', '')
                        if avg_text.isdigit():
                            seven_day_avg = int(avg_text)
                    
                    # 사이트명 정규화
                    site_name = self.normalize_site_name(site_name)
                    
                    site_data = {
                        'site_name': site_name,
                        'players_online': players_online,
                        'cash_players': cash_players,
                        'peak_24h': peak_24h,
                        'seven_day_avg': seven_day_avg
                    }
                    
                    collected_data.append(site_data)
                    
                    # GG POKER 사이트는 특별 표시
                    is_gg = any(gg in site_name for gg in self.gg_poker_sites)
                    status = "TARGET" if is_gg else "OK"
                    logger.info(f"{status} {site_name}: {players_online:,} players (cash: {cash_players:,})")
                    
                except Exception as e:
                    logger.error(f"Error parsing row {i+1}: {str(e)}")
                    continue
            
            logger.info(f"Crawling complete: {len(collected_data)} sites")
            return collected_data
            
        except Exception as e:
            logger.error(f"PokerScout crawling failed: {str(e)}")
            return []
    
    def normalize_site_name(self, raw_name):
        """사이트명 정규화"""
        name_mapping = {
            'ggnetwork': 'GGNetwork',
            'gg network': 'GGNetwork',
            'ggpoker': 'GGNetwork',
            'gg poker': 'GGNetwork',
            'ggpoker on': 'GGPoker ON',
            'pokerstars': 'PokerStars',
            'pokerstars ontario': 'PokerStars Ontario',
            'wpt global': 'WPT Global',
            '888poker': '888poker',
            'partypoker': 'partypoker',
            'chico poker': 'Chico Poker',
            'ipoker': 'iPoker',
            'winamax': 'Winamax'
        }
        
        normalized = raw_name.lower().strip()
        return name_mapping.get(normalized, raw_name)
    
    def save_data_to_online_db(self, data):
        """온라인 데이터베이스에 저장"""
        if not data:
            logger.error("No data to save")
            return False
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            collection_date = datetime.now().strftime('%Y-%m-%d')
            collection_time = datetime.now().strftime('%H:%M:%S')
            
            saved_count = 0
            gg_poker_count = 0
            total_players = 0
            
            for site_data in data:
                try:
                    if not self.use_sqlite_fallback and DB_TYPE in ['postgresql', 'mysql']:
                        sql = """
                        INSERT INTO daily_traffic 
                        (site_name, collection_date, collection_time, players_online, 
                         cash_players, peak_24h, seven_day_avg)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (site_name, collection_date, collection_time) 
                        DO UPDATE SET 
                            players_online = EXCLUDED.players_online,
                            cash_players = EXCLUDED.cash_players,
                            peak_24h = EXCLUDED.peak_24h,
                            seven_day_avg = EXCLUDED.seven_day_avg
                        """
                    else:
                        sql = """
                        INSERT OR REPLACE INTO daily_traffic 
                        (site_name, collection_date, collection_time, players_online, 
                         cash_players, peak_24h, seven_day_avg)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """
                    
                    cursor.execute(sql, (
                        site_data['site_name'],
                        collection_date,
                        collection_time,
                        site_data['players_online'],
                        site_data['cash_players'],
                        site_data['peak_24h'],
                        site_data['seven_day_avg']
                    ))
                    
                    saved_count += 1
                    total_players += site_data['players_online']
                    
                    # GG POKER 사이트 카운트
                    if any(gg in site_data['site_name'] for gg in self.gg_poker_sites):
                        gg_poker_count += 1
                        
                except Exception as e:
                    logger.error(f"Failed to save {site_data['site_name']}: {str(e)}")
            
            # 수집 통계 저장
            if not self.use_sqlite_fallback and DB_TYPE in ['postgresql', 'mysql']:
                stats_sql = """
                INSERT INTO collection_stats 
                (collection_date, collection_time, total_sites, gg_poker_sites, total_players)
                VALUES (%s, %s, %s, %s, %s)
                """
            else:
                stats_sql = """
                INSERT INTO collection_stats 
                (collection_date, collection_time, total_sites, gg_poker_sites, total_players)
                VALUES (?, ?, ?, ?, ?)
                """
            
            cursor.execute(stats_sql, (
                collection_date, collection_time, saved_count, gg_poker_count, total_players
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved to online DB:")
            logger.info(f"  Sites: {saved_count}")
            logger.info(f"  GG POKER: {gg_poker_count}")
            logger.info(f"  Total Players: {total_players:,}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save to online DB: {str(e)}")
            return False
    
    def run_online_collection(self):
        """온라인 데이터 수집 실행"""
        start_time = datetime.now()
        logger.info(f"Starting online data collection: {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        try:
            # 크롤링
            data = self.crawl_pokerscout_data()
            
            if not data:
                logger.error("No data crawled")
                return False
            
            # 온라인 DB 저장
            success = self.save_data_to_online_db(data)
            
            # 수집 리포트 생성
            if success:
                self.generate_collection_report(data, start_time)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Online collection complete (Duration: {duration:.1f}s)")
            return success
            
        except Exception as e:
            logger.error(f"Online collection failed: {str(e)}")
            return False
    
    def generate_collection_report(self, data, start_time):
        """수집 리포트 생성"""
        end_time = datetime.now()
        
        report = {
            'timestamp': end_time.isoformat(),
            'collection_start': start_time.isoformat(),
            'collection_end': end_time.isoformat(),
            'duration_seconds': (end_time - start_time).total_seconds(),
            'total_sites': len(data),
            'gg_poker_sites': len([d for d in data if 'GG' in d['site_name']]),
            'total_players': sum(d['players_online'] for d in data),
            'total_cash_players': sum(d['cash_players'] for d in data),
            'sites_data': data,
            'success': True
        }
        
        # JSON 리포트 저장
        filename = f"collection_report_{end_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Collection report saved: {filename}")
        return filename

def main():
    """메인 실행"""
    print("Starting Online Poker Data Collector")
    print("=" * 50)
    
    try:
        # 환경변수 확인
        db_url = os.getenv('DATABASE_URL', '')
        db_type = os.getenv('DB_TYPE', 'postgresql')
        
        logger.info(f"Checking environment variables:")
        logger.info(f"  DB_TYPE: {db_type}")
        logger.info(f"  DATABASE_URL exists: {'Yes' if db_url else 'No'}")
        
        if not db_url:
            logger.warning("[WARNING] DATABASE_URL not set, using SQLite fallback")
            print("[INFO] Using SQLite fallback for local execution")
        
        collector = OnlineDataCollector()
        success = collector.run_online_collection()
        
        if success:
            print("Online data collection successful")
            logger.info("Entire process complete")
            sys.exit(0)
        else:
            print("Online data collection failed")
            logger.error("Data collection process failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
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
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'linux', 'mobile': False}
        )
        # PokerScout의 모든 사이트를 수집하므로 특정 타겟 제한 없음
        self.gg_poker_sites = ['GGNetwork', 'GGPoker ON', 'GG Poker', 'GGPoker']  # GG POKER 식별용
        self.setup_database()
        
    def get_db_connection(self):
        """데이터베이스 연결"""
        try:
            if DB_TYPE == 'postgresql':
                if not self.db_url:
                    raise ValueError("DATABASE_URL이 설정되지 않았습니다")
                return psycopg2.connect(self.db_url)
            elif DB_TYPE == 'mysql':
                if not self.db_url:
                    raise ValueError("DATABASE_URL이 설정되지 않았습니다")
                return pymysql.connect(self.db_url)
            else:
                return sqlite3.connect('online_poker_data.db')
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {str(e)}")
            logger.error(f"DB_TYPE: {DB_TYPE}")
            logger.error(f"DATABASE_URL 존재: {'Yes' if self.db_url else 'No'}")
            # 연결 문자열에서 민감정보 제거하여 로깅
            if self.db_url:
                try:
                    safe_url = self.db_url.split('@')[1] if '@' in self.db_url else 'invalid_format'
                    logger.error(f"DB 호스트: {safe_url}")
                except:
                    logger.error("DB URL 파싱 실패")
            raise
    
    def setup_database(self):
        """데이터베이스 테이블 설정"""
        logger.info("📊 온라인 데이터베이스 설정...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # PostgreSQL/MySQL용 SQL
            if DB_TYPE in ['postgresql', 'mysql']:
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
            logger.info("✅ 데이터베이스 설정 완료")
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 설정 실패: {str(e)}")
            raise
    
    def crawl_pokerscout_data(self):
        """PokerScout 크롤링"""
        logger.info("🔍 PokerScout 온라인 크롤링 시작...")
        
        try:
            response = self.scraper.get('https://www.pokerscout.com', timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'class': 'rankTable'})
            
            if not table:
                logger.error("❌ PokerScout 테이블을 찾을 수 없습니다")
                return []
            
            collected_data = []
            rows = table.find_all('tr')[1:]
            
            for row in rows:
                try:
                    cells = row.find_all('td')
                    if len(cells) < 6:
                        continue
                    
                    site_name = cells[1].get_text(strip=True)
                    
                    # 모든 사이트 수집 (필터링 제거)
                    if not site_name or site_name.strip() == '':
                        continue
                    
                    # 데이터 추출
                    players_text = cells[2].get_text(strip=True).replace(',', '')
                    players_online = int(re.sub(r'[^\d]', '', players_text)) if re.sub(r'[^\d]', '', players_text) else 0
                    
                    cash_text = cells[3].get_text(strip=True).replace(',', '')
                    cash_players = int(re.sub(r'[^\d]', '', cash_text)) if re.sub(r'[^\d]', '', cash_text) else 0
                    
                    peak_text = cells[4].get_text(strip=True).replace(',', '')
                    peak_24h = int(re.sub(r'[^\d]', '', peak_text)) if re.sub(r'[^\d]', '', peak_text) else 0
                    
                    avg_text = cells[5].get_text(strip=True).replace(',', '')
                    seven_day_avg = int(re.sub(r'[^\d]', '', avg_text)) if re.sub(r'[^\d]', '', avg_text) else 0
                    
                    # 최소 플레이어 수가 있는 사이트만 포함 (노이즈 제거)
                    if players_online == 0 and cash_players == 0:
                        continue
                    
                    site_data = {
                        'site_name': site_name,  # 원본 사이트명 사용
                        'players_online': players_online,
                        'cash_players': cash_players,
                        'peak_24h': peak_24h,
                        'seven_day_avg': seven_day_avg
                    }
                    
                    collected_data.append(site_data)
                    
                    # GG POKER 사이트는 특별 표시
                    is_gg = any(gg in site_name for gg in self.gg_poker_sites)
                    emoji = "🎯" if is_gg else "✅"
                    logger.info(f"{emoji} {site_name}: {players_online:,}명")
                    
                except Exception as e:
                    logger.error(f"❌ 행 파싱 오류: {str(e)}")
                    continue
            
            logger.info(f"🎯 크롤링 완료: {len(collected_data)}개 사이트")
            return collected_data
            
        except Exception as e:
            logger.error(f"❌ PokerScout 크롤링 실패: {str(e)}")
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
            logger.error("❌ 저장할 데이터가 없습니다")
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
                    if DB_TYPE in ['postgresql', 'mysql']:
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
                    logger.error(f"❌ {site_data['site_name']} 저장 실패: {str(e)}")
            
            # 수집 통계 저장
            if DB_TYPE in ['postgresql', 'mysql']:
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
            
            logger.info(f"💾 온라인 DB 저장 완료:")
            logger.info(f"  📊 사이트: {saved_count}개")
            logger.info(f"  🎯 GG POKER: {gg_poker_count}개")
            logger.info(f"  👥 총 플레이어: {total_players:,}명")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 온라인 DB 저장 실패: {str(e)}")
            return False
    
    def run_online_collection(self):
        """온라인 데이터 수집 실행"""
        start_time = datetime.now()
        logger.info(f"🚀 온라인 데이터 수집 시작: {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        try:
            # 크롤링
            data = self.crawl_pokerscout_data()
            
            if not data:
                logger.error("❌ 크롤링 데이터 없음")
                return False
            
            # 온라인 DB 저장
            success = self.save_data_to_online_db(data)
            
            # 수집 리포트 생성
            if success:
                self.generate_collection_report(data, start_time)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ 온라인 수집 완료 (소요: {duration:.1f}초)")
            return success
            
        except Exception as e:
            logger.error(f"❌ 온라인 수집 실패: {str(e)}")
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
        
        logger.info(f"📋 수집 리포트 저장: {filename}")
        return filename

def main():
    """메인 실행"""
    print("온라인 포커 데이터 수집기 시작")
    print("=" * 50)
    
    try:
        # 환경변수 확인
        db_url = os.getenv('DATABASE_URL', '')
        db_type = os.getenv('DB_TYPE', 'postgresql')
        
        logger.info(f"환경변수 확인:")
        logger.info(f"  DB_TYPE: {db_type}")
        logger.info(f"  DATABASE_URL 존재: {'Yes' if db_url else 'No'}")
        
        if not db_url:
            logger.error("❌ DATABASE_URL 환경변수가 설정되지 않았습니다")
            print("FAILED: DATABASE_URL not set")
            sys.exit(1)
        
        collector = OnlineDataCollector()
        success = collector.run_online_collection()
        
        if success:
            print("온라인 데이터 수집 성공")
            logger.info("✅ 전체 프로세스 완료")
            sys.exit(0)
        else:
            print("온라인 데이터 수집 실패")
            logger.error("❌ 데이터 수집 프로세스 실패")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ 치명적 오류: {str(e)}")
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
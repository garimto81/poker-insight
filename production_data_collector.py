#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
운영용 포커 사이트 데이터 수집기
- GG POKER 데이터 포함 크롤링
- 4개 핵심 지표 자동 수집
- 한 달간 일일 데이터 축적
- CloudScraper를 통한 안정적 수집
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import os
import time
import logging
import sqlite3
from datetime import datetime, timedelta
import cloudscraper
from bs4 import BeautifulSoup
import re
import json
from gg_poker_monitoring import GGPokerMonitoringPlatform

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('poker_data_collection.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProductionDataCollector:
    def __init__(self, db_path='gg_poker_monitoring.db'):
        self.db_path = db_path
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )
        self.monitoring_platform = GGPokerMonitoringPlatform(db_path)
        self.setup_target_sites()
        
    def setup_target_sites(self):
        """수집 대상 사이트 설정 (GG POKER 포함)"""
        self.target_sites = {
            # GG POKER 네트워크 (최고 우선순위)
            'GGNetwork': {
                'priority': 1,
                'category': 'GG_POKER',
                'expected_players': 130000
            },
            'GGPoker ON': {
                'priority': 1, 
                'category': 'GG_POKER',
                'expected_players': 5000
            },
            
            # Tier 1 직접 경쟁사
            'PokerStars': {
                'priority': 2,
                'category': 'DIRECT_COMPETITOR',
                'expected_players': 55000
            },
            'PokerStars Ontario': {
                'priority': 2,
                'category': 'DIRECT_COMPETITOR', 
                'expected_players': 55000
            },
            
            # Tier 2 주요 경쟁사
            'WPT Global': {
                'priority': 3,
                'category': 'MAJOR_COMPETITOR',
                'expected_players': 3000
            },
            '888poker': {
                'priority': 3,
                'category': 'MAJOR_COMPETITOR',
                'expected_players': 2000
            },
            'partypoker': {
                'priority': 3,
                'category': 'MAJOR_COMPETITOR',
                'expected_players': 1500
            },
            
            # Tier 3 기타 경쟁사
            'Chico Poker': {
                'priority': 4,
                'category': 'OTHER_COMPETITOR',
                'expected_players': 2000
            },
            'iPoker': {
                'priority': 4,
                'category': 'OTHER_COMPETITOR',
                'expected_players': 1000
            },
            'Winamax': {
                'priority': 4,
                'category': 'OTHER_COMPETITOR',
                'expected_players': 800
            }
        }
        
        logger.info(f"📋 수집 대상 사이트 설정 완료: {len(self.target_sites)}개")
        
    def crawl_pokerscout_data(self):
        """PokerScout에서 실시간 데이터 크롤링"""
        logger.info("🔍 PokerScout 데이터 크롤링 시작...")
        
        try:
            # PokerScout 메인 페이지 크롤링
            response = self.scraper.get('https://www.pokerscout.com', timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 랭킹 테이블 찾기
            table = soup.find('table', {'class': 'rankTable'})
            if not table:
                logger.error("❌ PokerScout 랭킹 테이블을 찾을 수 없습니다")
                return []
            
            collected_data = []
            rows = table.find_all('tr')[1:]  # 헤더 제외
            
            for row in rows:
                try:
                    cells = row.find_all('td')
                    if len(cells) < 6:
                        continue
                    
                    # 사이트명 추출
                    site_name_cell = cells[1]
                    site_name = site_name_cell.get_text(strip=True)
                    
                    # 정확한 사이트명 매칭
                    normalized_site = self.normalize_site_name(site_name)
                    if normalized_site not in self.target_sites:
                        continue
                    
                    # 플레이어 수 추출
                    players_text = cells[2].get_text(strip=True).replace(',', '')
                    players_online = int(re.sub(r'[^\d]', '', players_text)) if players_text.isdigit() else 0
                    
                    # 캐시 플레이어 추출
                    cash_text = cells[3].get_text(strip=True).replace(',', '')
                    cash_players = int(re.sub(r'[^\d]', '', cash_text)) if cash_text.isdigit() else 0
                    
                    # 24시간 피크 추출
                    peak_text = cells[4].get_text(strip=True).replace(',', '')
                    peak_24h = int(re.sub(r'[^\d]', '', peak_text)) if peak_text.isdigit() else 0
                    
                    # 7일 평균 추출
                    avg_text = cells[5].get_text(strip=True).replace(',', '')
                    seven_day_avg = int(re.sub(r'[^\d]', '', avg_text)) if avg_text.isdigit() else 0
                    
                    site_data = {
                        'site_name': normalized_site,
                        'players_online': players_online,
                        'cash_players': cash_players,
                        'peak_24h': peak_24h,
                        'seven_day_avg': seven_day_avg,
                        'collection_time': datetime.now().isoformat(),
                        'source': 'PokerScout'
                    }
                    
                    collected_data.append(site_data)
                    
                    logger.info(f"✅ {normalized_site}: {players_online:,}명 (캐시: {cash_players:,}명)")
                    
                except Exception as e:
                    logger.error(f"❌ 행 파싱 오류: {str(e)}")
                    continue
            
            logger.info(f"🎯 PokerScout 크롤링 완료: {len(collected_data)}개 사이트")
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
            'pokerstars.it': 'PokerStars.it',
            'wpt global': 'WPT Global',
            'worldpokertour': 'WPT Global',
            '888poker': '888poker',
            '888 poker': '888poker',
            'partypoker': 'partypoker',
            'party poker': 'partypoker',
            'chico poker': 'Chico Poker',
            'chico': 'Chico Poker',
            'ipoker': 'iPoker',
            'winamax': 'Winamax'
        }
        
        normalized = raw_name.lower().strip()
        return name_mapping.get(normalized, raw_name)
    
    def validate_data_quality(self, data):
        """데이터 품질 검증"""
        validated_data = []
        
        for site_data in data:
            site_name = site_data['site_name']
            players = site_data['players_online']
            
            # 예상 플레이어 수와 비교하여 이상치 검증
            expected = self.target_sites.get(site_name, {}).get('expected_players', 0)
            
            # 너무 크거나 작은 값 필터링
            if expected > 0:
                ratio = players / expected if expected > 0 else 0
                if ratio > 10 or ratio < 0.01:  # 10배 초과 또는 1% 미만
                    logger.warning(f"⚠️ {site_name} 이상치 감지: {players:,}명 (예상: {expected:,}명)")
                    continue
            
            # 기본적인 범위 검증
            if players < 0 or players > 500000:  # 음수이거나 50만 초과
                logger.warning(f"⚠️ {site_name} 범위 초과: {players:,}명")
                continue
            
            # 캐시 플레이어가 총 플레이어보다 많은 경우
            if site_data['cash_players'] > players:
                logger.warning(f"⚠️ {site_name} 캐시 플레이어 수 이상: {site_data['cash_players']:,} > {players:,}")
                site_data['cash_players'] = players  # 수정
            
            validated_data.append(site_data)
        
        logger.info(f"✅ 데이터 검증 완료: {len(validated_data)}/{len(data)}개 유효")
        return validated_data
    
    def save_daily_data(self, data):
        """일일 데이터 저장"""
        if not data:
            logger.error("❌ 저장할 데이터가 없습니다")
            return False
        
        try:
            collected_count = self.monitoring_platform.collect_daily_data(data)
            
            # 수집 통계 로깅
            collection_stats = {
                'collection_date': datetime.now().strftime('%Y-%m-%d'),
                'collection_time': datetime.now().strftime('%H:%M:%S'),
                'total_sites_collected': collected_count,
                'gg_poker_sites': len([d for d in data if 'GG' in d['site_name']]),
                'total_players': sum(d['players_online'] for d in data),
                'total_cash_players': sum(d['cash_players'] for d in data)
            }
            
            logger.info(f"💾 일일 데이터 저장 완료:")
            logger.info(f"  📊 수집 사이트: {collection_stats['total_sites_collected']}개")
            logger.info(f"  🎯 GG POKER: {collection_stats['gg_poker_sites']}개 사이트")
            logger.info(f"  👥 총 플레이어: {collection_stats['total_players']:,}명")
            logger.info(f"  💰 캐시 플레이어: {collection_stats['total_cash_players']:,}명")
            
            # 수집 통계 저장
            self.save_collection_stats(collection_stats)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 데이터 저장 실패: {str(e)}")
            return False
    
    def save_collection_stats(self, stats):
        """수집 통계 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 수집 통계 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collection_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_date DATE NOT NULL,
                collection_time TIME NOT NULL,
                total_sites_collected INTEGER,
                gg_poker_sites INTEGER,
                total_players INTEGER,
                total_cash_players INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            INSERT INTO collection_stats 
            (collection_date, collection_time, total_sites_collected, gg_poker_sites,
             total_players, total_cash_players)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            stats['collection_date'],
            stats['collection_time'],
            stats['total_sites_collected'],
            stats['gg_poker_sites'],
            stats['total_players'],
            stats['total_cash_players']
        ))
        
        conn.commit()
        conn.close()
    
    def run_daily_collection(self):
        """일일 데이터 수집 실행"""
        start_time = datetime.now()
        logger.info(f"🚀 일일 데이터 수집 시작: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 1. PokerScout 크롤링
            raw_data = self.crawl_pokerscout_data()
            
            if not raw_data:
                logger.error("❌ 크롤링 데이터가 없습니다")
                return False
            
            # 2. 데이터 검증
            validated_data = self.validate_data_quality(raw_data)
            
            # 3. 데이터 저장
            success = self.save_daily_data(validated_data)
            
            # 4. 변화 감지 (전일 대비)
            if success:
                changes = self.monitoring_platform.detect_significant_changes()
                if changes:
                    logger.info(f"🚨 유의미한 변화 감지: {len(changes)}건")
                    for change in changes[:3]:  # 상위 3개만 로깅
                        logger.info(f"  📈 {change['site_name']}: {change['metric']} {change['change_percentage']:+.1f}%")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ 일일 데이터 수집 완료 (소요시간: {duration:.1f}초)")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 일일 데이터 수집 실패: {str(e)}")
            return False
    
    def get_collection_summary(self, days_back=7):
        """수집 현황 요약"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 최근 수집 통계
        cursor.execute('''
            SELECT 
                collection_date,
                total_sites_collected,
                gg_poker_sites,
                total_players,
                total_cash_players
            FROM collection_stats 
            WHERE collection_date >= date('now', '-' || ? || ' days')
            ORDER BY collection_date DESC
        ''', (days_back,))
        
        recent_stats = cursor.fetchall()
        
        # 전체 수집 현황
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT collection_date) as total_days,
                AVG(total_sites_collected) as avg_sites,
                AVG(total_players) as avg_players,
                MIN(collection_date) as first_collection,
                MAX(collection_date) as last_collection
            FROM collection_stats
        ''')
        
        overall_stats = cursor.fetchone()
        
        summary = {
            'collection_period': {
                'total_days': overall_stats[0] if overall_stats else 0,
                'first_date': overall_stats[3] if overall_stats else None,
                'last_date': overall_stats[4] if overall_stats else None
            },
            'averages': {
                'sites_per_day': round(overall_stats[1], 1) if overall_stats and overall_stats[1] else 0,
                'players_per_day': round(overall_stats[2], 0) if overall_stats and overall_stats[2] else 0
            },
            'recent_collections': []
        }
        
        for stat in recent_stats:
            summary['recent_collections'].append({
                'date': stat[0],
                'sites': stat[1],
                'gg_poker_sites': stat[2],
                'total_players': stat[3],
                'cash_players': stat[4]
            })
        
        conn.close()
        return summary

def main():
    """운영용 데이터 수집 실행"""
    print("🎯 운영용 포커 사이트 데이터 수집기")
    print("=" * 60)
    
    collector = ProductionDataCollector()
    
    # 일일 데이터 수집 실행
    success = collector.run_daily_collection()
    
    if success:
        print("\n📊 수집 현황 요약")
        print("-" * 40)
        summary = collector.get_collection_summary()
        
        print(f"총 수집 일수: {summary['collection_period']['total_days']}일")
        print(f"일평균 사이트: {summary['averages']['sites_per_day']}개")
        print(f"일평균 플레이어: {summary['averages']['players_per_day']:,.0f}명")
        
        if summary['recent_collections']:
            print(f"\n📅 최근 수집 내역:")
            for collection in summary['recent_collections'][:5]:
                print(f"  {collection['date']}: {collection['sites']}개 사이트, {collection['total_players']:,}명")
        
        print(f"\n🎉 데이터 수집 완료!")
        print(f"📈 GG POKER 모니터링 시스템 가동 중")
        print(f"💾 데이터베이스: {collector.db_path}")
        
    else:
        print(f"\n💀 데이터 수집 실패 - 로그를 확인하세요")
    
    return success

if __name__ == "__main__":
    main()
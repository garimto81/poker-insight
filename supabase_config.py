#!/usr/bin/env python3
"""
Supabase 연동 설정 및 테스트
포커 인사이트 데이터를 Supabase에 저장하고 프론트엔드에서 실시간으로 조회
"""

import os
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import requests

# Supabase 설정
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://your-project.supabase.co')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', 'your-anon-key')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', 'your-service-key')

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseClient:
    """Supabase 클라이언트 클래스"""
    
    def __init__(self, use_service_key: bool = False):
        self.base_url = SUPABASE_URL
        self.api_key = SUPABASE_SERVICE_KEY if use_service_key else SUPABASE_ANON_KEY
        self.headers = {
            'apikey': self.api_key,
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
    
    def test_connection(self) -> bool:
        """Supabase 연결 테스트"""
        try:
            response = requests.get(
                f"{self.base_url}/rest/v1/",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                logger.info("✅ Supabase 연결 성공")
                return True
            else:
                logger.error(f"❌ Supabase 연결 실패: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Supabase 연결 오류: {e}")
            return False
    
    def create_tables(self) -> bool:
        """필요한 테이블들을 생성합니다"""
        
        # SQL 스크립트들
        create_tables_sql = """
        -- 포커 사이트 정보 테이블
        CREATE TABLE IF NOT EXISTS poker_sites (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            url VARCHAR(255),
            network VARCHAR(100),
            category VARCHAR(50) DEFAULT 'OTHER',
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        -- 일일 트래픽 데이터 테이블
        CREATE TABLE IF NOT EXISTS daily_traffic (
            id SERIAL PRIMARY KEY,
            site_name VARCHAR(100) NOT NULL,
            collection_date DATE NOT NULL,
            collection_time TIME NOT NULL,
            players_online INTEGER NOT NULL DEFAULT 0,
            cash_players INTEGER NOT NULL DEFAULT 0,
            peak_24h INTEGER DEFAULT 0,
            seven_day_avg INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(site_name, collection_date, collection_time)
        );

        -- 수집 통계 테이블
        CREATE TABLE IF NOT EXISTS collection_stats (
            id SERIAL PRIMARY KEY,
            collection_date DATE NOT NULL,
            collection_time TIME NOT NULL,
            total_sites INTEGER NOT NULL,
            gg_poker_sites INTEGER DEFAULT 0,
            total_players INTEGER NOT NULL,
            success BOOLEAN DEFAULT TRUE,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- 포커 이벤트 테이블
        CREATE TABLE IF NOT EXISTS poker_events (
            id SERIAL PRIMARY KEY,
            event_date DATE NOT NULL,
            event_title VARCHAR(500) NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            affected_sites TEXT,
            impact_level VARCHAR(20),
            description TEXT,
            news_url VARCHAR(500),
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- 인덱스 생성
        CREATE INDEX IF NOT EXISTS idx_daily_traffic_date ON daily_traffic(collection_date DESC);
        CREATE INDEX IF NOT EXISTS idx_daily_traffic_site ON daily_traffic(site_name);
        CREATE INDEX IF NOT EXISTS idx_collection_stats_date ON collection_stats(collection_date DESC);
        """
        
        try:
            # Supabase SQL 함수 실행
            response = requests.post(
                f"{self.base_url}/rest/v1/rpc/exec_sql",
                headers=self.headers,
                json={"sql": create_tables_sql},
                timeout=30
            )
            
            if response.status_code in [200, 204]:
                logger.info("✅ Supabase 테이블 생성 완료")
                return True
            else:
                logger.error(f"❌ 테이블 생성 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 테이블 생성 오류: {e}")
            return False
    
    def insert_daily_traffic(self, data: List[Dict]) -> bool:
        """일일 트래픽 데이터 삽입"""
        try:
            response = requests.post(
                f"{self.base_url}/rest/v1/daily_traffic",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"✅ {len(data)}개 트래픽 데이터 삽입 완료")
                return True
            else:
                logger.error(f"❌ 데이터 삽입 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 데이터 삽입 오류: {e}")
            return False
    
    def get_latest_traffic_data(self, days: int = 7) -> Optional[List[Dict]]:
        """최근 N일간의 트래픽 데이터 조회"""
        try:
            # 최근 N일간 데이터 조회
            response = requests.get(
                f"{self.base_url}/rest/v1/daily_traffic",
                headers=self.headers,
                params={
                    'select': '*',
                    'order': 'collection_date.desc,collection_time.desc',
                    'collection_date': f'gte.{(datetime.now().date() - timedelta(days=days)).isoformat()}'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ {len(data)}개 트래픽 데이터 조회 완료")
                return data
            else:
                logger.error(f"❌ 데이터 조회 실패: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 데이터 조회 오류: {e}")
            return None
    
    def get_dashboard_data(self) -> Optional[Dict]:
        """대시보드용 데이터 조회 (프론트엔드 API와 호환)"""
        try:
            # 최근 데이터 조회
            traffic_data = self.get_latest_traffic_data(days=30)
            if not traffic_data:
                return None
            
            # 데이터 변환
            dashboard_data = self._convert_to_dashboard_format(traffic_data)
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ 대시보드 데이터 조회 오류: {e}")
            return None
    
    def _convert_to_dashboard_format(self, traffic_data: List[Dict]) -> Dict:
        """트래픽 데이터를 대시보드 형식으로 변환"""
        sites = {}
        dates = set()
        
        for row in traffic_data:
            site_name = row['site_name']
            collection_date = row['collection_date']
            
            dates.add(collection_date)
            
            if site_name not in sites:
                sites[site_name] = {
                    'name': site_name,
                    'category': 'GG_POKER' if 'GG' in site_name.upper() else 'OTHER',
                    'data': {
                        'dates': [],
                        'players_online': [],
                        'cash_players': [],
                        'peak_24h': [],
                        'seven_day_avg': []
                    }
                }
            
            sites[site_name]['data']['dates'].append(collection_date)
            sites[site_name]['data']['players_online'].append(row['players_online'])
            sites[site_name]['data']['cash_players'].append(row['cash_players'])
            sites[site_name]['data']['peak_24h'].append(row['peak_24h'] or 0)
            sites[site_name]['data']['seven_day_avg'].append(row['seven_day_avg'] or 0)
        
        # 요약 통계 계산
        latest_total_players = sum(
            sites[site]['data']['players_online'][-1] 
            for site in sites 
            if sites[site]['data']['players_online']
        )
        
        gg_poker_sites = len([
            site for site in sites 
            if sites[site]['category'] == 'GG_POKER'
        ])
        
        return {
            'last_updated': datetime.now().isoformat(),
            'data_period_days': len(dates),
            'sites': sites,
            'dates': sorted(list(dates)),
            'summary': {
                'total_sites': len(sites),
                'gg_poker_sites': gg_poker_sites,
                'latest_total_players': latest_total_players,
                'data_points': len(traffic_data)
            }
        }

def main():
    """테스트 실행"""
    print("🚀 Supabase 연동 테스트 시작")
    print("=" * 50)
    
    # 환경변수 확인
    if SUPABASE_URL == 'https://your-project.supabase.co':
        print("❌ SUPABASE_URL 환경변수를 설정하세요")
        return False
    
    if SUPABASE_ANON_KEY == 'your-anon-key':
        print("❌ SUPABASE_ANON_KEY 환경변수를 설정하세요")
        return False
    
    # 클라이언트 생성
    client = SupabaseClient(use_service_key=True)
    
    # 연결 테스트
    if not client.test_connection():
        return False
    
    # 테이블 생성
    if not client.create_tables():
        return False
    
    # 대시보드 데이터 조회 테스트
    dashboard_data = client.get_dashboard_data()
    if dashboard_data:
        print("✅ 대시보드 데이터 조회 성공")
        print(f"   - 사이트 수: {dashboard_data['summary']['total_sites']}")
        print(f"   - 총 플레이어: {dashboard_data['summary']['latest_total_players']:,}")
    
    print("\n✅ Supabase 연동 테스트 완료")
    return True

if __name__ == "__main__":
    from datetime import timedelta
    main()
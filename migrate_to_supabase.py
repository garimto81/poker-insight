#!/usr/bin/env python3
"""
SQLite 데이터를 Supabase로 마이그레이션
기존 로컬 데이터베이스의 데이터를 Supabase로 이전합니다.
"""

import os
import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict
from supabase_config import SupabaseClient

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataMigrator:
    """데이터 마이그레이션 클래스"""
    
    def __init__(self):
        self.supabase_client = SupabaseClient(use_service_key=True)
        self.sqlite_dbs = [
            'github_actions_fallback.db',
            'poker_insight.db',
            'gg_poker_monitoring.db',
            'online_poker_data.db'
        ]
    
    def get_sqlite_data(self, db_path: str) -> List[Dict]:
        """SQLite에서 데이터 추출"""
        data = []
        
        if not os.path.exists(db_path):
            logger.warning(f"⚠️ 데이터베이스 파일 없음: {db_path}")
            return data
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 반환
            cursor = conn.cursor()
            
            # daily_traffic 테이블 확인
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='daily_traffic'
            """)
            
            if cursor.fetchone():
                cursor.execute("""
                    SELECT 
                        site_name,
                        collection_date,
                        collection_time,
                        players_online,
                        cash_players,
                        peak_24h,
                        seven_day_avg,
                        created_at
                    FROM daily_traffic
                    ORDER BY collection_date DESC, collection_time DESC
                """)
                
                rows = cursor.fetchall()
                for row in rows:
                    data.append({
                        'site_name': row['site_name'],
                        'collection_date': row['collection_date'],
                        'collection_time': row['collection_time'],
                        'players_online': row['players_online'] or 0,
                        'cash_players': row['cash_players'] or 0,
                        'peak_24h': row['peak_24h'] or 0,
                        'seven_day_avg': row['seven_day_avg'] or 0,
                        'created_at': row.get('created_at', datetime.now().isoformat())
                    })
                
                logger.info(f"✅ {db_path}에서 {len(data)}개 레코드 추출")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ {db_path} 데이터 추출 실패: {e}")
        
        return data
    
    def merge_and_deduplicate(self, all_data: List[List[Dict]]) -> List[Dict]:
        """여러 데이터베이스의 데이터를 병합하고 중복 제거"""
        merged = {}
        
        for data_list in all_data:
            for record in data_list:
                # 고유 키 생성 (사이트명 + 날짜 + 시간)
                key = f"{record['site_name']}_{record['collection_date']}_{record['collection_time']}"
                
                # 중복이면 더 최신 데이터 유지
                if key not in merged:
                    merged[key] = record
                elif record.get('created_at', '') > merged[key].get('created_at', ''):
                    merged[key] = record
        
        result = list(merged.values())
        logger.info(f"✅ 중복 제거 후 {len(result)}개 레코드")
        return result
    
    def batch_insert(self, data: List[Dict], batch_size: int = 100) -> bool:
        """배치 단위로 데이터 삽입"""
        total_inserted = 0
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            
            try:
                if self.supabase_client.insert_daily_traffic(batch):
                    total_inserted += len(batch)
                    logger.info(f"✅ 배치 {i//batch_size + 1}: {len(batch)}개 삽입 완료")
                else:
                    logger.error(f"❌ 배치 {i//batch_size + 1} 삽입 실패")
                    
            except Exception as e:
                logger.error(f"❌ 배치 삽입 오류: {e}")
        
        logger.info(f"🎯 총 {total_inserted}개 레코드 삽입 완료")
        return total_inserted > 0
    
    def run_migration(self) -> bool:
        """전체 마이그레이션 실행"""
        logger.info("🚀 SQLite → Supabase 마이그레이션 시작")
        
        # 1. Supabase 연결 테스트
        if not self.supabase_client.test_connection():
            logger.error("❌ Supabase 연결 실패")
            return False
        
        # 2. 테이블 생성
        if not self.supabase_client.create_tables():
            logger.error("❌ 테이블 생성 실패")
            return False
        
        # 3. 모든 SQLite 데이터베이스에서 데이터 추출
        all_data = []
        for db_name in self.sqlite_dbs:
            db_path = os.path.join('.', db_name)
            data = self.get_sqlite_data(db_path)
            if data:
                all_data.append(data)
        
        if not all_data:
            logger.warning("⚠️ 마이그레이션할 데이터가 없습니다")
            return False
        
        # 4. 데이터 병합 및 중복 제거
        merged_data = self.merge_and_deduplicate(all_data)
        
        if not merged_data:
            logger.warning("⚠️ 병합할 데이터가 없습니다")
            return False
        
        # 5. Supabase에 데이터 삽입
        success = self.batch_insert(merged_data)
        
        if success:
            logger.info("✅ 마이그레이션 완료")
            
            # 6. 마이그레이션 결과 검증
            dashboard_data = self.supabase_client.get_dashboard_data()
            if dashboard_data:
                logger.info("📊 마이그레이션 결과:")
                logger.info(f"   - 사이트 수: {dashboard_data['summary']['total_sites']}")
                logger.info(f"   - 총 플레이어: {dashboard_data['summary']['latest_total_players']:,}")
                logger.info(f"   - 데이터 포인트: {dashboard_data['summary']['data_points']}")
        
        return success

def create_env_template():
    """환경변수 템플릿 파일 생성"""
    env_template = """# Supabase 설정
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here

# 사용법:
# 1. Supabase 프로젝트를 생성하세요
# 2. Settings > API에서 URL과 키들을 복사하세요
# 3. 이 파일을 .env로 저장하고 실제 값으로 교체하세요
# 4. python migrate_to_supabase.py 실행하세요
"""
    
    with open('.env.template', 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    logger.info("📄 .env.template 파일이 생성되었습니다")

def main():
    """메인 실행 함수"""
    print("🚀 SQLite → Supabase 마이그레이션 도구")
    print("=" * 50)
    
    # 환경변수 확인
    supabase_url = os.getenv('SUPABASE_URL', '')
    if not supabase_url or supabase_url == 'https://your-project.supabase.co':
        print("❌ 환경변수가 설정되지 않았습니다.")
        print("💡 다음 단계를 따라하세요:")
        print("   1. Supabase 프로젝트 생성")
        print("   2. .env 파일에 URL과 키 설정")
        print("   3. 스크립트 재실행")
        
        create_env_template()
        return False
    
    # 마이그레이션 실행
    migrator = DataMigrator()
    success = migrator.run_migration()
    
    if success:
        print("\n🎉 마이그레이션이 성공적으로 완료되었습니다!")
        print("💡 다음 단계: 프론트엔드에서 Supabase API 연동")
    else:
        print("\n❌ 마이그레이션 실패")
    
    return success

if __name__ == "__main__":
    main()
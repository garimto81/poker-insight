#!/usr/bin/env python3
"""
Supabase 연동 테스트 스크립트
실제 Supabase 프로젝트와의 연동을 테스트합니다.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from supabase_config import SupabaseClient
from migrate_to_supabase import DataMigrator

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_environment_setup():
    """환경 설정 테스트"""
    print("[TEST] 환경 설정 테스트")
    print("-" * 30)
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_SERVICE_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var, '')
        if not value or 'your-' in value:
            missing_vars.append(var)
        else:
            print(f"[OK] {var}: 설정됨")
    
    if missing_vars:
        print(f"[ERROR] 누락된 환경변수: {', '.join(missing_vars)}")
        print("[INFO] .env 파일을 생성하고 실제 Supabase 정보를 입력하세요")
        return False
    
    return True

def test_basic_connection():
    """기본 연결 테스트"""
    print("\n[TEST] Supabase 연결 테스트")
    print("-" * 30)
    
    client = SupabaseClient()
    return client.test_connection()

def test_table_creation():
    """테이블 생성 테스트"""
    print("\n[TEST] 테이블 생성 테스트")
    print("-" * 30)
    
    client = SupabaseClient(use_service_key=True)
    return client.create_tables()

def test_data_insertion():
    """데이터 삽입 테스트"""
    print("\n[TEST] 데이터 삽입 테스트")
    print("-" * 30)
    
    client = SupabaseClient(use_service_key=True)
    
    # 테스트 데이터
    test_data = [
        {
            'site_name': 'Test Site 1',
            'collection_date': datetime.now().date().isoformat(),
            'collection_time': datetime.now().time().isoformat(),
            'players_online': 1000,
            'cash_players': 500,
            'peak_24h': 1200,
            'seven_day_avg': 950
        },
        {
            'site_name': 'Test Site 2',
            'collection_date': datetime.now().date().isoformat(),
            'collection_time': datetime.now().time().isoformat(),
            'players_online': 2000,
            'cash_players': 800,
            'peak_24h': 2500,
            'seven_day_avg': 1800
        }
    ]
    
    success = client.insert_daily_traffic(test_data)
    if success:
        print(f"[OK] {len(test_data)}개 테스트 데이터 삽입 성공")
    
    return success

def test_data_retrieval():
    """데이터 조회 테스트"""
    print("\n[TEST] 데이터 조회 테스트")
    print("-" * 30)
    
    client = SupabaseClient()
    
    # 최근 데이터 조회
    data = client.get_latest_traffic_data(days=1)
    if data:
        print(f"[OK] {len(data)}개 레코드 조회 성공")
        
        # 샘플 데이터 출력
        if len(data) > 0:
            sample = data[0]
            print(f"   샘플: {sample['site_name']} - {sample['players_online']}명")
        
        return True
    else:
        print("[ERROR] 데이터 조회 실패")
        return False

def test_dashboard_data_format():
    """대시보드 데이터 형식 테스트"""
    print("\n[TEST] 대시보드 데이터 형식 테스트")
    print("-" * 30)
    
    client = SupabaseClient()
    
    dashboard_data = client.get_dashboard_data()
    if dashboard_data:
        print("[OK] 대시보드 데이터 변환 성공")
        print(f"   - 사이트 수: {dashboard_data['summary']['total_sites']}")
        print(f"   - 총 플레이어: {dashboard_data['summary']['latest_total_players']:,}")
        print(f"   - 데이터 기간: {dashboard_data['data_period_days']}일")
        
        # 데이터 구조 확인
        required_keys = ['last_updated', 'sites', 'summary']
        for key in required_keys:
            if key in dashboard_data:
                print(f"   [OK] {key} 키 존재")
            else:
                print(f"   [ERROR] {key} 키 누락")
                return False
        
        return True
    else:
        print("[ERROR] 대시보드 데이터 생성 실패")
        return False

def test_migration():
    """마이그레이션 테스트"""
    print("\n[TEST] 데이터 마이그레이션 테스트")
    print("-" * 30)
    
    migrator = DataMigrator()
    
    # SQLite 데이터 존재 확인
    has_local_data = False
    for db_name in migrator.sqlite_dbs:
        if os.path.exists(db_name):
            data = migrator.get_sqlite_data(db_name)
            if data:
                has_local_data = True
                print(f"[OK] {db_name}에서 {len(data)}개 레코드 발견")
                break
    
    if not has_local_data:
        print("[WARNING] 마이그레이션할 로컬 데이터가 없습니다")
        return True  # 데이터가 없는 것은 오류가 아님
    
    # 마이그레이션 실행
    return migrator.run_migration()

def generate_frontend_config():
    """프론트엔드 설정 파일 생성"""
    print("\n[TEST] 프론트엔드 설정 파일 생성")
    print("-" * 30)
    
    supabase_url = os.getenv('SUPABASE_URL', '')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY', '')
    
    if not supabase_url or not supabase_anon_key:
        print("[ERROR] Supabase URL 또는 ANON KEY가 설정되지 않음")
        return False
    
    # 프론트엔드 설정 파일 생성
    config_js = f"""// Supabase 설정 (자동 생성됨)
// 이 파일은 프론트엔드에서 Supabase 연동을 위해 사용됩니다.

window.SUPABASE_URL = '{supabase_url}';
window.SUPABASE_ANON_KEY = '{supabase_anon_key}';

console.log('🔗 Supabase 설정 로드됨:', window.SUPABASE_URL);
"""
    
    config_path = os.path.join('docs', 'supabase-config.js')
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_js)
        
        print(f"[OK] 프론트엔드 설정 파일 생성: {config_path}")
        print("[INFO] HTML 파일에 다음 스크립트 태그 추가:")
        print(f"   <script src=\"./supabase-config.js\"></script>")
        return True
        
    except Exception as e:
        print(f"[ERROR] 설정 파일 생성 실패: {e}")
        return False

def run_all_tests():
    """모든 테스트 실행"""
    print("[START] Supabase 연동 전체 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("환경 설정", test_environment_setup),
        ("기본 연결", test_basic_connection),
        ("테이블 생성", test_table_creation),
        ("데이터 삽입", test_data_insertion),
        ("데이터 조회", test_data_retrieval),
        ("대시보드 형식", test_dashboard_data_format),
        ("데이터 마이그레이션", test_migration),
        ("프론트엔드 설정", generate_frontend_config)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"[ERROR] {test_name} 테스트 중 오류: {e}")
            results[test_name] = False
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("[RESULT] 테스트 결과 요약")
    print("-" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "[OK] 성공" if result else "[FAIL] 실패"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n[SUMMARY] 전체 결과: {passed}/{total} 테스트 통과")
    
    if passed == total:
        print("[SUCCESS] 모든 테스트가 성공했습니다!")
        print("[INFO] 다음 단계:")
        print("   1. 프론트엔드에서 Supabase 연동 테스트")
        print("   2. 실제 데이터 수집기에 Supabase 연동 적용")
        print("   3. GitHub Actions에 Supabase 환경변수 설정")
    else:
        print("[WARNING] 일부 테스트가 실패했습니다. 설정을 확인하세요.")
    
    return passed == total

def main():
    """메인 실행 함수"""
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        
        if test_name == 'env':
            test_environment_setup()
        elif test_name == 'connect':
            test_basic_connection()
        elif test_name == 'tables':
            test_table_creation()
        elif test_name == 'insert':
            test_data_insertion()
        elif test_name == 'query':
            test_data_retrieval()
        elif test_name == 'dashboard':
            test_dashboard_data_format()
        elif test_name == 'migrate':
            test_migration()
        elif test_name == 'frontend':
            generate_frontend_config()
        else:
            print("사용법: python test_supabase_integration.py [env|connect|tables|insert|query|dashboard|migrate|frontend]")
    else:
        run_all_tests()

if __name__ == "__main__":
    main()
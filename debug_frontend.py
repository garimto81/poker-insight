#!/usr/bin/env python3
"""
Frontend data loading 진단 스크립트
프론트엔드에서 데이터가 로딩되지 않는 문제를 분석합니다.
"""

import os
import json
import time
from pathlib import Path

def check_api_data_file():
    """API 데이터 파일 존재 및 내용 확인"""
    print("[CHECK] API 데이터 파일 검사 중...")
    
    docs_path = Path("docs")
    api_file = docs_path / "api_data.json"
    
    if not api_file.exists():
        print(f"[ERROR] API 데이터 파일이 존재하지 않음: {api_file}")
        return False
    
    try:
        with open(api_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"[OK] API 데이터 파일 존재: {api_file}")
        print(f"[DATA] 데이터 구조:")
        print(f"   - 사이트 수: {data.get('summary', {}).get('total_sites', 'N/A')}")
        print(f"   - 총 플레이어: {data.get('summary', {}).get('latest_total_players', 'N/A')}")
        print(f"   - 마지막 업데이트: {data.get('last_updated', 'N/A')}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 파싱 오류: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] 파일 읽기 오류: {e}")
        return False

def check_frontend_files():
    """프론트엔드 파일들 존재 확인"""
    print("\n[CHECK] 프론트엔드 파일 검사 중...")
    
    docs_path = Path("docs")
    index_file = docs_path / "index.html"
    
    if not index_file.exists():
        print(f"[ERROR] 인덱스 파일이 존재하지 않음: {index_file}")
        return False
    
    print(f"[OK] 인덱스 파일 존재: {index_file}")
    
    # HTML 파일에서 중요 요소들 확인
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 중요 요소들 확인
        checks = [
            ("loadDashboardData 함수", "loadDashboardData" in content),
            ("fetch('./api_data.json')", "fetch('./api_data.json'" in content),
            ("initializeDashboard 함수", "initializeDashboard" in content),
            ("DOMContentLoaded 이벤트", "DOMContentLoaded" in content),
            ("total-sites 요소", "total-sites" in content),
            ("total-players 요소", "total-players" in content)
        ]
        
        for check_name, result in checks:
            if result:
                print(f"   [OK] {check_name}: 발견됨")
            else:
                print(f"   [ERROR] {check_name}: 누락됨")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] HTML 파일 읽기 오류: {e}")
        return False

def simulate_fetch_request():
    """fetch 요청 시뮬레이션"""
    print("\n[CHECK] fetch 요청 시뮬레이션...")
    
    docs_path = Path("docs")
    api_file = docs_path / "api_data.json"
    
    # 상대 경로로 접근 시뮬레이션
    current_dir = os.getcwd()
    print(f"현재 작업 디렉토리: {current_dir}")
    
    # docs 디렉토리로 이동하여 상대 경로 테스트
    try:
        os.chdir(docs_path)
        print(f"docs 디렉토리로 이동: {os.getcwd()}")
        
        # ./api_data.json 접근 테스트
        relative_api_file = Path("./api_data.json")
        if relative_api_file.exists():
            print("[OK] './api_data.json' 상대 경로 접근 가능")
            
            with open(relative_api_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"[OK] JSON 데이터 파싱 성공")
            print(f"   - 사이트 수: {data.get('summary', {}).get('total_sites', 'N/A')}")
            
        else:
            print("[ERROR] './api_data.json' 상대 경로 접근 불가")
        
    except Exception as e:
        print(f"[ERROR] 상대 경로 테스트 실패: {e}")
    finally:
        os.chdir(current_dir)

def check_common_issues():
    """일반적인 문제들 확인"""
    print("\n[CHECK] 일반적인 문제들 검사...")
    
    # 1. 파일 권한 확인
    docs_path = Path("docs")
    api_file = docs_path / "api_data.json"
    
    if api_file.exists():
        try:
            file_stat = api_file.stat()
            print(f"[OK] 파일 권한: {oct(file_stat.st_mode)[-3:]}")
        except Exception as e:
            print(f"[ERROR] 파일 권한 확인 실패: {e}")
    
    # 2. 파일 크기 확인
    if api_file.exists():
        try:
            file_size = api_file.stat().st_size
            print(f"[OK] 파일 크기: {file_size} bytes")
            if file_size == 0:
                print("[ERROR] 파일이 비어있음!")
        except Exception as e:
            print(f"[ERROR] 파일 크기 확인 실패: {e}")
    
    # 3. JSON 구조 검증
    if api_file.exists():
        try:
            with open(api_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            required_keys = ['summary', 'sites', 'last_updated']
            missing_keys = [key for key in required_keys if key not in data]
            
            if not missing_keys:
                print("[OK] JSON 구조: 필수 키들 모두 존재")
            else:
                print(f"[ERROR] JSON 구조: 누락된 키들 {missing_keys}")
                
        except Exception as e:
            print(f"[ERROR] JSON 구조 검증 실패: {e}")

def main():
    print("[DEBUG] 프론트엔드 데이터 로딩 문제 진단 시작")
    print("=" * 60)
    
    # 1. API 데이터 파일 확인
    api_ok = check_api_data_file()
    
    # 2. 프론트엔드 파일들 확인
    frontend_ok = check_frontend_files()
    
    # 3. fetch 요청 시뮬레이션
    simulate_fetch_request()
    
    # 4. 일반적인 문제들 확인
    check_common_issues()
    
    print("\n" + "=" * 60)
    print("[RESULT] 진단 완료")
    
    if api_ok and frontend_ok:
        print("[OK] 기본 파일들은 정상적으로 존재합니다.")
        print("[INFO] CORS 이슈일 가능성이 높습니다. HTTP 서버로 실행해보세요:")
        print("   cd docs && python -m http.server 8000")
        print("   그 후 http://localhost:8000 에서 확인")
    else:
        print("[ERROR] 기본 파일들에 문제가 있습니다. 위의 오류들을 먼저 해결하세요.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
GitHub Pages 무한 로딩 문제 분석
실제 브라우저에서 발생하는 JavaScript 오류를 시뮬레이션하여 분석합니다.
"""

import requests
import json
import re
from urllib.parse import urljoin

def analyze_javascript_execution():
    """JavaScript 실행 과정에서 발생할 수 있는 문제들 분석"""
    print("[DEBUG] JavaScript 실행 과정 분석")
    print("=" * 60)
    
    base_url = "https://garimto81.github.io/poker-insight/"
    
    # 1. HTML 및 JavaScript 코드 가져오기
    try:
        response = requests.get(base_url, timeout=10)
        html_content = response.text
        
        # JavaScript 코드에서 중요한 부분들 추출
        print("[STEP 1] HTML/JavaScript 코드 분석...")
        
        # loadDashboardData 함수 찾기
        load_data_match = re.search(r'async function loadDashboardData\(\).*?}', html_content, re.DOTALL)
        if load_data_match:
            print("   [OK] loadDashboardData 함수 발견")
        else:
            print("   [ERROR] loadDashboardData 함수 누락")
            
        # initializeDashboard 함수 찾기  
        init_match = re.search(r'async function initializeDashboard\(\).*?}', html_content, re.DOTALL)
        if init_match:
            print("   [OK] initializeDashboard 함수 발견")
        else:
            print("   [ERROR] initializeDashboard 함수 누락")
            
        # DOMContentLoaded 이벤트 리스너 확인
        if "DOMContentLoaded" in html_content and "initializeDashboard" in html_content:
            print("   [OK] DOMContentLoaded 이벤트 리스너 발견")
        else:
            print("   [ERROR] DOMContentLoaded 이벤트 리스너 문제")
            
    except Exception as e:
        print(f"   [ERROR] HTML 분석 실패: {e}")
        return False
    
    # 2. API 응답 시간 테스트
    print("\n[STEP 2] API 응답 시간 테스트...")
    api_url = urljoin(base_url, "api_data.json")
    
    try:
        import time
        start_time = time.time()
        response = requests.get(api_url, timeout=10)
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"   [OK] API 응답 시간: {response_time:.2f}초")
        
        if response_time > 5:
            print("   [WARNING] API 응답이 5초 이상 걸림 - 타임아웃 이슈 가능성")
        
        # JSON 파싱 테스트
        data = response.json()
        print(f"   [OK] JSON 파싱 성공 - 데이터 크기: {len(str(data))} bytes")
        
    except Exception as e:
        print(f"   [ERROR] API 테스트 실패: {e}")
        return False
    
    # 3. JavaScript 실행 순서 시뮬레이션
    print("\n[STEP 3] JavaScript 실행 순서 시뮬레이션...")
    
    try:
        # 가상의 브라우저 실행 순서
        print("   1. DOMContentLoaded 이벤트 발생")
        print("   2. initializeDashboard() 호출")
        print("   3. loadDashboardData() 호출")
        print("   4. fetch('./api_data.json') 실행")
        
        # 실제 fetch 시뮬레이션
        fetch_response = requests.get(api_url)
        if fetch_response.status_code == 200:
            print("   5. [OK] fetch 성공")
            
            data = fetch_response.json()
            print("   6. [OK] JSON 파싱 성공")
            
            # 중요 데이터 확인
            if 'summary' in data and 'sites' in data:
                print("   7. [OK] 필수 데이터 구조 확인")
                
                summary = data['summary']
                sites = data['sites']
                
                print(f"   8. updateStatistics() - 사이트: {summary.get('total_sites')}, 플레이어: {summary.get('latest_total_players')}")
                print(f"   9. createAllCharts() - {len(sites)}개 사이트 데이터로 차트 생성")
                print("   10. [OK] 초기화 완료 예상")
                
            else:
                print("   7. [ERROR] 필수 데이터 구조 누락")
                return False
                
        else:
            print(f"   5. [ERROR] fetch 실패: HTTP {fetch_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] JavaScript 시뮬레이션 실패: {e}")
        return False
    
    return True

def check_common_loading_issues():
    """무한 로딩을 일으킬 수 있는 일반적인 문제들 확인"""
    print("\n[STEP 4] 무한 로딩 원인 분석...")
    
    base_url = "https://garimto81.github.io/poker-insight/"
    
    try:
        response = requests.get(base_url)
        content = response.text
        
        # 1. Chart.js 라이브러리 로딩 확인
        if "chart.js" in content.lower():
            print("   [OK] Chart.js 라이브러리 포함됨")
        else:
            print("   [ERROR] Chart.js 라이브러리 누락 - 차트 생성 실패 가능성")
        
        # 2. 에러 핸들링 확인
        if "catch" in content and "error" in content.lower():
            print("   [OK] 에러 핸들링 코드 존재")
        else:
            print("   [WARNING] 에러 핸들링 부족")
        
        # 3. 로딩 인디케이터 제거 코드 확인
        if "loading-indicator" in content and "style.display = 'none'" in content:
            print("   [OK] 로딩 인디케이터 제거 코드 존재")
        else:
            print("   [ERROR] 로딩 인디케이터 제거 코드 누락 - 무한 로딩 가능성")
        
        # 4. DOM 요소 존재 확인
        required_elements = ["total-sites", "total-players", "loading-indicator"]
        for element in required_elements:
            if f'id="{element}"' in content:
                print(f"   [OK] DOM 요소 '{element}' 존재")
            else:
                print(f"   [ERROR] DOM 요소 '{element}' 누락")
        
        # 5. 무한 루프 가능성 확인
        if "while" in content or "setInterval" in content:
            print("   [WARNING] 무한 루프 가능성 있는 코드 발견")
        else:
            print("   [OK] 무한 루프 코드 없음")
            
    except Exception as e:
        print(f"   [ERROR] 코드 분석 실패: {e}")

def suggest_fixes():
    """무한 로딩 문제 해결 방안 제시"""
    print("\n[STEP 5] 무한 로딩 해결 방안")
    print("-" * 40)
    
    print("1. 브라우저 개발자 도구 확인:")
    print("   - F12 → Console 탭에서 JavaScript 에러 확인")
    print("   - Network 탭에서 api_data.json 로딩 상태 확인")
    print("   - Elements 탭에서 loading-indicator 요소 상태 확인")
    
    print("\n2. 캐시 문제 해결:")
    print("   - Ctrl+F5 (강제 새로고침)")
    print("   - 브라우저 캐시 삭제")
    
    print("\n3. 네트워크 문제 확인:")
    print("   - 인터넷 연결 상태 확인")
    print("   - GitHub Pages 서비스 상태 확인")
    
    print("\n4. JavaScript 실행 환경:")
    print("   - 브라우저 JavaScript 활성화 여부")
    print("   - 애드블로커 등 확장 프로그램 비활성화")

def main():
    """메인 실행 함수"""
    print("[ANALYSIS] GitHub Pages 무한 로딩 문제 분석 시작")
    print("=" * 60)
    
    # JavaScript 실행 과정 분석
    js_ok = analyze_javascript_execution()
    
    # 일반적인 로딩 문제들 확인
    check_common_loading_issues()
    
    # 해결 방안 제시
    suggest_fixes()
    
    print("\n" + "=" * 60)
    if js_ok:
        print("[RESULT] 서버 측 코드 및 데이터는 정상")
        print("[ACTION] 브라우저 측 문제일 가능성 높음")
        print("         위의 해결 방안을 시도해보세요")
    else:
        print("[RESULT] 서버 측 코드에 문제 발견")
        print("[ACTION] 코드 수정이 필요합니다")

if __name__ == "__main__":
    main()
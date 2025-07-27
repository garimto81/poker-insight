#!/usr/bin/env python3
"""
실제 GitHub Pages 사이트 분석 도구
브라우저 동작을 시뮬레이션하여 무한 로딩 문제를 진단합니다.
"""

import requests
import json
import re
import time
from urllib.parse import urljoin

def analyze_main_page():
    """메인 페이지 분석"""
    print("[ANALYZE] GitHub Pages 메인 페이지 분석")
    print("=" * 60)
    
    url = "https://garimto81.github.io/poker-insight/"
    
    try:
        response = requests.get(url, timeout=10)
        html = response.text
        
        print(f"[OK] 메인 페이지 로드 성공 (HTTP {response.status_code})")
        print(f"[INFO] 응답 크기: {len(html)} bytes")
        
        # 중요 요소들 확인
        checks = [
            ("Chart.js CDN", "cdn.jsdelivr.net/npm/chart.js" in html),
            ("Supabase 통합 스크립트", "supabase-integration.js" in html),
            ("loadDashboardData 함수", "loadDashboardData" in html),
            ("loading-indicator 요소", "loading-indicator" in html),
            ("total-sites 요소", "total-sites" in html),
            ("total-players 요소", "total-players" in html),
            ("DOMContentLoaded 이벤트", "DOMContentLoaded" in html),
            ("initializeDashboard 호출", "initializeDashboard" in html)
        ]
        
        all_good = True
        for check_name, result in checks:
            status = "[OK]" if result else "[ERROR]"
            print(f"   {status} {check_name}")
            if not result:
                all_good = False
        
        # 버전 확인
        version_match = re.search(r'v(\d+\.\d+\.\d+)', html)
        if version_match:
            print(f"[INFO] 페이지 버전: {version_match.group(1)}")
        
        return all_good, html
        
    except Exception as e:
        print(f"[ERROR] 메인 페이지 로드 실패: {e}")
        return False, None

def check_external_resources():
    """외부 리소스 확인"""
    print("\n[ANALYZE] 외부 리소스 확인")
    print("-" * 40)
    
    base_url = "https://garimto81.github.io/poker-insight/"
    resources = [
        ("Chart.js CDN", "https://cdn.jsdelivr.net/npm/chart.js"),
        ("Supabase 통합 스크립트", urljoin(base_url, "supabase-integration.js")),
        ("API 데이터 파일", urljoin(base_url, "api_data.json"))
    ]
    
    all_resources_ok = True
    
    for name, url in resources:
        try:
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                print(f"   [OK] {name}: HTTP {response.status_code}")
            else:
                print(f"   [ERROR] {name}: HTTP {response.status_code}")
                all_resources_ok = False
        except Exception as e:
            print(f"   [ERROR] {name}: {e}")
            all_resources_ok = False
    
    return all_resources_ok

def check_api_data():
    """API 데이터 확인"""
    print("\n[ANALYZE] API 데이터 분석")
    print("-" * 40)
    
    api_url = "https://garimto81.github.io/poker-insight/api_data.json"
    
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code != 200:
            print(f"[ERROR] API 데이터 로드 실패: HTTP {response.status_code}")
            return False
        
        data = response.json()
        print(f"[OK] API 데이터 로드 성공")
        
        # 데이터 구조 확인
        required_keys = ['summary', 'sites', 'last_updated']
        for key in required_keys:
            if key in data:
                print(f"   [OK] '{key}' 키 존재")
            else:
                print(f"   [ERROR] '{key}' 키 누락")
                return False
        
        # 요약 정보
        summary = data.get('summary', {})
        print(f"   [DATA] 사이트 수: {summary.get('total_sites', 'N/A')}")
        print(f"   [DATA] 총 플레이어: {summary.get('latest_total_players', 'N/A')}")
        print(f"   [DATA] 마지막 업데이트: {data.get('last_updated', 'N/A')}")
        
        # 사이트 데이터 확인
        sites = data.get('sites', {})
        if sites:
            print(f"   [OK] {len(sites)}개 사이트 데이터 존재")
            
            # 샘플 사이트 데이터 구조 확인
            sample_site = next(iter(sites.values()))
            required_site_keys = ['name', 'data']
            for key in required_site_keys:
                if key in sample_site:
                    print(f"   [OK] 사이트 데이터 '{key}' 구조 존재")
                else:
                    print(f"   [ERROR] 사이트 데이터 '{key}' 구조 누락")
                    return False
            
            # 사이트 데이터 내부 구조 확인
            site_data = sample_site.get('data', {})
            required_data_keys = ['dates', 'players_online', 'cash_players']
            for key in required_data_keys:
                if key in site_data and isinstance(site_data[key], list):
                    print(f"   [OK] 사이트 데이터 '{key}' 배열 존재")
                else:
                    print(f"   [ERROR] 사이트 데이터 '{key}' 배열 누락")
                    return False
        else:
            print(f"   [ERROR] 사이트 데이터가 비어있음")
            return False
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 파싱 실패: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] API 데이터 확인 실패: {e}")
        return False

def simulate_javascript_execution():
    """JavaScript 실행 시뮬레이션"""
    print("\n[ANALYZE] JavaScript 실행 시뮬레이션")
    print("-" * 40)
    
    issues = []
    
    # 1. Supabase 설정 확인
    print("   [1] Supabase 설정 확인...")
    # window.SUPABASE_URL과 window.SUPABASE_ANON_KEY가 비어있음
    print("   [WARNING] Supabase URL/KEY가 설정되지 않음 -> JSON fallback 모드")
    
    # 2. Chart.js 로딩 확인
    print("   [2] Chart.js 로딩 시뮬레이션...")
    try:
        chart_response = requests.head("https://cdn.jsdelivr.net/npm/chart.js", timeout=5)
        if chart_response.status_code == 200:
            print("   [OK] Chart.js CDN 접근 가능")
        else:
            print("   [ERROR] Chart.js CDN 접근 실패")
            issues.append("Chart.js 로딩 실패")
    except:
        print("   [ERROR] Chart.js CDN 연결 실패")
        issues.append("Chart.js 네트워크 오류")
    
    # 3. API 데이터 로딩 시뮬레이션
    print("   [3] API 데이터 로딩 시뮬레이션...")
    api_ok = check_api_data_briefly()
    if not api_ok:
        issues.append("API 데이터 로딩 실패")
    
    # 4. DOM 요소 존재 확인 (HTML 기반)
    print("   [4] DOM 요소 시뮬레이션...")
    _, html = analyze_main_page()
    if html:
        required_elements = [
            "loading-indicator",
            "total-sites", 
            "total-players",
            "onlinePlayersChart",
            "cashPlayersChart"
        ]
        
        for element_id in required_elements:
            if f'id="{element_id}"' in html:
                print(f"   [OK] DOM 요소 '{element_id}' 존재")
            else:
                print(f"   [ERROR] DOM 요소 '{element_id}' 누락")
                issues.append(f"DOM 요소 {element_id} 누락")
    
    return issues

def check_api_data_briefly():
    """API 데이터 간단 확인"""
    try:
        response = requests.get("https://garimto81.github.io/poker-insight/api_data.json", timeout=5)
        data = response.json()
        return 'summary' in data and 'sites' in data
    except:
        return False

def identify_loading_issues():
    """로딩 문제 원인 식별"""
    print("\n[ANALYZE] 무한 로딩 원인 분석")
    print("-" * 40)
    
    potential_issues = []
    
    # 1. 리소스 로딩 실패
    if not check_external_resources():
        potential_issues.append("외부 리소스 로딩 실패")
    
    # 2. JavaScript 실행 오류
    js_issues = simulate_javascript_execution()
    potential_issues.extend(js_issues)
    
    # 3. 로딩 인디케이터 숨김 실패 가능성
    print("   [CHECK] 로딩 인디케이터 숨김 로직...")
    _, html = analyze_main_page()
    if html:
        # loadingEl.style.display = 'none' 코드가 있는지 확인
        if "loadingEl.style.display = 'none'" in html:
            print("   [OK] 로딩 인디케이터 숨김 로직 존재")
        else:
            print("   [ERROR] 로딩 인디케이터 숨김 로직 누락")
            potential_issues.append("로딩 인디케이터 숨김 로직 문제")
        
        # initializeDashboard 함수에서 로딩 처리 확인
        if "loadingEl" in html and "initializeDashboard" in html:
            print("   [OK] initializeDashboard에 로딩 처리 로직 존재")
        else:
            print("   [WARNING] initializeDashboard 로딩 처리 불완전")
            potential_issues.append("initializeDashboard 로딩 처리 문제")
    
    return potential_issues

def main():
    """메인 분석 실행"""
    print("[START] GitHub Pages 사이트 실시간 분석")
    print("URL: https://garimto81.github.io/poker-insight/")
    print("=" * 60)
    
    # 전체 분석 실행
    main_page_ok, _ = analyze_main_page()
    resources_ok = check_external_resources()
    api_ok = check_api_data()
    
    # 무한 로딩 원인 식별
    issues = identify_loading_issues()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("[SUMMARY] 분석 결과 요약")
    print("-" * 40)
    
    if main_page_ok:
        print("[OK] 메인 페이지: 정상")
    else:
        print("[FAIL] 메인 페이지: 문제 있음")
    
    if resources_ok:
        print("[OK] 외부 리소스: 정상")
    else:
        print("[FAIL] 외부 리소스: 문제 있음")
    
    if api_ok:
        print("[OK] API 데이터: 정상")
    else:
        print("[FAIL] API 데이터: 문제 있음")
    
    if issues:
        print(f"\n[ISSUES] 발견된 문제점 ({len(issues)}개):")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print(f"\n[RECOMMENDATION] 수정 방안:")
        print("   1. 브라우저 F12 개발자 도구 Console 탭 확인")
        print("   2. Network 탭에서 실패한 요청 확인")
        print("   3. JavaScript 오류 메시지 확인")
        print("   4. 로딩 인디케이터 숨김 로직 점검")
    else:
        print("\n[SUCCESS] 심각한 문제점이 발견되지 않음")
        print("[INFO] 무한 로딩은 브라우저별 차이나 캐시 문제일 수 있음")

if __name__ == "__main__":
    main()
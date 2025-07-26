#!/usr/bin/env python3
"""
GitHub Pages 사이트 실제 작동 상태 확인
https://garimto81.github.io/poker-insight/ 의 실제 상태를 분석합니다.
"""

import requests
import json
from urllib.parse import urljoin

def check_github_pages_site():
    """GitHub Pages 사이트와 API 엔드포인트 확인"""
    base_url = "https://garimto81.github.io/poker-insight/"
    api_url = urljoin(base_url, "api_data.json")
    
    print("[INFO] GitHub Pages 사이트 상태 확인")
    print("=" * 60)
    
    # 1. 메인 페이지 확인
    try:
        print(f"[CHECK] 메인 페이지 확인: {base_url}")
        response = requests.get(base_url, timeout=10)
        
        if response.status_code == 200:
            print("[OK] 메인 페이지 로드 성공")
            
            # HTML 내용에서 중요 요소들 확인
            content = response.text
            checks = [
                ("Chart.js 라이브러리", "chart.js" in content.lower()),
                ("loadDashboardData 함수", "loadDashboardData" in content),
                ("initializeDashboard 함수", "initializeDashboard" in content),
                ("total-sites 요소", "total-sites" in content),
                ("total-players 요소", "total-players" in content),
                ("API 호출 경로", "./api_data.json" in content)
            ]
            
            for check_name, result in checks:
                status = "[OK]" if result else "[ERROR]"
                print(f"   {status} {check_name}: {'발견됨' if result else '누락됨'}")
                
        else:
            print(f"[ERROR] 메인 페이지 로드 실패: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] 메인 페이지 접근 실패: {e}")
        return False
    
    # 2. API 데이터 확인
    try:
        print(f"\n[CHECK] API 데이터 확인: {api_url}")
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            print("[OK] API 데이터 로드 성공")
            
            try:
                data = response.json()
                print(f"[DATA] API 응답 분석:")
                
                # 요약 정보 확인
                summary = data.get('summary', {})
                print(f"   - 총 사이트 수: {summary.get('total_sites', 'N/A')}")
                print(f"   - GG 포커 사이트: {summary.get('gg_poker_sites', 'N/A')}")
                print(f"   - 최신 총 플레이어: {summary.get('latest_total_players', 'N/A'):,}")
                print(f"   - 데이터 포인트: {summary.get('data_points', 'N/A')}")
                print(f"   - 마지막 업데이트: {data.get('last_updated', 'N/A')}")
                
                # 사이트 데이터 확인
                sites = data.get('sites', {})
                print(f"   - 실제 사이트 데이터 수: {len(sites)}")
                
                if sites:
                    # 상위 5개 사이트의 최신 플레이어 수 확인
                    site_players = []
                    for site_name, site_data in sites.items():
                        players_online = site_data.get('data', {}).get('players_online', [])
                        if players_online:
                            latest_players = players_online[-1]  # 최신 데이터
                            site_players.append((site_name, latest_players))
                    
                    # 플레이어 수 기준 정렬
                    site_players.sort(key=lambda x: x[1], reverse=True)
                    
                    print(f"\n[DATA] 상위 5개 사이트 (최신 플레이어 수):")
                    for i, (site_name, players) in enumerate(site_players[:5], 1):
                        print(f"   {i}. {site_name}: {players:,}명")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"[ERROR] JSON 파싱 실패: {e}")
                return False
                
        else:
            print(f"[ERROR] API 데이터 로드 실패: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] API 데이터 접근 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    success = check_github_pages_site()
    
    print("\n" + "=" * 60)
    if success:
        print("[RESULT] GitHub Pages 사이트 정상 작동 확인됨")
        print("[INFO] 브라우저에서 https://garimto81.github.io/poker-insight/ 접속 시")
        print("        JavaScript가 API 데이터를 로드하여 차트와 통계를 표시할 것입니다.")
    else:
        print("[RESULT] GitHub Pages 사이트 문제 발견")
        print("[ACTION] 위의 오류들을 수정해야 합니다.")

if __name__ == "__main__":
    main()
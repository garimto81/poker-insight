#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerScout 데이터 수집을 위한 다양한 크롤링 방법
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import requests
import cloudscraper
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AdvancedPokerScoutCrawler:
    def __init__(self):
        self.results = []
        
    def parse_table_data(self, soup):
        """테이블 데이터 파싱"""
        table = soup.find('table', {'class': 'ranktable'})
        if not table:
            return None
            
        rows = table.find_all('tr')[1:]  # 헤더 제외
        results = []
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 6:
                data = {
                    'rank': cols[0].text.strip(),
                    'name': cols[1].text.strip(),
                    'network': self.extract_network(cols[1]),
                    'cash_players': self.parse_number(cols[2].text.strip()),
                    'tournament_players': self.parse_number(cols[3].text.strip()),
                    'total_players': self.parse_number(cols[4].text.strip()),
                    '7_day_average': self.parse_number(cols[5].text.strip())
                }
                results.append(data)
                
        return results
        
    def parse_number(self, text):
        """숫자 파싱 (1,234 -> 1234)"""
        if not text or text == '-':
            return 0
        try:
            return int(text.replace(',', '').replace(' ', ''))
        except:
            return 0
            
    def extract_network(self, cell):
        """네트워크 정보 추출"""
        title = cell.get('title', '')
        if title:
            return title
        return 'Unknown'
        
    def method1_cloudscraper(self):
        """방법 1: CloudScraper 사용 (Cloudflare 우회)"""
        print("\n=== 방법 1: CloudScraper 사용 ===")
        try:
            scraper = cloudscraper.create_scraper()
            response = scraper.get('https://www.pokerscout.com', timeout=30)
            
            if response.status_code == 200:
                print(f"✓ 성공! 응답 크기: {len(response.content)} bytes")
                soup = BeautifulSoup(response.content, 'html.parser')
                results = self.parse_table_data(soup)
                if results:
                    print(f"✓ {len(results)}개 사이트 데이터 수집 성공!")
                    return results
                else:
                    print("✗ 테이블 파싱 실패")
            else:
                print(f"✗ 실패: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"✗ 오류: {str(e)}")
        return None
        
    def method2_undetected_chrome(self):
        """방법 2: Undetected ChromeDriver 사용"""
        print("\n=== 방법 2: Undetected ChromeDriver 사용 ===")
        driver = None
        try:
            print("Chrome 드라이버 시작...")
            options = uc.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = uc.Chrome(options=options)
            
            print("PokerScout 접속 중...")
            driver.get('https://www.pokerscout.com')
            
            # Cloudflare 통과 대기
            print("Cloudflare 체크 대기...")
            time.sleep(15)
            
            # 테이블 확인
            try:
                table = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ranktable"))
                )
                print("✓ 테이블 발견!")
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                results = self.parse_table_data(soup)
                if results:
                    print(f"✓ {len(results)}개 사이트 데이터 수집 성공!")
                    return results
                    
            except Exception as e:
                print(f"✗ 테이블 대기 실패: {str(e)}")
                
        except Exception as e:
            print(f"✗ 오류: {str(e)}")
        finally:
            if driver:
                driver.quit()
        return None
        
    def method3_mobile_version(self):
        """방법 3: 모바일 버전 시도"""
        print("\n=== 방법 3: 모바일 버전 시도 ===")
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        urls = [
            'https://m.pokerscout.com',
            'https://mobile.pokerscout.com',
            'https://www.pokerscout.com/mobile',
            'https://www.pokerscout.com/?mobile=1'
        ]
        
        for url in urls:
            try:
                print(f"시도 중: {url}")
                response = requests.get(url, headers=mobile_headers, timeout=10)
                if response.status_code == 200:
                    print(f"✓ 성공! {url}")
                    soup = BeautifulSoup(response.content, 'html.parser')
                    results = self.parse_table_data(soup)
                    if results:
                        return results
            except Exception as e:
                print(f"  ✗ 실패: {str(e)}")
                
        return None
        
    def method4_api_endpoints(self):
        """방법 4: API 엔드포인트 탐색"""
        print("\n=== 방법 4: API 엔드포인트 탐색 ===")
        api_endpoints = [
            'https://www.pokerscout.com/api/data',
            'https://www.pokerscout.com/api/rankings',
            'https://www.pokerscout.com/data.json',
            'https://www.pokerscout.com/rankings.json',
            'https://api.pokerscout.com/rankings',
            'https://data.pokerscout.com/current'
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        for endpoint in api_endpoints:
            try:
                print(f"시도 중: {endpoint}")
                response = requests.get(endpoint, headers=headers, timeout=10)
                if response.status_code == 200:
                    print(f"✓ 발견! {endpoint}")
                    try:
                        data = response.json()
                        print(f"JSON 데이터 크기: {len(str(data))}")
                        return self.parse_api_data(data)
                    except:
                        print("JSON이 아님, HTML 파싱 시도...")
                        soup = BeautifulSoup(response.content, 'html.parser')
                        return self.parse_table_data(soup)
            except Exception as e:
                print(f"  ✗ {response.status_code if 'response' in locals() else 'Connection error'}")
                
        return None
        
    def parse_api_data(self, data):
        """API 데이터 파싱"""
        # API 응답 구조에 따라 파싱 로직 구현
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'sites' in data:
            return data['sites']
        return None
        
    def method5_cached_pages(self):
        """방법 5: 캐시된 페이지 접근"""
        print("\n=== 방법 5: 캐시된 페이지 접근 ===")
        
        # Google Cache
        google_cache_url = "https://webcache.googleusercontent.com/search?q=cache:pokerscout.com"
        
        try:
            print("Google Cache 시도...")
            response = requests.get(google_cache_url, timeout=10)
            if response.status_code == 200:
                print("✓ Google Cache 접근 성공!")
                soup = BeautifulSoup(response.content, 'html.parser')
                results = self.parse_table_data(soup)
                if results:
                    return results
        except Exception as e:
            print(f"✗ Google Cache 실패: {str(e)}")
            
        # Wayback Machine
        try:
            print("Wayback Machine 최신 스냅샷 확인...")
            # 최신 스냅샷 URL 가져오기
            wayback_api = "http://archive.org/wayback/available?url=pokerscout.com"
            response = requests.get(wayback_api, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'archived_snapshots' in data and 'closest' in data['archived_snapshots']:
                    snapshot_url = data['archived_snapshots']['closest']['url']
                    print(f"✓ 스냅샷 발견: {snapshot_url}")
                    
                    snapshot_response = requests.get(snapshot_url, timeout=10)
                    if snapshot_response.status_code == 200:
                        soup = BeautifulSoup(snapshot_response.content, 'html.parser')
                        results = self.parse_table_data(soup)
                        if results:
                            print("✓ Wayback Machine에서 데이터 수집 성공!")
                            return results
        except Exception as e:
            print(f"✗ Wayback Machine 실패: {str(e)}")
            
        return None
        
    def run_all_methods(self):
        """모든 방법 순차 실행"""
        print("PokerScout 데이터 수집을 위한 다양한 방법 시도 중...")
        
        methods = [
            ('CloudScraper', self.method1_cloudscraper),
            ('Mobile Version', self.method3_mobile_version),
            ('Cached Pages', self.method5_cached_pages),
            ('API Endpoints', self.method4_api_endpoints),
            ('Undetected Chrome', self.method2_undetected_chrome)
        ]
        
        for method_name, method_func in methods:
            print(f"\n{'='*50}")
            print(f"시도 중: {method_name}")
            print(f"{'='*50}")
            
            try:
                results = method_func()
                if results and len(results) > 0:
                    print(f"\n🎉 성공! {method_name}으로 {len(results)}개 사이트 데이터 수집 완료!")
                    
                    # 결과 저장
                    output = {
                        'source': 'PokerScout.com',
                        'method': method_name,
                        'timestamp': datetime.now().isoformat(),
                        'site_count': len(results),
                        'data': results
                    }
                    
                    with open('pokerscout_success.json', 'w', encoding='utf-8') as f:
                        json.dump(output, f, indent=2, ensure_ascii=False)
                    
                    print(f"✓ 데이터가 'pokerscout_success.json'에 저장되었습니다.")
                    
                    # 상위 5개 사이트 출력
                    print("\n상위 5개 포커 사이트:")
                    for i, site in enumerate(results[:5]):
                        print(f"{site['rank']}. {site['name']} - {site['total_players']:,} players")
                    
                    return True
                else:
                    print(f"✗ {method_name} 실패 - 데이터 없음")
                    
            except Exception as e:
                print(f"✗ {method_name} 오류: {str(e)}")
                
            # 방법 간 딜레이
            time.sleep(2)
            
        print("\n💀 모든 방법 실패...")
        return False

if __name__ == "__main__":
    crawler = AdvancedPokerScoutCrawler()
    success = crawler.run_all_methods()
    
    if not success:
        print("\n⚠️  모든 크롤링 방법이 실패했습니다.")
        print("권장 사항:")
        print("1. VPN 사용하여 다른 지역에서 접속")
        print("2. PokerScout에 직접 문의하여 API 액세스 요청")
        print("3. 대체 데이터 소스 사용 고려")
    else:
        print("\n✅ 프로젝트 계속 진행 가능!")
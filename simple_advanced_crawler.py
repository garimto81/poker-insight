#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerScout 데이터 수집 - 단순화된 버전
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

class PokerScoutHunter:
    def __init__(self):
        self.session = requests.Session()
        
    def parse_table_data(self, soup):
        """테이블 데이터 파싱"""
        table = soup.find('table', {'class': 'ranktable'})
        if not table:
            # 다른 가능한 선택자들 시도
            table = soup.find('table', id='ranktable')
            if not table:
                table = soup.find('table', {'id': 'rankings'})
            if not table:
                tables = soup.find_all('table')
                for t in tables:
                    if 'rank' in str(t).lower() or 'poker' in str(t).lower():
                        table = t
                        break
                        
        if not table:
            print("테이블을 찾을 수 없습니다.")
            return None
            
        rows = table.find_all('tr')
        if len(rows) < 2:
            print("데이터 행이 없습니다.")
            return None
            
        results = []
        header_found = False
        
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 5:  # 최소 5개 컬럼
                # 헤더 스킵
                if not header_found and any('rank' in col.text.lower() for col in cols):
                    header_found = True
                    continue
                    
                if header_found or len(results) == 0:  # 첫 데이터 행부터
                    try:
                        data = {
                            'rank': self.parse_number(cols[0].text.strip()) or len(results) + 1,
                            'name': cols[1].text.strip(),
                            'cash_players': self.parse_number(cols[2].text.strip()) if len(cols) > 2 else 0,
                            'tournament_players': self.parse_number(cols[3].text.strip()) if len(cols) > 3 else 0,
                            'total_players': self.parse_number(cols[4].text.strip()) if len(cols) > 4 else 0,
                            '7_day_average': self.parse_number(cols[5].text.strip()) if len(cols) > 5 else 0
                        }
                        
                        # 유효한 데이터인지 확인
                        if data['name'] and len(data['name']) > 1:
                            results.append(data)
                            
                    except Exception as e:
                        continue
                        
        return results if results else None
        
    def parse_number(self, text):
        """숫자 파싱"""
        if not text or text == '-' or text == '':
            return 0
        text = text.replace(',', '').replace(' ', '').replace('players', '')
        try:
            return int(float(text))
        except:
            return 0
            
    def method_cloudscraper(self):
        """CloudScraper 방법"""
        print("\n=== CloudScraper 시도 ===")
        try:
            scraper = cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
            )
            
            print("PokerScout 접속 중...")
            response = scraper.get('https://www.pokerscout.com', timeout=30)
            
            print(f"응답 코드: {response.status_code}")
            print(f"응답 크기: {len(response.content)} bytes")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 페이지 내용 확인
                if 'cloudflare' in response.text.lower():
                    print("Cloudflare 차단 감지됨")
                    return None
                    
                results = self.parse_table_data(soup)
                if results and len(results) > 0:
                    print(f"✓ 성공! {len(results)}개 사이트 발견")
                    return results
                else:
                    print("데이터 파싱 실패 - HTML 구조 확인")
                    # HTML 일부 출력
                    print("\nHTML 샘플:")
                    print(response.text[:1000])
            else:
                print(f"HTTP 오류: {response.status_code}")
                
        except Exception as e:
            print(f"오류: {str(e)}")
        return None
        
    def method_mobile_headers(self):
        """모바일 헤더로 시도"""
        print("\n=== 모바일 헤더 시도 ===")
        
        mobile_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Android 11; Mobile; rv:83.0) Gecko/83.0 Firefox/83.0',
            'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36'
        ]
        
        for agent in mobile_agents:
            try:
                headers = {
                    'User-Agent': agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive'
                }
                
                print(f"시도 중: {agent[:50]}...")
                response = requests.get('https://www.pokerscout.com', headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    results = self.parse_table_data(soup)
                    if results:
                        print(f"✓ 모바일 접근 성공! {len(results)}개 사이트")
                        return results
                        
                time.sleep(2)
                
            except Exception as e:
                print(f"  실패: {str(e)}")
                
        return None
        
    def method_wayback_machine(self):
        """Wayback Machine 시도"""
        print("\n=== Wayback Machine 시도 ===")
        try:
            # 최신 스냅샷 찾기
            api_url = "http://archive.org/wayback/available?url=pokerscout.com"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'archived_snapshots' in data and 'closest' in data['archived_snapshots']:
                    snapshot_url = data['archived_snapshots']['closest']['url']
                    timestamp = data['archived_snapshots']['closest']['timestamp']
                    
                    print(f"스냅샷 발견: {timestamp}")
                    print(f"URL: {snapshot_url}")
                    
                    # 스냅샷 데이터 가져오기
                    snapshot_response = requests.get(snapshot_url, timeout=15)
                    if snapshot_response.status_code == 200:
                        soup = BeautifulSoup(snapshot_response.content, 'html.parser')
                        results = self.parse_table_data(soup)
                        if results:
                            print(f"✓ Wayback Machine 성공! {len(results)}개 사이트")
                            return results
                            
        except Exception as e:
            print(f"Wayback Machine 오류: {str(e)}")
            
        return None
        
    def method_google_cache(self):
        """Google Cache 시도"""
        print("\n=== Google Cache 시도 ===")
        try:
            cache_url = "https://webcache.googleusercontent.com/search?q=cache:www.pokerscout.com"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(cache_url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = self.parse_table_data(soup)
                if results:
                    print(f"✓ Google Cache 성공! {len(results)}개 사이트")
                    return results
                    
        except Exception as e:
            print(f"Google Cache 오류: {str(e)}")
            
        return None
        
    def method_direct_with_delay(self):
        """지연시간을 두고 직접 접근"""
        print("\n=== 지연 접근 시도 ===")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        try:
            # 첫 방문 (쿠키 설정)
            print("첫 방문 - 쿠키 설정...")
            response1 = session.get('https://www.pokerscout.com', timeout=15)
            print(f"첫 방문 응답: {response1.status_code}")
            
            # 잠시 대기
            time.sleep(5)
            
            # 두 번째 방문
            print("두 번째 방문...")
            response2 = session.get('https://www.pokerscout.com', timeout=15)
            print(f"두 번째 방문 응답: {response2.status_code}")
            
            if response2.status_code == 200:
                soup = BeautifulSoup(response2.content, 'html.parser')
                results = self.parse_table_data(soup)
                if results:
                    print(f"✓ 지연 접근 성공! {len(results)}개 사이트")
                    return results
                    
        except Exception as e:
            print(f"지연 접근 오류: {str(e)}")
            
        return None
        
    def hunt_data(self):
        """모든 방법 시도"""
        print("🎯 PokerScout 데이터 헌팅 시작!")
        print("="*60)
        
        methods = [
            ("CloudScraper", self.method_cloudscraper),
            ("모바일 헤더", self.method_mobile_headers),
            ("지연 접근", self.method_direct_with_delay),
            ("Google Cache", self.method_google_cache),
            ("Wayback Machine", self.method_wayback_machine)
        ]
        
        for method_name, method_func in methods:
            print(f"\n🔍 {method_name} 시도 중...")
            try:
                results = method_func()
                if results and len(results) > 0:
                    print(f"\n🎉 성공! {method_name}으로 데이터 수집 완료!")
                    
                    # 결과 저장
                    output = {
                        'source': 'PokerScout.com',
                        'method': method_name,
                        'timestamp': datetime.now().isoformat(),
                        'total_sites': len(results),
                        'data': results
                    }
                    
                    with open('pokerscout_real_data.json', 'w', encoding='utf-8') as f:
                        json.dump(output, f, indent=2, ensure_ascii=False)
                    
                    print(f"\n💾 데이터 저장 완료: pokerscout_real_data.json")
                    print(f"📊 수집된 사이트 수: {len(results)}")
                    
                    print("\n🏆 상위 10개 포커 사이트:")
                    for i, site in enumerate(results[:10]):
                        players = site['total_players']
                        avg = site['7_day_average']
                        print(f"{site['rank']:2d}. {site['name']:<20} - {players:,} players (7일 평균: {avg:,})")
                    
                    return True
                else:
                    print(f"❌ {method_name} 실패")
                    
            except Exception as e:
                print(f"❌ {method_name} 오류: {str(e)}")
                
            # 방법 간 휴식
            time.sleep(3)
            
        print("\n💀 모든 방법 실패... 프로젝트 폐기 위기!")
        return False

if __name__ == "__main__":
    hunter = PokerScoutHunter()
    success = hunter.hunt_data()
    
    if success:
        print("\n✅ 프로젝트 구출 성공!")
    else:
        print("\n💀 프로젝트 폐기...")
        print("\n최후의 수단:")
        print("1. VPN 사용")
        print("2. 다른 네트워크에서 시도")
        print("3. PokerScout 운영진에게 API 액세스 요청")
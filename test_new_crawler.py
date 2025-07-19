#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새로운 크롤러 테스트
"""
import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime

def test_crawl():
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'linux', 'mobile': False}
    )
    
    print("PokerScout 크롤링 시작...")
    
    try:
        response = scraper.get('https://www.pokerscout.com', timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'class': 'rankTable'})
        
        if not table:
            print("테이블을 찾을 수 없습니다")
            return
        
        collected_data = []
        rows = table.find_all('tr')[1:]  # Skip header
        print(f"발견된 행 수: {len(rows)}")
        
        for i, row in enumerate(rows):
            try:
                # CoinPoker 광고 행은 건너뛰기
                if 'cus_top_traffic_coin' in row.get('class', []):
                    continue
                
                # 사이트명 추출
                brand_title = row.find('span', {'class': 'brand-title'})
                if not brand_title:
                    continue
                
                site_name = brand_title.get_text(strip=True)
                if not site_name or len(site_name) < 2:
                    continue
                
                # 각 데이터 필드를 ID로 직접 찾기
                players_online = 0
                cash_players = 0
                peak_24h = 0
                seven_day_avg = 0
                
                # Players Online
                online_td = row.find('td', {'id': 'online'})
                if online_td:
                    online_span = online_td.find('span')
                    if online_span:
                        online_text = online_span.get_text(strip=True).replace(',', '')
                        if online_text.isdigit():
                            players_online = int(online_text)
                
                # Cash Players
                cash_td = row.find('td', {'id': 'cash'})
                if cash_td:
                    cash_text = cash_td.get_text(strip=True).replace(',', '')
                    if cash_text.isdigit():
                        cash_players = int(cash_text)
                
                # 24H Peak
                peak_td = row.find('td', {'id': 'peak'})
                if peak_td:
                    peak_span = peak_td.find('span')
                    if peak_span:
                        peak_text = peak_span.get_text(strip=True).replace(',', '')
                        if peak_text.isdigit():
                            peak_24h = int(peak_text)
                
                # 7 Day Average
                avg_td = row.find('td', {'id': 'avg'})
                if avg_td:
                    avg_span = avg_td.find('span')
                    if avg_span:
                        avg_text = avg_span.get_text(strip=True).replace(',', '')
                        if avg_text.isdigit():
                            seven_day_avg = int(avg_text)
                
                # 데이터 검증 - 모든 값이 0인 경우 제외
                if players_online == 0 and cash_players == 0 and peak_24h == 0:
                    continue
                
                site_data = {
                    'site_name': site_name,
                    'players_online': players_online,
                    'cash_players': cash_players,
                    'peak_24h': peak_24h,
                    'seven_day_avg': seven_day_avg
                }
                
                collected_data.append(site_data)
                
                # GGNetwork만 출력
                if 'GG' in site_name:
                    print(f"\n[{site_name}]")
                    print(f"  Players Online: {players_online:,}")
                    print(f"  Cash Players: {cash_players:,}")
                    print(f"  24H Peak: {peak_24h:,}")
                    print(f"  7 Day Avg: {seven_day_avg:,}")
                    
            except Exception as e:
                print(f"행 {i+1} 파싱 오류: {str(e)}")
                continue
        
        print(f"\n크롤링 완료: {len(collected_data)}개 사이트")
        
        # 결과 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_crawl_result_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(collected_data, f, indent=2, ensure_ascii=False)
        print(f"결과 저장: {filename}")
        
    except Exception as e:
        print(f"크롤링 실패: {str(e)}")

if __name__ == "__main__":
    test_crawl()
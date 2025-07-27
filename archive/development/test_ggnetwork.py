#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GGNetwork 데이터 수집 문제 진단
"""
import cloudscraper
from bs4 import BeautifulSoup

def test_ggnetwork():
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'linux', 'mobile': False}
    )
    
    response = scraper.get('https://www.pokerscout.com', timeout=30)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'class': 'rankTable'})
    
    if not table:
        print("테이블을 찾을 수 없습니다")
        return
    
    rows = table.find_all('tr')[1:]
    
    # GGNetwork 행 찾기
    for i, row in enumerate(rows):
        brand_title = row.find('span', {'class': 'brand-title'})
        if brand_title and 'GGNetwork' in brand_title.get_text():
            print(f"\n=== GGNetwork 행 발견 (행 {i+1}) ===")
            
            # HTML 구조 출력
            print("\n전체 행 HTML (처음 1000자):")
            print(str(row)[:1000])
            
            # 모든 TD 요소 확인
            tds = row.find_all('td')
            print(f"\nTD 개수: {len(tds)}")
            
            for j, td in enumerate(tds):
                print(f"\n--- TD {j+1} ---")
                print(f"ID: {td.get('id', 'None')}")
                print(f"Class: {td.get('class', 'None')}")
                print(f"Text: {td.get_text(strip=True)}")
                
                # span 태그 확인
                spans = td.find_all('span')
                for k, span in enumerate(spans):
                    print(f"  Span {k+1}: {span.get_text(strip=True)}")
            
            # 현재 코드대로 데이터 추출
            print("\n=== 현재 코드로 추출한 값 ===")
            
            # Players Online
            online_td = row.find('td', {'id': 'online'})
            if online_td:
                online_span = online_td.find('span')
                if online_span:
                    online_text = online_span.get_text(strip=True).replace(',', '')
                    print(f"Players Online: {online_text}")
                else:
                    print(f"Players Online (td text): {online_td.get_text(strip=True)}")
            
            # Cash Players
            cash_td = row.find('td', {'id': 'cash'})
            if cash_td:
                cash_text = cash_td.get_text(strip=True).replace(',', '')
                print(f"Cash Players: {cash_text}")
            
            # 24H Peak
            peak_td = row.find('td', {'id': 'peak'})
            if peak_td:
                peak_span = peak_td.find('span')
                if peak_span:
                    peak_text = peak_span.get_text(strip=True).replace(',', '')
                    print(f"24H Peak: {peak_text}")
            
            # 7 Day Average
            avg_td = row.find('td', {'id': 'avg'})
            if avg_td:
                avg_span = avg_td.find('span')
                if avg_span:
                    avg_text = avg_span.get_text(strip=True).replace(',', '')
                    print(f"7 Day Average: {avg_text}")
            
            break

if __name__ == "__main__":
    test_ggnetwork()
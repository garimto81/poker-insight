#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 크롤러 테스트 스크립트 (데이터베이스 없이)
"""
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import sys

# Windows에서 유니코드 출력 문제 해결
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_pokerscout():
    print("\n=== Testing PokerScout Access ===")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        url = 'https://www.pokerscout.com'
        print(f"Accessing {url}...")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 테이블 찾기
            table = soup.find('table', {'class': 'ranktable'})
            if table:
                print("✓ Found ranking table")
                
                # 상위 5개 사이트 출력
                rows = table.find_all('tr')[1:6]
                print(f"\nTop {len(rows)} poker sites:")
                
                for i, row in enumerate(rows, 1):
                    cols = row.find_all('td')
                    if len(cols) >= 6:
                        rank = cols[0].text.strip()
                        site_name = cols[1].text.strip()
                        total_players = cols[4].text.strip()
                        seven_day_avg = cols[5].text.strip()
                        
                        print(f"{rank}. {site_name}")
                        print(f"   Total Players: {total_players}")
                        print(f"   7-Day Average: {seven_day_avg}")
                        print()
                
                return True
            else:
                print("✗ Could not find ranking table")
                print("Page structure might have changed")
                
                # 디버깅을 위해 일부 HTML 출력
                print("\nFirst 500 characters of HTML:")
                print(response.text[:500])
        else:
            print(f"✗ Failed to access site (Status: {response.status_code})")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_pokernews():
    print("\n=== Testing PokerNews Access ===")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        url = 'https://www.pokernews.com/news/'
        print(f"Accessing {url}...")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 뉴스 기사 찾기
            articles = soup.find_all('article', limit=5)
            
            if articles:
                print(f"✓ Found {len(articles)} articles")
                print("\nLatest news:")
                
                for i, article in enumerate(articles, 1):
                    # 제목 찾기
                    title_elem = article.find(['h2', 'h3'])
                    if title_elem:
                        link_elem = title_elem.find('a')
                        if link_elem:
                            title = link_elem.text.strip()
                            url = link_elem.get('href', '')
                            
                            print(f"\n{i}. {title}")
                            
                            # 날짜 찾기
                            date_elem = article.find('time')
                            if date_elem:
                                print(f"   Date: {date_elem.text.strip()}")
                            
                            # 요약 찾기
                            summary_elem = article.find('p')
                            if summary_elem:
                                summary = summary_elem.text.strip()
                                print(f"   Summary: {summary[:100]}...")
                
                return True
            else:
                print("✗ Could not find any articles")
                print("Page structure might have changed")
                
                # 디버깅 정보
                print("\nChecking for alternative selectors...")
                # h2 태그 확인
                h2_tags = soup.find_all('h2', limit=5)
                if h2_tags:
                    print(f"Found {len(h2_tags)} h2 tags")
                    for h2 in h2_tags[:3]:
                        print(f"  - {h2.text.strip()[:50]}...")
                        
        else:
            print(f"✗ Failed to access site (Status: {response.status_code})")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    print("Starting crawler tests...")
    print("=" * 50)
    
    # PokerScout 테스트
    ps_success = test_pokerscout()
    
    # 잠시 대기
    time.sleep(2)
    
    # PokerNews 테스트
    pn_success = test_pokernews()
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print(f"PokerScout: {'✓ PASSED' if ps_success else '✗ FAILED'}")
    print(f"PokerNews: {'✓ PASSED' if pn_success else '✗ FAILED'}")
    
    if ps_success and pn_success:
        print("\nAll tests passed! The crawlers should work correctly.")
    else:
        print("\nSome tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
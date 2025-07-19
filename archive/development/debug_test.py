#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
디버깅용 테스트 스크립트
"""
import requests
from bs4 import BeautifulSoup
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def debug_pokernews():
    print("=== Debugging PokerNews ===")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    try:
        # 메인 페이지 테스트
        url = 'https://www.pokernews.com'
        print(f"\nTesting main page: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 다양한 선택자 시도
            print("\nSearching for news content...")
            
            # 1. article 태그
            articles = soup.find_all('article')
            print(f"Found {len(articles)} article tags")
            
            # 2. 클래스명으로 찾기
            news_items = soup.find_all(class_=['news-item', 'article', 'post', 'entry'])
            print(f"Found {len(news_items)} elements with news-related classes")
            
            # 3. 링크 패턴으로 찾기
            links = soup.find_all('a', href=True)
            news_links = [a for a in links if '/news/' in a['href'] or '/article/' in a['href']]
            print(f"Found {len(news_links)} links containing /news/ or /article/")
            
            # 4. 제목 태그 찾기
            titles = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            print(f"Found {len(titles)} heading tags")
            
            # 샘플 출력
            if titles:
                print("\nFirst 5 titles found:")
                for i, title in enumerate(titles[:5]):
                    text = title.text.strip()
                    if text:
                        print(f"{i+1}. {text[:80]}...")
                        
            # HTML 구조 파악
            print("\nHTML structure sample:")
            sample = str(soup.prettify()[:2000])
            print(sample)
            
    except Exception as e:
        print(f"Error: {str(e)}")

def test_alternative_sources():
    print("\n=== Testing Alternative Sources ===")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # 대체 가능한 포커 데이터 소스들
    sources = {
        'PokerListings': 'https://www.pokerlistings.com',
        'CardPlayer': 'https://www.cardplayer.com',
        '888poker': 'https://www.888poker.com/magazine/'
    }
    
    for name, url in sources.items():
        try:
            print(f"\nTesting {name}: {url}")
            response = requests.get(url, headers=headers, timeout=5)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✓ Accessible")
            else:
                print("✗ Not accessible")
        except Exception as e:
            print(f"✗ Error: {str(e)}")

if __name__ == "__main__":
    debug_pokernews()
    test_alternative_sources()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
대체 데이터 소스를 사용한 크롤러
"""
import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlternativeCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def crawl_888poker_magazine(self):
        """888poker 매거진에서 뉴스 크롤링"""
        try:
            url = 'https://www.888poker.com/magazine/'
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = []
                
                # 기사 찾기
                article_elements = soup.find_all(['article', 'div'], class_=['post', 'article-item', 'news-item'])
                
                for elem in article_elements[:10]:
                    title_elem = elem.find(['h2', 'h3', 'h4'])
                    if title_elem:
                        title = title_elem.text.strip()
                        link_elem = title_elem.find('a') or elem.find('a')
                        url = link_elem.get('href') if link_elem else ''
                        
                        articles.append({
                            'source': '888poker',
                            'title': title,
                            'url': url,
                            'date': datetime.now().isoformat()
                        })
                        
                logger.info(f"Found {len(articles)} articles from 888poker")
                return articles
        except Exception as e:
            logger.error(f"Error crawling 888poker: {str(e)}")
            return []
            
    def get_sample_poker_data(self):
        """테스트용 샘플 데이터 생성"""
        # 실제 환경에서는 실시간 데이터를 크롤링하지만,
        # 테스트를 위해 샘플 데이터 제공
        sample_sites = [
            {
                'rank': 1,
                'name': 'PokerStars',
                'network': 'Independent',
                'cash_players': 8500,
                'tournament_players': 12000,
                'total_players': 20500,
                '7_day_average': 19800
            },
            {
                'rank': 2,
                'name': 'GGPoker',
                'network': 'GGNetwork',
                'cash_players': 7200,
                'tournament_players': 9500,
                'total_players': 16700,
                '7_day_average': 16200
            },
            {
                'rank': 3,
                'name': '888poker',
                'network': '888',
                'cash_players': 1800,
                'tournament_players': 2200,
                'total_players': 4000,
                '7_day_average': 3850
            },
            {
                'rank': 4,
                'name': 'partypoker',
                'network': 'partypoker',
                'cash_players': 1500,
                'tournament_players': 1800,
                'total_players': 3300,
                '7_day_average': 3200
            },
            {
                'rank': 5,
                'name': 'Winamax',
                'network': 'Independent',
                'cash_players': 1200,
                'tournament_players': 1500,
                'total_players': 2700,
                '7_day_average': 2600
            }
        ]
        
        logger.info(f"Generated {len(sample_sites)} sample poker sites")
        return sample_sites
        
    def get_sample_news(self):
        """테스트용 샘플 뉴스 데이터"""
        sample_news = [
            {
                'title': 'WSOP 2024 Main Event Breaks All-Time Record',
                'source': 'Sample',
                'category': 'tournaments',
                'date': datetime.now().isoformat()
            },
            {
                'title': 'GGPoker Launches New High Stakes Cash Games',
                'source': 'Sample',
                'category': 'online-poker',
                'date': datetime.now().isoformat()
            },
            {
                'title': 'Phil Ivey Returns to High Stakes Poker',
                'source': 'Sample',
                'category': 'news',
                'date': datetime.now().isoformat()
            }
        ]
        
        logger.info(f"Generated {len(sample_news)} sample news items")
        return sample_news

def test_alternative_crawler():
    """대체 크롤러 테스트"""
    crawler = AlternativeCrawler()
    
    print("\n=== Testing Alternative Data Sources ===")
    
    # 888poker 매거진 테스트
    print("\n1. Testing 888poker Magazine...")
    news_888 = crawler.crawl_888poker_magazine()
    print(f"   Found {len(news_888)} articles")
    
    # 샘플 데이터 테스트
    print("\n2. Getting sample poker site data...")
    sites = crawler.get_sample_poker_data()
    print(f"   Generated {len(sites)} poker sites")
    for site in sites[:3]:
        print(f"   - {site['name']}: {site['total_players']} players")
        
    print("\n3. Getting sample news data...")
    news = crawler.get_sample_news()
    print(f"   Generated {len(news)} news items")
    for item in news:
        print(f"   - {item['title']}")
        
    # 결과 저장
    results = {
        'timestamp': datetime.now().isoformat(),
        'poker_sites': sites,
        'news': news + news_888,
        'status': 'success'
    }
    
    with open('sample_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n[SUCCESS] Sample data saved to sample_data.json")
    print("\nNOTE: In production, real-time data would be crawled from actual sources.")
    print("Due to access restrictions, using alternative sources and sample data for testing.")

if __name__ == "__main__":
    test_alternative_crawler()
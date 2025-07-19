#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerNews.com 사이트 구조 분석 및 크롤링 테스트
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import cloudscraper
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta

class PokerNewsAnalyzer:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        
    def analyze_pokernews_structure(self):
        """PokerNews 사이트 구조 분석"""
        print("🔍 PokerNews.com 구조 분석 중...")
        
        urls_to_test = [
            'https://www.pokernews.com',
            'https://www.pokernews.com/news/',
            'https://www.pokernews.com/strategy/',
            'https://www.pokernews.com/tournaments/',
            'https://www.pokernews.com/live/',
        ]
        
        for url in urls_to_test:
            try:
                print(f"\n📄 분석 중: {url}")
                response = self.scraper.get(url, timeout=15)
                
                if response.status_code == 200:
                    print(f"✅ 접근 성공! 크기: {len(response.content)} bytes")
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 기사 관련 요소들 찾기
                    self.find_article_elements(soup, url)
                    
                else:
                    print(f"❌ 접근 실패: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 오류: {str(e)}")
                
    def find_article_elements(self, soup, url):
        """기사 관련 요소들 찾기"""
        print("  🔎 기사 요소 탐색:")
        
        # 1. article 태그
        articles = soup.find_all('article')
        print(f"    • article 태그: {len(articles)}개")
        
        # 2. 다양한 뉴스 관련 클래스들
        news_classes = [
            'news-item', 'article-item', 'post', 'entry',
            'story', 'content-item', 'news-card', 'article-card',
            'post-item', 'news-list-item'
        ]
        
        for class_name in news_classes:
            elements = soup.find_all(class_=class_name)
            if elements:
                print(f"    • .{class_name}: {len(elements)}개")
                
        # 3. 링크 패턴 분석
        links = soup.find_all('a', href=True)
        news_links = []
        pattern = r'/(news|article|story|post)/'
        
        for link in links:
            href = link.get('href', '')
            if re.search(pattern, href) and link.text.strip():
                news_links.append({
                    'url': href,
                    'title': link.text.strip()[:50] + '...' if len(link.text.strip()) > 50 else link.text.strip()
                })
                
        print(f"    • 뉴스 링크 패턴: {len(news_links)}개")
        
        # 샘플 링크 출력
        if news_links:
            print("    📝 샘플 뉴스 링크:")
            for i, link in enumerate(news_links[:3]):
                print(f"      {i+1}. {link['title']}")
                
        # 4. 제목 태그들
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        print(f"    • 제목 태그: {len(headings)}개")
        
        # 5. 특정 URL에서 더 자세한 분석
        if 'news' in url:
            self.analyze_news_page(soup)
            
    def analyze_news_page(self, soup):
        """뉴스 페이지 상세 분석"""
        print("  📰 뉴스 페이지 상세 분석:")
        
        # HTML 구조 저장
        with open('pokernews_structure.html', 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print("    💾 HTML 구조 저장: pokernews_structure.html")
        
        # 잠재적 기사 컨테이너 찾기
        potential_containers = soup.find_all(['div', 'section', 'main'], 
                                           class_=re.compile(r'news|article|post|story|content'))
        
        print(f"    • 잠재적 기사 컨테이너: {len(potential_containers)}개")
        
        for i, container in enumerate(potential_containers[:3]):
            classes = container.get('class', [])
            print(f"      컨테이너 {i+1}: {classes}")
            
    def test_news_extraction(self):
        """뉴스 추출 테스트"""
        print("\n🧪 PokerNews 뉴스 추출 테스트...")
        
        try:
            response = self.scraper.get('https://www.pokernews.com/news/', timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 방법 1: article 태그에서 추출
                articles = self.extract_from_articles(soup)
                if articles:
                    print(f"✅ 방법 1 성공: article 태그에서 {len(articles)}개 추출")
                    return articles
                    
                # 방법 2: 링크 패턴으로 추출
                articles = self.extract_from_links(soup)
                if articles:
                    print(f"✅ 방법 2 성공: 링크 패턴에서 {len(articles)}개 추출")
                    return articles
                    
                # 방법 3: 일반적인 선택자로 추출
                articles = self.extract_from_selectors(soup)
                if articles:
                    print(f"✅ 방법 3 성공: 일반 선택자에서 {len(articles)}개 추출")
                    return articles
                    
                print("❌ 모든 추출 방법 실패")
                
            else:
                print(f"❌ 페이지 접근 실패: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 추출 테스트 오류: {str(e)}")
            
        return None
        
    def extract_from_articles(self, soup):
        """article 태그에서 뉴스 추출"""
        articles = soup.find_all('article')
        results = []
        
        for article in articles:
            try:
                # 제목 찾기
                title_elem = article.find(['h1', 'h2', 'h3', 'h4'])
                if not title_elem:
                    continue
                    
                title = title_elem.get_text().strip()
                
                # 링크 찾기
                link_elem = title_elem.find('a') or article.find('a')
                if link_elem:
                    url = link_elem.get('href', '')
                    if not url.startswith('http'):
                        url = 'https://www.pokernews.com' + url
                else:
                    url = ''
                    
                # 날짜 찾기
                date_elem = article.find('time') or article.find(class_=re.compile(r'date|time'))
                date = date_elem.get_text().strip() if date_elem else ''
                
                # 요약 찾기
                summary_elem = article.find('p')
                summary = summary_elem.get_text().strip() if summary_elem else ''
                
                if title and len(title) > 5:
                    results.append({
                        'title': title,
                        'url': url,
                        'date': date,
                        'summary': summary[:200] + '...' if len(summary) > 200 else summary,
                        'source': 'PokerNews'
                    })
                    
            except Exception:
                continue
                
        return results if len(results) > 3 else None
        
    def extract_from_links(self, soup):
        """링크 패턴에서 뉴스 추출"""
        links = soup.find_all('a', href=re.compile(r'/(news|article)/'))
        results = []
        seen_urls = set()
        
        for link in links:
            try:
                url = link.get('href', '')
                if not url.startswith('http'):
                    url = 'https://www.pokernews.com' + url
                    
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                
                title = link.get_text().strip()
                if title and len(title) > 10:
                    results.append({
                        'title': title,
                        'url': url,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'summary': '',
                        'source': 'PokerNews'
                    })
                    
            except Exception:
                continue
                
        return results[:20] if len(results) > 5 else None
        
    def extract_from_selectors(self, soup):
        """일반적인 CSS 선택자로 추출"""
        selectors = [
            'div[class*="news"] h3 a',
            'div[class*="article"] h2 a',
            'div[class*="post"] h3 a',
            '.content-item a',
            '.story-item a',
            'h2 a[href*="/news/"]',
            'h3 a[href*="/news/"]'
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                if len(elements) > 5:
                    results = []
                    for elem in elements[:15]:
                        title = elem.get_text().strip()
                        url = elem.get('href', '')
                        if not url.startswith('http'):
                            url = 'https://www.pokernews.com' + url
                            
                        if title and len(title) > 10:
                            results.append({
                                'title': title,
                                'url': url,
                                'date': datetime.now().strftime('%Y-%m-%d'),
                                'summary': '',
                                'source': 'PokerNews'
                            })
                            
                    if len(results) > 5:
                        print(f"    성공한 선택자: {selector}")
                        return results
                        
            except Exception:
                continue
                
        return None
        
    def save_sample_data(self, articles):
        """샘플 데이터 저장"""
        if not articles:
            return False
            
        output = {
            'source': 'PokerNews.com',
            'timestamp': datetime.now().isoformat(),
            'total_articles': len(articles),
            'data': articles
        }
        
        with open('pokernews_sample_data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        return True
        
    def display_results(self, articles):
        """결과 출력"""
        if not articles:
            print("❌ 추출된 기사가 없습니다.")
            return
            
        print(f"\n📰 PokerNews 기사 {len(articles)}개 추출 성공!")
        print("="*80)
        
        for i, article in enumerate(articles[:10], 1):
            print(f"{i:2d}. {article['title']}")
            if article['date']:
                print(f"    📅 {article['date']}")
            if article['summary']:
                print(f"    📝 {article['summary'][:80]}...")
            print(f"    🔗 {article['url']}")
            print()

def main():
    """메인 실행 함수"""
    print("🚀 PokerNews.com 분석 및 크롤링 테스트")
    print("="*60)
    
    analyzer = PokerNewsAnalyzer()
    
    # 1. 사이트 구조 분석
    analyzer.analyze_pokernews_structure()
    
    # 2. 뉴스 추출 테스트
    articles = analyzer.test_news_extraction()
    
    if articles:
        # 3. 결과 출력
        analyzer.display_results(articles)
        
        # 4. 데이터 저장
        success = analyzer.save_sample_data(articles)
        if success:
            print("💾 샘플 데이터 저장: pokernews_sample_data.json")
            
        print(f"\n✅ PokerNews 크롤링 가능!")
        print(f"📊 추출 가능한 기사 수: {len(articles)}개")
        
    else:
        print(f"\n❌ PokerNews 크롤링 실패")
        print("구조 분석 파일을 확인하여 수동 디버깅 필요")

if __name__ == "__main__":
    main()
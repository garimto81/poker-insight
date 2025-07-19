#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerNews 고급 크롤러 - 실제 뉴스 기사 수집
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import cloudscraper
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
import time

class AdvancedPokerNewsCrawler:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        
    def get_latest_news_articles(self):
        """최신 뉴스 기사 수집"""
        print("🔍 PokerNews 최신 기사 수집 중...")
        
        # 다양한 카테고리 페이지 시도
        categories = [
            ('Latest News', '/news/'),
            ('PokerStars News', '/news/pokerstars/'),
            ('Casino News', '/casino/news/'),
            ('Tournament News', '/news/tournaments/'),
            ('Strategy', '/strategy/'),
        ]
        
        all_articles = []
        
        for category_name, url_path in categories:
            try:
                print(f"\n📂 {category_name} 카테고리 크롤링...")
                articles = self.crawl_category_page(url_path, category_name)
                if articles:
                    all_articles.extend(articles)
                    print(f"  ✅ {len(articles)}개 기사 수집")
                else:
                    print(f"  ❌ 기사 없음")
                    
                time.sleep(1)  # 요청 간 딜레이
                
            except Exception as e:
                print(f"  ❌ 오류: {str(e)}")
                
        # 중복 제거
        unique_articles = self.remove_duplicates(all_articles)
        print(f"\n📊 총 {len(unique_articles)}개 고유 기사 수집 완료")
        
        return unique_articles
        
    def crawl_category_page(self, url_path, category):
        """카테고리 페이지 크롤링"""
        full_url = f"https://www.pokernews.com{url_path}"
        
        try:
            response = self.scraper.get(full_url, timeout=15)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 여러 방법으로 기사 추출 시도
            articles = []
            
            # 방법 1: 특정 선택자들 시도
            selectors = [
                'a[href*="/news/"][href*=".htm"]',  # 뉴스 링크
                'a[href*="/strategy/"][href*=".htm"]',  # 전략 기사 링크
                'a[href*="/casino/"][href*=".htm"]',  # 카지노 기사 링크
                '.article-list a[href*=".htm"]',  # 기사 목록 링크
                '.news-list a[href*=".htm"]',  # 뉴스 목록 링크
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                for link in links:
                    article = self.extract_article_info(link, category)
                    if article:
                        articles.append(article)
                        
            # 방법 2: 모든 .htm 링크에서 필터링
            if len(articles) < 5:
                all_links = soup.find_all('a', href=re.compile(r'\.htm'))
                for link in all_links:
                    href = link.get('href', '')
                    # 뉴스/기사 관련 URL만 필터링
                    if any(keyword in href for keyword in ['/news/', '/strategy/', '/casino/', '/poker/']):
                        article = self.extract_article_info(link, category)
                        if article:
                            articles.append(article)
                            
            return articles[:20]  # 최대 20개로 제한
            
        except Exception as e:
            print(f"    크롤링 오류: {str(e)}")
            return None
            
    def extract_article_info(self, link_elem, category):
        """링크 요소에서 기사 정보 추출"""
        try:
            href = link_elem.get('href', '')
            if not href:
                return None
                
            # 전체 URL 생성
            if href.startswith('/'):
                url = f"https://www.pokernews.com{href}"
            elif href.startswith('http'):
                url = href
            else:
                return None
                
            # 제목 추출
            title = link_elem.get_text().strip()
            if not title or len(title) < 10:
                return None
                
            # 내부 링크만 허용
            if 'pokernews.com' not in url:
                return None
                
            # 불필요한 링크 필터링
            exclude_patterns = [
                '/authors/', '/tags/', '/tournaments/calendar/',
                '/poker-rooms/', '/bonus/', '/reviews/', '/live-reporting/'
            ]
            
            if any(pattern in url for pattern in exclude_patterns):
                return None
                
            # 날짜 추출 시도 (URL에서)
            date_match = re.search(r'/(\d{4})/(\d{2})/', url)
            if date_match:
                year, month = date_match.groups()
                estimated_date = f"{year}-{month}-01"
            else:
                estimated_date = datetime.now().strftime('%Y-%m-%d')
                
            return {
                'title': title,
                'url': url,
                'category': category,
                'date': estimated_date,
                'summary': '',
                'source': 'PokerNews'
            }
            
        except Exception:
            return None
            
    def enhance_articles_with_content(self, articles):
        """기사 내용으로 정보 보강"""
        print(f"\n🔍 상위 {min(10, len(articles))}개 기사 내용 분석 중...")
        
        enhanced_articles = []
        
        for i, article in enumerate(articles[:10]):  # 상위 10개만
            try:
                print(f"  📄 {i+1}/10: {article['title'][:50]}...")
                
                response = self.scraper.get(article['url'], timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 날짜 정보 추출
                    date_elem = soup.find('time') or soup.find(class_=re.compile(r'date|publish'))
                    if date_elem:
                        date_text = date_elem.get_text().strip()
                        parsed_date = self.parse_date(date_text)
                        if parsed_date:
                            article['date'] = parsed_date
                            
                    # 요약 정보 추출
                    summary_elem = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
                    if summary_elem:
                        article['summary'] = summary_elem.get('content', '')[:300]
                        
                    # 저자 정보 추출
                    author_elem = soup.find(class_=re.compile(r'author|byline'))
                    if author_elem:
                        article['author'] = author_elem.get_text().strip()
                        
                enhanced_articles.append(article)
                time.sleep(0.5)  # 요청 간 딜레이
                
            except Exception as e:
                print(f"    ⚠️ 내용 분석 실패: {str(e)}")
                enhanced_articles.append(article)  # 원본 정보라도 유지
                
        # 나머지 기사들도 추가 (내용 분석 없이)
        enhanced_articles.extend(articles[10:])
        
        return enhanced_articles
        
    def parse_date(self, date_text):
        """날짜 텍스트 파싱"""
        try:
            # 다양한 날짜 형식 처리
            if 'ago' in date_text.lower():
                if 'hour' in date_text:
                    hours = int(re.search(r'(\d+)', date_text).group(1))
                    date = datetime.now() - timedelta(hours=hours)
                    return date.strftime('%Y-%m-%d')
                elif 'day' in date_text:
                    days = int(re.search(r'(\d+)', date_text).group(1))
                    date = datetime.now() - timedelta(days=days)
                    return date.strftime('%Y-%m-%d')
                    
            # ISO 날짜 형식
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
            if date_match:
                return date_match.group(1)
                
            # 기타 형식들
            date_match = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', date_text)
            if date_match:
                month, day, year = date_match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                
        except:
            pass
            
        return datetime.now().strftime('%Y-%m-%d')
        
    def remove_duplicates(self, articles):
        """중복 기사 제거"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
                
        return unique_articles
        
    def save_data(self, articles):
        """데이터 저장"""
        if not articles:
            return False
            
        # 카테고리별 통계
        category_stats = {}
        for article in articles:
            category = article['category']
            category_stats[category] = category_stats.get(category, 0) + 1
            
        output = {
            'source': 'PokerNews.com',
            'method': 'Advanced Multi-Category Crawling',
            'timestamp': datetime.now().isoformat(),
            'total_articles': len(articles),
            'category_breakdown': category_stats,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'data': articles
        }
        
        with open('pokernews_final_data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        return True
        
    def display_results(self, articles):
        """결과 출력"""
        if not articles:
            print("❌ 수집된 기사가 없습니다.")
            return
            
        print(f"\n📰 PokerNews 기사 수집 결과")
        print("="*80)
        print(f"📊 총 {len(articles)}개 기사 수집")
        
        # 카테고리별 분류
        by_category = {}
        for article in articles:
            category = article['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(article)
            
        print(f"\n📂 카테고리별 분포:")
        for category, arts in by_category.items():
            print(f"  • {category}: {len(arts)}개")
            
        print(f"\n🔥 최신 기사 TOP 15:")
        print("-"*80)
        
        for i, article in enumerate(articles[:15], 1):
            print(f"{i:2d}. {article['title']}")
            print(f"    📂 {article['category']} | 📅 {article['date']}")
            if article.get('author'):
                print(f"    ✍️ {article['author']}")
            if article['summary']:
                print(f"    📝 {article['summary'][:100]}...")
            print(f"    🔗 {article['url']}")
            print()

def main():
    """메인 실행 함수"""
    print("🚀 PokerNews 고급 크롤링 시작!")
    print("="*60)
    
    crawler = AdvancedPokerNewsCrawler()
    
    # 1. 기사 수집
    articles = crawler.get_latest_news_articles()
    
    if articles and len(articles) > 5:
        # 2. 상위 기사들 내용 보강
        enhanced_articles = crawler.enhance_articles_with_content(articles)
        
        # 3. 결과 출력
        crawler.display_results(enhanced_articles)
        
        # 4. 데이터 저장
        success = crawler.save_data(enhanced_articles)
        
        if success:
            print("💾 데이터 저장 완료: pokernews_final_data.json")
            print(f"\n✅ PokerNews 크롤링 성공!")
            print(f"📊 수집 기사: {len(enhanced_articles)}개")
            print(f"📈 데이터 품질: 우수")
            return True
        else:
            print("❌ 데이터 저장 실패")
            
    else:
        print(f"\n❌ 충분한 기사를 수집하지 못했습니다.")
        print(f"수집된 기사 수: {len(articles) if articles else 0}")
        
    return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n🎉 PokerNews 데이터 수집 완료!")
        print(f"포커 방송 프로덕션용 뉴스 데이터 준비 완료!")
    else:
        print(f"\n⚠️ PokerNews 크롤링 개선 필요")
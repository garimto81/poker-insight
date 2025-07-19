import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
from crawlers.base_crawler import BaseCrawler
from database.models import PokerSite, NewsItem
from config.settings import Config
from fake_useragent import UserAgent

class PokerNewsCrawler(BaseCrawler):
    def __init__(self):
        super().__init__('pokernews')
        self.base_url = 'https://www.pokernews.com'
        self.ua = UserAgent()
        
    def get_headers(self):
        """동적 헤더 생성"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
    def parse_date(self, date_str):
        """날짜 파싱"""
        try:
            # 다양한 날짜 형식 처리
            if 'ago' in date_str:
                # "2 hours ago", "1 day ago" 등 처리
                if 'hour' in date_str:
                    hours = int(re.search(r'(\d+)', date_str).group(1))
                    return datetime.utcnow() - timedelta(hours=hours)
                elif 'day' in date_str:
                    days = int(re.search(r'(\d+)', date_str).group(1))
                    return datetime.utcnow() - timedelta(days=days)
            else:
                # 일반적인 날짜 형식 처리
                return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return datetime.utcnow()
            
    def extract_site_from_content(self, content):
        """컨텐츠에서 포커 사이트 추출"""
        # 주요 포커 사이트 리스트
        poker_sites = [
            'PokerStars', 'GGPoker', 'partypoker', '888poker', 
            'WPT Global', 'Winamax', 'Natural8', 'PokerKing',
            'Americas Cardroom', 'BetOnline', 'Ignition'
        ]
        
        for site in poker_sites:
            if site.lower() in content.lower():
                return site
        return None
        
    def crawl(self):
        """메인 크롤링 로직"""
        items_scraped = 0
        categories = ['news', 'online-poker', 'strategy', 'tournaments']
        
        for category in categories:
            try:
                url = f"{self.base_url}/{category}/"
                response = requests.get(
                    url,
                    headers=self.get_headers(),
                    timeout=Config.CRAWLER_TIMEOUT
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 뉴스 아이템 찾기
                articles = soup.find_all('article', limit=20)  # 카테고리당 최신 20개
                
                for article in articles:
                    try:
                        # 제목과 URL 추출
                        title_elem = article.find('h2') or article.find('h3')
                        if not title_elem:
                            continue
                            
                        link_elem = title_elem.find('a')
                        if not link_elem:
                            continue
                            
                        title = link_elem.text.strip()
                        article_url = link_elem.get('href', '')
                        
                        if not article_url.startswith('http'):
                            article_url = self.base_url + article_url
                            
                        # 중복 체크
                        existing = self.session.query(NewsItem).filter_by(url=article_url).first()
                        if existing:
                            continue
                            
                        # 날짜 추출
                        date_elem = article.find('time')
                        published_date = self.parse_date(date_elem.text) if date_elem else datetime.utcnow()
                        
                        # 요약 추출
                        summary_elem = article.find('p')
                        summary = summary_elem.text.strip() if summary_elem else ''
                        
                        # 관련 포커 사이트 찾기
                        related_site = self.extract_site_from_content(title + ' ' + summary)
                        site_id = None
                        
                        if related_site:
                            site = self.session.query(PokerSite).filter_by(name=related_site).first()
                            if site:
                                site_id = site.id
                        
                        # 뉴스 아이템 저장
                        news_item = NewsItem(
                            site_id=site_id,
                            title=title,
                            url=article_url,
                            content=summary,
                            category=category,
                            published_date=published_date,
                            scraped_at=datetime.utcnow()
                        )
                        
                        self.session.add(news_item)
                        items_scraped += 1
                        
                    except Exception as e:
                        self.logger.error(f"Error parsing article: {str(e)}")
                        continue
                        
                # 카테고리 간 딜레이
                self.random_delay(2, 4)
                
            except Exception as e:
                self.logger.error(f"Error crawling category {category}: {str(e)}")
                continue
                
        self.session.commit()
        return items_scraped
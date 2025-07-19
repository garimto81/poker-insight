import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from crawlers.base_crawler import BaseCrawler
from database.models import PokerSite, TrafficData
from config.settings import Config
from fake_useragent import UserAgent

class PokerScoutCrawler(BaseCrawler):
    def __init__(self):
        super().__init__('pokerscout')
        self.base_url = 'https://www.pokerscout.com'
        self.ua = UserAgent()
        
    def get_headers(self):
        """동적 헤더 생성"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
    def parse_player_count(self, text):
        """플레이어 수 파싱 (예: "1,234" -> 1234)"""
        if not text:
            return None
        text = text.strip().replace(',', '')
        try:
            return int(text)
        except ValueError:
            return None
            
    def crawl(self):
        """메인 크롤링 로직"""
        items_scraped = 0
        
        try:
            # 메인 페이지에서 사이트 목록 가져오기
            response = requests.get(
                self.base_url, 
                headers=self.get_headers(),
                timeout=Config.CRAWLER_TIMEOUT
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 포커 사이트 테이블 찾기
            site_table = soup.find('table', {'class': 'ranktable'})
            if not site_table:
                self.logger.error("Could not find ranking table")
                return 0
                
            rows = site_table.find_all('tr')[1:]  # 헤더 제외
            
            for row in rows:
                try:
                    cols = row.find_all('td')
                    if len(cols) < 6:
                        continue
                        
                    # 데이터 추출
                    rank = self.parse_player_count(cols[0].text)
                    site_name = cols[1].text.strip()
                    
                    # URL 추출
                    site_link = cols[1].find('a')
                    site_url = site_link.get('href', '') if site_link else ''
                    if site_url and not site_url.startswith('http'):
                        site_url = self.base_url + site_url
                        
                    # 플레이어 수 데이터
                    cash_players = self.parse_player_count(cols[2].text)
                    tournament_players = self.parse_player_count(cols[3].text)
                    total_players = self.parse_player_count(cols[4].text)
                    seven_day_avg = None
                    
                    # 7일 평균 파싱
                    avg_text = cols[5].text.strip()
                    if avg_text and avg_text != '-':
                        try:
                            seven_day_avg = float(avg_text.replace(',', ''))
                        except ValueError:
                            pass
                    
                    # 데이터베이스에 저장
                    site = self.session.query(PokerSite).filter_by(name=site_name).first()
                    if not site:
                        site = PokerSite(
                            name=site_name,
                            url=site_url
                        )
                        self.session.add(site)
                        self.session.commit()
                    
                    # 트래픽 데이터 저장
                    traffic_data = TrafficData(
                        site_id=site.id,
                        cash_players=cash_players,
                        tournament_players=tournament_players,
                        total_players=total_players,
                        seven_day_average=seven_day_avg,
                        rank=rank,
                        timestamp=datetime.utcnow()
                    )
                    self.session.add(traffic_data)
                    
                    items_scraped += 1
                    
                    # 요청 간 딜레이
                    self.random_delay(1, 2)
                    
                except Exception as e:
                    self.logger.error(f"Error parsing row: {str(e)}")
                    continue
                    
            self.session.commit()
            
        except Exception as e:
            self.logger.error(f"Error during crawl: {str(e)}")
            self.session.rollback()
            raise
            
        return items_scraped
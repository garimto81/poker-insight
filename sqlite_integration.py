#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite 기반 데이터베이스 통합
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import json
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLite 기반 모델 정의
Base = declarative_base()

class PokerSite(Base):
    __tablename__ = 'poker_sites'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    url = Column(String(255))
    network = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    traffic_data = relationship('TrafficData', back_populates='site')
    news_items = relationship('NewsItem', back_populates='site')

class TrafficData(Base):
    __tablename__ = 'traffic_data'
    
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('poker_sites.id'), nullable=False)
    cash_players = Column(Integer)
    tournament_players = Column(Integer)
    total_players = Column(Integer)
    seven_day_average = Column(Float)
    peak_players = Column(Integer)
    rank = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    site = relationship('PokerSite', back_populates='traffic_data')

class NewsItem(Base):
    __tablename__ = 'news_items'
    
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('poker_sites.id'))
    title = Column(String(500), nullable=False)
    url = Column(String(500), unique=True)
    content = Column(Text)
    author = Column(String(100))
    published_date = Column(DateTime)
    category = Column(String(50))
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    site = relationship('PokerSite', back_populates='news_items')

class CrawlLog(Base):
    __tablename__ = 'crawl_logs'
    
    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    items_scraped = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)

class SQLiteDataIntegrator:
    def __init__(self, db_path='poker_insight.db'):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(bind=self.engine)
        self.session = SessionLocal()
        
    def load_json_data(self, file_path):
        """JSON 파일에서 데이터 로드"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return None
            
    def integrate_pokerscout_data(self):
        """PokerScout 데이터 통합"""
        logger.info("🎯 PokerScout 데이터 통합 시작...")
        
        data = self.load_json_data('pokerscout_perfect_data.json')
        if not data:
            logger.error("PokerScout 데이터 파일을 찾을 수 없습니다.")
            return False
            
        sites_added = 0
        traffic_records = 0
        
        try:
            for site_data in data['data']:
                # 포커 사이트 저장/업데이트
                site = self.session.query(PokerSite).filter_by(name=site_data['name']).first()
                if not site:
                    site = PokerSite(
                        name=site_data['name'],
                        network=site_data.get('network', 'Unknown')
                    )
                    self.session.add(site)
                    self.session.flush()
                    sites_added += 1
                    logger.info(f"  새 사이트 추가: {site.name}")
                    
                # 트래픽 데이터 저장
                traffic_data = TrafficData(
                    site_id=site.id,
                    cash_players=site_data.get('cash_players', 0),
                    tournament_players=site_data.get('tournament_players', 0),
                    total_players=site_data.get('players_online', 0),
                    seven_day_average=site_data.get('7_day_average', 0),
                    peak_players=site_data.get('peak_24h', 0),
                    rank=site_data.get('rank', 0),
                    timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                )
                self.session.add(traffic_data)
                traffic_records += 1
                
            # 크롤 로그 저장
            crawl_log = CrawlLog(
                source='pokerscout',
                status='success',
                items_scraped=len(data['data']),
                started_at=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
                completed_at=datetime.utcnow()
            )
            self.session.add(crawl_log)
            
            self.session.commit()
            
            logger.info(f"✅ PokerScout 데이터 통합 완료!")
            logger.info(f"  - 새 사이트: {sites_added}개")
            logger.info(f"  - 트래픽 레코드: {traffic_records}개")
            
            return True
            
        except Exception as e:
            logger.error(f"PokerScout 데이터 통합 오류: {str(e)}")
            self.session.rollback()
            return False
            
    def integrate_pokernews_data(self):
        """PokerNews 데이터 통합"""
        logger.info("📰 PokerNews 데이터 통합 시작...")
        
        data = self.load_json_data('pokernews_final_data.json')
        if not data:
            logger.error("PokerNews 데이터 파일을 찾을 수 없습니다.")
            return False
            
        news_added = 0
        
        try:
            for article_data in data['data']:
                # 중복 체크
                existing = self.session.query(NewsItem).filter_by(url=article_data['url']).first()
                if existing:
                    continue
                    
                # 관련 사이트 찾기
                site_id = None
                site_name = self.extract_site_from_title(article_data['title'])
                if site_name:
                    site = self.session.query(PokerSite).filter_by(name=site_name).first()
                    if site:
                        site_id = site.id
                        
                # 뉴스 아이템 저장
                news_item = NewsItem(
                    site_id=site_id,
                    title=article_data['title'],
                    url=article_data['url'],
                    content=article_data.get('summary', ''),
                    author=self.clean_author_name(article_data.get('author', '')),
                    published_date=self.parse_news_date(article_data.get('date')),
                    category=article_data.get('category', 'general'),
                    scraped_at=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                )
                self.session.add(news_item)
                news_added += 1
                
            # 크롤 로그 저장
            crawl_log = CrawlLog(
                source='pokernews',
                status='success',
                items_scraped=len(data['data']),
                started_at=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
                completed_at=datetime.utcnow()
            )
            self.session.add(crawl_log)
            
            self.session.commit()
            
            logger.info(f"✅ PokerNews 데이터 통합 완료!")
            logger.info(f"  - 새 뉴스: {news_added}개")
            
            return True
            
        except Exception as e:
            logger.error(f"PokerNews 데이터 통합 오류: {str(e)}")
            self.session.rollback()
            return False
            
    def extract_site_from_title(self, title):
        """제목에서 포커 사이트명 추출"""
        poker_sites = {
            'PokerStars': ['pokerstars', 'stars'],
            'GGNetwork': ['ggpoker', 'ggnetwork', 'gg poker'],
            '888poker': ['888poker', '888'],
            'partypoker': ['partypoker', 'party poker'],
            'WPT Global': ['wpt', 'world poker tour'],
            'WSOP': ['wsop', 'world series']
        }
        
        title_lower = title.lower()
        for site_name, keywords in poker_sites.items():
            if any(keyword in title_lower for keyword in keywords):
                return site_name
                
        return None
        
    def clean_author_name(self, author_text):
        """저자명 정리"""
        if not author_text:
            return ''
            
        lines = author_text.split('\n')
        if lines:
            return lines[0].strip()
            
        return author_text.strip()
        
    def parse_news_date(self, date_str):
        """뉴스 날짜 파싱"""
        try:
            if date_str:
                return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            pass
        return datetime.utcnow()
        
    def generate_analysis_report(self):
        """분석 리포트 생성"""
        logger.info("📊 분석 리포트 생성 중...")
        
        try:
            # 기본 통계
            total_sites = self.session.query(PokerSite).count()
            total_traffic_records = self.session.query(TrafficData).count()
            total_news = self.session.query(NewsItem).count()
            
            # TOP 10 포커 사이트 (트래픽 기준)
            top_sites = self.session.query(PokerSite, TrafficData)\
                .join(TrafficData)\
                .order_by(TrafficData.total_players.desc())\
                .limit(10).all()
                
            # 최신 뉴스 (상위 10개)
            latest_news = self.session.query(NewsItem)\
                .order_by(NewsItem.scraped_at.desc())\
                .limit(10).all()
                
            # 카테고리별 뉴스 통계
            from sqlalchemy import func
            news_by_category = self.session.query(
                NewsItem.category, func.count(NewsItem.id)
            ).group_by(NewsItem.category).all()
            
            report = {
                'generated_at': datetime.utcnow().isoformat(),
                'summary': {
                    'total_poker_sites': total_sites,
                    'total_traffic_records': total_traffic_records,
                    'total_news_articles': total_news
                },
                'top_poker_sites': [
                    {
                        'rank': i + 1,
                        'name': site.name,
                        'total_players': traffic.total_players,
                        'cash_players': traffic.cash_players,
                        'tournament_players': traffic.tournament_players,
                        '7_day_average': traffic.seven_day_average
                    }
                    for i, (site, traffic) in enumerate(top_sites)
                ],
                'latest_news': [
                    {
                        'title': news.title,
                        'category': news.category,
                        'author': news.author,
                        'published_date': news.published_date.isoformat() if news.published_date else None,
                        'url': news.url
                    }
                    for news in latest_news
                ],
                'news_by_category': {
                    category: count for category, count in news_by_category
                }
            }
            
            # 리포트 저장
            with open('analysis_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                
            return report
            
        except Exception as e:
            logger.error(f"리포트 생성 오류: {str(e)}")
            return None
            
    def display_summary(self):
        """요약 정보 출력"""
        try:
            total_sites = self.session.query(PokerSite).count()
            total_traffic = self.session.query(TrafficData).count()
            total_news = self.session.query(NewsItem).count()
            
            print(f"\n📊 데이터베이스 현황:")
            print(f"  포커 사이트: {total_sites}개")
            print(f"  트래픽 레코드: {total_traffic}개")
            print(f"  뉴스 기사: {total_news}개")
            
            # TOP 5 사이트
            top_sites = self.session.query(PokerSite, TrafficData)\
                .join(TrafficData)\
                .order_by(TrafficData.total_players.desc())\
                .limit(5).all()
                
            print(f"\n🏆 TOP 5 포커 사이트:")
            for i, (site, traffic) in enumerate(top_sites, 1):
                print(f"  {i}. {site.name}: {traffic.total_players:,}명")
                
        except Exception as e:
            logger.error(f"요약 출력 오류: {str(e)}")
            
    def close(self):
        """세션 종료"""
        self.session.close()

def main():
    """메인 실행 함수"""
    print("🔄 SQLite 데이터베이스 통합 시작")
    print("="*50)
    
    integrator = SQLiteDataIntegrator()
    
    try:
        # 1. PokerScout 데이터 통합
        pokerscout_success = integrator.integrate_pokerscout_data()
        
        # 2. PokerNews 데이터 통합
        pokernews_success = integrator.integrate_pokernews_data()
        
        if pokerscout_success and pokernews_success:
            # 3. 요약 정보 출력
            integrator.display_summary()
            
            # 4. 분석 리포트 생성
            report = integrator.generate_analysis_report()
            
            print(f"\n🎉 데이터베이스 통합 완료!")
            print(f"✅ PokerScout 데이터 통합 성공")
            print(f"✅ PokerNews 데이터 통합 성공")
            print(f"📊 분석 리포트: analysis_report.json")
            print(f"💾 데이터베이스: poker_insight.db")
            
            return True
        else:
            print(f"\n⚠️ 일부 데이터 통합 실패")
            return False
            
    except Exception as e:
        logger.error(f"통합 프로세스 오류: {str(e)}")
        return False
    finally:
        integrator.close()

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🚀 다음 단계: 포커 트래픽 분석 기능 개발 준비 완료!")
    else:
        print(f"\n💀 데이터베이스 통합 실패 - 문제 해결 필요")
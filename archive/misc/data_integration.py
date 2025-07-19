#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스 통합 - 수집된 데이터를 DB에 저장
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Windows에서 유니코드 출력 문제 해결
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import json
import logging
from datetime import datetime
from database.models import SessionLocal, PokerSite, TrafficData, NewsItem, CrawlLog
from config.settings import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIntegrator:
    def __init__(self):
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
                    self.session.flush()  # ID 생성을 위해
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
            
        # 첫 번째 줄만 가져오기 (이름 부분)
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
        
    def create_summary_report(self):
        """통합 후 요약 리포트 생성"""
        logger.info("📊 데이터베이스 통합 요약 리포트 생성...")
        
        try:
            # 포커 사이트 통계
            total_sites = self.session.query(PokerSite).count()
            
            # 트래픽 데이터 통계
            total_traffic_records = self.session.query(TrafficData).count()
            latest_traffic = self.session.query(TrafficData).order_by(TrafficData.timestamp.desc()).first()
            
            # 뉴스 데이터 통계
            total_news = self.session.query(NewsItem).count()
            latest_news = self.session.query(NewsItem).order_by(NewsItem.scraped_at.desc()).first()
            
            # 크롤 로그 통계
            total_crawls = self.session.query(CrawlLog).count()
            successful_crawls = self.session.query(CrawlLog).filter_by(status='success').count()
            
            report = {
                'integration_summary': {
                    'timestamp': datetime.utcnow().isoformat(),
                    'poker_sites': total_sites,
                    'traffic_records': total_traffic_records,
                    'news_articles': total_news,
                    'total_crawls': total_crawls,
                    'successful_crawls': successful_crawls,
                    'success_rate': f"{(successful_crawls/total_crawls*100):.1f}%" if total_crawls > 0 else "0%"
                },
                'latest_data': {
                    'latest_traffic_update': latest_traffic.timestamp.isoformat() if latest_traffic else None,
                    'latest_news_update': latest_news.scraped_at.isoformat() if latest_news else None
                }
            }
            
            # 리포트 저장
            with open('integration_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                
            logger.info("📄 통합 리포트:")
            logger.info(f"  포커 사이트: {total_sites}개")
            logger.info(f"  트래픽 레코드: {total_traffic_records}개")
            logger.info(f"  뉴스 기사: {total_news}개")
            logger.info(f"  크롤링 성공률: {report['integration_summary']['success_rate']}")
            
            return report
            
        except Exception as e:
            logger.error(f"리포트 생성 오류: {str(e)}")
            return None
            
    def close(self):
        """세션 종료"""
        self.session.close()
        
def main():
    """메인 실행 함수"""
    print("🔄 데이터베이스 통합 시작")
    print("="*50)
    
    # 데이터베이스 초기화 확인
    try:
        from database.models import init_db
        init_db()
        print("✅ 데이터베이스 초기화 완료")
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {str(e)}")
        print("SQLite 모드로 진행합니다...")
        
        # SQLite 모드로 전환
        import tempfile
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        from database.models import Base, engine
        Base.metadata.create_all(bind=engine)
    
    integrator = DataIntegrator()
    
    try:
        # 1. PokerScout 데이터 통합
        pokerscout_success = integrator.integrate_pokerscout_data()
        
        # 2. PokerNews 데이터 통합
        pokernews_success = integrator.integrate_pokernews_data()
        
        # 3. 요약 리포트 생성
        report = integrator.create_summary_report()
        
        if pokerscout_success and pokernews_success:
            print(f"\n🎉 데이터베이스 통합 완료!")
            print(f"✅ PokerScout 데이터 통합 성공")
            print(f"✅ PokerNews 데이터 통합 성공")
            print(f"📊 통합 리포트: integration_report.json")
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
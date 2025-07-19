#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
향상된 포커 트렌드 분석기 - 데이터베이스 연동 수정
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedPokerTrendAnalyzer:
    def __init__(self, db_path='poker_insight.db'):
        self.db_path = db_path
        
    def get_db_connection(self):
        """SQLite 데이터베이스 연결"""
        return sqlite3.connect(self.db_path)
        
    def analyze_current_market_data(self):
        """실제 데이터베이스에서 현재 시장 데이터 분석"""
        logger.info("🏆 실제 데이터베이스 시장 분석...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # 현재 트래픽 데이터
            query = """
            SELECT 
                ps.name,
                td.total_players,
                td.cash_players,
                td.tournament_players,
                td.seven_day_average,
                td.rank
            FROM poker_sites ps
            JOIN traffic_data td ON ps.id = td.site_id
            ORDER BY td.total_players DESC
            LIMIT 20
            """
            
            cursor.execute(query)
            sites_data = cursor.fetchall()
            
            if not sites_data:
                logger.warning("데이터베이스에서 데이터를 찾을 수 없습니다.")
                return {}
                
            total_players = sum(row[1] for row in sites_data)
            total_cash = sum(row[2] for row in sites_data)
            total_tournaments = sum(row[3] for row in sites_data)
            
            # 활성 사이트 수
            active_sites = len([row for row in sites_data if row[1] > 0])
            
            # 상위 3개 사이트 점유율
            top3_share = sum(row[1] for row in sites_data[:3]) / total_players * 100 if total_players > 0 else 0
            
            market_analysis = {
                'total_players_online': total_players,
                'total_cash_players': total_cash,
                'total_tournament_players': total_tournaments,
                'active_sites_count': active_sites,
                'total_sites_tracked': len(sites_data),
                'top3_market_share': round(top3_share, 1),
                'cash_tournament_ratio': round((total_cash / total_tournaments) * 100, 1) if total_tournaments > 0 else 0,
                'market_leader': sites_data[0][0] if sites_data else 'N/A',
                'market_leader_share': round((sites_data[0][1] / total_players) * 100, 1) if sites_data and total_players > 0 else 0,
                'top_sites_data': [
                    {
                        'name': row[0],
                        'players': row[1],
                        'cash_players': row[2],
                        'tournament_players': row[3],
                        '7_day_avg': row[4],
                        'rank': row[5]
                    }
                    for row in sites_data[:10]
                ]
            }
            
            conn.close()
            return market_analysis
            
        except Exception as e:
            logger.error(f"시장 분석 오류: {str(e)}")
            return {}
            
    def analyze_news_data(self):
        """실제 뉴스 데이터 분석"""
        logger.info("📰 실제 뉴스 데이터 분석...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # 뉴스 데이터 조회
            query = """
            SELECT title, content, category, author, published_date
            FROM news_items
            ORDER BY scraped_at DESC
            LIMIT 100
            """
            
            cursor.execute(query)
            news_data = cursor.fetchall()
            
            if not news_data:
                logger.warning("뉴스 데이터를 찾을 수 없습니다.")
                return {}
                
            # 키워드 분석
            keywords_analysis = self.analyze_keywords_enhanced(news_data)
            
            # 카테고리 분석
            categories_analysis = self.analyze_categories_enhanced(news_data)
            
            # 저자 분석
            authors_analysis = self.analyze_authors(news_data)
            
            # 트렌딩 토픽 분석
            trending_topics = self.identify_trending_topics(news_data)
            
            conn.close()
            
            return {
                'keywords': keywords_analysis,
                'categories': categories_analysis,
                'authors': authors_analysis,
                'trending_topics': trending_topics,
                'total_articles': len(news_data)
            }
            
        except Exception as e:
            logger.error(f"뉴스 분석 오류: {str(e)}")
            return {}
            
    def analyze_keywords_enhanced(self, news_data):
        """향상된 키워드 분석"""
        # 확장된 포커 키워드 리스트
        poker_keywords = [
            # 플랫폼
            'PokerStars', 'GGPoker', 'GGNetwork', '888poker', 'partypoker', 
            'WPT Global', 'WPT', 'Winamax', 'Unibet', 'iPoker',
            
            # 이벤트
            'WSOP', 'World Series', 'EPT', 'European Poker Tour', 
            'Main Event', 'bracelet', 'final table', 'heads-up',
            
            # 게임 타입
            'tournament', 'cash game', 'high stakes', 'sit and go',
            'spin and go', 'bounty', 'progressive knockout', 'PKO',
            
            # 일반
            'poker', 'player', 'champion', 'winner', 'prize pool',
            'buy-in', 'blinds', 'ante', 'all-in', 'bluff'
        ]
        
        keyword_counts = Counter()
        keyword_contexts = defaultdict(list)
        
        for row in news_data:
            title = row[0] or ''
            content = row[1] or ''
            text = (title + ' ' + content).lower()
            
            for keyword in poker_keywords:
                keyword_lower = keyword.lower()
                count = text.count(keyword_lower)
                if count > 0:
                    keyword_counts[keyword] += count
                    # 키워드 주변 컨텍스트 저장
                    if keyword_lower in title.lower():
                        keyword_contexts[keyword].append(title[:100])
                        
        # 상위 15개 키워드
        top_keywords = dict(keyword_counts.most_common(15))
        
        # 키워드별 컨텍스트 정보
        keyword_details = {}
        for keyword, count in top_keywords.items():
            keyword_details[keyword] = {
                'count': count,
                'contexts': keyword_contexts[keyword][:3]  # 상위 3개 컨텍스트
            }
            
        return keyword_details
        
    def analyze_categories_enhanced(self, news_data):
        """향상된 카테고리 분석"""
        category_stats = defaultdict(int)
        category_trends = defaultdict(list)
        
        for row in news_data:
            category = row[2] or 'general'
            published_date = row[4] or datetime.now().strftime('%Y-%m-%d')
            
            category_stats[category] += 1
            category_trends[category].append(published_date)
            
        # 카테고리별 최근 활동도 계산
        category_analysis = {}
        for category, count in category_stats.items():
            recent_dates = category_trends[category]
            # 최근 7일 내 기사 비율
            recent_articles = len([d for d in recent_dates if d >= (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')])
            recent_ratio = (recent_articles / count) * 100 if count > 0 else 0
            
            category_analysis[category] = {
                'total_articles': count,
                'recent_activity': round(recent_ratio, 1),
                'trend': 'hot' if recent_ratio > 50 else 'normal' if recent_ratio > 20 else 'cold'
            }
            
        return category_analysis
        
    def analyze_authors(self, news_data):
        """저자별 분석"""
        author_stats = Counter()
        
        for row in news_data:
            author = row[3] or 'Unknown'
            # 저자명 정리 (첫 번째 줄만)
            clean_author = author.split('\n')[0].strip() if author else 'Unknown'
            if clean_author and len(clean_author) < 50:  # 너무 긴 텍스트 제외
                author_stats[clean_author] += 1
                
        # 상위 10명 저자
        top_authors = dict(author_stats.most_common(10))
        
        return top_authors
        
    def identify_trending_topics(self, news_data):
        """트렌딩 토픽 식별"""
        # 제목에서 자주 등장하는 단어 조합 찾기
        title_words = []
        
        for row in news_data:
            title = row[0] or ''
            # 제목을 단어로 분리하고 정리
            words = [word.strip('.,!?()[]{}').lower() for word in title.split() if len(word) > 3]
            # 의미없는 단어 제외
            stop_words = {'the', 'and', 'for', 'with', 'from', 'this', 'that', 'they', 'have', 'been', 'will', 'were'}
            words = [word for word in words if word not in stop_words]
            title_words.extend(words)
            
        # 단어 빈도 계산
        word_counts = Counter(title_words)
        trending_words = dict(word_counts.most_common(20))
        
        # 연관 키워드 그룹 생성
        trending_groups = self.group_related_keywords(trending_words)
        
        return {
            'individual_words': trending_words,
            'topic_groups': trending_groups
        }
        
    def group_related_keywords(self, word_counts):
        """연관 키워드 그룹화"""
        # 포커 관련 주제별 그룹
        topic_groups = {
            'tournaments': ['tournament', 'wsop', 'bracelet', 'event', 'championship', 'series'],
            'players': ['player', 'winner', 'champion', 'professional', 'pro'],
            'platforms': ['pokerstars', 'ggpoker', 'online', 'platform', 'site'],
            'money': ['prize', 'million', 'dollar', 'money', 'pot', 'stakes'],
            'events': ['final', 'table', 'heads', 'victory', 'defeated', 'wins']
        }
        
        grouped_results = {}
        
        for group_name, keywords in topic_groups.items():
            group_score = 0
            group_words = []
            
            for word, count in word_counts.items():
                if any(keyword in word.lower() for keyword in keywords):
                    group_score += count
                    group_words.append(f"{word} ({count})")
                    
            if group_score > 0:
                grouped_results[group_name] = {
                    'total_mentions': group_score,
                    'keywords': group_words[:5]  # 상위 5개만
                }
                
        return grouped_results
        
    def generate_broadcast_summary(self, market_data, news_data):
        """방송용 종합 요약 생성"""
        logger.info("📺 방송용 종합 요약 생성...")
        
        summary = {
            'headline_stats': [],
            'market_insights': [],
            'news_highlights': [],
            'trending_now': [],
            'quick_facts': []
        }
        
        # 헤드라인 통계
        if market_data:
            total_players = market_data.get('total_players_online', 0)
            market_leader = market_data.get('market_leader', 'N/A')
            leader_share = market_data.get('market_leader_share', 0)
            
            summary['headline_stats'] = [
                f"전 세계 온라인 포커 플레이어: {total_players:,}명",
                f"시장 리더: {market_leader} ({leader_share}% 점유)",
                f"활성 포커 사이트: {market_data.get('active_sites_count', 0)}개"
            ]
            
        # 시장 인사이트
        if market_data and market_data.get('top_sites_data'):
            top_sites = market_data['top_sites_data'][:5]
            
            summary['market_insights'] = [
                f"TOP 5 사이트 현황:",
                *[f"  {i+1}. {site['name']}: {site['players']:,}명" for i, site in enumerate(top_sites)]
            ]
            
        # 뉴스 하이라이트
        if news_data and news_data.get('keywords'):
            top_keywords = list(news_data['keywords'].items())[:5]
            summary['news_highlights'] = [
                f"최근 포커 뉴스 주요 키워드:",
                *[f"  • {keyword}: {data['count'] if isinstance(data, dict) else data}회 언급" 
                  for keyword, data in top_keywords]
            ]
            
        # 현재 트렌딩
        if news_data and news_data.get('trending_topics'):
            trending = news_data['trending_topics'].get('topic_groups', {})
            if trending:
                summary['trending_now'] = [
                    "현재 트렌딩 토픽:",
                    *[f"  📈 {topic}: {data['total_mentions']}회 언급" 
                      for topic, data in list(trending.items())[:3]]
                ]
                
        # 빠른 팩트
        if market_data:
            cash_ratio = market_data.get('cash_tournament_ratio', 0)
            top3_share = market_data.get('top3_market_share', 0)
            
            summary['quick_facts'] = [
                f"캐시게임 vs 토너먼트 비율: {cash_ratio:.1f}% vs {100-cash_ratio:.1f}%",
                f"상위 3개 사이트 시장 점유율: {top3_share:.1f}%",
                f"분석된 뉴스 기사: {news_data.get('total_articles', 0)}개" if news_data else "뉴스 데이터 없음"
            ]
            
        return summary
        
    def save_comprehensive_analysis(self, results):
        """종합 분석 결과 저장"""
        output = {
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_version': '2.0_enhanced',
            'data_source': 'poker_insight_database',
            'results': results
        }
        
        # 상세 결과 저장
        with open('comprehensive_trend_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        # 방송용 요약 저장
        if 'broadcast_summary' in results:
            with open('broadcast_ready_summary.txt', 'w', encoding='utf-8') as f:
                summary = results['broadcast_summary']
                
                f.write("=== 포커 시장 브리핑 ===\n\n")
                
                for section, items in summary.items():
                    if items:
                        f.write(f"{section.replace('_', ' ').title()}:\n")
                        for item in items:
                            f.write(f"{item}\n")
                        f.write("\n")
                        
        logger.info("💾 종합 분석 결과 저장 완료")

def main():
    """메인 실행 함수"""
    print("📊 향상된 포커 트렌드 분석 시작")
    print("="*60)
    
    analyzer = EnhancedPokerTrendAnalyzer()
    
    try:
        # 1. 현재 시장 데이터 분석
        market_data = analyzer.analyze_current_market_data()
        
        # 2. 뉴스 데이터 분석
        news_data = analyzer.analyze_news_data()
        
        # 3. 방송용 요약 생성
        broadcast_summary = analyzer.generate_broadcast_summary(market_data, news_data)
        
        # 4. 결과 출력
        print("\n🏆 시장 현황:")
        if market_data:
            print(f"  총 플레이어: {market_data.get('total_players_online', 0):,}명")
            print(f"  시장 리더: {market_data.get('market_leader', 'N/A')}")
            print(f"  활성 사이트: {market_data.get('active_sites_count', 0)}개")
            
        print("\n📰 뉴스 분석:")
        if news_data:
            print(f"  분석된 기사: {news_data.get('total_articles', 0)}개")
            if news_data.get('keywords'):
                top_keyword = list(news_data['keywords'].items())[0]
                print(f"  최다 언급 키워드: {top_keyword[0]}")
                
        print("\n📺 방송용 요약:")
        for section, items in broadcast_summary.items():
            if items:
                print(f"  {section}:")
                for item in items[:2]:  # 각 섹션별 상위 2개만 출력
                    print(f"    {item}")
                    
        # 5. 결과 저장
        comprehensive_results = {
            'market_analysis': market_data,
            'news_analysis': news_data,
            'broadcast_summary': broadcast_summary
        }
        
        analyzer.save_comprehensive_analysis(comprehensive_results)
        
        print(f"\n✅ 향상된 트렌드 분석 완료!")
        print(f"📊 상세 결과: comprehensive_trend_analysis.json")
        print(f"📺 방송용 요약: broadcast_ready_summary.txt")
        
        return True
        
    except Exception as e:
        logger.error(f"분석 오류: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🚀 트렌드 분석 완료! 다음: 일일 리포트 자동 생성 또는 대시보드 구현")
    else:
        print(f"\n💀 분석 실패 - 문제 해결 필요")
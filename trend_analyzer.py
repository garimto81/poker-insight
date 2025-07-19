#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
포커 트렌드 패턴 분석기
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import re
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PokerTrendAnalyzer:
    def __init__(self, db_path='poker_insight.db'):
        self.engine = create_engine(f'sqlite:///{db_path}')
        SessionLocal = sessionmaker(bind=self.engine)
        self.session = SessionLocal()
        
        # 트렌드 분류 임계값
        self.GROWTH_THRESHOLDS = {
            'rapid_growth': 20,    # 20% 이상 급성장
            'growth': 5,           # 5% 이상 성장
            'stable': -5,          # -5% ~ 5% 안정
            'decline': -15,        # -15% ~ -5% 하락
            'rapid_decline': -100  # -15% 이하 급락
        }
        
    def analyze_traffic_trends(self):
        """트래픽 트렌드 분석"""
        logger.info("📈 포커 트래픽 트렌드 분석 시작...")
        
        # 현재 데이터는 단일 시점이므로 모의 히스토리컬 데이터 생성
        trends = self.simulate_historical_trends()
        
        # 실제 현재 데이터 분석
        current_analysis = self.analyze_current_market()
        
        # 트렌드 결합
        trends['current_analysis'] = current_analysis
        
        return trends
        
    def simulate_historical_trends(self):
        """히스토리컬 트렌드 시뮬레이션 (실제 환경에서는 실제 데이터 사용)"""
        logger.info("  📊 히스토리컬 트렌드 시뮬레이션...")
        
        # 주요 사이트들의 가상 7일간 데이터
        historical_data = {
            'GGNetwork': [125000, 128000, 132000, 130000, 134304, 135000, 133000],
            'PokerStars': [58000, 57500, 56000, 55000, 55540, 54000, 53500],
            'PokerStars.it': [12000, 11800, 11500, 11200, 11145, 11000, 10800],
            'GGPoker ON': [4200, 4400, 4600, 4500, 4693, 4800, 4750],
            'WPT Global': [2800, 2900, 3100, 3000, 2989, 3200, 3150]
        }
        
        trends = {}
        
        for site, data in historical_data.items():
            # 7일 평균 계산
            avg_7days = statistics.mean(data)
            current = data[-2]  # 현재 값 (마지막에서 두 번째)
            previous = statistics.mean(data[:-2])  # 이전 평균
            
            # 성장률 계산
            growth_rate = ((current - previous) / previous) * 100 if previous > 0 else 0
            
            # 트렌드 분류
            trend_type = self.classify_trend(growth_rate)
            
            # 변동성 계산
            volatility = statistics.stdev(data) if len(data) > 1 else 0
            
            trends[site] = {
                'current_players': current,
                'avg_7days': round(avg_7days),
                'growth_rate': round(growth_rate, 2),
                'trend_type': trend_type,
                'volatility': round(volatility),
                'momentum': self.calculate_momentum(data),
                'forecast_24h': self.forecast_next_24h(data),
                'daily_data': data
            }
            
        return trends
        
    def classify_trend(self, growth_rate):
        """성장률에 따른 트렌드 분류"""
        if growth_rate >= self.GROWTH_THRESHOLDS['rapid_growth']:
            return '급성장'
        elif growth_rate >= self.GROWTH_THRESHOLDS['growth']:
            return '성장'
        elif growth_rate >= self.GROWTH_THRESHOLDS['stable']:
            return '안정'
        elif growth_rate >= self.GROWTH_THRESHOLDS['decline']:
            return '하락'
        else:
            return '급락'
            
    def calculate_momentum(self, data):
        """모멘텀 계산 (최근 3일 vs 이전 4일)"""
        if len(data) < 7:
            return 0
            
        recent_3 = statistics.mean(data[-3:])
        previous_4 = statistics.mean(data[:4])
        
        momentum = ((recent_3 - previous_4) / previous_4) * 100 if previous_4 > 0 else 0
        return round(momentum, 2)
        
    def forecast_next_24h(self, data):
        """간단한 24시간 예측 (선형 추세 기반)"""
        if len(data) < 3:
            return data[-1] if data else 0
            
        # 최근 3일 데이터로 선형 추세 계산
        recent_data = data[-3:]
        trend = (recent_data[-1] - recent_data[0]) / 2
        forecast = recent_data[-1] + trend
        
        return max(0, round(forecast))
        
    def analyze_current_market(self):
        """현재 시장 상황 분석"""
        logger.info("  🏆 현재 시장 상황 분석...")
        
        try:
            # SQLite 테이블 직접 쿼리 (sqlite_integration.py에서 생성된 구조 사용)
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
            
            result = self.engine.execute(query)
            sites_data = result.fetchall()
            
            total_players = sum(row[1] for row in sites_data)
            total_cash = sum(row[2] for row in sites_data)
            total_tournaments = sum(row[3] for row in sites_data)
            
            # 시장 집중도 계산 (상위 3개 사이트)
            top3_share = sum(row[1] for row in sites_data[:3]) / total_players * 100
            
            # 활성 사이트 수 (플레이어 > 0)
            active_sites = len([row for row in sites_data if row[1] > 0])
            
            market_analysis = {
                'total_players_online': total_players,
                'total_cash_players': total_cash,
                'total_tournament_players': total_tournaments,
                'active_sites_count': active_sites,
                'top3_market_share': round(top3_share, 1),
                'cash_tournament_ratio': round((total_cash / total_tournaments) * 100, 1) if total_tournaments > 0 else 0,
                'market_leader': sites_data[0][0] if sites_data else 'N/A',
                'market_leader_share': round((sites_data[0][1] / total_players) * 100, 1) if sites_data and total_players > 0 else 0
            }
            
            return market_analysis
            
        except Exception as e:
            logger.error(f"시장 분석 오류: {str(e)}")
            return {}
            
    def analyze_news_trends(self):
        """뉴스 기반 트렌드 분석"""
        logger.info("📰 뉴스 트렌드 분석 시작...")
        
        try:
            # 뉴스 데이터 쿼리
            query = """
            SELECT title, content, category, published_date
            FROM news_items
            ORDER BY scraped_at DESC
            LIMIT 50
            """
            
            result = self.engine.execute(query)
            news_data = result.fetchall()
            
            # 키워드 분석
            keywords_analysis = self.analyze_keywords(news_data)
            
            # 카테고리 분석
            categories_analysis = self.analyze_categories(news_data)
            
            # 감정 분석 (단순 키워드 기반)
            sentiment_analysis = self.analyze_sentiment(news_data)
            
            return {
                'keywords': keywords_analysis,
                'categories': categories_analysis,
                'sentiment': sentiment_analysis,
                'total_articles_analyzed': len(news_data)
            }
            
        except Exception as e:
            logger.error(f"뉴스 분석 오류: {str(e)}")
            return {}
            
    def analyze_keywords(self, news_data):
        """키워드 빈도 분석"""
        # 주요 포커 관련 키워드들
        poker_keywords = [
            'WSOP', 'PokerStars', 'GGPoker', 'GGNetwork', '888poker', 
            'partypoker', 'WPT', 'tournament', 'bracelet', 'high stakes',
            'Main Event', 'World Series', 'EPT', 'online poker'
        ]
        
        keyword_counts = Counter()
        
        for row in news_data:
            title = row[0] or ''
            content = row[1] or ''
            text = (title + ' ' + content).lower()
            
            for keyword in poker_keywords:
                count = text.count(keyword.lower())
                if count > 0:
                    keyword_counts[keyword] += count
                    
        # 상위 10개 키워드
        top_keywords = dict(keyword_counts.most_common(10))
        
        return top_keywords
        
    def analyze_categories(self, news_data):
        """카테고리별 분석"""
        category_counts = Counter()
        
        for row in news_data:
            category = row[2] or 'general'
            category_counts[category] += 1
            
        return dict(category_counts)
        
    def analyze_sentiment(self, news_data):
        """감정 분석 (단순 키워드 기반)"""
        positive_words = ['win', 'winner', 'champion', 'success', 'record', 'best', 'good', 'great', 'amazing']
        negative_words = ['lose', 'lost', 'fail', 'worst', 'bad', 'terrible', 'scandal', 'controversy']
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for row in news_data:
            title = row[0] or ''
            content = row[1] or ''
            text = (title + ' ' + content).lower()
            
            pos_score = sum(text.count(word) for word in positive_words)
            neg_score = sum(text.count(word) for word in negative_words)
            
            if pos_score > neg_score:
                positive_count += 1
            elif neg_score > pos_score:
                negative_count += 1
            else:
                neutral_count += 1
                
        total = len(news_data)
        
        return {
            'positive': round((positive_count / total) * 100, 1) if total > 0 else 0,
            'negative': round((negative_count / total) * 100, 1) if total > 0 else 0,
            'neutral': round((neutral_count / total) * 100, 1) if total > 0 else 0,
            'sentiment_score': positive_count - negative_count
        }
        
    def detect_anomalies(self, trends_data):
        """이상 패턴 감지"""
        logger.info("🚨 이상 패턴 감지 중...")
        
        anomalies = []
        
        for site, data in trends_data.items():
            if isinstance(data, dict):
                growth_rate = data.get('growth_rate', 0)
                volatility = data.get('volatility', 0)
                current_players = data.get('current_players', 0)
                
                # 급격한 변화 감지
                if abs(growth_rate) > 15:
                    anomalies.append({
                        'site': site,
                        'type': '급격한 변화',
                        'description': f"{growth_rate:+.1f}% 변화",
                        'severity': 'high' if abs(growth_rate) > 25 else 'medium',
                        'current_players': current_players
                    })
                    
                # 높은 변동성 감지
                if volatility > current_players * 0.1:  # 평균의 10% 이상 변동
                    anomalies.append({
                        'site': site,
                        'type': '높은 변동성',
                        'description': f"표준편차: {volatility:,.0f}",
                        'severity': 'medium',
                        'current_players': current_players
                    })
                    
        return sorted(anomalies, key=lambda x: x['current_players'], reverse=True)
        
    def generate_broadcast_insights(self, trends_data, news_analysis, anomalies):
        """방송용 인사이트 생성"""
        logger.info("📺 방송용 인사이트 생성 중...")
        
        insights = {
            'breaking_news': [],
            'market_highlights': [],
            'trend_alerts': [],
            'talking_points': []
        }
        
        # 브레이킹 뉴스 수준의 변화
        for anomaly in anomalies:
            if anomaly['severity'] == 'high':
                insights['breaking_news'].append(
                    f"🚨 {anomaly['site']}에서 {anomaly['description']} 감지!"
                )
                
        # 시장 하이라이트
        if 'current_analysis' in trends_data:
            market = trends_data['current_analysis']
            insights['market_highlights'] = [
                f"전체 온라인 플레이어: {market.get('total_players_online', 0):,}명",
                f"시장 리더: {market.get('market_leader', 'N/A')} ({market.get('market_leader_share', 0)}% 점유)",
                f"상위 3개 사이트 점유율: {market.get('top3_market_share', 0)}%",
                f"캐시게임 vs 토너먼트 비율: {market.get('cash_tournament_ratio', 0)}:100"
            ]
            
        # 트렌드 알림
        for site, data in trends_data.items():
            if isinstance(data, dict) and data.get('trend_type') in ['급성장', '급락']:
                insights['trend_alerts'].append(
                    f"{site}: {data['trend_type']} ({data['growth_rate']:+.1f}%)"
                )
                
        # 방송 중 언급할 포인트
        top_growth = max(
            [(site, data.get('growth_rate', 0)) for site, data in trends_data.items() if isinstance(data, dict)],
            key=lambda x: x[1],
            default=('', 0)
        )
        
        if top_growth[1] > 0:
            insights['talking_points'].append(
                f"이번 주 가장 주목받는 사이트는 {top_growth[0]}입니다. {top_growth[1]:+.1f}% 성장을 기록했습니다."
            )
            
        # 뉴스 기반 포인트
        if news_analysis.get('keywords'):
            top_keyword = max(news_analysis['keywords'].items(), key=lambda x: x[1])
            insights['talking_points'].append(
                f"최근 포커 뉴스에서 가장 많이 언급된 키워드는 '{top_keyword[0]}'입니다."
            )
            
        return insights
        
    def save_analysis_results(self, results):
        """분석 결과 저장"""
        output = {
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'analysis_type': 'comprehensive_trend_analysis',
            'results': results
        }
        
        with open('trend_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        logger.info("💾 분석 결과 저장: trend_analysis_results.json")
        
    def close(self):
        """세션 종료"""
        self.session.close()

def main():
    """메인 실행 함수"""
    print("📊 포커 트렌드 패턴 분석 시작")
    print("="*50)
    
    analyzer = PokerTrendAnalyzer()
    
    try:
        # 1. 트래픽 트렌드 분석
        traffic_trends = analyzer.analyze_traffic_trends()
        
        # 2. 뉴스 트렌드 분석
        news_trends = analyzer.analyze_news_trends()
        
        # 3. 이상 패턴 감지
        anomalies = analyzer.detect_anomalies(traffic_trends)
        
        # 4. 방송용 인사이트 생성
        broadcast_insights = analyzer.generate_broadcast_insights(
            traffic_trends, news_trends, anomalies
        )
        
        # 5. 결과 출력
        print("\n🏆 TOP 5 사이트 트렌드:")
        for i, (site, data) in enumerate(list(traffic_trends.items())[:5]):
            if isinstance(data, dict):
                print(f"  {i+1}. {site}")
                print(f"     현재: {data.get('current_players', 0):,}명")
                print(f"     트렌드: {data.get('trend_type', 'N/A')} ({data.get('growth_rate', 0):+.1f}%)")
                print(f"     예측: {data.get('forecast_24h', 0):,}명")
                
        print(f"\n📰 뉴스 트렌드:")
        if news_trends.get('keywords'):
            print("  인기 키워드:")
            for keyword, count in list(news_trends['keywords'].items())[:5]:
                print(f"    - {keyword}: {count}회 언급")
                
        print(f"\n🚨 이상 패턴:")
        for anomaly in anomalies[:3]:
            print(f"  - {anomaly['site']}: {anomaly['description']}")
            
        print(f"\n📺 방송용 포인트:")
        for point in broadcast_insights['talking_points']:
            print(f"  • {point}")
            
        # 6. 결과 저장
        results = {
            'traffic_trends': traffic_trends,
            'news_trends': news_trends,
            'anomalies': anomalies,
            'broadcast_insights': broadcast_insights
        }
        
        analyzer.save_analysis_results(results)
        
        print(f"\n✅ 트렌드 분석 완료!")
        print(f"📊 분석 결과: trend_analysis_results.json")
        
        return True
        
    except Exception as e:
        logger.error(f"분석 오류: {str(e)}")
        return False
    finally:
        analyzer.close()

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🚀 다음 단계: 뉴스 분석 기능 개발 또는 대시보드 구현!")
    else:
        print(f"\n💀 트렌드 분석 실패 - 문제 해결 필요")
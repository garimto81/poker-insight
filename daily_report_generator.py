#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
일일 포커 시장 리포트 자동 생성기
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DailyReportGenerator:
    def __init__(self, db_path='poker_insight.db'):
        self.db_path = db_path
        
    def get_db_connection(self):
        """SQLite 데이터베이스 연결"""
        return sqlite3.connect(self.db_path)
        
    def generate_daily_report(self):
        """일일 종합 리포트 생성"""
        logger.info("📋 일일 포커 시장 리포트 생성 시작...")
        
        report_data = {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'report_time': datetime.now().strftime('%H:%M:%S'),
            'market_summary': self.get_market_summary(),
            'top_performers': self.get_top_performers(),
            'market_trends': self.get_market_trends(),
            'news_highlights': self.get_news_highlights(),
            'broadcast_segments': self.generate_broadcast_segments(),
            'key_metrics': self.calculate_key_metrics(),
            'alerts_and_changes': self.detect_significant_changes()
        }
        
        return report_data
        
    def get_market_summary(self):
        """시장 전체 요약"""
        logger.info("  📊 시장 요약 데이터 수집...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # 전체 시장 데이터
            query = """
            SELECT 
                COUNT(*) as total_sites,
                SUM(td.total_players) as total_players,
                SUM(td.cash_players) as total_cash,
                SUM(td.tournament_players) as total_tournaments,
                AVG(td.seven_day_average) as avg_7day
            FROM poker_sites ps
            JOIN traffic_data td ON ps.id = td.site_id
            WHERE td.total_players > 0
            """
            
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result:
                total_sites, total_players, total_cash, total_tournaments, avg_7day = result
                
                summary = {
                    'total_active_sites': total_sites,
                    'total_players_online': total_players or 0,
                    'total_cash_players': total_cash or 0,
                    'total_tournament_players': total_tournaments or 0,
                    'average_7day_traffic': round(avg_7day or 0),
                    'cash_percentage': round((total_cash / total_players) * 100, 1) if total_players > 0 else 0,
                    'tournament_percentage': round((total_tournaments / total_players) * 100, 1) if total_players > 0 else 0
                }
            else:
                summary = {
                    'total_active_sites': 0,
                    'total_players_online': 0,
                    'total_cash_players': 0,
                    'total_tournament_players': 0,
                    'average_7day_traffic': 0,
                    'cash_percentage': 0,
                    'tournament_percentage': 0
                }
                
            conn.close()
            return summary
            
        except Exception as e:
            logger.error(f"시장 요약 데이터 수집 오류: {str(e)}")
            return {}
            
    def get_top_performers(self):
        """상위 성과 사이트들"""
        logger.info("  🏆 상위 성과 사이트 분석...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
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
            LIMIT 10
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            top_sites = []
            for row in results:
                name, total, cash, tournaments, avg_7day, rank = row
                
                # 성장률 계산 (7일 평균 대비 현재)
                growth_rate = 0
                if avg_7day and avg_7day > 0:
                    growth_rate = ((total - avg_7day) / avg_7day) * 100
                
                top_sites.append({
                    'name': name,
                    'rank': rank,
                    'total_players': total,
                    'cash_players': cash,
                    'tournament_players': tournaments,
                    'seven_day_average': avg_7day or 0,
                    'growth_rate': round(growth_rate, 1),
                    'market_share': 0  # 나중에 계산
                })
                
            # 시장 점유율 계산
            total_market = sum(site['total_players'] for site in top_sites)
            for site in top_sites:
                if total_market > 0:
                    site['market_share'] = round((site['total_players'] / total_market) * 100, 1)
                    
            conn.close()
            return top_sites
            
        except Exception as e:
            logger.error(f"상위 성과 사이트 분석 오류: {str(e)}")
            return []
            
    def get_market_trends(self):
        """시장 트렌드 분석"""
        logger.info("  📈 시장 트렌드 분석...")
        
        # 실제 환경에서는 히스토리컬 데이터를 사용
        # 현재는 시뮬레이션 데이터로 트렌드 생성
        trends = {
            'overall_trend': 'stable',  # 'growth', 'decline', 'stable'
            'growth_sites_count': 0,
            'decline_sites_count': 0,
            'stable_sites_count': 0,
            'biggest_gainer': {'name': '', 'growth': 0},
            'biggest_loser': {'name': '', 'decline': 0},
            'trend_analysis': []
        }
        
        try:
            top_sites = self.get_top_performers()
            
            growth_count = 0
            decline_count = 0
            stable_count = 0
            
            biggest_gainer = {'name': '', 'growth': 0}
            biggest_loser = {'name': '', 'decline': 0}
            
            for site in top_sites:
                growth_rate = site.get('growth_rate', 0)
                
                if growth_rate > 5:
                    growth_count += 1
                    if growth_rate > biggest_gainer['growth']:
                        biggest_gainer = {'name': site['name'], 'growth': growth_rate}
                elif growth_rate < -5:
                    decline_count += 1
                    if growth_rate < biggest_loser['decline']:
                        biggest_loser = {'name': site['name'], 'decline': growth_rate}
                else:
                    stable_count += 1
                    
            # 전체 트렌드 결정
            if growth_count > decline_count:
                overall_trend = 'growth'
            elif decline_count > growth_count:
                overall_trend = 'decline'
            else:
                overall_trend = 'stable'
                
            trends.update({
                'overall_trend': overall_trend,
                'growth_sites_count': growth_count,
                'decline_sites_count': decline_count,
                'stable_sites_count': stable_count,
                'biggest_gainer': biggest_gainer,
                'biggest_loser': biggest_loser
            })
            
            return trends
            
        except Exception as e:
            logger.error(f"시장 트렌드 분석 오류: {str(e)}")
            return trends
            
    def get_news_highlights(self):
        """뉴스 하이라이트"""
        logger.info("  📰 뉴스 하이라이트 수집...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # 최신 뉴스 가져오기
            query = """
            SELECT title, content, category, author, published_date, url
            FROM news_items
            ORDER BY scraped_at DESC
            LIMIT 20
            """
            
            cursor.execute(query)
            news_data = cursor.fetchall()
            
            # 카테고리별 분류
            category_stats = Counter()
            top_keywords = Counter()
            featured_news = []
            
            # 중요 키워드 정의
            important_keywords = ['WSOP', 'PokerStars', 'GGPoker', 'tournament', 'bracelet', 'winner', 'champion']
            
            for row in news_data:
                title, content, category, author, pub_date, url = row
                
                category_stats[category or 'general'] += 1
                
                # 키워드 분석
                text = (title + ' ' + (content or '')).lower()
                for keyword in important_keywords:
                    if keyword.lower() in text:
                        top_keywords[keyword] += 1
                        
                # 중요 뉴스 선별 (제목에 중요 키워드가 포함된 경우)
                if any(keyword.lower() in title.lower() for keyword in important_keywords[:5]):
                    featured_news.append({
                        'title': title,
                        'category': category,
                        'author': author,
                        'published_date': pub_date,
                        'url': url,
                        'importance': 'high'
                    })
                    
            conn.close()
            
            return {
                'total_articles': len(news_data),
                'category_breakdown': dict(category_stats.most_common(5)),
                'trending_keywords': dict(top_keywords.most_common(10)),
                'featured_articles': featured_news[:5],
                'news_sentiment': self.analyze_news_sentiment(news_data)
            }
            
        except Exception as e:
            logger.error(f"뉴스 하이라이트 수집 오류: {str(e)}")
            return {}
            
    def analyze_news_sentiment(self, news_data):
        """뉴스 감정 분석"""
        positive_words = ['win', 'winner', 'champion', 'success', 'record', 'best', 'great', 'amazing', 'victory']
        negative_words = ['lose', 'lost', 'fail', 'worst', 'bad', 'terrible', 'scandal', 'controversy', 'defeat']
        
        positive_count = 0
        negative_count = 0
        
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
                
        total = len(news_data)
        if total > 0:
            return {
                'positive_ratio': round((positive_count / total) * 100, 1),
                'negative_ratio': round((negative_count / total) * 100, 1),
                'neutral_ratio': round(((total - positive_count - negative_count) / total) * 100, 1),
                'overall_sentiment': 'positive' if positive_count > negative_count else 'negative' if negative_count > positive_count else 'neutral'
            }
        return {'positive_ratio': 0, 'negative_ratio': 0, 'neutral_ratio': 100, 'overall_sentiment': 'neutral'}
        
    def generate_broadcast_segments(self):
        """방송 세그먼트 생성"""
        logger.info("  📺 방송 세그먼트 생성...")
        
        market_summary = self.get_market_summary()
        top_performers = self.get_top_performers()
        market_trends = self.get_market_trends()
        news_highlights = self.get_news_highlights()
        
        segments = {
            'opening_segment': self.create_opening_segment(market_summary, top_performers),
            'market_analysis': self.create_market_analysis_segment(market_trends, top_performers),
            'news_segment': self.create_news_segment(news_highlights),
            'closing_segment': self.create_closing_segment(market_trends)
        }
        
        return segments
        
    def create_opening_segment(self, market_summary, top_performers):
        """오프닝 세그먼트"""
        total_players = market_summary.get('total_players_online', 0)
        leader = top_performers[0] if top_performers else {'name': 'N/A', 'total_players': 0}
        
        segment = {
            'headline': f"오늘의 온라인 포커 시장 현황",
            'key_stats': [
                f"전 세계 온라인 포커 플레이어: {total_players:,}명",
                f"시장 리더: {leader['name']} ({leader['total_players']:,}명)",
                f"활성 포커 사이트: {market_summary.get('total_active_sites', 0)}개"
            ],
            'talking_points': [
                f"현재 온라인 포커 시장에는 총 {total_players:,}명의 플레이어가 활동하고 있습니다.",
                f"{leader['name']}이 {leader['total_players']:,}명으로 시장을 선도하고 있습니다."
            ]
        }
        
        return segment
        
    def create_market_analysis_segment(self, market_trends, top_performers):
        """시장 분석 세그먼트"""
        trend = market_trends.get('overall_trend', 'stable')
        trend_desc = {
            'growth': '성장세',
            'decline': '하락세',
            'stable': '안정세'
        }.get(trend, '안정세')
        
        biggest_gainer = market_trends.get('biggest_gainer', {})
        top_3_sites = top_performers[:3] if len(top_performers) >= 3 else top_performers
        
        segment = {
            'headline': f"시장 분석: 전체적으로 {trend_desc}를 보이고 있습니다",
            'market_overview': [
                f"성장 사이트: {market_trends.get('growth_sites_count', 0)}개",
                f"하락 사이트: {market_trends.get('decline_sites_count', 0)}개",
                f"안정 사이트: {market_trends.get('stable_sites_count', 0)}개"
            ],
            'top_3_breakdown': [
                f"{i+1}위. {site['name']}: {site['total_players']:,}명 ({site['market_share']}%)"
                for i, site in enumerate(top_3_sites)
            ],
            'highlight': biggest_gainer.get('name', '') and f"가장 주목할 만한 성장을 보인 사이트는 {biggest_gainer['name']}로 {biggest_gainer['growth']:+.1f}% 증가했습니다." or ""
        }
        
        return segment
        
    def create_news_segment(self, news_highlights):
        """뉴스 세그먼트"""
        trending_keywords = news_highlights.get('trending_keywords', {})
        featured_articles = news_highlights.get('featured_articles', [])
        sentiment = news_highlights.get('news_sentiment', {})
        
        top_keyword = max(trending_keywords.items(), key=lambda x: x[1]) if trending_keywords else ('', 0)
        
        segment = {
            'headline': "포커 뉴스 하이라이트",
            'news_overview': [
                f"분석된 기사: {news_highlights.get('total_articles', 0)}개",
                f"전체 뉴스 톤: {sentiment.get('overall_sentiment', 'neutral')}",
                f"가장 핫한 키워드: {top_keyword[0]} ({top_keyword[1]}회 언급)" if top_keyword[0] else "키워드 분석 데이터 없음"
            ],
            'featured_stories': [
                {
                    'title': article['title'],
                    'category': article['category'],
                    'talking_point': f"{article['category']} 카테고리의 주요 소식입니다."
                }
                for article in featured_articles[:3]
            ],
            'trending_topics': list(trending_keywords.keys())[:5]
        }
        
        return segment
        
    def create_closing_segment(self, market_trends):
        """클로징 세그먼트"""
        trend = market_trends.get('overall_trend', 'stable')
        
        outlook = {
            'growth': "앞으로도 성장세가 지속될 것으로 예상됩니다.",
            'decline': "시장 회복을 위한 관찰이 필요한 상황입니다.",
            'stable': "안정적인 시장 상황이 유지되고 있습니다."
        }.get(trend, "시장 상황을 지속적으로 모니터링하겠습니다.")
        
        segment = {
            'headline': "오늘의 포커 시장 총평",
            'summary_points': [
                f"전체 시장은 {trend}한 모습을 보였습니다.",
                f"상위 사이트들의 경쟁이 계속되고 있습니다.",
                "포커 뉴스에서는 다양한 토너먼트 소식이 주를 이뤘습니다."
            ],
            'outlook': outlook,
            'next_watch': "내일은 어떤 변화가 있을지 지켜보겠습니다."
        }
        
        return segment
        
    def calculate_key_metrics(self):
        """핵심 지표 계산"""
        logger.info("  📊 핵심 지표 계산...")
        
        market_summary = self.get_market_summary()
        top_performers = self.get_top_performers()
        
        # HHI (허핀달-허시만 지수) - 시장 집중도
        hhi = 0
        total_players = market_summary.get('total_players_online', 0)
        
        if total_players > 0:
            for site in top_performers:
                market_share = (site['total_players'] / total_players) * 100
                hhi += market_share ** 2
                
        # 상위 3개 사이트 집중도
        top3_concentration = sum(site['market_share'] for site in top_performers[:3])
        
        metrics = {
            'market_concentration_hhi': round(hhi, 2),
            'top3_concentration': round(top3_concentration, 1),
            'average_site_size': round(total_players / len(top_performers), 0) if top_performers else 0,
            'cash_vs_tournament_ratio': f"{market_summary.get('cash_percentage', 0):.1f}% : {market_summary.get('tournament_percentage', 0):.1f}%",
            'market_diversity': 'high' if hhi < 1500 else 'medium' if hhi < 2500 else 'low'
        }
        
        return metrics
        
    def detect_significant_changes(self):
        """중요한 변화 감지"""
        logger.info("  🚨 중요한 변화 감지...")
        
        alerts = []
        
        try:
            top_performers = self.get_top_performers()
            
            for site in top_performers:
                growth_rate = site.get('growth_rate', 0)
                
                # 급격한 변화 감지
                if abs(growth_rate) > 20:
                    severity = 'high'
                    alert_type = '급등' if growth_rate > 0 else '급락'
                elif abs(growth_rate) > 10:
                    severity = 'medium'
                    alert_type = '상승' if growth_rate > 0 else '하락'
                else:
                    continue
                    
                alerts.append({
                    'site': site['name'],
                    'type': alert_type,
                    'change': f"{growth_rate:+.1f}%",
                    'severity': severity,
                    'current_players': site['total_players'],
                    'description': f"{site['name']}에서 {alert_type} ({growth_rate:+.1f}%) 감지"
                })
                
            # 심각도순으로 정렬
            alerts.sort(key=lambda x: (x['severity'] == 'high', abs(float(x['change'].replace('%', '').replace('+', '')))), reverse=True)
            
            return alerts[:5]  # 상위 5개만
            
        except Exception as e:
            logger.error(f"변화 감지 오류: {str(e)}")
            return []
            
    def save_daily_report(self, report_data):
        """일일 리포트 저장"""
        logger.info("💾 일일 리포트 저장...")
        
        # JSON 형태로 상세 리포트 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f'daily_report_{timestamp}.json'
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        # 방송용 간단 리포트 저장
        text_filename = f'broadcast_report_{timestamp}.txt'
        self.save_broadcast_report(report_data, text_filename)
        
        logger.info(f"📊 상세 리포트: {json_filename}")
        logger.info(f"📺 방송용 리포트: {text_filename}")
        
        return json_filename, text_filename
        
    def save_broadcast_report(self, report_data, filename):
        """방송용 간단 리포트 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"일일 포커 시장 브리핑 - {report_data['report_date']}\n")
            f.write("=" * 60 + "\n\n")
            
            # 오프닝 세그먼트
            opening = report_data['broadcast_segments']['opening_segment']
            f.write("📺 오프닝 세그먼트\n")
            f.write("-" * 30 + "\n")
            f.write(f"헤드라인: {opening['headline']}\n\n")
            f.write("주요 통계:\n")
            for stat in opening['key_stats']:
                f.write(f"  • {stat}\n")
            f.write("\n방송 멘트:\n")
            for point in opening['talking_points']:
                f.write(f"  \"{point}\"\n")
            f.write("\n")
            
            # 시장 분석 세그먼트
            market = report_data['broadcast_segments']['market_analysis']
            f.write("📊 시장 분석 세그먼트\n")
            f.write("-" * 30 + "\n")
            f.write(f"헤드라인: {market['headline']}\n\n")
            f.write("TOP 3 사이트:\n")
            for breakdown in market['top_3_breakdown']:
                f.write(f"  • {breakdown}\n")
            if market['highlight']:
                f.write(f"\n특별 언급: {market['highlight']}\n")
            f.write("\n")
            
            # 뉴스 세그먼트
            news = report_data['broadcast_segments']['news_segment']
            f.write("📰 뉴스 세그먼트\n")
            f.write("-" * 30 + "\n")
            f.write("뉴스 개요:\n")
            for overview in news['news_overview']:
                f.write(f"  • {overview}\n")
            f.write("\n주요 기사:\n")
            for story in news['featured_stories']:
                f.write(f"  • {story['title']}\n")
            f.write("\n")
            
            # 클로징 세그먼트
            closing = report_data['broadcast_segments']['closing_segment']
            f.write("🎬 클로징 세그먼트\n")
            f.write("-" * 30 + "\n")
            f.write(f"헤드라인: {closing['headline']}\n\n")
            f.write("총평:\n")
            for summary in closing['summary_points']:
                f.write(f"  • {summary}\n")
            f.write(f"\n전망: {closing['outlook']}\n")
            f.write(f"마무리: {closing['next_watch']}\n")
            f.write("\n")
            
            # 알림 사항
            if report_data['alerts_and_changes']:
                f.write("🚨 주요 변화 알림\n")
                f.write("-" * 30 + "\n")
                for alert in report_data['alerts_and_changes']:
                    f.write(f"  • {alert['description']}\n")
                f.write("\n")
                
            f.write("=" * 60 + "\n")
            f.write("리포트 생성 시간: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")

def main():
    """메인 실행 함수"""
    print("📋 일일 포커 시장 리포트 생성기")
    print("=" * 50)
    
    generator = DailyReportGenerator()
    
    try:
        # 일일 리포트 생성
        print("\n🔄 리포트 생성 중...")
        report_data = generator.generate_daily_report()
        
        # 결과 미리보기
        print("\n📊 리포트 미리보기:")
        market_summary = report_data.get('market_summary', {})
        print(f"  총 플레이어: {market_summary.get('total_players_online', 0):,}명")
        print(f"  활성 사이트: {market_summary.get('total_active_sites', 0)}개")
        
        top_performers = report_data.get('top_performers', [])
        if top_performers:
            print(f"  시장 리더: {top_performers[0]['name']} ({top_performers[0]['total_players']:,}명)")
            
        news_highlights = report_data.get('news_highlights', {})
        print(f"  분석된 뉴스: {news_highlights.get('total_articles', 0)}개")
        
        alerts = report_data.get('alerts_and_changes', [])
        if alerts:
            print(f"  중요 알림: {len(alerts)}건")
            for alert in alerts[:2]:
                print(f"    - {alert['description']}")
                
        # 리포트 저장
        print("\n💾 리포트 저장 중...")
        json_file, text_file = generator.save_daily_report(report_data)
        
        print(f"\n✅ 일일 리포트 생성 완료!")
        print(f"📊 상세 분석: {json_file}")
        print(f"📺 방송용 스크립트: {text_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"리포트 생성 오류: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🚀 일일 리포트 완료! 다음: 기본 대시보드 구현")
    else:
        print(f"\n💀 리포트 생성 실패 - 문제 해결 필요")
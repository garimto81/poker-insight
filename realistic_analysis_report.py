#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
현실적인 포커 시장 분석 리포트 생성기
- 실제 데이터 상황을 반영한 분석
- 데이터 한계 명시 및 현실적 인사이트 제공
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

class RealisticAnalysisReportGenerator:
    def __init__(self, db_path='poker_insight.db'):
        self.db_path = db_path
        
    def get_db_connection(self):
        """SQLite 데이터베이스 연결"""
        return sqlite3.connect(self.db_path)
        
    def generate_realistic_report(self):
        """현실적인 분석 리포트 생성"""
        logger.info("📊 현실적인 포커 시장 분석 시작...")
        
        report_data = {
            'report_metadata': self.get_report_metadata(),
            'data_quality_assessment': self.assess_data_quality(),
            'current_market_snapshot': self.analyze_current_snapshot(),
            'comparative_analysis': self.perform_comparative_analysis(),
            'news_based_insights': self.extract_news_insights(),
            'actionable_recommendations': self.generate_realistic_recommendations(),
            'data_limitations': self.document_data_limitations()
        }
        
        return report_data
        
    def get_report_metadata(self):
        """리포트 메타데이터"""
        return {
            'generated_at': datetime.now().isoformat(),
            'report_type': 'realistic_market_analysis',
            'data_collection_date': datetime.now().strftime('%Y-%m-%d'),
            'analysis_approach': 'single_snapshot_with_limitations',
            'reliability_level': 'current_state_accurate_trends_limited'
        }
        
    def assess_data_quality(self):
        """데이터 품질 평가"""
        logger.info("  🔍 데이터 품질 평가...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # 전체 사이트 데이터 품질 체크
            query = """
            SELECT 
                ps.name,
                td.total_players,
                td.seven_day_average,
                CASE WHEN td.seven_day_average > 0 THEN 1 ELSE 0 END as has_historical_data
            FROM poker_sites ps
            JOIN traffic_data td ON ps.id = td.site_id
            WHERE td.total_players > 0
            ORDER BY td.total_players DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            total_sites = len(results)
            sites_with_historical = sum(row[3] for row in results)
            sites_without_historical = total_sites - sites_with_historical
            
            # 히스토리컬 데이터가 있는 사이트들의 현실성 체크
            realistic_data = []
            questionable_data = []
            
            for row in results:
                name, current, avg_7day, has_historical = row
                if has_historical:
                    if avg_7day > 0:
                        growth_rate = ((current - avg_7day) / avg_7day) * 100
                        # 현실적인 성장률 범위 체크 (일주일에 ±50% 이내)
                        if abs(growth_rate) <= 50:
                            realistic_data.append((name, current, avg_7day, growth_rate))
                        else:
                            questionable_data.append((name, current, avg_7day, growth_rate))
                            
            quality_assessment = {
                'total_active_sites': total_sites,
                'sites_with_historical_data': sites_with_historical,
                'sites_without_historical_data': sites_without_historical,
                'historical_data_coverage': round((sites_with_historical / total_sites) * 100, 1),
                'realistic_trend_data': len(realistic_data),
                'questionable_trend_data': len(questionable_data),
                'data_reliability': self.calculate_data_reliability(sites_with_historical, total_sites, len(realistic_data)),
                'realistic_sites': realistic_data,
                'questionable_sites': questionable_data
            }
            
            conn.close()
            return quality_assessment
            
        except Exception as e:
            logger.error(f"데이터 품질 평가 오류: {str(e)}")
            return {}
            
    def calculate_data_reliability(self, sites_with_historical, total_sites, realistic_count):
        """데이터 신뢰도 계산"""
        if total_sites == 0:
            return "UNKNOWN"
            
        historical_ratio = sites_with_historical / total_sites
        
        if historical_ratio >= 0.8 and realistic_count >= sites_with_historical * 0.8:
            return "HIGH"
        elif historical_ratio >= 0.5 and realistic_count >= sites_with_historical * 0.6:
            return "MEDIUM"
        elif historical_ratio >= 0.2:
            return "LOW"
        else:
            return "VERY_LOW"
            
    def analyze_current_snapshot(self):
        """현재 시점 스냅샷 분석"""
        logger.info("  📸 현재 시점 스냅샷 분석...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT 
                ps.name,
                ps.url,
                td.total_players,
                td.cash_players,
                td.tournament_players,
                td.rank
            FROM poker_sites ps
            JOIN traffic_data td ON ps.id = td.site_id
            WHERE td.total_players > 0
            ORDER BY td.total_players DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            # 현재 시장 구조 분석
            total_players = sum(row[2] for row in results)
            total_cash = sum(row[3] for row in results)
            total_tournaments = sum(row[4] for row in results)
            
            # 시장 집중도 (HHI) 계산
            market_shares = [(row[2] / total_players) * 100 for row in results]
            hhi = sum(share ** 2 for share in market_shares)
            
            # 상위 사이트 분석
            top_sites = []
            cumulative_share = 0
            
            for i, row in enumerate(results):
                name, url, players, cash, tournaments, rank = row
                market_share = (players / total_players) * 100
                cumulative_share += market_share
                
                # 플레이어 구성 분석
                cash_ratio = (cash / players) * 100 if players > 0 else 0
                tournament_ratio = (tournaments / players) * 100 if players > 0 else 0
                
                site_info = {
                    'rank': i + 1,
                    'name': name,
                    'url': url,
                    'total_players': players,
                    'cash_players': cash,
                    'tournament_players': tournaments,
                    'market_share': round(market_share, 2),
                    'cumulative_share': round(cumulative_share, 2),
                    'cash_ratio': round(cash_ratio, 1),
                    'tournament_ratio': round(tournament_ratio, 1),
                    'size_category': self.categorize_by_size(players),
                    'player_focus': self.determine_player_focus(cash_ratio, tournament_ratio)
                }
                
                top_sites.append(site_info)
                
            snapshot = {
                'capture_timestamp': datetime.now().isoformat(),
                'total_market_players': total_players,
                'total_cash_players': total_cash,
                'total_tournament_players': total_tournaments,
                'active_sites_count': len(results),
                'market_concentration': {
                    'hhi_index': round(hhi, 2),
                    'concentration_level': self.classify_concentration(hhi),
                    'top3_share': round(sum(market_shares[:3]), 1),
                    'top5_share': round(sum(market_shares[:5]), 1),
                    'top10_share': round(sum(market_shares[:10]), 1)
                },
                'player_distribution': {
                    'cash_percentage': round((total_cash / total_players) * 100, 1),
                    'tournament_percentage': round((total_tournaments / total_players) * 100, 1),
                    'cash_vs_tournament_ratio': f"{round((total_cash / total_players) * 100, 1)}% : {round((total_tournaments / total_players) * 100, 1)}%"
                },
                'site_rankings': top_sites
            }
            
            conn.close()
            return snapshot
            
        except Exception as e:
            logger.error(f"스냅샷 분석 오류: {str(e)}")
            return {}
            
    def categorize_by_size(self, players):
        """사이트 규모 분류"""
        if players >= 50000:
            return "메이저 사이트"
        elif players >= 10000:
            return "대형 사이트"
        elif players >= 1000:
            return "중형 사이트"
        elif players >= 100:
            return "소형 사이트"
        else:
            return "마이크로 사이트"
            
    def determine_player_focus(self, cash_ratio, tournament_ratio):
        """플레이어 포커스 결정"""
        if tournament_ratio > 80:
            return "토너먼트 중심"
        elif cash_ratio > 50:
            return "캐시게임 중심"
        elif 30 <= cash_ratio <= 70:
            return "균형형"
        else:
            return "토너먼트 위주"
            
    def classify_concentration(self, hhi):
        """시장 집중도 분류"""
        if hhi < 1500:
            return "경쟁적 시장"
        elif hhi < 2500:
            return "중간 집중도"
        else:
            return "고도 집중 시장"
            
    def perform_comparative_analysis(self):
        """비교 분석 수행"""
        logger.info("  📊 비교 분석 수행...")
        
        snapshot = self.analyze_current_snapshot()
        sites = snapshot.get('site_rankings', [])
        
        if not sites:
            return {}
            
        # 규모별 그룹 분석
        size_groups = defaultdict(list)
        for site in sites:
            size_groups[site['size_category']].append(site)
            
        # 플레이어 타입별 분석
        focus_groups = defaultdict(list)
        for site in sites:
            focus_groups[site['player_focus']].append(site)
            
        # 브랜드 패밀리 분석
        brand_families = self.analyze_brand_families(sites)
        
        # 네트워크별 집계
        network_analysis = self.analyze_networks(sites)
        
        comparative_analysis = {
            'size_distribution': {
                category: {
                    'count': len(sites_list),
                    'total_players': sum(site['total_players'] for site in sites_list),
                    'market_share': sum(site['market_share'] for site in sites_list),
                    'average_size': round(sum(site['total_players'] for site in sites_list) / len(sites_list), 0) if sites_list else 0
                }
                for category, sites_list in size_groups.items()
            },
            'focus_distribution': {
                focus: {
                    'count': len(sites_list),
                    'total_players': sum(site['total_players'] for site in sites_list),
                    'average_cash_ratio': round(sum(site['cash_ratio'] for site in sites_list) / len(sites_list), 1) if sites_list else 0
                }
                for focus, sites_list in focus_groups.items()
            },
            'brand_families': brand_families,
            'network_analysis': network_analysis,
            'market_leaders': sites[:5],  # 상위 5개
            'emerging_players': [site for site in sites if 1000 <= site['total_players'] <= 10000]  # 중형 사이트들
        }
        
        return comparative_analysis
        
    def analyze_brand_families(self, sites):
        """브랜드 패밀리 분석"""
        brand_families = defaultdict(list)
        
        for site in sites:
            name = site['name']
            
            # 브랜드 분류
            if 'PokerStars' in name:
                brand_families['PokerStars'].append(site)
            elif 'GG' in name:
                brand_families['GGNetwork'].append(site)
            elif 'iPoker' in name:
                brand_families['iPoker'].append(site)
            elif 'WPT' in name:
                brand_families['WPT'].append(site)
            else:
                brand_families['기타'].append(site)
                
        # 브랜드별 집계
        brand_summary = {}
        for brand, sites_list in brand_families.items():
            if sites_list:
                brand_summary[brand] = {
                    'site_count': len(sites_list),
                    'total_players': sum(site['total_players'] for site in sites_list),
                    'market_share': sum(site['market_share'] for site in sites_list),
                    'sites': [{'name': site['name'], 'players': site['total_players']} for site in sites_list]
                }
                
        return brand_summary
        
    def analyze_networks(self, sites):
        """네트워크별 분석"""
        # 주요 네트워크 식별
        networks = {
            'GGNetwork': [site for site in sites if 'GG' in site['name']],
            'PokerStars': [site for site in sites if 'PokerStars' in site['name']],
            'iPoker': [site for site in sites if 'iPoker' in site['name']],
            '독립형': [site for site in sites if not any(keyword in site['name'] for keyword in ['GG', 'PokerStars', 'iPoker'])]
        }
        
        network_summary = {}
        for network, sites_list in networks.items():
            if sites_list:
                network_summary[network] = {
                    'site_count': len(sites_list),
                    'total_players': sum(site['total_players'] for site in sites_list),
                    'market_share': sum(site['market_share'] for site in sites_list),
                    'largest_site': max(sites_list, key=lambda x: x['total_players'])['name'],
                    'average_site_size': round(sum(site['total_players'] for site in sites_list) / len(sites_list), 0)
                }
                
        return network_summary
        
    def extract_news_insights(self):
        """뉴스 기반 인사이트 추출"""
        logger.info("  📰 뉴스 기반 인사이트 추출...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT title, content, category, author, published_date, url
            FROM news_items
            ORDER BY scraped_at DESC
            LIMIT 30
            """
            
            cursor.execute(query)
            news_data = cursor.fetchall()
            
            # 실제 뉴스에서 인사이트 추출
            insights = {
                'recent_news_count': len(news_data),
                'category_distribution': self.analyze_news_categories(news_data),
                'trending_topics': self.extract_trending_topics(news_data),
                'brand_mentions': self.find_brand_mentions(news_data),
                'market_impact_news': self.identify_market_impact_news(news_data),
                'tournament_calendar': self.extract_tournament_info(news_data)
            }
            
            conn.close()
            return insights
            
        except Exception as e:
            logger.error(f"뉴스 인사이트 추출 오류: {str(e)}")
            return {}
            
    def analyze_news_categories(self, news_data):
        """뉴스 카테고리 분석"""
        categories = Counter()
        for row in news_data:
            category = row[2] or 'general'
            categories[category] += 1
        return dict(categories.most_common(5))
        
    def extract_trending_topics(self, news_data):
        """트렌딩 토픽 추출"""
        keywords = ['WSOP', 'PokerStars', 'GGPoker', 'tournament', 'bracelet', 'high stakes', 'online poker']
        keyword_counts = Counter()
        
        for row in news_data:
            title = row[0] or ''
            content = row[1] or ''
            text = (title + ' ' + content).lower()
            
            for keyword in keywords:
                if keyword.lower() in text:
                    keyword_counts[keyword] += 1
                    
        return dict(keyword_counts.most_common(5))
        
    def find_brand_mentions(self, news_data):
        """브랜드 언급 찾기"""
        brands = ['PokerStars', 'GGPoker', 'WPT Global', '888poker', 'partypoker']
        brand_mentions = defaultdict(list)
        
        for row in news_data:
            title = row[0] or ''
            
            for brand in brands:
                if brand.lower() in title.lower():
                    brand_mentions[brand].append({
                        'title': title,
                        'category': row[2],
                        'published_date': row[4]
                    })
                    
        return dict(brand_mentions)
        
    def identify_market_impact_news(self, news_data):
        """시장 임팩트 뉴스 식별"""
        impact_keywords = ['regulation', 'launch', 'partnership', 'acquisition', 'license', 'ban']
        impact_news = []
        
        for row in news_data:
            title = row[0] or ''
            content = row[1] or ''
            text = (title + ' ' + content).lower()
            
            if any(keyword in text for keyword in impact_keywords):
                impact_news.append({
                    'title': title,
                    'category': row[2],
                    'published_date': row[4],
                    'impact_type': [kw for kw in impact_keywords if kw in text][0]
                })
                
        return impact_news[:5]
        
    def extract_tournament_info(self, news_data):
        """토너먼트 정보 추출"""
        tournament_news = []
        tournament_keywords = ['WSOP', 'WPT', 'EPT', 'tournament', 'bracelet']
        
        for row in news_data:
            title = row[0] or ''
            
            if any(keyword.lower() in title.lower() for keyword in tournament_keywords):
                tournament_news.append({
                    'title': title,
                    'category': row[2],
                    'published_date': row[4]
                })
                
        return tournament_news[:5]
        
    def generate_realistic_recommendations(self):
        """현실적인 권고사항 생성"""
        logger.info("  💡 현실적인 권고사항 생성...")
        
        snapshot = self.analyze_current_snapshot()
        quality = self.assess_data_quality()
        
        recommendations = {
            'data_improvement': [],
            'monitoring_priorities': [],
            'analysis_enhancements': [],
            'broadcast_focus_areas': []
        }
        
        # 데이터 개선 권고
        if quality.get('historical_data_coverage', 0) < 50:
            recommendations['data_improvement'].append({
                'priority': 'HIGH',
                'action': '히스토리컬 데이터 수집 시스템 구축',
                'description': '정확한 트렌드 분석을 위해 매일 데이터 수집 필요',
                'timeline': '1-2주'
            })
            
        if quality.get('questionable_trend_data'):
            recommendations['data_improvement'].append({
                'priority': 'MEDIUM',
                'action': '데이터 검증 프로세스 강화',
                'description': '비현실적인 성장률 데이터 필터링 로직 추가',
                'timeline': '1주'
            })
            
        # 모니터링 우선순위
        top_sites = snapshot.get('site_rankings', [])[:5]
        for site in top_sites:
            if site['market_share'] > 20:
                recommendations['monitoring_priorities'].append({
                    'site': site['name'],
                    'reason': f"시장 리더 ({site['market_share']}% 점유)",
                    'focus': '시장 영향력이 큰 사이트로 변화 모니터링 필수'
                })
                
        # 분석 강화 영역
        recommendations['analysis_enhancements'] = [
            {
                'area': '뉴스-트래픽 상관관계 분석',
                'description': '프로모션, 토너먼트 발표와 트래픽 변화 패턴 분석',
                'benefit': '마케팅 이벤트 효과 측정 가능'
            },
            {
                'area': '지역별 시장 세분화',
                'description': '유럽, 아시아, 북미 지역별 포커 사이트 선호도 분석',
                'benefit': '지역별 맞춤 콘텐츠 제작 가능'
            },
            {
                'area': '실시간 알림 시스템',
                'description': '급격한 트래픽 변화 시 즉시 알림 기능',
                'benefit': '브레이킹 뉴스 발굴 및 즉시 대응 가능'
            }
        ]
        
        # 방송 포커스 영역
        recommendations['broadcast_focus_areas'] = [
            {
                'topic': '시장 집중도 이슈',
                'angle': f"상위 3개 사이트가 {snapshot.get('market_concentration', {}).get('top3_share', 0)}% 점유",
                'talking_points': ['시장 다양성', '신규 사이트 기회', '플레이어 선택권']
            },
            {
                'topic': '토너먼트 vs 캐시게임 트렌드',
                'angle': snapshot.get('player_distribution', {}).get('cash_vs_tournament_ratio', ''),
                'talking_points': ['플레이어 성향 변화', '사이트별 전략', '게임 유형별 성장']
            }
        ]
        
        return recommendations
        
    def document_data_limitations(self):
        """데이터 한계 문서화"""
        return {
            'current_limitations': [
                '단일 시점 스냅샷으로 트렌드 분석 제한',
                '대부분 사이트의 히스토리컬 데이터 부족',
                '일부 성장률 데이터의 현실성 의문',
                '시간대별, 요일별 패턴 분석 불가'
            ],
            'reliability_assessment': {
                '현재 시장 상황': 'HIGH - 실시간 데이터 정확',
                '시장 점유율': 'HIGH - 상대적 순위 신뢰 가능',
                '성장 트렌드': 'LOW - 히스토리컬 데이터 부족',
                '뉴스 연관성': 'MEDIUM - 시점 차이로 인한 제약'
            },
            'improvement_roadmap': [
                '1주차: 매일 데이터 수집 시스템 구축',
                '2주차: 7일 이동평균 트렌드 분석 시작',
                '1개월차: 월별 비교 분석 가능',
                '3개월차: 계절성 및 패턴 분석 가능'
            ],
            'alternative_analysis_methods': [
                '현재 시점 시장 구조 분석에 집중',
                '뉴스 기반 정성적 분석 강화',
                '사이트별 특성 및 포지셔닝 분석',
                '브랜드별 전략 및 경쟁 구도 분석'
            ]
        }
        
    def save_realistic_report(self, report_data):
        """현실적인 리포트 저장"""
        logger.info("💾 현실적인 리포트 저장...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON 상세 리포트
        json_filename = f'realistic_analysis_{timestamp}.json'
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        # 방송용 현실적 브리핑
        brief_filename = f'realistic_brief_{timestamp}.txt'
        self.save_realistic_brief(report_data, brief_filename)
        
        logger.info(f"📊 상세 분석: {json_filename}")
        logger.info(f"📺 현실적 브리핑: {brief_filename}")
        
        return json_filename, brief_filename
        
    def save_realistic_brief(self, report_data, filename):
        """현실적 브리핑 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("📊 현실적인 온라인 포커 시장 분석 브리핑\n")
            f.write(f"분석 시점: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}\n")
            f.write("=" * 80 + "\n\n")
            
            # 데이터 신뢰도 공지
            quality = report_data.get('data_quality_assessment', {})
            f.write("⚠️ 데이터 신뢰도 안내\n")
            f.write("-" * 40 + "\n")
            f.write(f"현재 시점 데이터: 신뢰 가능\n")
            f.write(f"히스토리컬 데이터 보유율: {quality.get('historical_data_coverage', 0)}%\n")
            f.write(f"트렌드 분석 신뢰도: {quality.get('data_reliability', 'UNKNOWN')}\n\n")
            
            # 현재 시장 현황
            snapshot = report_data.get('current_market_snapshot', {})
            f.write("📊 현재 시장 현황 (확실한 데이터)\n")
            f.write("-" * 40 + "\n")
            f.write(f"총 온라인 플레이어: {snapshot.get('total_market_players', 0):,}명\n")
            f.write(f"활성 포커 사이트: {snapshot.get('active_sites_count', 0)}개\n")
            concentration = snapshot.get('market_concentration', {})
            f.write(f"시장 집중도: {concentration.get('concentration_level', 'N/A')}\n")
            f.write(f"상위 3개 사이트 점유율: {concentration.get('top3_share', 0)}%\n\n")
            
            # 시장 구조 분석
            comparative = report_data.get('comparative_analysis', {})
            brand_families = comparative.get('brand_families', {})
            f.write("🏢 주요 브랜드별 현황\n")
            f.write("-" * 40 + "\n")
            for brand, data in brand_families.items():
                if data.get('total_players', 0) > 1000:  # 1천명 이상만 표시
                    f.write(f"{brand}: {data['total_players']:,}명 ({data['market_share']:.1f}%, {data['site_count']}개 사이트)\n")
            f.write("\n")
            
            # 뉴스 인사이트
            news = report_data.get('news_based_insights', {})
            f.write("📰 뉴스 기반 인사이트\n")
            f.write("-" * 40 + "\n")
            f.write(f"최근 분석 기사: {news.get('recent_news_count', 0)}개\n")
            
            trending = news.get('trending_topics', {})
            if trending:
                f.write("주요 키워드:\n")
                for keyword, count in list(trending.items())[:3]:
                    f.write(f"  • {keyword}: {count}회 언급\n")
                    
            brand_mentions = news.get('brand_mentions', {})
            if brand_mentions:
                f.write("브랜드 뉴스 언급:\n")
                for brand, mentions in brand_mentions.items():
                    if mentions:
                        f.write(f"  • {brand}: {len(mentions)}개 기사\n")
            f.write("\n")
            
            # 한계 및 주의사항
            limitations = report_data.get('data_limitations', {})
            f.write("⚠️ 분석 한계 및 주의사항\n")
            f.write("-" * 40 + "\n")
            for limitation in limitations.get('current_limitations', []):
                f.write(f"  • {limitation}\n")
            f.write("\n")
            
            # 권고사항
            recommendations = report_data.get('actionable_recommendations', {})
            broadcast_areas = recommendations.get('broadcast_focus_areas', [])
            f.write("📺 방송 추천 포커스 영역\n")
            f.write("-" * 40 + "\n")
            for area in broadcast_areas:
                f.write(f"주제: {area['topic']}\n")
                f.write(f"앵글: {area['angle']}\n")
                f.write(f"포인트: {', '.join(area['talking_points'])}\n\n")

def main():
    """메인 실행 함수"""
    print("📊 현실적인 포커 시장 분석 리포트 생성기")
    print("=" * 60)
    
    generator = RealisticAnalysisReportGenerator()
    
    try:
        # 현실적인 분석 리포트 생성
        print("\n🔄 현실적인 분석 중...")
        report_data = generator.generate_realistic_report()
        
        # 결과 미리보기
        print("\n📊 분석 결과:")
        
        quality = report_data.get('data_quality_assessment', {})
        print(f"데이터 신뢰도: {quality.get('data_reliability', 'UNKNOWN')}")
        print(f"히스토리컬 데이터 보유율: {quality.get('historical_data_coverage', 0)}%")
        
        snapshot = report_data.get('current_market_snapshot', {})
        print(f"현재 총 플레이어: {snapshot.get('total_market_players', 0):,}명")
        print(f"활성 사이트: {snapshot.get('active_sites_count', 0)}개")
        
        # 뉴스 인사이트
        news = report_data.get('news_based_insights', {})
        print(f"분석된 뉴스: {news.get('recent_news_count', 0)}개")
        
        trending = news.get('trending_topics', {})
        if trending:
            top_trend = list(trending.items())[0]
            print(f"최다 언급 키워드: {top_trend[0]} ({top_trend[1]}회)")
            
        # 리포트 저장
        print("\n💾 리포트 저장 중...")
        json_file, brief_file = generator.save_realistic_report(report_data)
        
        print(f"\n✅ 현실적인 분석 리포트 완료!")
        print(f"📊 상세 분석: {json_file}")
        print(f"📺 현실적 브리핑: {brief_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"리포트 생성 오류: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🎯 현실적인 분석 완료! 데이터 한계를 고려한 정확한 인사이트 제공")
    else:
        print(f"\n💀 분석 실패 - 문제 해결 필요")
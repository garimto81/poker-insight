#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고급 인포그래픽 형태 포커 시장 분석 리포트 생성기
- 모든 활성 사이트 수치 분석
- 특이 변화 감지 및 뉴스 연관성 분석
- 온라인 포커 사이트 데이터 집중 분석
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
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedInfographicReportGenerator:
    def __init__(self, db_path='poker_insight.db'):
        self.db_path = db_path
        
        # 분석 임계값 설정
        self.SIGNIFICANT_CHANGE_THRESHOLD = 15.0  # 15% 이상 변화
        self.MAJOR_CHANGE_THRESHOLD = 25.0        # 25% 이상 주요 변화
        self.ANOMALY_THRESHOLD = 50.0             # 50% 이상 이상 징후
        
    def get_db_connection(self):
        """SQLite 데이터베이스 연결"""
        return sqlite3.connect(self.db_path)
        
    def generate_comprehensive_infographic_report(self):
        """종합 인포그래픽 리포트 생성"""
        logger.info("🎨 고급 인포그래픽 리포트 생성 시작...")
        
        report_data = {
            'report_metadata': self.get_report_metadata(),
            'market_overview': self.analyze_complete_market_overview(),
            'all_sites_analysis': self.analyze_all_active_sites(),
            'anomaly_detection': self.detect_market_anomalies(),
            'news_correlation': self.analyze_news_correlations(),
            'infographic_sections': self.generate_infographic_sections(),
            'executive_summary': {},  # 마지막에 생성
            'actionable_insights': self.generate_actionable_insights()
        }
        
        # 경영진 요약 생성
        report_data['executive_summary'] = self.generate_executive_summary(report_data)
        
        return report_data
        
    def get_report_metadata(self):
        """리포트 메타데이터"""
        return {
            'generated_at': datetime.now().isoformat(),
            'report_type': 'comprehensive_infographic_analysis',
            'version': '2.0_advanced',
            'focus': 'online_poker_sites_data_analysis',
            'analysis_scope': 'all_active_sites_with_news_correlation'
        }
        
    def analyze_complete_market_overview(self):
        """완전한 시장 개요 분석"""
        logger.info("  📊 완전한 시장 개요 분석...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # 모든 사이트 데이터 조회
            query = """
            SELECT 
                ps.name,
                ps.url,
                td.total_players,
                td.cash_players,
                td.tournament_players,
                td.seven_day_average,
                td.rank
            FROM poker_sites ps
            JOIN traffic_data td ON ps.id = td.site_id
            ORDER BY td.total_players DESC
            """
            
            cursor.execute(query)
            all_sites_data = cursor.fetchall()
            
            # 전체 시장 통계 계산
            total_players = sum(row[2] for row in all_sites_data)
            total_cash = sum(row[3] for row in all_sites_data)
            total_tournaments = sum(row[4] for row in all_sites_data)
            
            # 활성 사이트 분류
            active_sites = [row for row in all_sites_data if row[2] > 0]
            large_sites = [row for row in active_sites if row[2] > 10000]  # 1만명 이상
            medium_sites = [row for row in active_sites if 1000 < row[2] <= 10000]  # 1천-1만명
            small_sites = [row for row in active_sites if 100 < row[2] <= 1000]    # 100-1천명
            micro_sites = [row for row in active_sites if row[2] <= 100]           # 100명 이하
            
            # 시장 집중도 계산 (HHI)
            hhi = sum(((site[2] / total_players) * 100) ** 2 for site in active_sites) if total_players > 0 else 0
            
            # 상위 사이트들의 점유율
            top5_share = sum(row[2] for row in active_sites[:5]) / total_players * 100 if total_players > 0 else 0
            top10_share = sum(row[2] for row in active_sites[:10]) / total_players * 100 if total_players > 0 else 0
            
            overview = {
                'total_market_size': total_players,
                'total_cash_players': total_cash,
                'total_tournament_players': total_tournaments,
                'market_segmentation': {
                    'large_sites_count': len(large_sites),
                    'medium_sites_count': len(medium_sites),
                    'small_sites_count': len(small_sites),
                    'micro_sites_count': len(micro_sites),
                    'large_sites_share': round(sum(site[2] for site in large_sites) / total_players * 100, 1) if total_players > 0 else 0,
                    'medium_sites_share': round(sum(site[2] for site in medium_sites) / total_players * 100, 1) if total_players > 0 else 0
                },
                'market_concentration': {
                    'hhi_index': round(hhi, 2),
                    'top5_market_share': round(top5_share, 1),
                    'top10_market_share': round(top10_share, 1),
                    'concentration_level': self.classify_market_concentration(hhi)
                },
                'player_distribution': {
                    'cash_vs_tournament_ratio': f"{round(total_cash/total_players*100, 1)}% : {round(total_tournaments/total_players*100, 1)}%" if total_players > 0 else "0% : 0%",
                    'average_players_per_site': round(total_players / len(active_sites), 0) if active_sites else 0
                },
                'total_active_sites': len(active_sites),
                'total_tracked_sites': len(all_sites_data)
            }
            
            conn.close()
            return overview
            
        except Exception as e:
            logger.error(f"시장 개요 분석 오류: {str(e)}")
            return {}
            
    def classify_market_concentration(self, hhi):
        """시장 집중도 분류"""
        if hhi < 1500:
            return "경쟁적 시장"
        elif hhi < 2500:
            return "중간 집중도"
        else:
            return "고도 집중 시장"
            
    def analyze_all_active_sites(self):
        """모든 활성 사이트 상세 분석"""
        logger.info("  🔍 모든 활성 사이트 상세 분석...")
        
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
                td.seven_day_average,
                td.rank
            FROM poker_sites ps
            JOIN traffic_data td ON ps.id = td.site_id
            WHERE td.total_players > 0
            ORDER BY td.total_players DESC
            """
            
            cursor.execute(query)
            sites_data = cursor.fetchall()
            
            analyzed_sites = []
            total_market = sum(row[2] for row in sites_data)
            
            for i, row in enumerate(sites_data):
                name, url, total_players, cash_players, tournament_players, seven_day_avg, rank = row
                
                # 성장률 계산
                growth_rate = 0
                if seven_day_avg and seven_day_avg > 0:
                    growth_rate = ((total_players - seven_day_avg) / seven_day_avg) * 100
                
                # 사이트 분류
                site_category = self.categorize_site_size(total_players)
                
                # 플레이어 구성 분석
                cash_ratio = (cash_players / total_players * 100) if total_players > 0 else 0
                tournament_ratio = (tournament_players / total_players * 100) if total_players > 0 else 0
                
                # 시장 점유율
                market_share = (total_players / total_market * 100) if total_market > 0 else 0
                
                # 특이사항 감지
                anomaly_flags = self.detect_site_anomalies(total_players, growth_rate, cash_ratio)
                
                site_analysis = {
                    'rank': rank or (i + 1),
                    'name': name,
                    'url': url,
                    'metrics': {
                        'total_players': total_players,
                        'cash_players': cash_players,
                        'tournament_players': tournament_players,
                        'seven_day_average': seven_day_avg or 0
                    },
                    'percentages': {
                        'market_share': round(market_share, 2),
                        'cash_ratio': round(cash_ratio, 1),
                        'tournament_ratio': round(tournament_ratio, 1),
                        'growth_rate': round(growth_rate, 1)
                    },
                    'classification': {
                        'size_category': site_category,
                        'growth_trend': self.classify_growth_trend(growth_rate),
                        'player_type_focus': 'tournament' if tournament_ratio > 70 else 'cash' if cash_ratio > 70 else 'balanced'
                    },
                    'anomaly_flags': anomaly_flags,
                    'notable_features': self.identify_notable_features(name, total_players, growth_rate, cash_ratio)
                }
                
                analyzed_sites.append(site_analysis)
                
            conn.close()
            
            # 사이트별 통계 요약
            site_stats = self.calculate_site_statistics(analyzed_sites)
            
            return {
                'sites_analysis': analyzed_sites,
                'statistics_summary': site_stats,
                'total_sites_analyzed': len(analyzed_sites)
            }
            
        except Exception as e:
            logger.error(f"사이트 분석 오류: {str(e)}")
            return {}
            
    def categorize_site_size(self, total_players):
        """사이트 규모 분류"""
        if total_players >= 50000:
            return "메이저 사이트"
        elif total_players >= 10000:
            return "대형 사이트"
        elif total_players >= 1000:
            return "중형 사이트"
        elif total_players >= 100:
            return "소형 사이트"
        else:
            return "마이크로 사이트"
            
    def classify_growth_trend(self, growth_rate):
        """성장 트렌드 분류"""
        if growth_rate >= 25:
            return "급성장"
        elif growth_rate >= 10:
            return "성장"
        elif growth_rate >= -10:
            return "안정"
        elif growth_rate >= -25:
            return "하락"
        else:
            return "급락"
            
    def detect_site_anomalies(self, total_players, growth_rate, cash_ratio):
        """사이트별 이상 징후 감지"""
        anomalies = []
        
        # 급격한 성장/하락
        if abs(growth_rate) > self.ANOMALY_THRESHOLD:
            anomalies.append(f"극도의 {'성장' if growth_rate > 0 else '하락'} ({growth_rate:+.1f}%)")
            
        # 비정상적인 플레이어 구성
        if cash_ratio > 90:
            anomalies.append("캐시게임 과도 집중")
        elif cash_ratio < 5 and total_players > 1000:
            anomalies.append("토너먼트 과도 집중")
            
        # 크기 대비 비정상적 성장
        if total_players < 1000 and growth_rate > 100:
            anomalies.append("소규모 사이트 폭발적 성장")
            
        return anomalies
        
    def identify_notable_features(self, name, total_players, growth_rate, cash_ratio):
        """주목할 만한 특징 식별"""
        features = []
        
        # 브랜드 특성 분석
        if 'PokerStars' in name:
            features.append("글로벌 브랜드")
        if 'GG' in name:
            features.append("GGNetwork 계열")
        if 'WPT' in name:
            features.append("WPT 브랜드")
            
        # 성과 특성
        if growth_rate > 20:
            features.append("고성장 사이트")
        if total_players > 50000:
            features.append("메이저 플레이어")
        if 30 <= cash_ratio <= 70:
            features.append("균형잡힌 게임 구성")
            
        return features
        
    def calculate_site_statistics(self, analyzed_sites):
        """사이트별 통계 계산"""
        if not analyzed_sites:
            return {}
            
        growth_rates = [site['percentages']['growth_rate'] for site in analyzed_sites]
        market_shares = [site['percentages']['market_share'] for site in analyzed_sites]
        total_players = [site['metrics']['total_players'] for site in analyzed_sites]
        
        return {
            'growth_statistics': {
                'average_growth_rate': round(statistics.mean(growth_rates), 1),
                'median_growth_rate': round(statistics.median(growth_rates), 1),
                'growth_rate_std': round(statistics.stdev(growth_rates), 1) if len(growth_rates) > 1 else 0,
                'positive_growth_sites': len([r for r in growth_rates if r > 0]),
                'negative_growth_sites': len([r for r in growth_rates if r < 0])
            },
            'market_distribution': {
                'top_10_share': round(sum(market_shares[:10]), 1),
                'market_share_std': round(statistics.stdev(market_shares), 2) if len(market_shares) > 1 else 0,
                'largest_site_share': round(max(market_shares), 1) if market_shares else 0
            },
            'size_distribution': {
                'average_site_size': round(statistics.mean(total_players), 0),
                'median_site_size': round(statistics.median(total_players), 0),
                'size_variance': round(statistics.variance(total_players), 0) if len(total_players) > 1 else 0
            }
        }
        
    def detect_market_anomalies(self):
        """시장 이상 징후 감지"""
        logger.info("  🚨 시장 이상 징후 감지...")
        
        try:
            sites_analysis = self.analyze_all_active_sites()
            sites = sites_analysis.get('sites_analysis', [])
            
            anomalies = {
                'significant_changes': [],
                'market_disruptions': [],
                'unusual_patterns': [],
                'risk_factors': []
            }
            
            for site in sites:
                growth_rate = site['percentages']['growth_rate']
                total_players = site['metrics']['total_players']
                anomaly_flags = site['anomaly_flags']
                
                # 중요한 변화 감지
                if abs(growth_rate) > self.SIGNIFICANT_CHANGE_THRESHOLD:
                    severity = "HIGH" if abs(growth_rate) > self.MAJOR_CHANGE_THRESHOLD else "MEDIUM"
                    change_type = "급등" if growth_rate > 0 else "급락"
                    
                    anomalies['significant_changes'].append({
                        'site': site['name'],
                        'change_type': change_type,
                        'growth_rate': growth_rate,
                        'severity': severity,
                        'current_players': total_players,
                        'impact_assessment': self.assess_market_impact(site, growth_rate)
                    })
                    
                # 시장 교란 요소 감지
                if total_players > 10000 and abs(growth_rate) > 30:
                    anomalies['market_disruptions'].append({
                        'site': site['name'],
                        'disruption_type': "대형 사이트 급변",
                        'description': f"{site['name']} ({total_players:,}명)에서 {growth_rate:+.1f}% 변화",
                        'market_share': site['percentages']['market_share']
                    })
                    
                # 비정상 패턴
                if anomaly_flags:
                    anomalies['unusual_patterns'].append({
                        'site': site['name'],
                        'patterns': anomaly_flags,
                        'total_players': total_players
                    })
                    
            # 리스크 요인 분석
            anomalies['risk_factors'] = self.analyze_risk_factors(sites)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"이상 징후 감지 오류: {str(e)}")
            return {}
            
    def assess_market_impact(self, site, growth_rate):
        """시장 영향 평가"""
        market_share = site['percentages']['market_share']
        
        if market_share > 20:
            return "HIGH - 시장 리더의 변화로 전체 시장에 큰 영향"
        elif market_share > 10:
            return "MEDIUM - 주요 플레이어 변화로 시장 동향에 영향"
        elif market_share > 5:
            return "LOW-MEDIUM - 중형 사이트 변화로 해당 세그먼트에 영향"
        else:
            return "LOW - 소규모 변화로 제한적 영향"
            
    def analyze_risk_factors(self, sites):
        """리스크 요인 분석"""
        risk_factors = []
        
        # 시장 집중도 리스크
        top3_share = sum(site['percentages']['market_share'] for site in sites[:3])
        if top3_share > 70:
            risk_factors.append({
                'type': '시장 집중도 리스크',
                'description': f'상위 3개 사이트가 {top3_share:.1f}% 점유',
                'level': 'HIGH'
            })
            
        # 급격한 변화 사이트 수
        rapid_change_sites = len([s for s in sites if abs(s['percentages']['growth_rate']) > 25])
        if rapid_change_sites > 3:
            risk_factors.append({
                'type': '시장 불안정성',
                'description': f'{rapid_change_sites}개 사이트에서 급격한 변화',
                'level': 'MEDIUM'
            })
            
        return risk_factors
        
    def analyze_news_correlations(self):
        """뉴스-데이터 연관성 분석"""
        logger.info("  📰 뉴스-데이터 연관성 분석...")
        
        try:
            # 이상 징후 사이트들 식별
            anomalies = self.detect_market_anomalies()
            significant_sites = [change['site'] for change in anomalies.get('significant_changes', [])]
            
            # 뉴스 데이터 조회
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT title, content, category, author, published_date, url
            FROM news_items
            ORDER BY scraped_at DESC
            LIMIT 50
            """
            
            cursor.execute(query)
            news_data = cursor.fetchall()
            
            correlations = {
                'direct_mentions': [],
                'indirect_correlations': [],
                'market_trend_news': [],
                'regulatory_impact': [],
                'tournament_effects': []
            }
            
            # 사이트별 뉴스 연관성 분석
            for site_name in significant_sites:
                site_mentions = self.find_site_news_mentions(site_name, news_data)
                if site_mentions:
                    correlations['direct_mentions'].extend(site_mentions)
                    
            # 간접 연관성 분석
            correlations['indirect_correlations'] = self.analyze_indirect_correlations(news_data, anomalies)
            
            # 시장 트렌드 관련 뉴스
            correlations['market_trend_news'] = self.identify_market_trend_news(news_data)
            
            # 규제 영향 분석
            correlations['regulatory_impact'] = self.analyze_regulatory_news_impact(news_data)
            
            # 토너먼트 효과 분석
            correlations['tournament_effects'] = self.analyze_tournament_effects(news_data)
            
            conn.close()
            return correlations
            
        except Exception as e:
            logger.error(f"뉴스 연관성 분석 오류: {str(e)}")
            return {}
            
    def find_site_news_mentions(self, site_name, news_data):
        """사이트별 뉴스 언급 찾기"""
        mentions = []
        
        # 사이트명 변형 패턴
        site_patterns = self.generate_site_search_patterns(site_name)
        
        for row in news_data:
            title, content, category, author, pub_date, url = row
            text = (title + ' ' + (content or '')).lower()
            
            for pattern in site_patterns:
                if pattern.lower() in text:
                    mentions.append({
                        'site': site_name,
                        'news_title': title,
                        'category': category,
                        'published_date': pub_date,
                        'url': url,
                        'mention_context': self.extract_mention_context(text, pattern),
                        'relevance_score': self.calculate_relevance_score(title, content, pattern)
                    })
                    break  # 중복 방지
                    
        return mentions
        
    def generate_site_search_patterns(self, site_name):
        """사이트 검색 패턴 생성"""
        patterns = [site_name]
        
        # 브랜드별 추가 패턴
        if 'PokerStars' in site_name:
            patterns.extend(['pokerstars', 'stars', 'ps'])
        elif 'GGPoker' in site_name or 'GGNetwork' in site_name:
            patterns.extend(['ggpoker', 'ggnetwork', 'gg poker'])
        elif 'WPT' in site_name:
            patterns.extend(['wpt global', 'world poker tour'])
        elif 'iPoker' in site_name:
            patterns.extend(['ipoker network'])
            
        return patterns
        
    def extract_mention_context(self, text, pattern):
        """언급 맥락 추출"""
        pattern_pos = text.find(pattern.lower())
        if pattern_pos == -1:
            return ""
            
        # 앞뒤 50자씩 추출
        start = max(0, pattern_pos - 50)
        end = min(len(text), pattern_pos + len(pattern) + 50)
        context = text[start:end].strip()
        
        return context
        
    def calculate_relevance_score(self, title, content, pattern):
        """관련성 점수 계산"""
        score = 0
        
        # 제목에 있으면 높은 점수
        if pattern.lower() in title.lower():
            score += 3
            
        # 내용에 있으면 점수 추가
        if content and pattern.lower() in content.lower():
            score += 1
            
        # 온라인 포커 관련 키워드가 있으면 추가 점수
        poker_keywords = ['online poker', 'tournament', 'cash game', 'promotion', 'bonus']
        text = (title + ' ' + (content or '')).lower()
        
        for keyword in poker_keywords:
            if keyword in text:
                score += 0.5
                
        return round(score, 1)
        
    def analyze_indirect_correlations(self, news_data, anomalies):
        """간접 연관성 분석"""
        correlations = []
        
        # 주요 키워드와 이상 징후 매핑
        correlation_keywords = {
            'promotion': '프로모션 효과',
            'bonus': '보너스 이벤트 영향',
            'tournament': '토너먼트 시즌 효과',
            'regulation': '규제 변화 영향',
            'partnership': '파트너십 발표 효과',
            'update': '플랫폼 업데이트 영향'
        }
        
        for row in news_data:
            title, content, category, author, pub_date, url = row
            text = (title + ' ' + (content or '')).lower()
            
            for keyword, effect_type in correlation_keywords.items():
                if keyword in text:
                    correlations.append({
                        'news_title': title,
                        'effect_type': effect_type,
                        'published_date': pub_date,
                        'potential_impact': self.assess_potential_impact(keyword, text),
                        'affected_segments': self.identify_affected_segments(keyword)
                    })
                    
        return correlations[:10]  # 상위 10개만
        
    def assess_potential_impact(self, keyword, text):
        """잠재적 영향 평가"""
        impact_indicators = {
            'major': ['major', 'significant', 'huge', 'massive'],
            'moderate': ['new', 'launch', 'introduce'],
            'minor': ['small', 'minor', 'slight']
        }
        
        for level, indicators in impact_indicators.items():
            if any(indicator in text for indicator in indicators):
                return level.upper()
                
        return "UNKNOWN"
        
    def identify_affected_segments(self, keyword):
        """영향받는 세그먼트 식별"""
        segment_mapping = {
            'promotion': ['모든 사이트', '캐시게임', '토너먼트'],
            'bonus': ['신규 가입자', '기존 플레이어'],
            'tournament': ['토너먼트 중심 사이트', '메이저 사이트'],
            'regulation': ['전체 시장', '특정 지역'],
            'partnership': ['관련 브랜드', '제휴 사이트'],
            'update': ['플랫폼 사용자', '모바일 플레이어']
        }
        
        return segment_mapping.get(keyword, ['전체 시장'])
        
    def identify_market_trend_news(self, news_data):
        """시장 트렌드 관련 뉴스 식별"""
        trend_news = []
        
        trend_keywords = ['market', 'growth', 'decline', 'trend', 'industry', 'revenue', 'player count']
        
        for row in news_data:
            title, content, category, author, pub_date, url = row
            text = (title + ' ' + (content or '')).lower()
            
            if any(keyword in text for keyword in trend_keywords):
                trend_news.append({
                    'title': title,
                    'category': category,
                    'published_date': pub_date,
                    'trend_indicators': [kw for kw in trend_keywords if kw in text],
                    'market_relevance': 'HIGH' if 'online poker' in text else 'MEDIUM'
                })
                
        return trend_news[:5]
        
    def analyze_regulatory_news_impact(self, news_data):
        """규제 뉴스 영향 분석"""
        regulatory_news = []
        
        regulatory_keywords = ['regulation', 'legal', 'law', 'government', 'license', 'ban', 'approval']
        
        for row in news_data:
            title, content, category, author, pub_date, url = row
            text = (title + ' ' + (content or '')).lower()
            
            if any(keyword in text for keyword in regulatory_keywords):
                regulatory_news.append({
                    'title': title,
                    'regulatory_type': [kw for kw in regulatory_keywords if kw in text],
                    'published_date': pub_date,
                    'impact_assessment': 'POSITIVE' if any(word in text for word in ['approval', 'legal', 'license']) else 'NEGATIVE' if any(word in text for word in ['ban', 'illegal']) else 'NEUTRAL'
                })
                
        return regulatory_news[:3]
        
    def analyze_tournament_effects(self, news_data):
        """토너먼트 효과 분석"""
        tournament_news = []
        
        tournament_keywords = ['wsop', 'wpt', 'ept', 'tournament', 'bracelet', 'main event']
        
        for row in news_data:
            title, content, category, author, pub_date, url = row
            text = (title + ' ' + (content or '')).lower()
            
            if any(keyword in text for keyword in tournament_keywords):
                tournament_news.append({
                    'title': title,
                    'tournament_type': [kw for kw in tournament_keywords if kw in text],
                    'published_date': pub_date,
                    'expected_impact': 'HIGH' if 'wsop' in text else 'MEDIUM'
                })
                
        return tournament_news[:5]
        
    def generate_infographic_sections(self):
        """인포그래픽 섹션 생성"""
        logger.info("  🎨 인포그래픽 섹션 생성...")
        
        market_overview = self.analyze_complete_market_overview()
        sites_analysis = self.analyze_all_active_sites()
        anomalies = self.detect_market_anomalies()
        
        sections = {
            'header_stats': self.create_header_statistics(market_overview),
            'market_composition': self.create_market_composition_chart(market_overview),
            'top_performers_grid': self.create_top_performers_grid(sites_analysis),
            'anomaly_alerts': self.create_anomaly_alerts_section(anomalies),
            'trend_indicators': self.create_trend_indicators(sites_analysis),
            'risk_dashboard': self.create_risk_dashboard(anomalies),
            'news_impact_summary': self.create_news_impact_summary()
        }
        
        return sections
        
    def create_header_statistics(self, market_overview):
        """헤더 통계 생성"""
        return {
            'primary_metrics': [
                {
                    'label': '전체 온라인 플레이어',
                    'value': f"{market_overview.get('total_market_size', 0):,}명",
                    'icon': '👥',
                    'trend': 'stable'
                },
                {
                    'label': '활성 포커 사이트',
                    'value': f"{market_overview.get('total_active_sites', 0)}개",
                    'icon': '🏢',
                    'trend': 'stable'
                },
                {
                    'label': '시장 집중도',
                    'value': market_overview.get('market_concentration', {}).get('concentration_level', 'N/A'),
                    'icon': '📊',
                    'trend': 'neutral'
                }
            ],
            'secondary_metrics': [
                {
                    'label': '캐시게임 플레이어',
                    'value': f"{market_overview.get('total_cash_players', 0):,}명",
                    'percentage': market_overview.get('player_distribution', {}).get('cash_vs_tournament_ratio', '').split(' : ')[0] if ' : ' in market_overview.get('player_distribution', {}).get('cash_vs_tournament_ratio', '') else '0%'
                },
                {
                    'label': '토너먼트 플레이어',
                    'value': f"{market_overview.get('total_tournament_players', 0):,}명",
                    'percentage': market_overview.get('player_distribution', {}).get('cash_vs_tournament_ratio', '').split(' : ')[1] if ' : ' in market_overview.get('player_distribution', {}).get('cash_vs_tournament_ratio', '') else '0%'
                }
            ]
        }
        
    def create_market_composition_chart(self, market_overview):
        """시장 구성 차트 데이터"""
        segmentation = market_overview.get('market_segmentation', {})
        
        return {
            'chart_type': 'donut_chart',
            'title': '사이트 규모별 시장 구성',
            'data': [
                {
                    'category': '대형 사이트 (1만명+)',
                    'count': segmentation.get('large_sites_count', 0),
                    'market_share': segmentation.get('large_sites_share', 0),
                    'color': '#FF6B6B'
                },
                {
                    'category': '중형 사이트 (1천-1만명)',
                    'count': segmentation.get('medium_sites_count', 0),
                    'market_share': segmentation.get('medium_sites_share', 0),
                    'color': '#4ECDC4'
                },
                {
                    'category': '소형 사이트 (1천명 미만)',
                    'count': segmentation.get('small_sites_count', 0) + segmentation.get('micro_sites_count', 0),
                    'market_share': 100 - segmentation.get('large_sites_share', 0) - segmentation.get('medium_sites_share', 0),
                    'color': '#45B7D1'
                }
            ]
        }
        
    def create_top_performers_grid(self, sites_analysis):
        """상위 성과자 그리드"""
        sites = sites_analysis.get('sites_analysis', [])[:12]  # 상위 12개
        
        grid_data = []
        for site in sites:
            grid_data.append({
                'rank': site['rank'],
                'name': site['name'],
                'players': site['metrics']['total_players'],
                'market_share': site['percentages']['market_share'],
                'growth_rate': site['percentages']['growth_rate'],
                'trend_indicator': self.get_trend_indicator(site['percentages']['growth_rate']),
                'size_category': site['classification']['size_category'],
                'notable_features': site['notable_features'][:2],  # 상위 2개 특징만
                'alert_level': self.get_alert_level(site['anomaly_flags'])
            })
            
        return {
            'grid_type': 'performance_grid',
            'title': 'TOP 12 포커 사이트 현황',
            'data': grid_data
        }
        
    def get_trend_indicator(self, growth_rate):
        """트렌드 지시자"""
        if growth_rate > 10:
            return {'icon': '📈', 'color': 'green', 'label': '상승'}
        elif growth_rate < -10:
            return {'icon': '📉', 'color': 'red', 'label': '하락'}
        else:
            return {'icon': '➡️', 'color': 'blue', 'label': '안정'}
            
    def get_alert_level(self, anomaly_flags):
        """알림 레벨 결정"""
        if not anomaly_flags:
            return 'normal'
        elif len(anomaly_flags) >= 2:
            return 'high'
        else:
            return 'medium'
            
    def create_anomaly_alerts_section(self, anomalies):
        """이상 징후 알림 섹션"""
        significant_changes = anomalies.get('significant_changes', [])
        
        alerts = []
        for change in significant_changes[:5]:  # 상위 5개
            alerts.append({
                'site': change['site'],
                'alert_type': change['change_type'],
                'severity': change['severity'],
                'change_value': f"{change['growth_rate']:+.1f}%",
                'current_players': change['current_players'],
                'impact_assessment': change['impact_assessment'],
                'alert_color': 'red' if change['severity'] == 'HIGH' else 'orange'
            })
            
        return {
            'section_type': 'alert_dashboard',
            'title': '🚨 중요 변화 감지',
            'alerts': alerts,
            'summary': f"{len(significant_changes)}개 사이트에서 중요한 변화 감지"
        }
        
    def create_trend_indicators(self, sites_analysis):
        """트렌드 지시자 생성"""
        stats = sites_analysis.get('statistics_summary', {})
        growth_stats = stats.get('growth_statistics', {})
        
        return {
            'section_type': 'trend_metrics',
            'title': '📊 시장 트렌드 지표',
            'metrics': [
                {
                    'label': '평균 성장률',
                    'value': f"{growth_stats.get('average_growth_rate', 0):+.1f}%",
                    'trend': 'positive' if growth_stats.get('average_growth_rate', 0) > 0 else 'negative'
                },
                {
                    'label': '성장 사이트 수',
                    'value': f"{growth_stats.get('positive_growth_sites', 0)}개",
                    'total': growth_stats.get('positive_growth_sites', 0) + growth_stats.get('negative_growth_sites', 0)
                },
                {
                    'label': '시장 변동성',
                    'value': f"{growth_stats.get('growth_rate_std', 0):.1f}%",
                    'level': 'high' if growth_stats.get('growth_rate_std', 0) > 20 else 'normal'
                }
            ]
        }
        
    def create_risk_dashboard(self, anomalies):
        """리스크 대시보드"""
        risk_factors = anomalies.get('risk_factors', [])
        
        return {
            'section_type': 'risk_assessment',
            'title': '⚠️ 리스크 평가',
            'risk_factors': risk_factors,
            'overall_risk_level': self.calculate_overall_risk_level(risk_factors),
            'recommendations': self.generate_risk_recommendations(risk_factors)
        }
        
    def calculate_overall_risk_level(self, risk_factors):
        """전체 리스크 레벨 계산"""
        if not risk_factors:
            return 'LOW'
            
        high_risks = len([r for r in risk_factors if r.get('level') == 'HIGH'])
        medium_risks = len([r for r in risk_factors if r.get('level') == 'MEDIUM'])
        
        if high_risks >= 2:
            return 'HIGH'
        elif high_risks >= 1 or medium_risks >= 3:
            return 'MEDIUM'
        else:
            return 'LOW'
            
    def generate_risk_recommendations(self, risk_factors):
        """리스크 권고사항 생성"""
        recommendations = []
        
        for risk in risk_factors:
            if risk.get('level') == 'HIGH':
                recommendations.append(f"즉시 모니터링 필요: {risk.get('description')}")
            elif risk.get('level') == 'MEDIUM':
                recommendations.append(f"주의 깊게 관찰: {risk.get('description')}")
                
        return recommendations[:3]  # 상위 3개 권고사항
        
    def create_news_impact_summary(self):
        """뉴스 영향 요약"""
        correlations = self.analyze_news_correlations()
        
        return {
            'section_type': 'news_impact',
            'title': '📰 뉴스 영향 분석',
            'direct_mentions_count': len(correlations.get('direct_mentions', [])),
            'indirect_correlations_count': len(correlations.get('indirect_correlations', [])),
            'regulatory_impact_count': len(correlations.get('regulatory_impact', [])),
            'tournament_effects_count': len(correlations.get('tournament_effects', [])),
            'key_insights': self.extract_key_news_insights(correlations)
        }
        
    def extract_key_news_insights(self, correlations):
        """주요 뉴스 인사이트 추출"""
        insights = []
        
        # 직접 언급이 있는 사이트
        direct_sites = set(mention['site'] for mention in correlations.get('direct_mentions', []))
        if direct_sites:
            insights.append(f"{len(direct_sites)}개 사이트가 뉴스에 직접 언급됨")
            
        # 토너먼트 효과
        tournament_count = len(correlations.get('tournament_effects', []))
        if tournament_count > 0:
            insights.append(f"{tournament_count}개 토너먼트 관련 뉴스 감지")
            
        # 규제 영향
        regulatory_count = len(correlations.get('regulatory_impact', []))
        if regulatory_count > 0:
            insights.append(f"{regulatory_count}개 규제 관련 뉴스 확인")
            
        return insights[:3]
        
    def generate_actionable_insights(self):
        """실행 가능한 인사이트 생성"""
        logger.info("  💡 실행 가능한 인사이트 생성...")
        
        market_overview = self.analyze_complete_market_overview()
        sites_analysis = self.analyze_all_active_sites()
        anomalies = self.detect_market_anomalies()
        
        insights = {
            'immediate_actions': [],
            'monitoring_priorities': [],
            'market_opportunities': [],
            'broadcast_talking_points': []
        }
        
        # 즉시 조치 사항
        significant_changes = anomalies.get('significant_changes', [])
        for change in significant_changes[:3]:
            if change['severity'] == 'HIGH':
                insights['immediate_actions'].append({
                    'priority': 'HIGH',
                    'action': f"{change['site']} 급변 원인 조사",
                    'description': f"{change['growth_rate']:+.1f}% 변화 원인 분석 필요"
                })
                
        # 모니터링 우선순위
        risk_factors = anomalies.get('risk_factors', [])
        for risk in risk_factors:
            insights['monitoring_priorities'].append({
                'priority': risk.get('level', 'MEDIUM'),
                'focus_area': risk.get('type'),
                'description': risk.get('description')
            })
            
        # 시장 기회
        growth_sites = [site for site in sites_analysis.get('sites_analysis', []) 
                       if site['percentages']['growth_rate'] > 15]
        for site in growth_sites[:3]:
            insights['market_opportunities'].append({
                'opportunity': f"{site['name']} 성장 모멘텀",
                'description': f"{site['percentages']['growth_rate']:+.1f}% 성장 중",
                'potential': '높음'
            })
            
        # 방송용 핵심 포인트
        insights['broadcast_talking_points'] = self.generate_broadcast_talking_points(
            market_overview, significant_changes
        )
        
        return insights
        
    def generate_broadcast_talking_points(self, market_overview, significant_changes):
        """방송용 핵심 포인트 생성"""
        talking_points = []
        
        # 시장 규모 포인트
        total_players = market_overview.get('total_market_size', 0)
        talking_points.append({
            'category': '시장 현황',
            'point': f"현재 전 세계 온라인 포커 시장에는 {total_players:,}명이 동시 접속 중",
            'visual_cue': '📊 전체 플레이어 수 그래프'
        })
        
        # 주요 변화 포인트
        if significant_changes:
            biggest_change = max(significant_changes, key=lambda x: abs(x['growth_rate']))
            talking_points.append({
                'category': '주요 변화',
                'point': f"{biggest_change['site']}에서 {biggest_change['growth_rate']:+.1f}% 급변 감지",
                'visual_cue': f"🚨 {biggest_change['site']} 변화 차트"
            })
            
        # 시장 집중도 포인트
        concentration = market_overview.get('market_concentration', {})
        top5_share = concentration.get('top5_market_share', 0)
        talking_points.append({
            'category': '시장 구조',
            'point': f"상위 5개 사이트가 전체 시장의 {top5_share:.1f}% 점유",
            'visual_cue': '🏆 시장 점유율 파이 차트'
        })
        
        return talking_points
        
    def generate_executive_summary(self, report_data):
        """경영진 요약 생성"""
        logger.info("  📋 경영진 요약 생성...")
        
        market_overview = report_data.get('market_overview', {})
        anomalies = report_data.get('anomaly_detection', {})
        
        return {
            'key_findings': [
                f"총 {market_overview.get('total_active_sites', 0)}개 활성 사이트에서 {market_overview.get('total_market_size', 0):,}명 동시 접속",
                f"{len(anomalies.get('significant_changes', []))}개 사이트에서 중요한 변화 감지",
                f"시장 집중도: {market_overview.get('market_concentration', {}).get('concentration_level', 'N/A')}"
            ],
            'critical_alerts': [change['site'] + ': ' + f"{change['growth_rate']:+.1f}%" 
                              for change in anomalies.get('significant_changes', [])[:3]],
            'market_health': self.assess_market_health(market_overview, anomalies),
            'recommended_actions': [insight['action'] for insight in 
                                  report_data.get('actionable_insights', {}).get('immediate_actions', [])[:3]]
        }
        
    def assess_market_health(self, market_overview, anomalies):
        """시장 건전성 평가"""
        health_factors = []
        
        # 시장 집중도 평가
        hhi = market_overview.get('market_concentration', {}).get('hhi_index', 0)
        if hhi < 1500:
            health_factors.append('경쟁적')
        elif hhi < 2500:
            health_factors.append('보통 집중')
        else:
            health_factors.append('고도 집중')
            
        # 변화 안정성 평가
        significant_changes = len(anomalies.get('significant_changes', []))
        if significant_changes < 3:
            health_factors.append('안정적')
        elif significant_changes < 6:
            health_factors.append('변동적')
        else:
            health_factors.append('불안정')
            
        return ' + '.join(health_factors)
        
    def save_infographic_report(self, report_data):
        """인포그래픽 리포트 저장"""
        logger.info("💾 인포그래픽 리포트 저장...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON 상세 리포트
        json_filename = f'infographic_report_{timestamp}.json'
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        # 방송용 요약 리포트
        summary_filename = f'broadcast_summary_{timestamp}.txt'
        self.save_broadcast_summary(report_data, summary_filename)
        
        # 인포그래픽 데이터 파일
        infographic_filename = f'infographic_data_{timestamp}.json'
        self.save_infographic_data(report_data, infographic_filename)
        
        logger.info(f"📊 상세 분석: {json_filename}")
        logger.info(f"📺 방송 요약: {summary_filename}")
        logger.info(f"🎨 인포그래픽 데이터: {infographic_filename}")
        
        return json_filename, summary_filename, infographic_filename
        
    def save_broadcast_summary(self, report_data, filename):
        """방송용 요약 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("📺 온라인 포커 시장 인포그래픽 브리핑\n")
            f.write(f"생성 시간: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}\n")
            f.write("=" * 80 + "\n\n")
            
            # 경영진 요약
            executive = report_data.get('executive_summary', {})
            f.write("🎯 핵심 요약\n")
            f.write("-" * 40 + "\n")
            for finding in executive.get('key_findings', []):
                f.write(f"  • {finding}\n")
            f.write(f"\n시장 건전성: {executive.get('market_health', 'N/A')}\n\n")
            
            # 중요 알림
            if executive.get('critical_alerts'):
                f.write("🚨 긴급 알림\n")
                f.write("-" * 40 + "\n")
                for alert in executive.get('critical_alerts', []):
                    f.write(f"  ⚠️ {alert}\n")
                f.write("\n")
                
            # 방송용 핵심 포인트
            talking_points = report_data.get('actionable_insights', {}).get('broadcast_talking_points', [])
            f.write("📺 방송 핵심 포인트\n")
            f.write("-" * 40 + "\n")
            for point in talking_points:
                f.write(f"  {point['category']}: {point['point']}\n")
                f.write(f"     시각 자료: {point['visual_cue']}\n\n")
                
            # 권장 조치
            if executive.get('recommended_actions'):
                f.write("💡 권장 조치사항\n")
                f.write("-" * 40 + "\n")
                for action in executive.get('recommended_actions', []):
                    f.write(f"  • {action}\n")
                    
    def save_infographic_data(self, report_data, filename):
        """인포그래픽 데이터 저장"""
        infographic_data = {
            'metadata': report_data.get('report_metadata', {}),
            'sections': report_data.get('infographic_sections', {}),
            'data_points': self.extract_key_data_points(report_data)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(infographic_data, f, indent=2, ensure_ascii=False)
            
    def extract_key_data_points(self, report_data):
        """주요 데이터 포인트 추출"""
        market_overview = report_data.get('market_overview', {})
        anomalies = report_data.get('anomaly_detection', {})
        
        return {
            'total_players': market_overview.get('total_market_size', 0),
            'active_sites': market_overview.get('total_active_sites', 0),
            'significant_changes': len(anomalies.get('significant_changes', [])),
            'market_concentration': market_overview.get('market_concentration', {}).get('hhi_index', 0),
            'top3_share': market_overview.get('market_concentration', {}).get('top3_market_share', 0)
        }

def main():
    """메인 실행 함수"""
    print("🎨 고급 인포그래픽 포커 시장 분석 리포트 생성기")
    print("=" * 70)
    
    generator = AdvancedInfographicReportGenerator()
    
    try:
        # 종합 인포그래픽 리포트 생성
        print("\n🔄 종합 분석 중...")
        report_data = generator.generate_comprehensive_infographic_report()
        
        # 결과 미리보기
        print("\n📊 분석 결과 미리보기:")
        executive = report_data.get('executive_summary', {})
        
        print("핵심 발견사항:")
        for finding in executive.get('key_findings', [])[:3]:
            print(f"  • {finding}")
            
        critical_alerts = executive.get('critical_alerts', [])
        if critical_alerts:
            print(f"\n🚨 긴급 알림: {len(critical_alerts)}건")
            for alert in critical_alerts[:2]:
                print(f"  ⚠️ {alert}")
                
        print(f"\n시장 건전성: {executive.get('market_health', 'N/A')}")
        
        # 뉴스 연관성
        correlations = report_data.get('news_correlation', {})
        direct_mentions = len(correlations.get('direct_mentions', []))
        if direct_mentions > 0:
            print(f"뉴스 연관성: {direct_mentions}개 사이트 직접 언급 발견")
            
        # 리포트 저장
        print("\n💾 리포트 저장 중...")
        json_file, summary_file, infographic_file = generator.save_infographic_report(report_data)
        
        print(f"\n✅ 고급 인포그래픽 리포트 생성 완료!")
        print(f"📊 상세 분석: {json_file}")
        print(f"📺 방송 요약: {summary_file}")
        print(f"🎨 인포그래픽 데이터: {infographic_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"리포트 생성 오류: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🚀 인포그래픽 리포트 완료! 모든 활성 사이트 수치 분석 및 뉴스 연관성 완료")
    else:
        print(f"\n💀 리포트 생성 실패 - 문제 해결 필요")
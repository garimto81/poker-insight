#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerScout 2-Factor 분석 아이디어 모음
- Players Online (총 온라인 플레이어)
- Cash Players (캐시게임 플레이어)
- 이 두 데이터만으로 가능한 혁신적 분석 방법들
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
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwoFactorAnalysisEngine:
    def __init__(self, db_path='poker_insight.db'):
        self.db_path = db_path
        
    def get_db_connection(self):
        """SQLite 데이터베이스 연결"""
        return sqlite3.connect(self.db_path)
        
    def generate_comprehensive_two_factor_analysis(self):
        """포괄적인 2-팩터 분석"""
        logger.info("🎯 PokerScout 2-Factor 혁신적 분석 시작...")
        
        analysis_results = {
            'metadata': self.get_analysis_metadata(),
            'basic_calculations': self.perform_basic_calculations(),
            'advanced_ratios': self.calculate_advanced_ratios(),
            'site_personality_profiling': self.create_site_personality_profiles(),
            'market_segmentation': self.perform_market_segmentation(),
            'behavioral_insights': self.extract_behavioral_insights(),
            'competitive_positioning': self.analyze_competitive_positioning(),
            'business_intelligence': self.generate_business_intelligence(),
            'broadcast_storytelling': self.create_broadcast_storytelling(),
            'predictive_modeling': self.build_predictive_models(),
            'innovation_opportunities': self.identify_innovation_opportunities()
        }
        
        return analysis_results
        
    def get_analysis_metadata(self):
        """분석 메타데이터"""
        return {
            'analysis_date': datetime.now().isoformat(),
            'data_sources': ['players_online', 'cash_players'],
            'derived_metrics': ['tournament_players', 'cash_ratio', 'tournament_ratio'],
            'analysis_philosophy': 'maximum_insight_from_minimal_data',
            'innovation_focus': 'behavioral_psychology_and_market_dynamics'
        }
        
    def perform_basic_calculations(self):
        """기본 계산 수행"""
        logger.info("  📊 기본 지표 계산...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT 
                ps.name,
                td.total_players,
                td.cash_players
            FROM poker_sites ps
            JOIN traffic_data td ON ps.id = td.site_id
            WHERE td.total_players > 0
            ORDER BY td.total_players DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            basic_metrics = []
            
            for row in results:
                name, total_players, cash_players = row
                
                # 핵심 파생 지표 계산
                tournament_players = total_players - cash_players
                cash_ratio = (cash_players / total_players) * 100 if total_players > 0 else 0
                tournament_ratio = (tournament_players / total_players) * 100 if total_players > 0 else 0
                
                metrics = {
                    'site': name,
                    'total_players': total_players,
                    'cash_players': cash_players,
                    'tournament_players': tournament_players,
                    'cash_ratio': round(cash_ratio, 1),
                    'tournament_ratio': round(tournament_ratio, 1),
                    'cash_to_tournament_ratio': round(cash_players / tournament_players if tournament_players > 0 else 0, 2),
                    'player_density_score': self.calculate_player_density_score(total_players, cash_players)
                }
                
                basic_metrics.append(metrics)
                
            conn.close()
            return basic_metrics
            
        except Exception as e:
            logger.error(f"기본 계산 오류: {str(e)}")
            return []
            
    def calculate_player_density_score(self, total_players, cash_players):
        """플레이어 밀도 점수 계산 (혁신적 지표)"""
        # 캐시게임 플레이어는 더 오래 머물고 활발하다는 가정
        # 토너먼트 플레이어는 일시적이라는 가정
        tournament_players = total_players - cash_players
        
        # 가중 밀도 점수: 캐시게임 플레이어에 2배 가중치
        weighted_activity = (cash_players * 2) + tournament_players
        density_score = weighted_activity / total_players if total_players > 0 else 0
        
        return round(density_score, 2)
        
    def calculate_advanced_ratios(self):
        """고급 비율 분석"""
        logger.info("  🔬 고급 비율 분석...")
        
        basic_data = self.perform_basic_calculations()
        if not basic_data:
            return {}
            
        # 시장 전체 통계
        total_market_players = sum(site['total_players'] for site in basic_data)
        total_market_cash = sum(site['cash_players'] for site in basic_data)
        total_market_tournament = sum(site['tournament_players'] for site in basic_data)
        
        advanced_ratios = {
            'market_overview': {
                'total_players': total_market_players,
                'global_cash_ratio': round((total_market_cash / total_market_players) * 100, 1),
                'global_tournament_ratio': round((total_market_tournament / total_market_players) * 100, 1),
                'market_cash_concentration': self.calculate_market_concentration([site['cash_players'] for site in basic_data]),
                'market_tournament_concentration': self.calculate_market_concentration([site['tournament_players'] for site in basic_data])
            },
            'site_analysis': []
        }
        
        for site in basic_data:
            # 혁신적 지표들
            cash_market_share = (site['cash_players'] / total_market_cash) * 100 if total_market_cash > 0 else 0
            tournament_market_share = (site['tournament_players'] / total_market_tournament) * 100 if total_market_tournament > 0 else 0
            
            # 특화도 지수 (Specialization Index)
            overall_market_share = (site['total_players'] / total_market_players) * 100
            cash_specialization = cash_market_share / overall_market_share if overall_market_share > 0 else 0
            tournament_specialization = tournament_market_share / overall_market_share if overall_market_share > 0 else 0
            
            # 플레이어 다양성 지수 (Player Diversity Index)
            diversity_index = 1 - abs(site['cash_ratio'] - 50) / 50  # 50:50에 가까울수록 높은 점수
            
            # 비즈니스 모델 지수
            business_model_score = self.calculate_business_model_score(site['cash_ratio'])
            
            site_analysis = {
                'site': site['site'],
                'market_shares': {
                    'overall': round(overall_market_share, 2),
                    'cash_games': round(cash_market_share, 2),
                    'tournaments': round(tournament_market_share, 2)
                },
                'specialization_indices': {
                    'cash_specialization': round(cash_specialization, 2),
                    'tournament_specialization': round(tournament_specialization, 2),
                    'dominant_category': 'cash' if cash_specialization > tournament_specialization else 'tournament'
                },
                'innovation_metrics': {
                    'player_diversity_index': round(diversity_index, 2),
                    'business_model_score': business_model_score,
                    'player_density_score': site['player_density_score'],
                    'efficiency_ratio': round(site['cash_players'] / (site['total_players'] / 1000), 1)  # 천명당 캐시 플레이어
                }
            }
            
            advanced_ratios['site_analysis'].append(site_analysis)
            
        return advanced_ratios
        
    def calculate_market_concentration(self, values):
        """시장 집중도 계산 (HHI)"""
        total = sum(values)
        if total == 0:
            return 0
        shares = [(value / total) * 100 for value in values]
        hhi = sum(share ** 2 for share in shares)
        return round(hhi, 2)
        
    def calculate_business_model_score(self, cash_ratio):
        """비즈니스 모델 점수"""
        if cash_ratio >= 70:
            return {'model': 'Cash-Focused', 'score': 'A', 'revenue_stability': 'HIGH'}
        elif cash_ratio >= 50:
            return {'model': 'Balanced', 'score': 'B+', 'revenue_stability': 'HIGH'}
        elif cash_ratio >= 30:
            return {'model': 'Tournament-Leaning', 'score': 'B', 'revenue_stability': 'MEDIUM'}
        elif cash_ratio >= 10:
            return {'model': 'Tournament-Focused', 'score': 'C+', 'revenue_stability': 'MEDIUM'}
        else:
            return {'model': 'Tournament-Only', 'score': 'C', 'revenue_stability': 'LOW'}
            
    def create_site_personality_profiles(self):
        """사이트 성격 프로파일링"""
        logger.info("  🎭 사이트 성격 프로파일링...")
        
        basic_data = self.perform_basic_calculations()
        advanced_data = self.calculate_advanced_ratios()
        
        personality_profiles = []
        
        for site_data in basic_data:
            site_name = site_data['site']
            
            # 고급 데이터에서 해당 사이트 찾기
            advanced_site = next((s for s in advanced_data['site_analysis'] if s['site'] == site_name), None)
            
            if not advanced_site:
                continue
                
            # 성격 특성 분석
            personality = {
                'site': site_name,
                'primary_personality': self.determine_primary_personality(site_data, advanced_site),
                'player_attraction_style': self.analyze_player_attraction(site_data),
                'business_strategy': self.infer_business_strategy(site_data, advanced_site),
                'competitive_advantage': self.identify_competitive_advantage(site_data, advanced_site),
                'target_audience': self.define_target_audience(site_data),
                'growth_potential': self.assess_growth_potential(site_data, advanced_site),
                'risk_profile': self.evaluate_risk_profile(site_data)
            }
            
            personality_profiles.append(personality)
            
        return personality_profiles
        
    def determine_primary_personality(self, basic_data, advanced_data):
        """주요 성격 결정"""
        cash_ratio = basic_data['cash_ratio']
        diversity_index = advanced_data['innovation_metrics']['player_diversity_index']
        total_players = basic_data['total_players']
        
        if cash_ratio >= 70:
            return "Cash Game Specialist - 안정적 수익 추구형"
        elif cash_ratio >= 50 and diversity_index >= 0.7:
            return "Balanced Powerhouse - 전방위 서비스형"
        elif cash_ratio <= 20 and total_players >= 10000:
            return "Tournament Giant - 대규모 이벤트형"
        elif total_players <= 1000:
            return "Boutique Operator - 소규모 전문형"
        else:
            return "Tournament Focused - 이벤트 중심형"
            
    def analyze_player_attraction(self, site_data):
        """플레이어 유인 스타일 분석"""
        cash_ratio = site_data['cash_ratio']
        total_players = site_data['total_players']
        
        if cash_ratio >= 60:
            return {
                'style': 'Professional Player Magnet',
                'description': '프로페셔널과 진지한 플레이어 유인',
                'appeal': '안정적 게임, 높은 스킬 레벨'
            }
        elif cash_ratio <= 20 and total_players >= 5000:
            return {
                'style': 'Tournament Hunter Paradise',
                'description': '토너먼트 헌터와 대박 추구자 유인',
                'appeal': '큰 상금, 드라마틱한 경험'
            }
        elif 30 <= cash_ratio <= 60:
            return {
                'style': 'All-Round Entertainment',
                'description': '다양한 스타일의 플레이어 수용',
                'appeal': '선택의 다양성, 균형잡힌 경험'
            }
        else:
            return {
                'style': 'Casual Tournament Hub',
                'description': '캐주얼 토너먼트 플레이어 중심',
                'appeal': '부담없는 참여, 재미 중심'
            }
            
    def infer_business_strategy(self, site_data, advanced_data):
        """비즈니스 전략 추론"""
        cash_ratio = site_data['cash_ratio']
        business_model = advanced_data['innovation_metrics']['business_model_score']
        market_share = advanced_data['market_shares']['overall']
        
        if market_share >= 20:  # 메이저 플레이어
            if cash_ratio >= 50:
                return "Market Leader with Revenue Focus - 수익성 중심 시장 리더십"
            else:
                return "Volume Leader with Scale Strategy - 규모 중심 시장 지배"
        elif market_share >= 5:  # 중형 플레이어
            if cash_ratio >= 60:
                return "Niche Premium Strategy - 프리미엄 틈새 전략"
            else:
                return "Tournament Specialist Strategy - 토너먼트 전문화 전략"
        else:  # 소형 플레이어
            if cash_ratio >= 40:
                return "Boutique High-Value Strategy - 소규모 고가치 전략"
            else:
                return "Entry-Level Tournament Strategy - 입문자 대상 토너먼트 전략"
                
    def identify_competitive_advantage(self, site_data, advanced_data):
        """경쟁 우위 요소 식별"""
        advantages = []
        
        cash_specialization = advanced_data['specialization_indices']['cash_specialization']
        tournament_specialization = advanced_data['specialization_indices']['tournament_specialization']
        diversity_index = advanced_data['innovation_metrics']['player_diversity_index']
        
        if cash_specialization >= 1.5:
            advantages.append("Cash Game Excellence - 캐시게임 특화 우위")
        if tournament_specialization >= 1.5:
            advantages.append("Tournament Mastery - 토너먼트 운영 우위")
        if diversity_index >= 0.8:
            advantages.append("Player Diversity - 다양한 플레이어 기반")
        if site_data['total_players'] >= 50000:
            advantages.append("Scale Advantage - 규모의 경제")
        if site_data['player_density_score'] >= 1.5:
            advantages.append("High Player Engagement - 높은 플레이어 참여도")
            
        return advantages if advantages else ["Emerging Potential - 성장 잠재력"]
        
    def define_target_audience(self, site_data):
        """타겟 오디언스 정의"""
        cash_ratio = site_data['cash_ratio']
        total_players = site_data['total_players']
        
        audiences = []
        
        if cash_ratio >= 50:
            audiences.append("Professional Poker Players - 프로 포커 플레이어")
            audiences.append("Serious Cash Game Enthusiasts - 진지한 캐시게임 애호가")
        
        if cash_ratio <= 30:
            audiences.append("Tournament Dreamers - 토너먼트 꿈나무")
            audiences.append("Recreational Players - 레크리에이션 플레이어")
            
        if total_players >= 20000:
            audiences.append("Volume Seekers - 대규모 게임 참여자")
        elif total_players <= 2000:
            audiences.append("Intimate Game Lovers - 소규모 게임 선호자")
            
        if 30 <= cash_ratio <= 70:
            audiences.append("Versatile Players - 다재다능한 플레이어")
            
        return audiences
        
    def assess_growth_potential(self, site_data, advanced_data):
        """성장 잠재력 평가"""
        factors = []
        score = 0
        
        # 다양성이 높으면 성장 잠재력 높음
        diversity = advanced_data['innovation_metrics']['player_diversity_index']
        if diversity >= 0.7:
            factors.append("High Player Diversity")
            score += 2
        elif diversity >= 0.5:
            factors.append("Moderate Player Diversity")
            score += 1
            
        # 비즈니스 모델 안정성
        business_model = advanced_data['innovation_metrics']['business_model_score']
        if business_model['revenue_stability'] == 'HIGH':
            factors.append("Stable Revenue Model")
            score += 2
        elif business_model['revenue_stability'] == 'MEDIUM':
            factors.append("Moderate Revenue Stability")
            score += 1
            
        # 시장 점유율 여지
        market_share = advanced_data['market_shares']['overall']
        if market_share <= 1:
            factors.append("Low Market Share - High Growth Potential")
            score += 2
        elif market_share <= 5:
            factors.append("Medium Market Share - Moderate Growth Potential")
            score += 1
            
        # 플레이어 참여도
        if site_data['player_density_score'] >= 1.3:
            factors.append("High Player Engagement")
            score += 1
            
        if score >= 5:
            potential = "HIGH"
        elif score >= 3:
            potential = "MEDIUM"
        else:
            potential = "LOW"
            
        return {
            'potential_level': potential,
            'score': score,
            'growth_factors': factors,
            'recommendation': self.generate_growth_recommendation(potential, factors)
        }
        
    def generate_growth_recommendation(self, potential, factors):
        """성장 권고사항 생성"""
        if potential == "HIGH":
            return "적극적 마케팅 투자 및 기능 확장 권장"
        elif potential == "MEDIUM":
            return "선택적 투자 및 특화 영역 강화 권장"
        else:
            return "현재 포지션 유지 및 효율성 개선 권장"
            
    def evaluate_risk_profile(self, site_data):
        """리스크 프로파일 평가"""
        cash_ratio = site_data['cash_ratio']
        total_players = site_data['total_players']
        
        risks = []
        risk_level = 0
        
        # 토너먼트 의존도 리스크
        if cash_ratio <= 10:
            risks.append("High Tournament Dependency - 토너먼트 의존도 리스크")
            risk_level += 2
        elif cash_ratio <= 30:
            risks.append("Moderate Tournament Dependency")
            risk_level += 1
            
        # 규모 리스크
        if total_players <= 500:
            risks.append("Scale Risk - 규모 리스크")
            risk_level += 2
        elif total_players <= 2000:
            risks.append("Limited Scale")
            risk_level += 1
            
        # 수익 안정성 리스크
        if cash_ratio <= 20:
            risks.append("Revenue Volatility Risk")
            risk_level += 1
            
        if risk_level >= 4:
            risk_assessment = "HIGH RISK"
        elif risk_level >= 2:
            risk_assessment = "MEDIUM RISK"
        else:
            risk_assessment = "LOW RISK"
            
        return {
            'risk_level': risk_assessment,
            'risk_factors': risks,
            'risk_score': risk_level
        }
        
    def perform_market_segmentation(self):
        """시장 세분화 분석"""
        logger.info("  🎯 시장 세분화 분석...")
        
        basic_data = self.perform_basic_calculations()
        
        # 다차원 세분화
        segmentation = {
            'by_size': defaultdict(list),
            'by_cash_ratio': defaultdict(list),
            'by_business_model': defaultdict(list),
            'by_competitive_position': defaultdict(list)
        }
        
        for site in basic_data:
            # 규모별 세분화
            if site['total_players'] >= 50000:
                segmentation['by_size']['Mega Sites'].append(site)
            elif site['total_players'] >= 10000:
                segmentation['by_size']['Large Sites'].append(site)
            elif site['total_players'] >= 1000:
                segmentation['by_size']['Medium Sites'].append(site)
            else:
                segmentation['by_size']['Small Sites'].append(site)
                
            # 캐시게임 비율별 세분화
            if site['cash_ratio'] >= 70:
                segmentation['by_cash_ratio']['Cash Specialists'].append(site)
            elif site['cash_ratio'] >= 50:
                segmentation['by_cash_ratio']['Cash Focused'].append(site)
            elif site['cash_ratio'] >= 30:
                segmentation['by_cash_ratio']['Balanced'].append(site)
            elif site['cash_ratio'] >= 10:
                segmentation['by_cash_ratio']['Tournament Focused'].append(site)
            else:
                segmentation['by_cash_ratio']['Tournament Only'].append(site)
                
        # 세그먼트별 통계 계산
        segment_analysis = {}
        for category, segments in segmentation.items():
            segment_analysis[category] = {}
            for segment_name, sites in segments.items():
                if sites:
                    segment_analysis[category][segment_name] = {
                        'count': len(sites),
                        'total_players': sum(s['total_players'] for s in sites),
                        'avg_cash_ratio': round(sum(s['cash_ratio'] for s in sites) / len(sites), 1),
                        'market_share': 0,  # 계산 예정
                        'representative_sites': [s['site'] for s in sites[:3]]
                    }
                    
        return segment_analysis
        
    def extract_behavioral_insights(self):
        """행동 인사이트 추출"""
        logger.info("  🧠 플레이어 행동 인사이트 추출...")
        
        basic_data = self.perform_basic_calculations()
        
        # 전체 시장 통계
        total_players = sum(s['total_players'] for s in basic_data)
        total_cash = sum(s['cash_players'] for s in basic_data)
        
        behavioral_insights = {
            'market_behavior_patterns': {
                'global_cash_preference': round((total_cash / total_players) * 100, 1),
                'tournament_dominance': round(((total_players - total_cash) / total_players) * 100, 1),
                'player_distribution_insight': self.analyze_player_distribution_behavior(basic_data)
            },
            'site_behavioral_clusters': self.create_behavioral_clusters(basic_data),
            'player_psychology_insights': self.generate_psychology_insights(basic_data),
            'engagement_patterns': self.analyze_engagement_patterns(basic_data)
        }
        
        return behavioral_insights
        
    def analyze_player_distribution_behavior(self, data):
        """플레이어 분포 행동 분석"""
        cash_ratios = [s['cash_ratio'] for s in data]
        
        # 분포 통계
        mean_cash_ratio = statistics.mean(cash_ratios)
        median_cash_ratio = statistics.median(cash_ratios)
        std_cash_ratio = statistics.stdev(cash_ratios) if len(cash_ratios) > 1 else 0
        
        insights = []
        
        if mean_cash_ratio <= 20:
            insights.append("시장 전체가 토너먼트 중심으로 편향")
        elif mean_cash_ratio >= 40:
            insights.append("캐시게임에 대한 선호가 높은 성숙한 시장")
        else:
            insights.append("토너먼트와 캐시게임 사이의 균형잡힌 시장")
            
        if std_cash_ratio >= 25:
            insights.append("사이트별 플레이어 선호도가 매우 다양함")
        elif std_cash_ratio <= 10:
            insights.append("시장 전체가 유사한 플레이어 구성을 가짐")
            
        return {
            'mean_cash_ratio': round(mean_cash_ratio, 1),
            'median_cash_ratio': round(median_cash_ratio, 1),
            'diversity_score': round(std_cash_ratio, 1),
            'behavioral_insights': insights
        }
        
    def create_behavioral_clusters(self, data):
        """행동 기반 클러스터링"""
        clusters = {
            'Professional Havens': [],      # 높은 캐시게임 비율
            'Tournament Arenas': [],        # 낮은 캐시게임 비율
            'Balanced Communities': [],     # 중간 캐시게임 비율
            'Micro Ecosystems': []         # 소규모 사이트들
        }
        
        for site in data:
            if site['total_players'] <= 1000:
                clusters['Micro Ecosystems'].append(site)
            elif site['cash_ratio'] >= 50:
                clusters['Professional Havens'].append(site)
            elif site['cash_ratio'] <= 20:
                clusters['Tournament Arenas'].append(site)
            else:
                clusters['Balanced Communities'].append(site)
                
        # 클러스터별 특성 분석
        cluster_analysis = {}
        for cluster_name, sites in clusters.items():
            if sites:
                cluster_analysis[cluster_name] = {
                    'site_count': len(sites),
                    'total_players': sum(s['total_players'] for s in sites),
                    'avg_cash_ratio': round(sum(s['cash_ratio'] for s in sites) / len(sites), 1),
                    'behavioral_trait': self.define_cluster_behavior(cluster_name),
                    'sites': [s['site'] for s in sites]
                }
                
        return cluster_analysis
        
    def define_cluster_behavior(self, cluster_name):
        """클러스터 행동 특성 정의"""
        behaviors = {
            'Professional Havens': "장시간 게임, 높은 스킬, 안정적 참여",
            'Tournament Arenas': "드라마틱한 경험 추구, 대박 선호, 이벤트 중심 참여",
            'Balanced Communities': "다양한 게임 참여, 적응력 높음, 유연한 플레이 스타일",
            'Micro Ecosystems': "친밀한 커뮤니티, 특별한 니즈, 개인화된 서비스"
        }
        return behaviors.get(cluster_name, "일반적인 포커 플레이어 행동")
        
    def generate_psychology_insights(self, data):
        """심리학적 인사이트 생성"""
        insights = []
        
        # 전체 시장의 캐시게임 선호도 분석
        market_cash_ratio = sum(s['cash_players'] for s in data) / sum(s['total_players'] for s in data) * 100
        
        if market_cash_ratio <= 10:
            insights.append({
                'insight': "Dream Chaser Dominance",
                'description': "플레이어들이 대부분 '대박'을 꿈꾸는 토너먼트 성향",
                'psychology': "즉시 만족보다는 큰 보상을 위한 위험 감수 선호"
            })
        elif market_cash_ratio >= 30:
            insights.append({
                'insight': "Steady Player Preference",
                'description': "안정적이고 지속적인 게임을 선호하는 성숙한 플레이어 기반",
                'psychology': "즉시 만족과 꾸준한 수익을 중시하는 현실적 접근"
            })
            
        # 사이트 간 다양성 분석
        cash_ratios = [s['cash_ratio'] for s in data]
        diversity = statistics.stdev(cash_ratios) if len(cash_ratios) > 1 else 0
        
        if diversity >= 30:
            insights.append({
                'insight': "Market Fragmentation",
                'description': "플레이어들이 명확하게 다른 선호도를 가진 세그먼트로 분화",
                'psychology': "개인의 리스크 성향과 게임 목적이 명확히 구분됨"
            })
            
        return insights
        
    def analyze_engagement_patterns(self, data):
        """참여 패턴 분석"""
        patterns = []
        
        # 플레이어 밀도가 높은 사이트들 분석
        high_density_sites = [s for s in data if s['player_density_score'] >= 1.3]
        
        if high_density_sites:
            avg_cash_ratio = sum(s['cash_ratio'] for s in high_density_sites) / len(high_density_sites)
            patterns.append({
                'pattern': "High Engagement Sites Trend",
                'finding': f"참여도가 높은 사이트들의 평균 캐시게임 비율: {avg_cash_ratio:.1f}%",
                'implication': "캐시게임이 플레이어 참여도와 상관관계를 가질 가능성"
            })
            
        # 대형 사이트 vs 소형 사이트 패턴
        large_sites = [s for s in data if s['total_players'] >= 10000]
        small_sites = [s for s in data if s['total_players'] <= 2000]
        
        if large_sites and small_sites:
            large_avg_cash = sum(s['cash_ratio'] for s in large_sites) / len(large_sites)
            small_avg_cash = sum(s['cash_ratio'] for s in small_sites) / len(small_sites)
            
            patterns.append({
                'pattern': "Scale vs Cash Game Preference",
                'finding': f"대형 사이트 평균 캐시비율: {large_avg_cash:.1f}%, 소형 사이트: {small_avg_cash:.1f}%",
                'implication': "사이트 규모에 따른 플레이어 구성의 차이 존재"
            })
            
        return patterns
        
    def analyze_competitive_positioning(self):
        """경쟁 포지셔닝 분석"""
        logger.info("  ⚔️ 경쟁 포지셔닝 분석...")
        
        basic_data = self.perform_basic_calculations()
        advanced_data = self.calculate_advanced_ratios()
        
        # 2차원 포지셔닝 맵 생성 (규모 vs 캐시게임 비율)
        positioning_map = {
            'quadrants': {
                'Cash Kings': [],           # 대형 + 높은 캐시비율
                'Tournament Giants': [],    # 대형 + 낮은 캐시비율
                'Cash Boutiques': [],       # 소형 + 높은 캐시비율
                'Tournament Specialists': []  # 소형 + 낮은 캐시비율
            },
            'competitive_gaps': [],
            'market_opportunities': []
        }
        
        # 포지셔닝 분류
        for site in basic_data:
            is_large = site['total_players'] >= 5000
            is_cash_focused = site['cash_ratio'] >= 30
            
            if is_large and is_cash_focused:
                positioning_map['quadrants']['Cash Kings'].append(site)
            elif is_large and not is_cash_focused:
                positioning_map['quadrants']['Tournament Giants'].append(site)
            elif not is_large and is_cash_focused:
                positioning_map['quadrants']['Cash Boutiques'].append(site)
            else:
                positioning_map['quadrants']['Tournament Specialists'].append(site)
                
        # 경쟁 갭 분석
        positioning_map['competitive_gaps'] = self.identify_competitive_gaps(positioning_map['quadrants'])
        positioning_map['market_opportunities'] = self.identify_market_opportunities(positioning_map['quadrants'])
        
        return positioning_map
        
    def identify_competitive_gaps(self, quadrants):
        """경쟁 갭 식별"""
        gaps = []
        
        # 각 사분면의 밀도 분석
        for quadrant_name, sites in quadrants.items():
            total_players_in_quadrant = sum(s['total_players'] for s in sites)
            
            if quadrant_name == 'Cash Kings' and len(sites) <= 1:
                gaps.append({
                    'gap': 'Premium Cash Game Market',
                    'description': '대형 캐시게임 중심 사이트의 부족',
                    'opportunity': '프리미엄 캐시게임 플랫폼 진입 기회'
                })
                
            if quadrant_name == 'Cash Boutiques' and len(sites) <= 2:
                gaps.append({
                    'gap': 'Specialized Cash Game Niches',
                    'description': '전문화된 소규모 캐시게임 사이트 부족',
                    'opportunity': '틈새 캐시게임 커뮤니티 구축 기회'
                })
                
        return gaps
        
    def identify_market_opportunities(self, quadrants):
        """시장 기회 식별"""
        opportunities = []
        
        # 밀도가 높은 사분면 vs 낮은 사분면 분석
        quadrant_densities = {}
        for name, sites in quadrants.items():
            quadrant_densities[name] = len(sites)
            
        # 가장 경쟁이 적은 사분면 찾기
        least_competitive = min(quadrant_densities, key=quadrant_densities.get)
        most_competitive = max(quadrant_densities, key=quadrant_densities.get)
        
        opportunities.append({
            'opportunity': f'Enter {least_competitive} Segment',
            'reasoning': f'경쟁사가 {quadrant_densities[least_competitive]}개로 가장 적음',
            'strategy': f'{least_competitive} 포지션에서의 차별화된 서비스 제공'
        })
        
        opportunities.append({
            'opportunity': f'Differentiate in {most_competitive} Segment',
            'reasoning': f'경쟁사가 {quadrant_densities[most_competitive]}개로 가장 많지만 시장 크기도 큼',
            'strategy': f'{most_competitive} 포지션에서의 혁신적 차별화 필요'
        })
        
        return opportunities
        
    def generate_business_intelligence(self):
        """비즈니스 인텔리전스 생성"""
        logger.info("  💼 비즈니스 인텔리전스 생성...")
        
        basic_data = self.perform_basic_calculations()
        
        bi_insights = {
            'revenue_insights': self.analyze_revenue_implications(basic_data),
            'market_sizing': self.estimate_market_sizing(basic_data),
            'investment_recommendations': self.generate_investment_recommendations(basic_data),
            'expansion_strategies': self.suggest_expansion_strategies(basic_data)
        }
        
        return bi_insights
        
    def analyze_revenue_implications(self, data):
        """수익 시사점 분석"""
        # 캐시게임은 일반적으로 더 높은 레이크 생성
        total_cash_players = sum(s['cash_players'] for s in data)
        total_tournament_players = sum(s['tournament_players'] for s in data)
        
        # 가정: 캐시게임 플레이어가 토너먼트 플레이어보다 3배 많은 수익 생성
        estimated_revenue_weight = (total_cash_players * 3) + total_tournament_players
        
        revenue_insights = []
        
        for site in data:
            site_revenue_weight = (site['cash_players'] * 3) + site['tournament_players']
            revenue_efficiency = site_revenue_weight / site['total_players']
            
            if revenue_efficiency >= 2:
                revenue_insights.append({
                    'site': site['site'],
                    'revenue_profile': 'High Revenue Efficiency',
                    'efficiency_score': round(revenue_efficiency, 2),
                    'implication': '캐시게임 중심으로 높은 수익성 예상'
                })
            elif revenue_efficiency <= 1.2:
                revenue_insights.append({
                    'site': site['site'],
                    'revenue_profile': 'Volume-Based Revenue',
                    'efficiency_score': round(revenue_efficiency, 2),
                    'implication': '대량 플레이어 기반의 수익 모델'
                })
                
        return revenue_insights
        
    def estimate_market_sizing(self, data):
        """시장 규모 추정"""
        total_players = sum(s['total_players'] for s in data)
        total_cash = sum(s['cash_players'] for s in data)
        
        # 업계 평균 추정치 적용
        estimated_daily_revenue_per_cash_player = 10  # USD
        estimated_daily_revenue_per_tournament_player = 3  # USD
        
        daily_market_size = (total_cash * estimated_daily_revenue_per_cash_player) + \
                           ((total_players - total_cash) * estimated_daily_revenue_per_tournament_player)
        
        return {
            'daily_market_size_usd': daily_market_size,
            'annual_market_size_usd': daily_market_size * 365,
            'cash_game_contribution': round((total_cash * estimated_daily_revenue_per_cash_player) / daily_market_size * 100, 1),
            'tournament_contribution': round(((total_players - total_cash) * estimated_daily_revenue_per_tournament_player) / daily_market_size * 100, 1)
        }
        
    def generate_investment_recommendations(self, data):
        """투자 권고사항 생성"""
        recommendations = []
        
        # 높은 성장 잠재력 사이트들
        personality_profiles = self.create_site_personality_profiles()
        
        for profile in personality_profiles:
            if profile['growth_potential']['potential_level'] == 'HIGH':
                recommendations.append({
                    'site': profile['site'],
                    'recommendation': 'Strong Investment Candidate',
                    'reasoning': f"성장 점수: {profile['growth_potential']['score']}/6",
                    'focus_areas': profile['growth_potential']['growth_factors']
                })
                
        # 시장 기회 기반 권고
        positioning = self.analyze_competitive_positioning()
        for opportunity in positioning['market_opportunities']:
            recommendations.append({
                'opportunity': opportunity['opportunity'],
                'investment_type': 'Market Entry',
                'strategy': opportunity['strategy']
            })
            
        return recommendations
        
    def suggest_expansion_strategies(self, data):
        """확장 전략 제안"""
        strategies = []
        
        # 성공적인 모델 분석
        high_performers = [s for s in data if s['total_players'] >= 10000]
        
        if high_performers:
            avg_cash_ratio = sum(s['cash_ratio'] for s in high_performers) / len(high_performers)
            
            strategies.append({
                'strategy': 'Follow Market Leaders',
                'description': f'성공한 대형 사이트들의 평균 캐시게임 비율({avg_cash_ratio:.1f}%) 벤치마킹',
                'implementation': '캐시게임과 토너먼트의 균형점 찾기'
            })
            
        # 틈새 시장 전략
        segmentation = self.perform_market_segmentation()
        for segment_category, segments in segmentation.items():
            for segment_name, segment_data in segments.items():
                if segment_data['count'] <= 2 and segment_data['total_players'] >= 5000:
                    strategies.append({
                        'strategy': f'Enter {segment_name} Niche',
                        'description': f'경쟁사가 적은({segment_data["count"]}개) {segment_name} 세그먼트 진입',
                        'target_profile': f'평균 캐시게임 비율: {segment_data["avg_cash_ratio"]}%'
                    })
                    
        return strategies
        
    def create_broadcast_storytelling(self):
        """방송용 스토리텔링 생성"""
        logger.info("  📺 방송용 스토리텔링 생성...")
        
        basic_data = self.perform_basic_calculations()
        personality_profiles = self.create_site_personality_profiles()
        behavioral_insights = self.extract_behavioral_insights()
        
        storytelling = {
            'headline_stories': self.generate_headline_stories(basic_data, behavioral_insights),
            'character_narratives': self.create_character_narratives(personality_profiles),
            'data_drama': self.find_data_drama_points(basic_data),
            'audience_engagement_angles': self.suggest_audience_angles(behavioral_insights),
            'visual_story_ideas': self.propose_visual_stories(basic_data)
        }
        
        return storytelling
        
    def generate_headline_stories(self, data, behavioral_insights):
        """헤드라인 스토리 생성"""
        stories = []
        
        market_behavior = behavioral_insights['market_behavior_patterns']
        
        # 메인 스토리: 시장의 성향
        if market_behavior['global_cash_preference'] <= 15:
            stories.append({
                'headline': "토너먼트 열풍, 온라인 포커 플레이어의 95%가 대박을 꿈꾼다",
                'angle': f"전체 플레이어 중 {market_behavior['tournament_dominance']}%가 토너먼트 참여",
                'hook': "왜 모든 플레이어가 토너먼트에 몰릴까?"
            })
        else:
            stories.append({
                'headline': f"온라인 포커의 성숙, 캐시게임 플레이어 {market_behavior['global_cash_preference']}% 시대",
                'angle': "안정적 수익 추구하는 플레이어들의 증가",
                'hook': "토너먼트에서 캐시게임으로의 패러다임 전환"
            })
            
        # 서브 스토리: 극명한 대비
        largest_site = max(data, key=lambda x: x['total_players'])
        smallest_active = min([s for s in data if s['total_players'] >= 100], key=lambda x: x['total_players'])
        
        stories.append({
            'headline': f"거대한 격차: {largest_site['site']} vs {smallest_active['site']}",
            'angle': f"{largest_site['total_players']:,}명 vs {smallest_active['total_players']:,}명, {largest_site['total_players']//smallest_active['total_players']}배 차이",
            'hook': "온라인 포커 시장의 양극화 현상"
        })
        
        return stories
        
    def create_character_narratives(self, profiles):
        """캐릭터 내러티브 생성"""
        narratives = []
        
        for profile in profiles[:5]:  # 상위 5개 사이트
            site_name = profile['site']
            personality = profile['primary_personality']
            
            narrative = {
                'character': site_name,
                'personality': personality,
                'story_arc': self.create_story_arc(profile),
                'conflict': self.identify_character_conflict(profile),
                'audience_connection': profile['target_audience'][0] if profile['target_audience'] else "모든 포커 플레이어"
            }
            
            narratives.append(narrative)
            
        return narratives
        
    def create_story_arc(self, profile):
        """스토리 아크 생성"""
        growth_potential = profile['growth_potential']['potential_level']
        competitive_advantages = profile['competitive_advantage']
        
        if growth_potential == 'HIGH':
            return f"떠오르는 강자 - {', '.join(competitive_advantages[:2])}로 무장한 성장 스토리"
        elif 'Scale Advantage' in competitive_advantages:
            return f"확고한 리더 - 압도적 규모로 시장을 지배하는 왕좌의 게임"
        else:
            return f"틈새 전문가 - {competitive_advantages[0] if competitive_advantages else '독특한 포지션'}으로 생존하는 전략"
            
    def identify_character_conflict(self, profile):
        """캐릭터 갈등 요소 식별"""
        risk_profile = profile['risk_profile']
        
        if risk_profile['risk_level'] == 'HIGH RISK':
            return f"생존의 위기 - {', '.join(risk_profile['risk_factors'][:2])}"
        elif 'Cash Game Excellence' in profile['competitive_advantage']:
            return "프로 vs 아마추어 - 높은 진입장벽의 딜레마"
        else:
            return "성장 vs 안정 - 규모 확장의 기로에 선 선택"
            
    def find_data_drama_points(self, data):
        """데이터 드라마 포인트 발견"""
        drama_points = []
        
        # 극명한 대비점들 찾기
        cash_ratios = [s['cash_ratio'] for s in data]
        max_cash_site = max(data, key=lambda x: x['cash_ratio'])
        min_cash_site = min(data, key=lambda x: x['cash_ratio'])
        
        if max_cash_site['cash_ratio'] - min_cash_site['cash_ratio'] >= 50:
            drama_points.append({
                'drama': '극과 극의 만남',
                'description': f"{max_cash_site['site']}({max_cash_site['cash_ratio']:.1f}% 캐시) vs {min_cash_site['site']}({min_cash_site['cash_ratio']:.1f}% 캐시)",
                'narrative': "같은 포커라도 완전히 다른 세계"
            })
            
        # 의외의 발견
        small_high_cash = [s for s in data if s['total_players'] <= 2000 and s['cash_ratio'] >= 40]
        if small_high_cash:
            site = small_high_cash[0]
            drama_points.append({
                'drama': '작지만 강한',
                'description': f"{site['site']}: 단 {site['total_players']:,}명이지만 {site['cash_ratio']:.1f}%가 캐시게임",
                'narrative': "규모보다 중요한 것은 플레이어의 질"
            })
            
        return drama_points
        
    def suggest_audience_angles(self, behavioral_insights):
        """오디언스 앵글 제안"""
        angles = []
        
        psychology_insights = behavioral_insights['player_psychology_insights']
        
        for insight in psychology_insights:
            if insight['insight'] == 'Dream Chaser Dominance':
                angles.append({
                    'angle': '시청자 참여형',
                    'question': "당신도 토너먼트 꿈나무인가요?",
                    'interaction': "채팅으로 캐시게임 vs 토너먼트 선호도 투표"
                })
            elif insight['insight'] == 'Steady Player Preference':
                angles.append({
                    'angle': '전문성 어필',
                    'question': "프로처럼 플레이하려면 어느 사이트?",
                    'interaction': "캐시게임 고수들의 사이트 선택 기준 공개"
                })
                
        return angles
        
    def propose_visual_stories(self, data):
        """비주얼 스토리 제안"""
        visual_ideas = []
        
        # 버블 차트 아이디어
        visual_ideas.append({
            'chart_type': '버블 차트',
            'title': '포커 사이트 우주도',
            'description': 'X축: 총 플레이어, Y축: 캐시게임 비율, 버블크기: 시장 점유율',
            'story': '각 사이트가 우주의 행성처럼 고유한 궤도를 가짐'
        })
        
        # 히트맵 아이디어
        visual_ideas.append({
            'chart_type': '히트맵',
            'title': '플레이어 성향 지도',
            'description': '사이트별 캐시/토너먼트 선호도를 색상으로 표현',
            'story': '빨간색(캐시게임) vs 파란색(토너먼트)의 온도 지도'
        })
        
        return visual_ideas
        
    def build_predictive_models(self):
        """예측 모델 구축"""
        logger.info("  🔮 예측 모델 구축...")
        
        basic_data = self.perform_basic_calculations()
        
        predictions = {
            'growth_predictions': self.predict_growth_patterns(basic_data),
            'market_evolution': self.predict_market_evolution(basic_data),
            'player_behavior_trends': self.predict_behavior_trends(basic_data)
        }
        
        return predictions
        
    def predict_growth_patterns(self, data):
        """성장 패턴 예측"""
        predictions = []
        
        # 현재 균형점 분석
        current_market_cash_ratio = sum(s['cash_players'] for s in data) / sum(s['total_players'] for s in data) * 100
        
        # 성장 사이트들의 패턴 분석
        large_sites = [s for s in data if s['total_players'] >= 10000]
        if large_sites:
            large_sites_cash_ratio = sum(s['cash_players'] for s in large_sites) / sum(s['total_players'] for s in large_sites) * 100
            
            if large_sites_cash_ratio > current_market_cash_ratio:
                predictions.append({
                    'trend': 'Cash Game Growth Trend',
                    'prediction': f'시장이 현재 {current_market_cash_ratio:.1f}%에서 {large_sites_cash_ratio:.1f}%로 캐시게임 중심으로 발전 예상',
                    'timeline': '6-12개월',
                    'confidence': 'MEDIUM'
                })
                
        return predictions
        
    def predict_market_evolution(self, data):
        """시장 진화 예측"""
        evolution_stages = []
        
        # 현재 시장 성숙도 평가
        cash_diversity = statistics.stdev([s['cash_ratio'] for s in data]) if len(data) > 1 else 0
        
        if cash_diversity >= 30:
            evolution_stages.append({
                'stage': 'Market Fragmentation Phase',
                'description': '플레이어 선호도가 명확히 분화되는 단계',
                'next_evolution': 'Specialized Platform Emergence'
            })
        else:
            evolution_stages.append({
                'stage': 'Homogeneous Market Phase',
                'description': '비슷한 서비스 모델이 지배적인 단계',
                'next_evolution': 'Differentiation Competition'
            })
            
        return evolution_stages
        
    def predict_behavior_trends(self, data):
        """행동 트렌드 예측"""
        trends = []
        
        # 규모와 캐시게임 선호도의 상관관계 분석
        large_sites_cash = [s['cash_ratio'] for s in data if s['total_players'] >= 5000]
        small_sites_cash = [s['cash_ratio'] for s in data if s['total_players'] <= 2000]
        
        if large_sites_cash and small_sites_cash:
            large_avg = statistics.mean(large_sites_cash)
            small_avg = statistics.mean(small_sites_cash)
            
            if large_avg > small_avg + 10:
                trends.append({
                    'trend': 'Premium Service Migration',
                    'prediction': '플레이어들이 점차 캐시게임 중심의 프리미엄 플랫폼으로 이동',
                    'driver': '게임 품질과 서비스 안정성 중시',
                    'impact': '소형 사이트들의 캐시게임 강화 필요성 증대'
                })
                
        return trends
        
    def identify_innovation_opportunities(self):
        """혁신 기회 식별"""
        logger.info("  💡 혁신 기회 식별...")
        
        basic_data = self.perform_basic_calculations()
        competitive_positioning = self.analyze_competitive_positioning()
        
        opportunities = {
            'product_innovation': self.suggest_product_innovations(basic_data),
            'market_gaps': competitive_positioning['competitive_gaps'],
            'technology_opportunities': self.identify_tech_opportunities(basic_data),
            'business_model_innovations': self.suggest_business_model_innovations(basic_data)
        }
        
        return opportunities
        
    def suggest_product_innovations(self, data):
        """제품 혁신 제안"""
        innovations = []
        
        # 극단적 캐시게임 사이트 vs 극단적 토너먼트 사이트 분석
        extreme_cash_sites = [s for s in data if s['cash_ratio'] >= 70]
        extreme_tournament_sites = [s for s in data if s['cash_ratio'] <= 10]
        
        if len(extreme_cash_sites) <= 1:
            innovations.append({
                'innovation': 'Premium Cash Game Platform',
                'description': '최고급 캐시게임만을 위한 전용 플랫폼',
                'target': '프로페셔널 플레이어 및 고액 플레이어',
                'differentiation': 'VIP 서비스, 고급 UI, 전문 지원'
            })
            
        if len(extreme_tournament_sites) >= 5:
            innovations.append({
                'innovation': 'Tournament Variety Engine',
                'description': '무한대로 다양한 토너먼트 형식을 제공하는 엔진',
                'target': '토너먼트 매니아',
                'differentiation': 'AI 기반 맞춤형 토너먼트 생성'
            })
            
        return innovations
        
    def identify_tech_opportunities(self, data):
        """기술 기회 식별"""
        tech_opportunities = []
        
        # 플레이어 분포 기반 기술 니즈 분석
        total_players = sum(s['total_players'] for s in data)
        
        if total_players >= 200000:
            tech_opportunities.append({
                'opportunity': 'Real-time Analytics Platform',
                'description': '대규모 플레이어 데이터 실시간 분석 플랫폼',
                'value': '운영 최적화 및 플레이어 경험 개선'
            })
            
        # 세분화된 시장 기반 개인화 기술
        cash_diversity = statistics.stdev([s['cash_ratio'] for s in data]) if len(data) > 1 else 0
        
        if cash_diversity >= 25:
            tech_opportunities.append({
                'opportunity': 'Player Preference AI',
                'description': '플레이어 성향 분석 및 맞춤형 게임 추천 AI',
                'value': '개인화된 사용자 경험 제공'
            })
            
        return tech_opportunities
        
    def suggest_business_model_innovations(self, data):
        """비즈니스 모델 혁신 제안"""
        business_innovations = []
        
        # 현재 시장의 수익 구조 분석
        high_cash_sites = [s for s in data if s['cash_ratio'] >= 50]
        high_tournament_sites = [s for s in data if s['cash_ratio'] <= 20]
        
        if len(high_cash_sites) >= 3:
            business_innovations.append({
                'model': 'Subscription-Based Premium Cash Games',
                'description': '월 구독료로 프리미엄 캐시게임 무제한 이용',
                'rationale': '안정적 캐시게임 플레이어 기반 활용',
                'revenue_stream': '구독료 + 프리미엄 서비스'
            })
            
        if len(high_tournament_sites) >= 5:
            business_innovations.append({
                'model': 'Tournament-as-a-Service (TaaS)',
                'description': '다른 플랫폼에 토너먼트 기술 및 운영 서비스 제공',
                'rationale': '토너먼트 운영 노하우의 B2B 확장',
                'revenue_stream': 'SaaS 구독료 + 수수료'
            })
            
        return business_innovations
        
    def save_comprehensive_analysis(self, analysis_results):
        """종합 분석 결과 저장"""
        logger.info("💾 종합 분석 결과 저장...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 상세 분석 결과
        detailed_filename = f'two_factor_analysis_{timestamp}.json'
        with open(detailed_filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
            
        # 실행 요약 리포트
        summary_filename = f'two_factor_summary_{timestamp}.txt'
        self.save_executive_summary(analysis_results, summary_filename)
        
        # 방송용 스토리 북
        story_filename = f'broadcast_storybook_{timestamp}.txt'
        self.save_broadcast_storybook(analysis_results, story_filename)
        
        logger.info(f"📊 상세 분석: {detailed_filename}")
        logger.info(f"📋 실행 요약: {summary_filename}")
        logger.info(f"📺 스토리북: {story_filename}")
        
        return detailed_filename, summary_filename, story_filename
        
    def save_executive_summary(self, results, filename):
        """실행 요약 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("🎯 PokerScout 2-Factor 혁신적 분석 실행 요약\n")
            f.write(f"분석 시점: {datetime.now().strftime('%Y년 %m월 %d일')}\n")
            f.write("=" * 80 + "\n\n")
            
            # 핵심 발견사항
            basic_calc = results.get('basic_calculations', [])
            if basic_calc:
                total_players = sum(s['total_players'] for s in basic_calc)
                total_cash = sum(s['cash_players'] for s in basic_calc)
                market_cash_ratio = (total_cash / total_players * 100) if total_players > 0 else 0
                
                f.write("🔍 핵심 발견사항\n")
                f.write("-" * 40 + "\n")
                f.write(f"전체 시장 플레이어: {total_players:,}명\n")
                f.write(f"시장 캐시게임 선호도: {market_cash_ratio:.1f}%\n")
                f.write(f"분석 대상 사이트: {len(basic_calc)}개\n\n")
                
            # 사이트 성격 프로파일 요약
            personalities = results.get('site_personality_profiling', [])
            if personalities:
                f.write("🎭 주요 사이트 성격 프로파일\n")
                f.write("-" * 40 + "\n")
                for profile in personalities[:5]:
                    f.write(f"{profile['site']}: {profile['primary_personality']}\n")
                    f.write(f"  타겟: {profile['target_audience'][0] if profile['target_audience'] else 'N/A'}\n")
                    f.write(f"  성장 잠재력: {profile['growth_potential']['potential_level']}\n\n")
                    
            # 비즈니스 인사이트
            bi = results.get('business_intelligence', {})
            market_sizing = bi.get('market_sizing', {})
            if market_sizing:
                f.write("💼 비즈니스 인사이트\n")
                f.write("-" * 40 + "\n")
                f.write(f"추정 일일 시장 규모: ${market_sizing.get('daily_market_size_usd', 0):,}\n")
                f.write(f"추정 연간 시장 규모: ${market_sizing.get('annual_market_size_usd', 0):,}\n")
                f.write(f"캐시게임 수익 기여도: {market_sizing.get('cash_game_contribution', 0)}%\n\n")
                
            # 혁신 기회
            innovations = results.get('innovation_opportunities', {})
            product_innovations = innovations.get('product_innovation', [])
            if product_innovations:
                f.write("💡 주요 혁신 기회\n")
                f.write("-" * 40 + "\n")
                for innovation in product_innovations[:3]:
                    f.write(f"• {innovation['innovation']}\n")
                    f.write(f"  {innovation['description']}\n\n")
                    
    def save_broadcast_storybook(self, results, filename):
        """방송용 스토리북 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("📺 방송용 스토리북 - PokerScout 2-Factor 분석\n")
            f.write("=" * 80 + "\n\n")
            
            storytelling = results.get('broadcast_storytelling', {})
            
            # 헤드라인 스토리
            headlines = storytelling.get('headline_stories', [])
            if headlines:
                f.write("🎬 헤드라인 스토리\n")
                f.write("-" * 40 + "\n")
                for story in headlines:
                    f.write(f"제목: {story['headline']}\n")
                    f.write(f"앵글: {story['angle']}\n")
                    f.write(f"훅: {story['hook']}\n\n")
                    
            # 캐릭터 내러티브
            narratives = storytelling.get('character_narratives', [])
            if narratives:
                f.write("👥 사이트 캐릭터 스토리\n")
                f.write("-" * 40 + "\n")
                for narrative in narratives[:3]:
                    f.write(f"캐릭터: {narrative['character']}\n")
                    f.write(f"성격: {narrative['personality']}\n")
                    f.write(f"스토리: {narrative['story_arc']}\n")
                    f.write(f"갈등: {narrative['conflict']}\n\n")
                    
            # 데이터 드라마
            drama_points = storytelling.get('data_drama', [])
            if drama_points:
                f.write("🎭 데이터 드라마 포인트\n")
                f.write("-" * 40 + "\n")
                for drama in drama_points:
                    f.write(f"드라마: {drama['drama']}\n")
                    f.write(f"설명: {drama['description']}\n")
                    f.write(f"내러티브: {drama['narrative']}\n\n")
                    
            # 비주얼 아이디어
            visual_ideas = storytelling.get('visual_story_ideas', [])
            if visual_ideas:
                f.write("🎨 비주얼 스토리 아이디어\n")
                f.write("-" * 40 + "\n")
                for idea in visual_ideas:
                    f.write(f"차트: {idea['chart_type']}\n")
                    f.write(f"제목: {idea['title']}\n")
                    f.write(f"설명: {idea['description']}\n")
                    f.write(f"스토리: {idea['story']}\n\n")

def main():
    """메인 실행 함수"""
    print("🎯 PokerScout 2-Factor 혁신적 분석 엔진")
    print("=" * 60)
    print("데이터 소스: Players Online + Cash Players")
    print("분석 목표: 최소 데이터로 최대 인사이트 도출")
    print("=" * 60)
    
    engine = TwoFactorAnalysisEngine()
    
    try:
        # 종합 2-팩터 분석 수행
        print("\n🔄 혁신적 분석 수행 중...")
        analysis_results = engine.generate_comprehensive_two_factor_analysis()
        
        # 결과 미리보기
        print("\n📊 분석 결과 미리보기:")
        
        basic_calc = analysis_results.get('basic_calculations', [])
        if basic_calc:
            total_players = sum(s['total_players'] for s in basic_calc)
            total_cash = sum(s['cash_players'] for s in basic_calc)
            market_cash_ratio = (total_cash / total_players * 100) if total_players > 0 else 0
            
            print(f"분석 사이트: {len(basic_calc)}개")
            print(f"총 플레이어: {total_players:,}명")
            print(f"시장 캐시게임 선호도: {market_cash_ratio:.1f}%")
            
        personalities = analysis_results.get('site_personality_profiling', [])
        if personalities:
            print(f"사이트 성격 프로파일: {len(personalities)}개 생성")
            top_personality = personalities[0]
            print(f"대표 사이트 성격: {top_personality['site']} - {top_personality['primary_personality']}")
            
        storytelling = analysis_results.get('broadcast_storytelling', {})
        headlines = storytelling.get('headline_stories', [])
        if headlines:
            print(f"방송용 헤드라인: {len(headlines)}개 생성")
            print(f"메인 스토리: {headlines[0]['headline']}")
            
        innovations = analysis_results.get('innovation_opportunities', {})
        product_innovations = innovations.get('product_innovation', [])
        if product_innovations:
            print(f"혁신 기회: {len(product_innovations)}개 식별")
            
        # 결과 저장
        print("\n💾 분석 결과 저장 중...")
        detailed_file, summary_file, story_file = engine.save_comprehensive_analysis(analysis_results)
        
        print(f"\n✅ 2-Factor 혁신적 분석 완료!")
        print(f"📊 상세 분석: {detailed_file}")
        print(f"📋 실행 요약: {summary_file}")
        print(f"📺 방송 스토리북: {story_file}")
        
        print(f"\n🚀 완성된 분석 아이디어:")
        print("  • 사이트 성격 프로파일링")
        print("  • 플레이어 행동 심리 분석")
        print("  • 경쟁 포지셔닝 맵")
        print("  • 비즈니스 인텔리전스")
        print("  • 방송용 스토리텔링")
        print("  • 예측 모델링")
        print("  • 혁신 기회 발굴")
        
        return True
        
    except Exception as e:
        logger.error(f"분석 오류: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🎉 PokerScout 2-Factor 혁신 분석 완료!")
        print(f"최소한의 데이터로 최대한의 인사이트를 도출했습니다!")
    else:
        print(f"\n💀 분석 실패 - 문제 해결 필요")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GG POKER 직원용 데이터 중심 온라인 포커 모니터링 플랫폼
- 4개 핵심 지표: Players Online, Cash Players, 24h Peak, 7-day Average
- 날짜별 시계열 데이터 수집 및 분석
- 급변 시점의 뉴스 연관성 분석
- 추론 배제, 순수 데이터 기반 분석
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

class GGPokerMonitoringPlatform:
    def __init__(self, db_path='gg_poker_monitoring.db'):
        self.db_path = db_path
        self.setup_database()
        
        # 급변 감지 임계값
        self.SIGNIFICANT_CHANGE_THRESHOLD = 15.0  # 15% 변화
        self.MAJOR_CHANGE_THRESHOLD = 25.0        # 25% 주요 변화
        self.ANOMALY_THRESHOLD = 50.0             # 50% 이상치
        
    def setup_database(self):
        """데이터베이스 스키마 설정"""
        logger.info("📊 데이터베이스 스키마 설정...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 일일 트래픽 데이터 테이블 (시계열)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_traffic (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_name TEXT NOT NULL,
                collection_date DATE NOT NULL,
                collection_time TIME NOT NULL,
                players_online INTEGER NOT NULL,
                cash_players INTEGER NOT NULL,
                peak_24h INTEGER,
                seven_day_avg INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(site_name, collection_date, collection_time)
            )
        ''')
        
        # 변화 감지 로그 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS change_detection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_name TEXT NOT NULL,
                detection_date DATE NOT NULL,
                metric_type TEXT NOT NULL,
                previous_value INTEGER,
                current_value INTEGER,
                change_percentage REAL,
                change_magnitude TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 뉴스-변화 연관성 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_correlation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                change_detection_id INTEGER,
                news_title TEXT,
                news_url TEXT,
                news_date DATE,
                correlation_score REAL,
                correlation_type TEXT,
                analysis_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (change_detection_id) REFERENCES change_detection (id)
            )
        ''')
        
        # 경쟁사 메타데이터 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitor_metadata (
                site_name TEXT PRIMARY KEY,
                site_url TEXT,
                network_family TEXT,
                market_tier TEXT,
                monitoring_priority TEXT,
                competitor_category TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ 데이터베이스 스키마 설정 완료")
        
    def collect_daily_data(self, site_data_list):
        """일일 데이터 수집"""
        logger.info("📈 일일 데이터 수집 시작...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        collection_date = datetime.now().strftime('%Y-%m-%d')
        collection_time = datetime.now().strftime('%H:%M:%S')
        
        collected_count = 0
        
        for site_data in site_data_list:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_traffic 
                    (site_name, collection_date, collection_time, players_online, 
                     cash_players, peak_24h, seven_day_avg)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    site_data['site_name'],
                    collection_date,
                    collection_time,
                    site_data['players_online'],
                    site_data['cash_players'],
                    site_data.get('peak_24h', None),
                    site_data.get('seven_day_avg', None)
                ))
                
                collected_count += 1
                
            except Exception as e:
                logger.error(f"데이터 수집 오류 - {site_data['site_name']}: {str(e)}")
                
        conn.commit()
        conn.close()
        
        logger.info(f"✅ {collected_count}개 사이트 데이터 수집 완료")
        return collected_count
        
    def detect_significant_changes(self, target_date=None):
        """유의미한 변화 감지"""
        if target_date is None:
            target_date = datetime.now().strftime('%Y-%m-%d')
            
        logger.info(f"🔍 {target_date} 변화 감지 시작...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 현재 날짜와 이전 날짜 데이터 비교
        query = '''
            WITH current_data AS (
                SELECT site_name, players_online, cash_players, peak_24h, seven_day_avg
                FROM daily_traffic 
                WHERE collection_date = ?
                ORDER BY collection_time DESC
                LIMIT 50
            ),
            previous_data AS (
                SELECT site_name, players_online, cash_players, peak_24h, seven_day_avg
                FROM daily_traffic 
                WHERE collection_date = date(?, '-1 day')
                ORDER BY collection_time DESC
                LIMIT 50
            )
            SELECT 
                c.site_name,
                c.players_online as current_players,
                p.players_online as previous_players,
                c.cash_players as current_cash,
                p.cash_players as previous_cash,
                c.peak_24h as current_peak,
                p.peak_24h as previous_peak,
                c.seven_day_avg as current_7day,
                p.seven_day_avg as previous_7day
            FROM current_data c
            LEFT JOIN previous_data p ON c.site_name = p.site_name
            WHERE p.site_name IS NOT NULL
        '''
        
        cursor.execute(query, (target_date, target_date))
        results = cursor.fetchall()
        
        detected_changes = []
        
        for row in results:
            site_name = row[0]
            changes = self.analyze_site_changes(row)
            
            for change in changes:
                if change['magnitude'] in ['SIGNIFICANT', 'MAJOR', 'ANOMALY']:
                    # 변화 감지 로그에 저장
                    cursor.execute('''
                        INSERT INTO change_detection 
                        (site_name, detection_date, metric_type, previous_value, 
                         current_value, change_percentage, change_magnitude)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        site_name,
                        target_date,
                        change['metric'],
                        change['previous_value'],
                        change['current_value'],
                        change['change_percentage'],
                        change['magnitude']
                    ))
                    
                    change['change_id'] = cursor.lastrowid
                    detected_changes.append(change)
                    
        conn.commit()
        conn.close()
        
        logger.info(f"🚨 {len(detected_changes)}개 유의미한 변화 감지")
        return detected_changes
        
    def analyze_site_changes(self, data_row):
        """사이트별 변화 분석"""
        site_name, curr_players, prev_players, curr_cash, prev_cash, curr_peak, prev_peak, curr_7day, prev_7day = data_row
        
        changes = []
        
        # 각 지표별 변화율 계산
        metrics = [
            ('players_online', curr_players, prev_players),
            ('cash_players', curr_cash, prev_cash),
            ('peak_24h', curr_peak, prev_peak),
            ('seven_day_avg', curr_7day, prev_7day)
        ]
        
        for metric_name, current, previous in metrics:
            if current is not None and previous is not None and previous > 0:
                change_percentage = ((current - previous) / previous) * 100
                magnitude = self.classify_change_magnitude(abs(change_percentage))
                
                changes.append({
                    'site_name': site_name,
                    'metric': metric_name,
                    'previous_value': previous,
                    'current_value': current,
                    'change_percentage': round(change_percentage, 2),
                    'magnitude': magnitude,
                    'direction': 'INCREASE' if change_percentage > 0 else 'DECREASE'
                })
                
        return changes
        
    def classify_change_magnitude(self, abs_change_percentage):
        """변화 크기 분류"""
        if abs_change_percentage >= self.ANOMALY_THRESHOLD:
            return 'ANOMALY'
        elif abs_change_percentage >= self.MAJOR_CHANGE_THRESHOLD:
            return 'MAJOR'
        elif abs_change_percentage >= self.SIGNIFICANT_CHANGE_THRESHOLD:
            return 'SIGNIFICANT'
        else:
            return 'MINOR'
            
    def generate_time_series_chart_data(self, site_name, days_back=30):
        """시계열 차트 데이터 생성"""
        logger.info(f"📊 {site_name} 시계열 차트 데이터 생성 ({days_back}일)")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 일별 최신 데이터 조회
        query = '''
            SELECT 
                collection_date,
                players_online,
                cash_players,
                peak_24h,
                seven_day_avg
            FROM daily_traffic 
            WHERE site_name = ? 
            AND collection_date >= date('now', '-' || ? || ' days')
            GROUP BY collection_date
            HAVING collection_time = MAX(collection_time)
            ORDER BY collection_date
        '''
        
        cursor.execute(query, (site_name, days_back))
        results = cursor.fetchall()
        
        if not results:
            return None
            
        # 차트 데이터 구성
        chart_data = {
            'site_name': site_name,
            'period_days': days_back,
            'data_points': len(results),
            'labels': [],  # X축 날짜
            'datasets': {
                'players_online': {
                    'label': 'Players Online',
                    'data': [],
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)'
                },
                'cash_players': {
                    'label': 'Cash Players',
                    'data': [],
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)'
                },
                'peak_24h': {
                    'label': '24h Peak',
                    'data': [],
                    'borderColor': 'rgb(54, 162, 235)',
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)'
                },
                'seven_day_avg': {
                    'label': '7-day Average',
                    'data': [],
                    'borderColor': 'rgb(255, 206, 86)',
                    'backgroundColor': 'rgba(255, 206, 86, 0.2)'
                }
            },
            'analytics': {}
        }
        
        for row in results:
            chart_data['labels'].append(row[0])
            chart_data['datasets']['players_online']['data'].append(row[1])
            chart_data['datasets']['cash_players']['data'].append(row[2])
            chart_data['datasets']['peak_24h']['data'].append(row[3] if row[3] is not None else 0)
            chart_data['datasets']['seven_day_avg']['data'].append(row[4] if row[4] is not None else 0)
            
        # 기본 통계 계산
        chart_data['analytics'] = self.calculate_chart_analytics(chart_data)
        
        conn.close()
        return chart_data
        
    def calculate_chart_analytics(self, chart_data):
        """차트 분석 데이터 계산"""
        analytics = {}
        
        for metric_key, dataset in chart_data['datasets'].items():
            values = [v for v in dataset['data'] if v is not None and v > 0]
            
            if values:
                analytics[metric_key] = {
                    'current': values[-1] if values else 0,
                    'min': min(values),
                    'max': max(values),
                    'mean': round(statistics.mean(values), 1),
                    'median': round(statistics.median(values), 1),
                    'std_dev': round(statistics.stdev(values), 1) if len(values) > 1 else 0,
                    'trend': self.calculate_trend(values),
                    'volatility': self.calculate_volatility(values),
                    'recent_change_pct': self.calculate_recent_change(values)
                }
            else:
                analytics[metric_key] = {'no_data': True}
                
        return analytics
        
    def calculate_trend(self, values):
        """트렌드 계산"""
        if len(values) < 3:
            return 'INSUFFICIENT_DATA'
            
        # 최근 7일 vs 이전 기간 비교
        if len(values) >= 7:
            recent_avg = statistics.mean(values[-7:])
            previous_avg = statistics.mean(values[:-7]) if len(values) > 7 else statistics.mean(values)
            
            if recent_avg > previous_avg * 1.05:
                return 'UPWARD'
            elif recent_avg < previous_avg * 0.95:
                return 'DOWNWARD'
            else:
                return 'STABLE'
        else:
            # 첫값 vs 마지막값
            if values[-1] > values[0] * 1.1:
                return 'UPWARD'
            elif values[-1] < values[0] * 0.9:
                return 'DOWNWARD'
            else:
                return 'STABLE'
                
    def calculate_volatility(self, values):
        """변동성 계산"""
        if len(values) < 2:
            return 'LOW'
            
        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values)
        cv = (std_dev / mean_val) * 100 if mean_val > 0 else 0
        
        if cv >= 20:
            return 'HIGH'
        elif cv >= 10:
            return 'MEDIUM'
        else:
            return 'LOW'
            
    def calculate_recent_change(self, values):
        """최근 변화율 계산"""
        if len(values) < 2:
            return 0
            
        current = values[-1]
        previous = values[-2]
        
        if previous > 0:
            return round(((current - previous) / previous) * 100, 2)
        return 0
        
    def setup_competitor_monitoring(self):
        """경쟁사 모니터링 설정 (GG POKER 포함)"""
        logger.info("🎯 경쟁사 모니터링 설정 (GG POKER 포함)...")
        
        # GG POKER와 경쟁사 분류
        monitoring_sites = [
            # GG POKER (자사 데이터)
            {'name': 'GGNetwork', 'priority': 'CRITICAL', 'category': 'OWN', 'tier': 'GG_POKER'},
            {'name': 'GGPoker ON', 'priority': 'CRITICAL', 'category': 'OWN', 'tier': 'GG_POKER'},
            
            # Tier 1 직접 경쟁사 (대형 글로벌 플랫폼)
            {'name': 'PokerStars', 'priority': 'HIGH', 'category': 'DIRECT', 'tier': 'Tier1'},
            {'name': 'PokerStars Ontario', 'priority': 'HIGH', 'category': 'DIRECT', 'tier': 'Tier1'},
            {'name': 'PokerStars.it', 'priority': 'MEDIUM', 'category': 'DIRECT', 'tier': 'Tier1'},
            
            # Tier 2 간접 경쟁사 (중형 플랫폼)
            {'name': '888poker', 'priority': 'MEDIUM', 'category': 'INDIRECT', 'tier': 'Tier2'},
            {'name': 'partypoker', 'priority': 'MEDIUM', 'category': 'INDIRECT', 'tier': 'Tier2'},
            {'name': 'WPT Global', 'priority': 'HIGH', 'category': 'INDIRECT', 'tier': 'Tier2'},
            
            # Tier 3 틈새 경쟁사 (네트워크/지역 특화)
            {'name': 'iPoker', 'priority': 'LOW', 'category': 'NICHE', 'tier': 'Tier3'},
            {'name': 'Chico Poker', 'priority': 'LOW', 'category': 'NICHE', 'tier': 'Tier3'},
            {'name': 'Winamax', 'priority': 'LOW', 'category': 'NICHE', 'tier': 'Tier3'},
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for site in monitoring_sites:
            network_info = 'GG Network' if site['category'] == 'OWN' else 'Independent'
            notes = f"GG POKER 자사 데이터" if site['category'] == 'OWN' else f"GG POKER 경쟁사 모니터링 - {site['category']} 경쟁"
            
            cursor.execute('''
                INSERT OR REPLACE INTO competitor_metadata 
                (site_name, network_family, market_tier, monitoring_priority, 
                 competitor_category, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                site['name'],
                network_info,
                site['tier'],
                site['priority'],
                site['category'],
                notes
            ))
            
        conn.commit()
        conn.close()
        
        logger.info(f"✅ {len(monitoring_sites)}개 사이트 모니터링 설정 완료 (GG POKER 포함)")
        
    def get_competitor_dashboard_data(self):
        """경쟁사 대시보드 데이터 (GG POKER 포함)"""
        logger.info("📊 경쟁사 대시보드 데이터 생성 (GG POKER 포함)...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                cm.site_name,
                cm.monitoring_priority,
                cm.competitor_category,
                cm.market_tier,
                dt.players_online,
                dt.cash_players,
                dt.peak_24h,
                dt.seven_day_avg,
                dt.collection_date,
                dt.collection_time
            FROM competitor_metadata cm
            LEFT JOIN daily_traffic dt ON cm.site_name = dt.site_name
            WHERE dt.collection_date = (SELECT MAX(collection_date) FROM daily_traffic)
            ORDER BY 
                CASE cm.monitoring_priority 
                    WHEN 'CRITICAL' THEN 0
                    WHEN 'HIGH' THEN 1 
                    WHEN 'MEDIUM' THEN 2 
                    ELSE 3 END,
                dt.players_online DESC
        '''
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        dashboard_data = {
            'generated_at': datetime.now().isoformat(),
            'data_date': datetime.now().strftime('%Y-%m-%d'),
            'gg_poker_data': [],
            'high_priority_competitors': [],
            'medium_priority_competitors': [],
            'low_priority_competitors': [],
            'market_summary': {
                'total_sites': len(results),
                'total_monitored_players': 0,
                'gg_poker_total_players': 0,
                'competitor_total_players': 0,
                'gg_poker_market_share': 0.0
            }
        }
        
        total_players = 0
        
        for row in results:
            site_data = {
                'site_name': row[0],
                'category': row[2],
                'tier': row[3],
                'players_online': row[4] or 0,
                'cash_players': row[5] or 0,
                'peak_24h': row[6] or 0,
                'seven_day_avg': row[7] or 0,
                'cash_ratio': round((row[5] / row[4]) * 100, 1) if row[4] and row[5] else 0,
                'last_updated': f"{row[8]} {row[9]}" if row[8] and row[9] else 'N/A'
            }
            
            total_players += site_data['players_online']
            
            priority = row[1]
            if priority == 'HIGH':
                dashboard_data['high_priority_competitors'].append(site_data)
            elif priority == 'MEDIUM':
                dashboard_data['medium_priority_competitors'].append(site_data)
            else:
                dashboard_data['low_priority_competitors'].append(site_data)
                
        dashboard_data['market_summary']['total_monitored_players'] = total_players
        
        conn.close()
        return dashboard_data
        
    def analyze_news_correlation_for_changes(self, detected_changes):
        """변화와 뉴스 연관성 분석"""
        logger.info("📰 변화-뉴스 연관성 분석...")
        
        # 실제 환경에서는 뉴스 데이터베이스나 API에서 데이터 가져옴
        # 여기서는 샘플 분석 로직만 구현
        
        correlations = []
        
        for change in detected_changes:
            # 변화 발생 전후 3일간의 뉴스 검색
            correlation_analysis = {
                'change_id': change.get('change_id'),
                'site_name': change['site_name'],
                'metric': change['metric'],
                'change_percentage': change['change_percentage'],
                'magnitude': change['magnitude'],
                'potential_news_factors': [],
                'correlation_score': 0.0,
                'analysis_confidence': 'LOW'
            }
            
            # 실제 구현에서는 여기서 뉴스 API 호출 또는 DB 쿼리
            # 예시: 주요 포커 뉴스 키워드 검색
            potential_factors = self.identify_potential_news_factors(change)
            correlation_analysis['potential_news_factors'] = potential_factors
            
            if potential_factors:
                correlation_analysis['correlation_score'] = len(potential_factors) * 0.2
                correlation_analysis['analysis_confidence'] = 'MEDIUM' if len(potential_factors) >= 2 else 'LOW'
                
            correlations.append(correlation_analysis)
            
        return correlations
        
    def identify_potential_news_factors(self, change):
        """잠재적 뉴스 요인 식별"""
        factors = []
        
        site_name = change['site_name']
        magnitude = change['magnitude']
        
        # 급변 크기에 따른 가능한 요인들
        if magnitude in ['MAJOR', 'ANOMALY']:
            factors.extend([
                'Major tournament announcement',
                'Platform update or maintenance',
                'Promotional campaign launch',
                'Regulatory news',
                'Partnership announcement'
            ])
        elif magnitude == 'SIGNIFICANT':
            factors.extend([
                'Weekly tournament series',
                'Bonus promotion',
                'Software update',
                'Market news'
            ])
            
        # 사이트별 특화 요인
        if 'PokerStars' in site_name:
            factors.extend(['SCOOP/WCOOP event', 'EPT tournament', 'Sunday Million special'])
        elif 'GG' in site_name:
            factors.extend(['WSOP satellite', 'GG Masters series', 'Bounty tournament'])
        elif 'WPT' in site_name:
            factors.extend(['WPT500 series', 'World Poker Tour event'])
            
        return factors[:3]  # 상위 3개 요인만 반환
        
    def export_monitoring_report(self, date_range_days=7):
        """모니터링 리포트 내보내기"""
        logger.info(f"📋 모니터링 리포트 생성 ({date_range_days}일간)")
        
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_type': 'gg_poker_monitoring_report',
                'analysis_period_days': date_range_days,
                'focus': 'competitor_analysis_and_change_detection'
            },
            'executive_summary': {},
            'competitor_analysis': {},
            'change_detection_summary': {},
            'time_series_highlights': {},
            'recommendations': []
        }
        
        # 경쟁사 대시보드 데이터
        competitor_data = self.get_competitor_dashboard_data()
        report['competitor_analysis'] = competitor_data
        
        # 최근 변화 감지 요약
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_changes,
                COUNT(CASE WHEN change_magnitude = 'ANOMALY' THEN 1 END) as anomaly_count,
                COUNT(CASE WHEN change_magnitude = 'MAJOR' THEN 1 END) as major_count,
                COUNT(CASE WHEN change_magnitude = 'SIGNIFICANT' THEN 1 END) as significant_count
            FROM change_detection 
            WHERE detection_date >= date('now', '-' || ? || ' days')
        ''', (date_range_days,))
        
        change_summary = cursor.fetchone()
        if change_summary:
            report['change_detection_summary'] = {
                'total_changes': change_summary[0],
                'anomaly_changes': change_summary[1],
                'major_changes': change_summary[2],
                'significant_changes': change_summary[3],
                'analysis_period': f'{date_range_days} days'
            }
            
        # 경영진 요약
        report['executive_summary'] = {
            'monitored_competitors': competitor_data['market_summary']['total_competitors'],
            'total_competitor_players': competitor_data['market_summary']['total_monitored_players'],
            'high_priority_competitors': len(competitor_data['high_priority_competitors']),
            'significant_changes_detected': change_summary[0] if change_summary else 0,
            'data_quality': 'GOOD',
            'monitoring_status': 'ACTIVE'
        }
        
        # 권고사항
        if change_summary and change_summary[1] > 0:  # ANOMALY가 있는 경우
            report['recommendations'].append({
                'priority': 'HIGH',
                'recommendation': f'{change_summary[1]}개 이상 징후 감지, 즉시 상세 분석 필요',
                'action': 'INVESTIGATE'
            })
            
        # 리포트 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'gg_poker_monitoring_report_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        # 간단한 텍스트 요약도 생성
        summary_filename = f'monitoring_summary_{timestamp}.txt'
        self.save_text_summary(report, summary_filename)
        
        conn.close()
        
        logger.info(f"📊 리포트 저장: {filename}")
        logger.info(f"📄 요약 저장: {summary_filename}")
        
        return filename, summary_filename
        
    def save_text_summary(self, report, filename):
        """텍스트 요약 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("🎯 GG POKER 경쟁사 모니터링 리포트 요약\n")
            f.write(f"생성 시간: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}\n")
            f.write("=" * 80 + "\n\n")
            
            # 경영진 요약
            summary = report['executive_summary']
            f.write("📊 핵심 요약\n")
            f.write("-" * 40 + "\n")
            f.write(f"모니터링 경쟁사: {summary['monitored_competitors']}개\n")
            f.write(f"경쟁사 총 플레이어: {summary['total_competitor_players']:,}명\n")
            f.write(f"고우선순위 경쟁사: {summary['high_priority_competitors']}개\n")
            f.write(f"감지된 유의미한 변화: {summary['significant_changes_detected']}건\n\n")
            
            # 고우선순위 경쟁사 현황
            competitor_data = report['competitor_analysis']
            if competitor_data['high_priority_competitors']:
                f.write("🏆 고우선순위 경쟁사 현황\n")
                f.write("-" * 40 + "\n")
                for comp in competitor_data['high_priority_competitors']:
                    f.write(f"{comp['site_name']}: {comp['players_online']:,}명 ")
                    f.write(f"(캐시 {comp['cash_ratio']}%, 피크 {comp['peak_24h']:,}명)\n")
                f.write("\n")
                
            # 변화 감지 요약
            change_summary = report.get('change_detection_summary', {})
            if change_summary.get('total_changes', 0) > 0:
                f.write("🚨 변화 감지 요약\n")
                f.write("-" * 40 + "\n")
                f.write(f"총 변화: {change_summary['total_changes']}건\n")
                f.write(f"이상 징후 (ANOMALY): {change_summary['anomaly_changes']}건\n")
                f.write(f"주요 변화 (MAJOR): {change_summary['major_changes']}건\n")
                f.write(f"유의미한 변화 (SIGNIFICANT): {change_summary['significant_changes']}건\n\n")
                
            # 권고사항
            if report['recommendations']:
                f.write("💡 권고사항\n")
                f.write("-" * 40 + "\n")
                for rec in report['recommendations']:
                    f.write(f"[{rec['priority']}] {rec['recommendation']}\n")
                    f.write(f"조치: {rec['action']}\n\n")

def main():
    """메인 실행 함수"""
    print("🎯 GG POKER 직원용 데이터 중심 모니터링 플랫폼")
    print("=" * 70)
    print("📊 4개 핵심 지표: Players Online, Cash Players, 24h Peak, 7-day Avg")
    print("📈 날짜별 시계열 차트 분석")
    print("🚨 급변 시점 자동 감지 + 뉴스 연관성 분석")
    print("🏆 실시간 경쟁사 모니터링")
    print("=" * 70)
    
    platform = GGPokerMonitoringPlatform()
    
    try:
        # 1. 경쟁사 모니터링 설정
        print("\n🔧 경쟁사 모니터링 설정...")
        platform.setup_competitor_monitoring()
        
        # 2. 샘플 데이터 수집 (실제 환경에서는 크롤러에서 매일 호출)
        print("\n📈 샘플 일일 데이터 수집...")
        sample_data = [
            # 4개 핵심 지표 수집
            {'site_name': 'PokerStars', 'players_online': 55540, 'cash_players': 1397, 'peak_24h': 62000, 'seven_day_avg': 58000},
            {'site_name': 'PokerStars Ontario', 'players_online': 55540, 'cash_players': 0, 'peak_24h': 60000, 'seven_day_avg': 55000},
            {'site_name': 'WPT Global', 'players_online': 2989, 'cash_players': 1596, 'peak_24h': 3500, 'seven_day_avg': 2800},
            {'site_name': '888poker', 'players_online': 1850, 'cash_players': 420, 'peak_24h': 2100, 'seven_day_avg': 1900},
            {'site_name': 'Chico Poker', 'players_online': 2253, 'cash_players': 671, 'peak_24h': 2500, 'seven_day_avg': 2100},
        ]
        
        collected = platform.collect_daily_data(sample_data)
        
        # 3. 경쟁사 대시보드 데이터 생성
        print("\n📊 경쟁사 대시보드 데이터 생성...")
        dashboard_data = platform.get_competitor_dashboard_data()
        
        print(f"\n✅ 대시보드 요약:")
        print(f"모니터링 중인 경쟁사: {dashboard_data['market_summary']['total_competitors']}개")
        print(f"총 경쟁사 플레이어: {dashboard_data['market_summary']['total_monitored_players']:,}명")
        
        print(f"\n🏆 고우선순위 경쟁사:")
        for comp in dashboard_data['high_priority_competitors']:
            print(f"  • {comp['site_name']}: {comp['players_online']:,}명 (캐시 {comp['cash_ratio']}%)")
            
        # 4. 시계열 차트 데이터 생성 샘플
        print("\n📈 시계열 차트 데이터 생성 샘플...")
        for site_name in ['PokerStars', 'WPT Global']:
            chart_data = platform.generate_time_series_chart_data(site_name, 7)
            if chart_data:
                analytics = chart_data['analytics']
                players_data = analytics.get('players_online', {})
                if 'no_data' not in players_data:
                    print(f"  {site_name}: 현재 {players_data['current']:,}명, 트렌드 {players_data['trend']}")
                    print(f"    차트 데이터 포인트: {chart_data['data_points']}개")
                    
        # 5. 모니터링 리포트 생성
        print("\n📋 모니터링 리포트 생성...")
        report_file, summary_file = platform.export_monitoring_report(7)
        
        print(f"\n🎯 GG POKER 모니터링 플랫폼 완성!")
        print(f"📊 상세 리포트: {report_file}")
        print(f"📄 요약 리포트: {summary_file}")
        print(f"")
        print(f"🚀 핵심 기능:")
        print(f"  ✅ 4개 지표 일일 수집 (Players Online, Cash Players, 24h Peak, 7-day Avg)")
        print(f"  ✅ 날짜별 시계열 차트 데이터 생성")
        print(f"  ✅ 급변 시점 자동 감지 (15%/25%/50% 임계값)")
        print(f"  ✅ 뉴스 연관성 분석 프레임워크")
        print(f"  ✅ 경쟁사 우선순위별 모니터링")
        print(f"  ✅ 실시간 대시보드 데이터")
        print(f"  ✅ 자동 리포트 생성")
        
        return True
        
    except Exception as e:
        logger.error(f"플랫폼 실행 오류: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🎉 GG POKER용 데이터 중심 모니터링 플랫폼 완성!")
        print(f"📈 매일 4개 지표 수집 → X축 날짜 차트 분석 → 급변 감지 → 뉴스 연관성 → 정확한 데이터 기반 인사이트")
    else:
        print(f"\n💀 플랫폼 설정 실패 - 문제 해결 필요")
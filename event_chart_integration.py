#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
포커 차트에 이벤트 통합 시스템
- 차트 포인트 형식: 특정 날짜에 발생한 이벤트
- 기간 형식: 대회 기간 등 여러 날에 걸친 이벤트
- PokerNews 대회/프로모션 자동 감지 및 차트 표시
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import json
import sqlite3
from datetime import datetime, timedelta
import re
from collections import defaultdict

class EventChartIntegration:
    def __init__(self, db_path='gg_poker_monitoring.db'):
        self.db_path = db_path
        self.setup_event_tables()
        
    def setup_event_tables(self):
        """이벤트 관련 테이블 설정"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 포인트 이벤트 (특정 날짜)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS point_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_date DATE NOT NULL,
                event_title TEXT NOT NULL,
                event_type TEXT NOT NULL,
                affected_sites TEXT,
                impact_level TEXT,
                chart_color TEXT,
                chart_symbol TEXT,
                description TEXT,
                news_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 기간 이벤트 (시작-종료 날짜)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS period_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                event_title TEXT NOT NULL,
                event_type TEXT NOT NULL,
                affected_sites TEXT,
                impact_level TEXT,
                chart_color TEXT,
                background_color TEXT,
                description TEXT,
                news_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def detect_tournament_events(self, news_data):
        """토너먼트 이벤트 감지 및 분류"""
        tournament_patterns = {
            # 포인트 이벤트 (특정 날짜)
            'final_table': {
                'keywords': ['Final Table', 'finale', 'winner', 'champion'],
                'type': 'POINT',
                'impact': 'HIGH',
                'color': '#FF0000',
                'symbol': '🏆'
            },
            'announcement': {
                'keywords': ['announced', 'schedule', 'released', 'unveiled'],
                'type': 'POINT', 
                'impact': 'MEDIUM',
                'color': '#0066FF',
                'symbol': '📢'
            },
            'satellite': {
                'keywords': ['satellite', 'qualifier', 'qualify'],
                'type': 'POINT',
                'impact': 'MEDIUM',
                'color': '#FF6600',
                'symbol': '🎯'
            },
            
            # 기간 이벤트 (여러 날)
            'series': {
                'keywords': ['SCOOP', 'WCOOP', 'series', 'festival', 'championship'],
                'type': 'PERIOD',
                'impact': 'HIGH',
                'color': '#FF0000',
                'background': '#FF000020'
            },
            'promotion': {
                'keywords': ['promotion', 'bonus', 'leaderboard', 'race'],
                'type': 'PERIOD',
                'impact': 'MEDIUM',
                'color': '#9900FF',
                'background': '#9900FF20'
            }
        }
        
        site_mapping = {
            'pokerstars': 'PokerStars',
            'gg poker': 'GGNetwork',
            'ggpoker': 'GGNetwork',
            'wpt global': 'WPT Global',
            '888poker': '888poker',
            'partypoker': 'partypoker'
        }
        
        point_events = []
        period_events = []
        
        for news in news_data:
            title = news.get('title', '').lower()
            content = news.get('content', '').lower()
            date = news.get('date', datetime.now().strftime('%Y-%m-%d'))
            url = news.get('url', '')
            
            full_text = f"{title} {content}"
            
            # 영향받는 사이트 감지
            affected_sites = []
            for keyword, site in site_mapping.items():
                if keyword in full_text:
                    affected_sites.append(site)
            
            if not affected_sites:
                continue
                
            # 이벤트 패턴 매칭
            for pattern_name, pattern_info in tournament_patterns.items():
                if any(keyword in full_text for keyword in pattern_info['keywords']):
                    
                    if pattern_info['type'] == 'POINT':
                        point_events.append({
                            'event_date': date,
                            'event_title': news.get('title', ''),
                            'event_type': pattern_name.upper(),
                            'affected_sites': ','.join(affected_sites),
                            'impact_level': pattern_info['impact'],
                            'chart_color': pattern_info['color'],
                            'chart_symbol': pattern_info['symbol'],
                            'description': content[:200] + '...' if len(content) > 200 else content,
                            'news_url': url
                        })
                        
                    elif pattern_info['type'] == 'PERIOD':
                        # 기간 추정 (실제로는 뉴스 내용 파싱으로 정확한 날짜 추출)
                        start_date = date
                        end_date = self.estimate_event_end_date(date, pattern_name)
                        
                        period_events.append({
                            'start_date': start_date,
                            'end_date': end_date,
                            'event_title': news.get('title', ''),
                            'event_type': pattern_name.upper(),
                            'affected_sites': ','.join(affected_sites),
                            'impact_level': pattern_info['impact'],
                            'chart_color': pattern_info['color'],
                            'background_color': pattern_info['background'],
                            'description': content[:200] + '...' if len(content) > 200 else content,
                            'news_url': url
                        })
                    
                    break  # 첫 번째 매칭된 패턴만 사용
        
        return point_events, period_events
    
    def estimate_event_end_date(self, start_date, event_type):
        """이벤트 종료 날짜 추정"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        
        duration_map = {
            'series': 14,      # 시리즈는 보통 2주
            'promotion': 7,    # 프로모션은 보통 1주
            'festival': 10,    # 페스티벌은 보통 10일
            'championship': 5  # 챔피언십은 보통 5일
        }
        
        duration = duration_map.get(event_type, 7)  # 기본 7일
        end = start + timedelta(days=duration)
        
        return end.strftime('%Y-%m-%d')
    
    def save_events(self, point_events, period_events):
        """이벤트를 데이터베이스에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 포인트 이벤트 저장
        for event in point_events:
            cursor.execute('''
                INSERT OR REPLACE INTO point_events 
                (event_date, event_title, event_type, affected_sites, impact_level,
                 chart_color, chart_symbol, description, news_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event['event_date'], event['event_title'], event['event_type'],
                event['affected_sites'], event['impact_level'], event['chart_color'],
                event['chart_symbol'], event['description'], event['news_url']
            ))
        
        # 기간 이벤트 저장
        for event in period_events:
            cursor.execute('''
                INSERT OR REPLACE INTO period_events 
                (start_date, end_date, event_title, event_type, affected_sites, 
                 impact_level, chart_color, background_color, description, news_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event['start_date'], event['end_date'], event['event_title'],
                event['event_type'], event['affected_sites'], event['impact_level'],
                event['chart_color'], event['background_color'], event['description'],
                event['news_url']
            ))
        
        conn.commit()
        conn.close()
        
        return len(point_events), len(period_events)
    
    def get_chart_events(self, start_date, end_date):
        """차트용 이벤트 데이터 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 포인트 이벤트 조회
        cursor.execute('''
            SELECT event_date, event_title, event_type, affected_sites,
                   impact_level, chart_color, chart_symbol, description
            FROM point_events 
            WHERE event_date BETWEEN ? AND ?
            ORDER BY event_date
        ''', (start_date, end_date))
        
        point_events = []
        for row in cursor.fetchall():
            point_events.append({
                'type': 'point',
                'date': row[0],
                'title': row[1],
                'event_type': row[2],
                'sites': row[3].split(',') if row[3] else [],
                'impact': row[4],
                'color': row[5],
                'symbol': row[6],
                'description': row[7]
            })
        
        # 기간 이벤트 조회
        cursor.execute('''
            SELECT start_date, end_date, event_title, event_type, affected_sites,
                   impact_level, chart_color, background_color, description
            FROM period_events 
            WHERE start_date <= ? AND end_date >= ?
            ORDER BY start_date
        ''', (end_date, start_date))
        
        period_events = []
        for row in cursor.fetchall():
            period_events.append({
                'type': 'period',
                'start_date': row[0],
                'end_date': row[1],
                'title': row[2],
                'event_type': row[3],
                'sites': row[4].split(',') if row[4] else [],
                'impact': row[5],
                'color': row[6],
                'background_color': row[7],
                'description': row[8]
            })
        
        conn.close()
        
        return {
            'point_events': point_events,
            'period_events': period_events
        }
    
    def generate_enhanced_chart_data(self, site_name, days_back=30):
        """이벤트가 통합된 차트 데이터 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기본 트래픽 데이터
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
            ORDER BY collection_date
        '''
        
        cursor.execute(query, (site_name, days_back))
        traffic_data = cursor.fetchall()
        
        if not traffic_data:
            return None
        
        # 날짜 범위 계산
        start_date = traffic_data[0][0]
        end_date = traffic_data[-1][0]
        
        # 이벤트 데이터 조회
        events = self.get_chart_events(start_date, end_date)
        
        # 차트 데이터 구성
        chart_data = {
            'site_name': site_name,
            'period_days': days_back,
            'labels': [],
            'datasets': {
                'players_online': {
                    'label': 'Players Online',
                    'data': [],
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'pointRadius': []  # 이벤트가 있는 날은 포인트 크기 조정
                },
                'cash_players': {
                    'label': 'Cash Players', 
                    'data': [],
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'pointRadius': []
                },
                'peak_24h': {
                    'label': '24h Peak',
                    'data': [],
                    'borderColor': 'rgb(54, 162, 235)',
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'pointRadius': []
                },
                'seven_day_avg': {
                    'label': '7-day Average',
                    'data': [],
                    'borderColor': 'rgb(255, 206, 86)',
                    'backgroundColor': 'rgba(255, 206, 86, 0.2)',
                    'pointRadius': []
                }
            },
            'events': events,
            'annotations': []  # Chart.js 어노테이션용
        }
        
        # 이벤트 날짜 맵 생성
        event_dates = set()
        for event in events['point_events']:
            if site_name in event['sites']:
                event_dates.add(event['date'])
        
        # 트래픽 데이터와 이벤트 통합
        for row in traffic_data:
            date, players, cash, peak, avg = row
            chart_data['labels'].append(date)
            
            # 이벤트가 있는 날은 포인트 크기 증가
            point_size = 8 if date in event_dates else 3
            
            chart_data['datasets']['players_online']['data'].append(players or 0)
            chart_data['datasets']['players_online']['pointRadius'].append(point_size)
            
            chart_data['datasets']['cash_players']['data'].append(cash or 0)
            chart_data['datasets']['cash_players']['pointRadius'].append(point_size)
            
            chart_data['datasets']['peak_24h']['data'].append(peak or 0)
            chart_data['datasets']['peak_24h']['pointRadius'].append(point_size)
            
            chart_data['datasets']['seven_day_avg']['data'].append(avg or 0)
            chart_data['datasets']['seven_day_avg']['pointRadius'].append(point_size)
        
        # Chart.js 어노테이션 생성
        for event in events['point_events']:
            if site_name in event['sites']:
                chart_data['annotations'].append({
                    'type': 'line',
                    'mode': 'vertical',
                    'scaleID': 'x',
                    'value': event['date'],
                    'borderColor': event['color'],
                    'borderWidth': 2,
                    'label': {
                        'content': event['symbol'] + ' ' + event['title'],
                        'enabled': True,
                        'position': 'top'
                    }
                })
        
        # 기간 이벤트를 배경 영역으로 추가
        for event in events['period_events']:
            if site_name in event['sites']:
                chart_data['annotations'].append({
                    'type': 'box',
                    'xMin': event['start_date'],
                    'xMax': event['end_date'],
                    'backgroundColor': event['background_color'],
                    'borderColor': event['color'],
                    'borderWidth': 1,
                    'label': {
                        'content': event['title'],
                        'enabled': True,
                        'position': 'center'
                    }
                })
        
        conn.close()
        return chart_data
    
    def create_event_timeline(self, days_back=30):
        """이벤트 타임라인 생성"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        events = self.get_chart_events(start_date, end_date)
        
        timeline = []
        
        # 포인트 이벤트 추가
        for event in events['point_events']:
            timeline.append({
                'date': event['date'],
                'type': 'point',
                'title': event['title'],
                'sites': event['sites'],
                'impact': event['impact'],
                'color': event['color'],
                'symbol': event['symbol']
            })
        
        # 기간 이벤트 추가
        for event in events['period_events']:
            timeline.append({
                'date': event['start_date'],
                'type': 'period_start',
                'title': f"{event['title']} (시작)",
                'sites': event['sites'],
                'impact': event['impact'],
                'color': event['color'],
                'end_date': event['end_date']
            })
            
            timeline.append({
                'date': event['end_date'],
                'type': 'period_end',
                'title': f"{event['title']} (종료)",
                'sites': event['sites'],
                'impact': event['impact'],
                'color': event['color'],
                'start_date': event['start_date']
            })
        
        # 날짜순 정렬
        timeline.sort(key=lambda x: x['date'])
        
        return timeline

def main():
    """테스트 실행"""
    print("🎯 이벤트-차트 통합 시스템 테스트...")
    
    integration = EventChartIntegration()
    
    # 샘플 뉴스 데이터
    sample_news = [
        {
            'title': 'PokerStars SCOOP 2024 Schedule Announced',
            'content': 'The Spring Championship of Online Poker returns with 85 events and $85 million in guarantees from May 5-26',
            'date': '2024-07-10',
            'url': 'https://pokernews.com/news/2024/07/pokerstars-scoop-announced.htm'
        },
        {
            'title': 'GGPoker WSOP Satellite Winner Crowned',
            'content': 'Player from Canada wins main event satellite tournament securing $10,000 seat',
            'date': '2024-07-15',
            'url': 'https://pokernews.com/news/2024/07/ggpoker-satellite-winner.htm'
        },
        {
            'title': 'WPT Global Summer Festival Final Table Set',
            'content': 'Nine players remain in the $5 million guaranteed main event with final table starting tomorrow',
            'date': '2024-07-18',
            'url': 'https://pokernews.com/news/2024/07/wpt-final-table.htm'
        },
        {
            'title': '888poker Summer Promotion Launches',
            'content': 'Massive $2 million leaderboard race runs through August with daily satellites and bonus rewards',
            'date': '2024-07-12',
            'url': 'https://pokernews.com/news/2024/07/888poker-summer-promo.htm'
        }
    ]
    
    # 이벤트 감지
    point_events, period_events = integration.detect_tournament_events(sample_news)
    
    print(f"✅ 포인트 이벤트 감지: {len(point_events)}개")
    print(f"✅ 기간 이벤트 감지: {len(period_events)}개")
    
    # 이벤트 저장
    saved_point, saved_period = integration.save_events(point_events, period_events)
    print(f"💾 저장 완료 - 포인트: {saved_point}개, 기간: {saved_period}개")
    
    # 이벤트 타임라인 생성
    timeline = integration.create_event_timeline(30)
    print(f"📅 이벤트 타임라인: {len(timeline)}개 항목")
    
    # 샘플 차트 데이터 생성
    chart_data = integration.generate_enhanced_chart_data('PokerStars', 30)
    if chart_data:
        print(f"📊 차트 데이터 생성 완료:")
        print(f"  - 데이터 포인트: {len(chart_data['labels'])}개")
        print(f"  - 포인트 이벤트: {len(chart_data['events']['point_events'])}개")
        print(f"  - 기간 이벤트: {len(chart_data['events']['period_events'])}개")
        print(f"  - 차트 어노테이션: {len(chart_data['annotations'])}개")
    
    return True

if __name__ == "__main__":
    main()
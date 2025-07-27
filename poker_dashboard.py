#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
포커 사이트 데이터 시각화 대시보드
- 5가지 차트 타입을 탭으로 제공
- PokerNews 이벤트 연동으로 차트에 이벤트 표시
- 대회/프로모션 등 주요 이벤트를 차트 포인트로 시각화
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import json
import sqlite3
from datetime import datetime, timedelta
import re
from collections import defaultdict

class PokerDashboard:
    def __init__(self, db_path='gg_poker_monitoring.db'):
        self.db_path = db_path
        self.setup_event_tracking()
        
    def setup_event_tracking(self):
        """이벤트 추적을 위한 테이블 설정"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 포커 이벤트 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS poker_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_date DATE NOT NULL,
                event_type TEXT NOT NULL,
                event_title TEXT NOT NULL,
                affected_sites TEXT,
                event_description TEXT,
                news_source TEXT,
                news_url TEXT,
                impact_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def detect_news_events(self, news_data):
        """뉴스에서 대회/이벤트 자동 감지"""
        tournament_keywords = [
            'WSOP', 'SCOOP', 'WCOOP', 'EPT', 'WPT', 'MILLIONS', 
            'Championship', 'Festival', 'Series', 'Tournament',
            'Satellite', 'Qualifier', 'Final Table', 'Main Event'
        ]
        
        promo_keywords = [
            'Promotion', 'Bonus', 'Freeroll', 'Jackpot', 'Leaderboard',
            'Rake Race', 'Cashback', 'Deposit', 'Welcome'
        ]
        
        site_keywords = {
            'PokerStars': ['PokerStars', 'pokerstars'],
            'GGNetwork': ['GGPoker', 'GG Poker', 'GGNetwork', 'GG Network'],
            'WPT Global': ['WPT Global', 'WPT'],
            '888poker': ['888poker', '888'],
            'partypoker': ['partypoker', 'party poker']
        }
        
        detected_events = []
        
        for news in news_data:
            title = news.get('title', '')
            content = news.get('content', '')
            date = news.get('date', datetime.now().strftime('%Y-%m-%d'))
            url = news.get('url', '')
            
            # 이벤트 타입 감지
            event_type = None
            impact_level = 'LOW'
            
            title_lower = title.lower()
            content_lower = content.lower()
            full_text = f"{title_lower} {content_lower}"
            
            # 토너먼트 감지
            for keyword in tournament_keywords:
                if keyword.lower() in full_text:
                    event_type = 'TOURNAMENT'
                    if keyword in ['WSOP', 'SCOOP', 'WCOOP', 'EPT']:
                        impact_level = 'HIGH'
                    elif keyword in ['Championship', 'Main Event']:
                        impact_level = 'MEDIUM'
                    break
            
            # 프로모션 감지
            if not event_type:
                for keyword in promo_keywords:
                    if keyword.lower() in full_text:
                        event_type = 'PROMOTION'
                        impact_level = 'MEDIUM'
                        break
            
            # 사이트 연관성 감지
            affected_sites = []
            for site, keywords in site_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in full_text:
                        affected_sites.append(site)
                        break
            
            if event_type and affected_sites:
                detected_events.append({
                    'event_date': date,
                    'event_type': event_type,
                    'event_title': title,
                    'affected_sites': ','.join(affected_sites),
                    'event_description': content[:200] + '...' if len(content) > 200 else content,
                    'news_source': 'PokerNews',
                    'news_url': url,
                    'impact_level': impact_level
                })
        
        return detected_events
    
    def save_events(self, events):
        """이벤트를 데이터베이스에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for event in events:
            cursor.execute('''
                INSERT OR REPLACE INTO poker_events 
                (event_date, event_type, event_title, affected_sites, 
                 event_description, news_source, news_url, impact_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event['event_date'],
                event['event_type'],
                event['event_title'],
                event['affected_sites'],
                event['event_description'],
                event['news_source'],
                event['news_url'],
                event['impact_level']
            ))
        
        conn.commit()
        conn.close()
        
    def generate_multi_line_chart(self, days_back=30):
        """탭 1: 멀티 라인 차트 (트렌드 분석)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 날짜별 데이터 조회
        query = '''
            SELECT 
                collection_date,
                site_name,
                players_online,
                cash_players,
                peak_24h,
                seven_day_avg
            FROM daily_traffic 
            WHERE collection_date >= date('now', '-' || ? || ' days')
            ORDER BY collection_date, site_name
        '''
        
        cursor.execute(query, (days_back,))
        results = cursor.fetchall()
        
        # 이벤트 데이터 조회
        cursor.execute('''
            SELECT event_date, event_title, event_type, affected_sites, impact_level
            FROM poker_events 
            WHERE event_date >= date('now', '-' || ? || ' days')
            ORDER BY event_date
        ''', (days_back,))
        events = cursor.fetchall()
        
        # 차트 데이터 구성
        chart_data = {
            'chart_type': 'multi_line',
            'title': '포커 사이트 트렌드 분석',
            'dates': [],
            'sites': {},
            'events': [],
            'metrics': ['players_online', 'cash_players', 'peak_24h', 'seven_day_avg']
        }
        
        # 데이터 정리
        data_by_date = defaultdict(dict)
        for row in results:
            date, site, players, cash, peak, avg = row
            if date not in chart_data['dates']:
                chart_data['dates'].append(date)
            
            if site not in chart_data['sites']:
                chart_data['sites'][site] = {
                    'players_online': [],
                    'cash_players': [],
                    'peak_24h': [],
                    'seven_day_avg': []
                }
            
            data_by_date[date][site] = {
                'players_online': players or 0,
                'cash_players': cash or 0,
                'peak_24h': peak or 0,
                'seven_day_avg': avg or 0
            }
        
        # 날짜별로 모든 사이트 데이터 정렬
        chart_data['dates'].sort()
        for date in chart_data['dates']:
            for site in chart_data['sites']:
                site_data = data_by_date[date].get(site, {})
                for metric in chart_data['metrics']:
                    chart_data['sites'][site][metric].append(site_data.get(metric, 0))
        
        # 이벤트 데이터 추가
        for event in events:
            event_date, title, event_type, affected_sites, impact = event
            chart_data['events'].append({
                'date': event_date,
                'title': title,
                'type': event_type,
                'sites': affected_sites.split(',') if affected_sites else [],
                'impact': impact,
                'color': self.get_event_color(event_type, impact)
            })
        
        conn.close()
        return chart_data
    
    def generate_radar_chart(self):
        """탭 2: 레이더 차트 (현재 상태 비교)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 최근 데이터 조회
        query = '''
            SELECT 
                site_name,
                players_online,
                cash_players,
                peak_24h,
                seven_day_avg
            FROM daily_traffic 
            WHERE collection_date = (SELECT MAX(collection_date) FROM daily_traffic)
            ORDER BY players_online DESC
        '''
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # 정규화를 위한 최대값 계산
        max_values = {
            'players_online': 0,
            'cash_players': 0,
            'peak_24h': 0,
            'seven_day_avg': 0
        }
        
        for row in results:
            max_values['players_online'] = max(max_values['players_online'], row[1] or 0)
            max_values['cash_players'] = max(max_values['cash_players'], row[2] or 0)
            max_values['peak_24h'] = max(max_values['peak_24h'], row[3] or 0)
            max_values['seven_day_avg'] = max(max_values['seven_day_avg'], row[4] or 0)
        
        chart_data = {
            'chart_type': 'radar',
            'title': '포커 사이트 현재 상태 비교',
            'metrics': ['Players Online', 'Cash Players', '24h Peak', '7-day Average'],
            'sites': [],
            'max_values': max_values
        }
        
        for row in results:
            site_name, players, cash, peak, avg = row
            
            # 0-100 스케일로 정규화
            normalized_data = [
                (players / max_values['players_online'] * 100) if max_values['players_online'] > 0 else 0,
                (cash / max_values['cash_players'] * 100) if max_values['cash_players'] > 0 else 0,
                (peak / max_values['peak_24h'] * 100) if max_values['peak_24h'] > 0 else 0,
                (avg / max_values['seven_day_avg'] * 100) if max_values['seven_day_avg'] > 0 else 0
            ]
            
            chart_data['sites'].append({
                'name': site_name,
                'data': normalized_data,
                'raw_data': [players or 0, cash or 0, peak or 0, avg or 0]
            })
        
        conn.close()
        return chart_data
    
    def generate_heatmap_chart(self, days_back=30):
        """탭 3: 히트맵 (변화 감지)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 일별 변화율 계산
        query = '''
            WITH daily_data AS (
                SELECT 
                    site_name,
                    collection_date,
                    players_online,
                    LAG(players_online) OVER (PARTITION BY site_name ORDER BY collection_date) as prev_players
                FROM daily_traffic 
                WHERE collection_date >= date('now', '-' || ? || ' days')
                ORDER BY site_name, collection_date
            )
            SELECT 
                site_name,
                collection_date,
                players_online,
                prev_players,
                CASE 
                    WHEN prev_players > 0 THEN 
                        ROUND(((players_online - prev_players) * 100.0 / prev_players), 2)
                    ELSE 0 
                END as change_pct
            FROM daily_data
            WHERE prev_players IS NOT NULL
        '''
        
        cursor.execute(query, (days_back,))
        results = cursor.fetchall()
        
        chart_data = {
            'chart_type': 'heatmap',
            'title': '포커 사이트 일별 변화율 히트맵',
            'dates': [],
            'sites': [],
            'data': []
        }
        
        # 데이터 정리
        heatmap_data = {}
        dates_set = set()
        sites_set = set()
        
        for row in results:
            site, date, players, prev_players, change_pct = row
            dates_set.add(date)
            sites_set.add(site)
            
            if site not in heatmap_data:
                heatmap_data[site] = {}
            heatmap_data[site][date] = change_pct
        
        chart_data['dates'] = sorted(list(dates_set))
        chart_data['sites'] = sorted(list(sites_set))
        
        # 히트맵 매트릭스 생성
        for site in chart_data['sites']:
            site_row = []
            for date in chart_data['dates']:
                change_pct = heatmap_data.get(site, {}).get(date, 0)
                site_row.append(change_pct)
            chart_data['data'].append(site_row)
        
        conn.close()
        return chart_data
    
    def generate_bubble_chart(self):
        """탭 4: 버블 차트 (4차원 분석)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                site_name,
                collection_date,
                players_online,
                cash_players,
                peak_24h,
                seven_day_avg
            FROM daily_traffic 
            WHERE collection_date >= date('now', '-7 days')
            ORDER BY collection_date DESC
        '''
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        chart_data = {
            'chart_type': 'bubble',
            'title': '포커 사이트 4차원 분석 (최근 7일)',
            'datasets': []
        }
        
        # 사이트별 데이터 그룹화
        site_data = defaultdict(list)
        for row in results:
            site, date, players, cash, peak, avg = row
            site_data[site].append({
                'date': date,
                'x': players or 0,  # X축: Players Online
                'y': cash or 0,     # Y축: Cash Players
                'r': (peak or 0) / 1000,  # 버블 크기: 24h Peak (스케일 조정)
                'avg': avg or 0     # 색상: 7-day Average
            })
        
        # 사이트별 데이터셋 생성
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        for i, (site, data) in enumerate(site_data.items()):
            chart_data['datasets'].append({
                'label': site,
                'data': data,
                'backgroundColor': colors[i % len(colors)],
                'borderColor': colors[i % len(colors)]
            })
        
        conn.close()
        return chart_data
    
    def generate_stacked_bar_chart(self, days_back=30):
        """탭 5: 스택 바 차트 (시장 점유율)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                collection_date,
                site_name,
                players_online
            FROM daily_traffic 
            WHERE collection_date >= date('now', '-' || ? || ' days')
            AND players_online > 0
            ORDER BY collection_date, players_online DESC
        '''
        
        cursor.execute(query, (days_back,))
        results = cursor.fetchall()
        
        chart_data = {
            'chart_type': 'stacked_bar',
            'title': '포커 사이트 시장 점유율 추이',
            'dates': [],
            'sites': set(),
            'datasets': []
        }
        
        # 데이터 정리
        data_by_date = defaultdict(dict)
        for row in results:
            date, site, players = row
            data_by_date[date][site] = players
            chart_data['sites'].add(site)
        
        chart_data['dates'] = sorted(data_by_date.keys())
        chart_data['sites'] = sorted(list(chart_data['sites']))
        
        # 각 사이트별 데이터셋 생성
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF']
        
        for i, site in enumerate(chart_data['sites']):
            site_data = []
            for date in chart_data['dates']:
                players = data_by_date[date].get(site, 0)
                site_data.append(players)
            
            chart_data['datasets'].append({
                'label': site,
                'data': site_data,
                'backgroundColor': colors[i % len(colors)],
                'borderColor': colors[i % len(colors)],
                'borderWidth': 1
            })
        
        conn.close()
        return chart_data
    
    def get_event_color(self, event_type, impact_level):
        """이벤트 타입과 임팩트에 따른 색상 반환"""
        color_map = {
            ('TOURNAMENT', 'HIGH'): '#FF0000',    # 빨강 - 주요 토너먼트
            ('TOURNAMENT', 'MEDIUM'): '#FF6600',  # 주황 - 중간 토너먼트
            ('TOURNAMENT', 'LOW'): '#FFCC00',     # 노랑 - 일반 토너먼트
            ('PROMOTION', 'HIGH'): '#0066FF',     # 파랑 - 주요 프로모션
            ('PROMOTION', 'MEDIUM'): '#6699FF',   # 연파랑 - 중간 프로모션
            ('PROMOTION', 'LOW'): '#99CCFF',      # 연한파랑 - 일반 프로모션
            ('NEWS', 'HIGH'): '#FF00FF',          # 자주 - 주요 뉴스
            ('NEWS', 'MEDIUM'): '#FF66FF',        # 연자주 - 일반 뉴스
            ('NEWS', 'LOW'): '#FFCCFF'            # 연한자주 - 기타 뉴스
        }
        
        return color_map.get((event_type, impact_level), '#CCCCCC')
    
    def generate_dashboard_html(self, output_file='poker_dashboard.html'):
        """HTML 대시보드 생성"""
        # 모든 차트 데이터 생성
        charts = {
            'multi_line': self.generate_multi_line_chart(),
            'radar': self.generate_radar_chart(),
            'heatmap': self.generate_heatmap_chart(),
            'bubble': self.generate_bubble_chart(),
            'stacked_bar': self.generate_stacked_bar_chart()
        }
        
        html_template = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>포커 사이트 데이터 대시보드</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .dashboard { max-width: 1200px; margin: 0 auto; }
        .tabs { display: flex; background: white; border-radius: 8px 8px 0 0; overflow: hidden; }
        .tab { padding: 15px 25px; cursor: pointer; background: #e0e0e0; border: none; font-size: 16px; }
        .tab.active { background: #007bff; color: white; }
        .chart-container { background: white; padding: 20px; border-radius: 0 0 8px 8px; }
        .chart-wrapper { position: relative; height: 500px; }
        .events-legend { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; }
        .event-item { display: inline-block; margin: 5px 10px; padding: 5px 10px; border-radius: 15px; font-size: 12px; }
        h1 { text-align: center; color: #333; margin-bottom: 30px; }
        h2 { color: #007bff; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>🎯 포커 사이트 데이터 대시보드</h1>
        
        <div class="tabs">
            <button class="tab active" onclick="showChart('multi_line')">📈 트렌드 분석</button>
            <button class="tab" onclick="showChart('radar')">🎯 현재 비교</button>
            <button class="tab" onclick="showChart('heatmap')">🔥 변화 히트맵</button>
            <button class="tab" onclick="showChart('bubble')">💭 4차원 분석</button>
            <button class="tab" onclick="showChart('stacked_bar')">📊 시장 점유율</button>
        </div>
        
        <div class="chart-container">
            <div id="chart-multi_line" class="chart-content">
                <h2>📈 포커 사이트 트렌드 분석</h2>
                <div class="chart-wrapper">
                    <canvas id="multiLineChart"></canvas>
                </div>
                <div class="events-legend" id="eventsLegend"></div>
            </div>
            
            <div id="chart-radar" class="chart-content" style="display:none;">
                <h2>🎯 포커 사이트 현재 상태 비교</h2>
                <div class="chart-wrapper">
                    <canvas id="radarChart"></canvas>
                </div>
            </div>
            
            <div id="chart-heatmap" class="chart-content" style="display:none;">
                <h2>🔥 포커 사이트 일별 변화율 히트맵</h2>
                <div class="chart-wrapper">
                    <canvas id="heatmapChart"></canvas>
                </div>
            </div>
            
            <div id="chart-bubble" class="chart-content" style="display:none;">
                <h2>💭 포커 사이트 4차원 분석</h2>
                <div class="chart-wrapper">
                    <canvas id="bubbleChart"></canvas>
                </div>
            </div>
            
            <div id="chart-stacked_bar" class="chart-content" style="display:none;">
                <h2>📊 포커 사이트 시장 점유율 추이</h2>
                <div class="chart-wrapper">
                    <canvas id="stackedBarChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script>
        const chartData = ''' + json.dumps(charts, ensure_ascii=False) + ''';
        
        let charts = {};
        
        function showChart(chartType) {
            // 탭 활성화
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
            
            // 차트 컨텐츠 표시
            document.querySelectorAll('.chart-content').forEach(content => content.style.display = 'none');
            document.getElementById('chart-' + chartType).style.display = 'block';
            
            // 차트 초기화 (필요시)
            if (!charts[chartType]) {
                createChart(chartType);
            }
        }
        
        function createChart(chartType) {
            const data = chartData[chartType];
            
            switch(chartType) {
                case 'multi_line':
                    createMultiLineChart(data);
                    break;
                case 'radar':
                    createRadarChart(data);
                    break;
                case 'heatmap':
                    createHeatmapChart(data);
                    break;
                case 'bubble':
                    createBubbleChart(data);
                    break;
                case 'stacked_bar':
                    createStackedBarChart(data);
                    break;
            }
        }
        
        function createMultiLineChart(data) {
            const ctx = document.getElementById('multiLineChart').getContext('2d');
            const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'];
            
            const datasets = [];
            let colorIndex = 0;
            
            Object.keys(data.sites).forEach(site => {
                datasets.push({
                    label: site,
                    data: data.sites[site].players_online,
                    borderColor: colors[colorIndex % colors.length],
                    backgroundColor: colors[colorIndex % colors.length] + '20',
                    fill: false,
                    tension: 0.1
                });
                colorIndex++;
            });
            
            charts.multi_line = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.dates,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: { display: true, text: 'Players Online 트렌드' },
                        legend: { position: 'top' }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
            
            // 이벤트 범례 생성
            createEventsLegend(data.events);
        }
        
        function createEventsLegend(events) {
            const legend = document.getElementById('eventsLegend');
            legend.innerHTML = '<strong>📅 이벤트 범례:</strong><br>';
            
            events.forEach(event => {
                const eventDiv = document.createElement('div');
                eventDiv.className = 'event-item';
                eventDiv.style.backgroundColor = event.color;
                eventDiv.style.color = 'white';
                eventDiv.innerHTML = `${event.date}: ${event.title} (${event.type})`;
                legend.appendChild(eventDiv);
            });
        }
        
        function createRadarChart(data) {
            const ctx = document.getElementById('radarChart').getContext('2d');
            const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'];
            
            const datasets = data.sites.slice(0, 5).map((site, index) => ({
                label: site.name,
                data: site.data,
                borderColor: colors[index],
                backgroundColor: colors[index] + '40',
                pointBackgroundColor: colors[index],
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: colors[index]
            }));
            
            charts.radar = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: data.metrics,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
        
        function createBubbleChart(data) {
            const ctx = document.getElementById('bubbleChart').getContext('2d');
            
            charts.bubble = new Chart(ctx, {
                type: 'bubble',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { title: { display: true, text: 'Players Online' } },
                        y: { title: { display: true, text: 'Cash Players' } }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label + ': (' + 
                                           context.parsed.x + ', ' + 
                                           context.parsed.y + ')';
                                }
                            }
                        }
                    }
                }
            });
        }
        
        function createStackedBarChart(data) {
            const ctx = document.getElementById('stackedBarChart').getContext('2d');
            
            charts.stacked_bar = new Chart(ctx, {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { stacked: true },
                        y: { stacked: true }
                    }
                }
            });
        }
        
        // 초기 차트 로드
        document.addEventListener('DOMContentLoaded', function() {
            createChart('multi_line');
        });
    </script>
</body>
</html>
        '''
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_template)
            
        return output_file

def main():
    """샘플 실행"""
    print("🎯 포커 대시보드 생성...")
    
    dashboard = PokerDashboard()
    
    # 샘플 뉴스 이벤트 생성
    sample_news = [
        {
            'title': 'PokerStars SCOOP 2024 Main Event Final Table',
            'content': 'The biggest online poker tournament series continues with massive guarantees',
            'date': '2024-07-15',
            'url': 'https://pokernews.com/news/2024/07/pokerstars-scoop-main-event.htm'
        },
        {
            'title': 'GGPoker WSOP Satellite Promotion',
            'content': 'Win your seat to the World Series of Poker with special satellite tournaments',
            'date': '2024-07-18',
            'url': 'https://pokernews.com/news/2024/07/ggpoker-wsop-satellite.htm'
        },
        {
            'title': 'WPT Global Summer Festival',
            'content': 'Massive tournament series with over $50M guaranteed across all events',
            'date': '2024-07-10',
            'url': 'https://pokernews.com/news/2024/07/wpt-global-summer.htm'
        }
    ]
    
    # 이벤트 감지 및 저장
    events = dashboard.detect_news_events(sample_news)
    dashboard.save_events(events)
    
    print(f"✅ {len(events)}개 이벤트 감지 및 저장 완료")
    
    # HTML 대시보드 생성
    html_file = dashboard.generate_dashboard_html()
    print(f"📊 대시보드 생성 완료: {html_file}")
    
    return html_file

if __name__ == "__main__":
    main()
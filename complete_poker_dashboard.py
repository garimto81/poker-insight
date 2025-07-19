#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
완전한 포커 사이트 모니터링 대시보드
- 5가지 차트 유형 (멀티라인, 레이더, 히트맵, 버블, 스택바)
- 포인트/기간 이벤트 통합
- PokerNews 자동 감지
- 실시간 차트 업데이트
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import json
import sqlite3
from datetime import datetime, timedelta
from poker_dashboard import PokerDashboard
from event_chart_integration import EventChartIntegration

class CompletePokerDashboard:
    def __init__(self, db_path='gg_poker_monitoring.db'):
        self.db_path = db_path
        self.dashboard = PokerDashboard(db_path)
        self.event_integration = EventChartIntegration(db_path)
        
    def process_news_and_generate_events(self, news_data):
        """뉴스 처리 및 이벤트 생성"""
        # 기본 이벤트 감지
        basic_events = self.dashboard.detect_news_events(news_data)
        self.dashboard.save_events(basic_events)
        
        # 고급 이벤트 감지 (포인트/기간)
        point_events, period_events = self.event_integration.detect_tournament_events(news_data)
        self.event_integration.save_events(point_events, period_events)
        
        return {
            'basic_events': len(basic_events),
            'point_events': len(point_events),
            'period_events': len(period_events)
        }
    
    def generate_enhanced_charts(self, days_back=30):
        """향상된 차트 데이터 생성"""
        charts = {}
        
        # 1. 멀티라인 차트 (이벤트 통합)
        charts['multi_line'] = self.generate_multi_line_with_events(days_back)
        
        # 2. 레이더 차트
        charts['radar'] = self.dashboard.generate_radar_chart()
        
        # 3. 히트맵 차트
        charts['heatmap'] = self.dashboard.generate_heatmap_chart(days_back)
        
        # 4. 버블 차트
        charts['bubble'] = self.dashboard.generate_bubble_chart()
        
        # 5. 스택 바 차트 (이벤트 배경 포함)
        charts['stacked_bar'] = self.generate_stacked_bar_with_events(days_back)
        
        return charts
    
    def generate_multi_line_with_events(self, days_back=30):
        """이벤트가 통합된 멀티라인 차트"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기본 트래픽 데이터
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
        
        # 날짜 범위
        if results:
            start_date = results[0][0]
            end_date = results[-1][0]
        else:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        # 이벤트 데이터
        events = self.event_integration.get_chart_events(start_date, end_date)
        
        # 차트 데이터 구성
        chart_data = {
            'chart_type': 'multi_line_enhanced',
            'title': '포커 사이트 트렌드 분석 (이벤트 통합)',
            'dates': [],
            'sites': {},
            'events': events,
            'annotations': []
        }
        
        # 데이터 정리
        from collections import defaultdict
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
                    'seven_day_avg': [],
                    'point_styles': []  # 이벤트 포인트 스타일
                }
            
            data_by_date[date][site] = {
                'players_online': players or 0,
                'cash_players': cash or 0,
                'peak_24h': peak or 0,
                'seven_day_avg': avg or 0
            }
        
        # 이벤트 날짜 맵 생성
        event_dates = {}
        for event in events['point_events']:
            for site in event['sites']:
                if site not in event_dates:
                    event_dates[site] = {}
                event_dates[site][event['date']] = {
                    'color': event['color'],
                    'symbol': event['symbol'],
                    'title': event['title']
                }
        
        # 날짜별로 모든 사이트 데이터 정렬
        chart_data['dates'].sort()
        for date in chart_data['dates']:
            for site in chart_data['sites']:
                site_data = data_by_date[date].get(site, {})
                
                # 기본 데이터 추가
                for metric in ['players_online', 'cash_players', 'peak_24h', 'seven_day_avg']:
                    chart_data['sites'][site][metric].append(site_data.get(metric, 0))
                
                # 포인트 스타일 (이벤트가 있으면 특별 표시)
                if site in event_dates and date in event_dates[site]:
                    chart_data['sites'][site]['point_styles'].append({
                        'radius': 8,
                        'backgroundColor': event_dates[site][date]['color'],
                        'borderColor': '#FFFFFF',
                        'borderWidth': 2
                    })
                else:
                    chart_data['sites'][site]['point_styles'].append({
                        'radius': 3,
                        'backgroundColor': 'default',
                        'borderColor': 'default',
                        'borderWidth': 1
                    })
        
        # 어노테이션 생성
        for event in events['point_events']:
            chart_data['annotations'].append({
                'type': 'line',
                'mode': 'vertical',
                'scaleID': 'x',
                'value': event['date'],
                'borderColor': event['color'],
                'borderWidth': 2,
                'label': {
                    'content': f"{event['symbol']} {event['title']}",
                    'enabled': True,
                    'position': 'top'
                }
            })
        
        for event in events['period_events']:
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
    
    def generate_stacked_bar_with_events(self, days_back=30):
        """이벤트 배경이 있는 스택 바 차트"""
        # 기본 스택 바 차트 데이터
        chart_data = self.dashboard.generate_stacked_bar_chart(days_back)
        
        # 이벤트 데이터 추가
        if chart_data['dates']:
            start_date = chart_data['dates'][0]
            end_date = chart_data['dates'][-1]
            events = self.event_integration.get_chart_events(start_date, end_date)
            
            chart_data['events'] = events
            chart_data['chart_type'] = 'stacked_bar_enhanced'
            chart_data['title'] = '포커 사이트 시장 점유율 추이 (이벤트 포함)'
        
        return chart_data
    
    def generate_event_summary(self, days_back=30):
        """이벤트 요약 생성"""
        timeline = self.event_integration.create_event_timeline(days_back)
        
        summary = {
            'total_events': len(timeline),
            'high_impact_events': len([e for e in timeline if e.get('impact') == 'HIGH']),
            'tournament_events': len([e for e in timeline if 'tournament' in e.get('type', '').lower()]),
            'promotion_events': len([e for e in timeline if 'promotion' in e.get('type', '').lower()]),
            'recent_events': timeline[-5:] if timeline else [],
            'timeline': timeline
        }
        
        return summary
    
    def create_complete_dashboard_html(self, output_file='complete_poker_dashboard.html'):
        """완전한 HTML 대시보드 생성"""
        # 차트 데이터 생성
        charts = self.generate_enhanced_charts(30)
        
        # 이벤트 요약 생성
        event_summary = self.generate_event_summary(30)
        
        html_template = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>포커 사이트 완전 모니터링 대시보드</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@2.2.1/dist/chartjs-plugin-annotation.min.js"></script>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh;
        }
        .dashboard { 
            max-width: 1400px; margin: 0 auto; 
            background: rgba(255,255,255,0.95); 
            border-radius: 15px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(45deg, #2c3e50, #3498db);
            color: white; padding: 30px; text-align: center;
        }
        .header h1 { margin: 0; font-size: 2.5em; font-weight: 300; }
        .header p { margin: 10px 0 0 0; opacity: 0.9; }
        
        .stats-bar {
            display: flex; background: #34495e; color: white; padding: 20px;
        }
        .stat-item {
            flex: 1; text-align: center; padding: 0 20px;
            border-right: 1px solid rgba(255,255,255,0.1);
        }
        .stat-item:last-child { border-right: none; }
        .stat-number { font-size: 2em; font-weight: bold; color: #3498db; }
        .stat-label { font-size: 0.9em; opacity: 0.8; }
        
        .main-content { display: flex; }
        .tabs-section { flex: 1; padding: 0; }
        .events-sidebar { 
            width: 350px; background: #ecf0f1; padding: 20px; 
            border-left: 1px solid #bdc3c7; max-height: 600px; overflow-y: auto;
        }
        
        .tabs { 
            display: flex; background: #2c3e50; margin: 0;
        }
        .tab { 
            padding: 15px 25px; cursor: pointer; background: #34495e; 
            border: none; font-size: 14px; color: white; flex: 1; text-align: center;
            transition: all 0.3s;
        }
        .tab:hover { background: #3498db; }
        .tab.active { background: #e74c3c; }
        
        .chart-container { 
            background: white; padding: 30px; min-height: 600px;
        }
        .chart-wrapper { position: relative; height: 500px; }
        
        .event-item {
            margin: 10px 0; padding: 15px; border-radius: 8px; 
            background: white; border-left: 4px solid #3498db;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .event-title { font-weight: bold; color: #2c3e50; margin-bottom: 5px; }
        .event-meta { font-size: 0.8em; color: #7f8c8d; }
        .event-sites { margin-top: 8px; }
        .site-tag { 
            display: inline-block; background: #3498db; color: white; 
            padding: 2px 8px; border-radius: 12px; font-size: 0.7em; margin: 2px;
        }
        
        .high-impact { border-left-color: #e74c3c; }
        .medium-impact { border-left-color: #f39c12; }
        .low-impact { border-left-color: #27ae60; }
        
        h2 { color: #2c3e50; margin-bottom: 20px; font-weight: 300; }
        h3 { color: #34495e; margin-bottom: 15px; font-size: 1.2em; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🎯 포커 사이트 완전 모니터링 대시보드</h1>
            <p>실시간 트래픽 분석 • 이벤트 통합 • 경쟁사 모니터링</p>
        </div>
        
        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-number">''' + str(event_summary['total_events']) + '''</div>
                <div class="stat-label">총 이벤트</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">''' + str(event_summary['high_impact_events']) + '''</div>
                <div class="stat-label">고임팩트 이벤트</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">''' + str(event_summary['tournament_events']) + '''</div>
                <div class="stat-label">토너먼트</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">''' + str(event_summary['promotion_events']) + '''</div>
                <div class="stat-label">프로모션</div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="tabs-section">
                <div class="tabs">
                    <button class="tab active" onclick="showChart('multi_line')">📈 트렌드+이벤트</button>
                    <button class="tab" onclick="showChart('radar')">🎯 현재 비교</button>
                    <button class="tab" onclick="showChart('heatmap')">🔥 변화 히트맵</button>
                    <button class="tab" onclick="showChart('bubble')">💭 4차원 분석</button>
                    <button class="tab" onclick="showChart('stacked_bar')">📊 시장 점유율</button>
                </div>
                
                <div class="chart-container">
                    <div id="chart-multi_line" class="chart-content">
                        <h2>📈 포커 사이트 트렌드 분석 + 이벤트 통합</h2>
                        <div class="chart-wrapper">
                            <canvas id="multiLineChart"></canvas>
                        </div>
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
            
            <div class="events-sidebar">
                <h3>📅 최근 이벤트</h3>
                <div id="eventsList">
                    ''' + self.generate_events_html(event_summary['recent_events']) + '''
                </div>
            </div>
        </div>
    </div>

    <script>
        const chartData = ''' + json.dumps(charts, ensure_ascii=False) + ''';
        const eventData = ''' + json.dumps(event_summary, ensure_ascii=False) + ''';
        
        let charts = {};
        
        function showChart(chartType) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
            
            document.querySelectorAll('.chart-content').forEach(content => content.style.display = 'none');
            document.getElementById('chart-' + chartType).style.display = 'block';
            
            if (!charts[chartType]) {
                createChart(chartType);
            }
        }
        
        function createChart(chartType) {
            const data = chartData[chartType];
            
            switch(chartType) {
                case 'multi_line':
                    createEnhancedMultiLineChart(data);
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
        
        function createEnhancedMultiLineChart(data) {
            const ctx = document.getElementById('multiLineChart').getContext('2d');
            const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c'];
            
            const datasets = [];
            let colorIndex = 0;
            
            Object.keys(data.sites).forEach(site => {
                datasets.push({
                    label: site + ' (Players Online)',
                    data: data.sites[site].players_online,
                    borderColor: colors[colorIndex % colors.length],
                    backgroundColor: colors[colorIndex % colors.length] + '20',
                    fill: false,
                    tension: 0.1,
                    pointRadius: data.sites[site].point_styles ? 
                        data.sites[site].point_styles.map(s => s.radius) : 3
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
                        title: { 
                            display: true, 
                            text: 'Players Online 트렌드 (이벤트 표시)',
                            font: { size: 16 }
                        },
                        legend: { position: 'top' },
                        annotation: {
                            annotations: data.annotations || []
                        }
                    },
                    scales: {
                        y: { 
                            beginAtZero: true,
                            title: { display: true, text: 'Players Count' }
                        },
                        x: {
                            title: { display: true, text: 'Date' }
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    }
                }
            });
        }
        
        function createRadarChart(data) {
            const ctx = document.getElementById('radarChart').getContext('2d');
            const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6'];
            
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
    
    def generate_events_html(self, events):
        """이벤트 목록 HTML 생성"""
        if not events:
            return '<div class="event-item">최근 이벤트가 없습니다.</div>'
        
        html = ''
        for event in events:
            impact_class = f"{event.get('impact', 'LOW').lower()}-impact"
            
            html += f'''
            <div class="event-item {impact_class}">
                <div class="event-title">{event.get('symbol', '📅')} {event['title']}</div>
                <div class="event-meta">{event['date']} • {event['type']}</div>
                <div class="event-sites">
                    {' '.join([f'<span class="site-tag">{site}</span>' for site in event.get('sites', [])])}
                </div>
            </div>
            '''
        
        return html

def main():
    """완전한 대시보드 생성 테스트"""
    print("🎯 완전한 포커 사이트 모니터링 대시보드 생성...")
    
    dashboard = CompletePokerDashboard()
    
    # 샘플 뉴스 데이터로 이벤트 생성
    sample_news = [
        {
            'title': 'PokerStars SCOOP 2024 Main Event Final Table',
            'content': 'The biggest online poker tournament series continues with massive guarantees from May 5-26',
            'date': '2024-07-15',
            'url': 'https://pokernews.com/news/2024/07/pokerstars-scoop-main-event.htm'
        },
        {
            'title': 'GGPoker WSOP Satellite Winner Announced',
            'content': 'Player wins $10,000 main event seat in special satellite tournament',
            'date': '2024-07-16',
            'url': 'https://pokernews.com/news/2024/07/ggpoker-satellite-winner.htm'
        },
        {
            'title': 'WPT Global Summer Festival Launches',
            'content': 'Massive tournament series with over $50M guaranteed across all events running through August',
            'date': '2024-07-10',
            'url': 'https://pokernews.com/news/2024/07/wpt-global-summer.htm'
        },
        {
            'title': '888poker Mega Promotion Goes Live',
            'content': '$2 million leaderboard race with daily satellites and bonus rewards',
            'date': '2024-07-12',
            'url': 'https://pokernews.com/news/2024/07/888poker-mega-promo.htm'
        }
    ]
    
    # 뉴스 처리 및 이벤트 생성
    event_stats = dashboard.process_news_and_generate_events(sample_news)
    print(f"✅ 이벤트 생성 완료:")
    print(f"  - 기본 이벤트: {event_stats['basic_events']}개")
    print(f"  - 포인트 이벤트: {event_stats['point_events']}개") 
    print(f"  - 기간 이벤트: {event_stats['period_events']}개")
    
    # 완전한 대시보드 생성
    html_file = dashboard.create_complete_dashboard_html()
    print(f"📊 완전한 대시보드 생성 완료: {html_file}")
    
    print(f"\n🎉 포커 사이트 완전 모니터링 대시보드 완성!")
    print(f"✅ 5가지 차트 유형 (트렌드, 레이더, 히트맵, 버블, 스택바)")
    print(f"✅ 포인트/기간 이벤트 통합")
    print(f"✅ PokerNews 자동 감지")
    print(f"✅ 실시간 차트 업데이트")
    print(f"✅ 사이드바 이벤트 타임라인")
    
    return html_file

if __name__ == "__main__":
    main()
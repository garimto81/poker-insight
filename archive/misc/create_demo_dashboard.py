#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데모 대시보드 생성기
- 실제 데이터가 없을 때 사용할 데모 대시보드 생성
"""
import json
import os
from datetime import datetime, timedelta

def create_demo_data():
    """데모 데이터 생성"""
    demo_sites = [
        {"name": "GGNetwork", "category": "GG_POKER", "players": 134304, "cash": 89230, "peak": 145678, "avg": 125890},
        {"name": "PokerStars", "category": "COMPETITOR", "players": 55540, "cash": 38900, "peak": 62340, "avg": 58720},
        {"name": "WPT Global", "category": "COMPETITOR", "players": 12450, "cash": 8900, "peak": 15670, "avg": 13200},
        {"name": "888poker", "category": "COMPETITOR", "players": 8920, "cash": 6780, "peak": 10450, "avg": 9350},
        {"name": "partypoker", "category": "COMPETITOR", "players": 7890, "cash": 5600, "peak": 9120, "avg": 8240},
        {"name": "GGPoker ON", "category": "GG_POKER", "players": 6750, "cash": 4890, "peak": 7890, "avg": 7100},
        {"name": "Chico Poker", "category": "COMPETITOR", "players": 5670, "cash": 4100, "peak": 6890, "avg": 6200},
        {"name": "iPoker", "category": "COMPETITOR", "players": 4560, "cash": 3200, "peak": 5670, "avg": 4890},
    ]
    
    # 최근 7일간의 데이터 생성
    dates = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=6-i)).strftime('%Y-%m-%d')
        dates.append(date)
    
    dashboard_data = {
        'last_updated': datetime.now().isoformat(),
        'data_period_days': 7,
        'sites': {},
        'dates': dates,
        'summary': {
            'total_sites': len(demo_sites),
            'gg_poker_sites': len([s for s in demo_sites if s['category'] == 'GG_POKER']),
            'latest_total_players': sum(s['players'] for s in demo_sites),
            'data_points': len(demo_sites) * len(dates)
        }
    }
    
    # 각 사이트별 데이터 생성
    for site in demo_sites:
        site_data = {
            'name': site['name'],
            'category': site['category'],
            'data': {
                'dates': dates,
                'players_online': [],
                'cash_players': [],
                'peak_24h': [],
                'seven_day_avg': []
            }
        }
        
        # 각 날짜별 약간의 변동 추가
        for i, date in enumerate(dates):
            variation = 1.0 + (i - 3) * 0.02  # -6% ~ +6% 변동
            site_data['data']['players_online'].append(int(site['players'] * variation))
            site_data['data']['cash_players'].append(int(site['cash'] * variation))
            site_data['data']['peak_24h'].append(int(site['peak'] * variation))
            site_data['data']['seven_day_avg'].append(int(site['avg'] * variation))
        
        dashboard_data['sites'][site['name']] = site_data
    
    return dashboard_data

def create_demo_dashboard():
    """데모 대시보드 생성"""
    print("데모 대시보드 생성 중...")
    
    # docs 디렉토리 확인
    os.makedirs('docs', exist_ok=True)
    
    # 데모 데이터 생성
    dashboard_data = create_demo_data()
    
    # API 데이터 파일 생성
    with open('docs/api_data.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
    
    # 요약 데이터 생성
    summary_data = {
        'last_updated': dashboard_data['last_updated'],
        'summary': dashboard_data['summary'],
        'latest_sites': {}
    }
    
    for site_name, site_data in dashboard_data['sites'].items():
        summary_data['latest_sites'][site_name] = {
            'name': site_name,
            'category': site_data['category'],
            'players_online': site_data['data']['players_online'][-1],
            'cash_players': site_data['data']['cash_players'][-1],
            'peak_24h': site_data['data']['peak_24h'][-1],
            'seven_day_avg': site_data['data']['seven_day_avg'][-1],
            'date': site_data['data']['dates'][-1]
        }
    
    with open('docs/api_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    # HTML 대시보드 생성
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GG POKER 모니터링 대시보드</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 0; padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{ 
            max-width: 1200px; margin: 0 auto; 
            background: rgba(255,255,255,0.95); 
            border-radius: 15px; padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #2c3e50; margin: 0; }}
        .header p {{ color: #7f8c8d; margin: 5px 0; }}
        .stats {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; margin-bottom: 30px; 
        }}
        .stat-card {{ 
            background: white; padding: 20px; border-radius: 10px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.1); text-align: center;
        }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        .stat-label {{ color: #7f8c8d; margin-top: 5px; }}
        .chart-container {{ 
            background: white; padding: 20px; border-radius: 10px; 
            margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .chart-wrapper {{ position: relative; height: 400px; }}
        .gg-highlight {{ border-left: 4px solid #e74c3c; }}
        .last-updated {{ 
            text-align: center; color: #7f8c8d; 
            font-size: 0.9em; margin-top: 20px; 
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>GG POKER 모니터링 대시보드</h1>
            <p>실시간 포커 사이트 트래픽 분석 (데모 데이터)</p>
        </div>
        
        <div class="stats">
            <div class="stat-card gg-highlight">
                <div class="stat-number">{dashboard_data['summary']['gg_poker_sites']}</div>
                <div class="stat-label">GG POKER 사이트</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{dashboard_data['summary']['total_sites']}</div>
                <div class="stat-label">모니터링 사이트</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{dashboard_data['summary']['latest_total_players']:,}</div>
                <div class="stat-label">현재 총 플레이어</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{dashboard_data['data_period_days']}</div>
                <div class="stat-label">데이터 수집 기간 (일)</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>사이트별 플레이어 트렌드 (최근 7일)</h3>
            <div class="chart-wrapper">
                <canvas id="trendChart"></canvas>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>현재 사이트 현황</h3>
            <div class="chart-wrapper">
                <canvas id="currentChart"></canvas>
            </div>
        </div>
        
        <div class="last-updated">
            마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (데모 데이터)<br>
            <a href="api_data.json">API 데이터</a> | <a href="api_summary.json">요약 데이터</a>
        </div>
    </div>

    <script>
        const dashboardData = {json.dumps(dashboard_data, ensure_ascii=False)};
        
        // 트렌드 차트
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#95a5a6'];
        
        const trendDatasets = [];
        let colorIndex = 0;
        
        Object.keys(dashboardData.sites).forEach(siteName => {{
            const siteData = dashboardData.sites[siteName];
            const isGG = siteData.category === 'GG_POKER';
            
            trendDatasets.push({{
                label: siteName,
                data: siteData.data.players_online,
                borderColor: colors[colorIndex % colors.length],
                backgroundColor: colors[colorIndex % colors.length] + '20',
                borderWidth: isGG ? 3 : 2,
                fill: false,
                tension: 0.1
            }});
            colorIndex++;
        }});
        
        new Chart(trendCtx, {{
            type: 'line',
            data: {{
                labels: dashboardData.dates,
                datasets: trendDatasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'top' }}
                }},
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});
        
        // 현재 상황 차트
        const currentCtx = document.getElementById('currentChart').getContext('2d');
        const currentLabels = [];
        const currentData = [];
        const currentColors = [];
        
        Object.keys(dashboardData.sites).forEach((siteName, index) => {{
            const siteData = dashboardData.sites[siteName];
            if (siteData.data.players_online.length > 0) {{
                currentLabels.push(siteName);
                currentData.push(siteData.data.players_online[siteData.data.players_online.length - 1]);
                currentColors.push(siteData.category === 'GG_POKER' ? '#e74c3c' : colors[index % colors.length]);
            }}
        }});
        
        new Chart(currentCtx, {{
            type: 'bar',
            data: {{
                labels: currentLabels,
                datasets: [{{
                    label: 'Players Online',
                    data: currentData,
                    backgroundColor: currentColors,
                    borderColor: currentColors,
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
    
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[SUCCESS] 데모 대시보드 생성 완료")
    print(f"- 총 사이트: {dashboard_data['summary']['total_sites']}개")
    print(f"- GG POKER: {dashboard_data['summary']['gg_poker_sites']}개") 
    print(f"- 총 플레이어: {dashboard_data['summary']['latest_total_players']:,}명")
    
    return True

if __name__ == "__main__":
    create_demo_dashboard()
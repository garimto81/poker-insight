#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
온라인 대시보드 업데이트
- 수집된 데이터로 웹 대시보드 자동 업데이트
- GitHub Pages 또는 Vercel 배포용 정적 파일 생성
- JSON API 형태로 데이터 제공
"""
import os
import sys
import json
import logging
from datetime import datetime, timedelta
from online_data_collector import OnlineDataCollector, DB_TYPE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardUpdater:
    def __init__(self):
        self.collector = OnlineDataCollector()
        self.output_dir = 'docs'  # GitHub Pages용
        os.makedirs(self.output_dir, exist_ok=True)
        
    def get_dashboard_data(self, days_back=365):
        """대시보드용 데이터 조회"""
        try:
            conn = self.collector.get_db_connection()
            cursor = conn.cursor()
            
            # 최근 30일 데이터  
            if not self.collector.use_sqlite_fallback and DB_TYPE in ['postgresql', 'mysql']:
                sql = """
                SELECT 
                    collection_date,
                    site_name,
                    players_online,
                    cash_players,
                    peak_24h,
                    seven_day_avg
                FROM daily_traffic 
                WHERE collection_date >= CURRENT_DATE - INTERVAL %s DAY
                ORDER BY collection_date, site_name
                """
                cursor.execute(sql, (days_back,))
            else:
                sql = """
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
                """
                cursor.execute(sql, (days_back,))
            
            results = cursor.fetchall()
            
            # 데이터 구조화
            dashboard_data = {
                'last_updated': datetime.now().isoformat(),
                'data_period_days': days_back,
                'sites': {},
                'dates': [],
                'summary': {
                    'total_sites': 0,
                    'gg_poker_sites': 0,
                    'latest_total_players': 0,
                    'data_points': len(results)
                }
            }
            
            dates_set = set()
            latest_date_data = {}
            
            for row in results:
                # PostgreSQL과 SQLite 모두 동일한 순서로 데이터 반환
                date, site, players, cash, peak, avg = row
                
                dates_set.add(date)
                
                if site not in dashboard_data['sites']:
                    dashboard_data['sites'][site] = {
                        'name': site,
                        'category': 'GG_POKER' if 'GG' in site else 'COMPETITOR',
                        'data': {
                            'dates': [],
                            'players_online': [],
                            'cash_players': [],
                            'peak_24h': [],
                            'seven_day_avg': []
                        }
                    }
                
                dashboard_data['sites'][site]['data']['dates'].append(date)
                dashboard_data['sites'][site]['data']['players_online'].append(players or 0)
                dashboard_data['sites'][site]['data']['cash_players'].append(cash or 0)
                dashboard_data['sites'][site]['data']['peak_24h'].append(peak or 0)
                dashboard_data['sites'][site]['data']['seven_day_avg'].append(avg or 0)
                
                # 최신 날짜 데이터 수집
                if date not in latest_date_data:
                    latest_date_data[date] = []
                latest_date_data[date].append({'site': site, 'players': players or 0})
            
            dashboard_data['dates'] = sorted(list(dates_set))
            
            # 요약 통계 계산
            dashboard_data['summary']['total_sites'] = len(dashboard_data['sites'])
            dashboard_data['summary']['gg_poker_sites'] = len([s for s in dashboard_data['sites'] if 'GG' in s])
            
            # 최신 날짜의 총 플레이어 수
            if dashboard_data['dates']:
                latest_date = max(dashboard_data['dates'])
                if latest_date in latest_date_data:
                    dashboard_data['summary']['latest_total_players'] = sum(
                        item['players'] for item in latest_date_data[latest_date]
                    )
            
            conn.close()
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ 대시보드 데이터 조회 실패: {str(e)}")
            return None
    
    def generate_api_endpoints(self, dashboard_data):
        """API 엔드포인트 JSON 파일 생성 - 기존 데이터와 병합"""
        try:
            # 기존 데이터 읽기
            existing_data = None
            api_data_path = f'{self.output_dir}/api_data.json'
            
            if os.path.exists(api_data_path):
                try:
                    with open(api_data_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except Exception as e:
                    logger.warning(f"기존 데이터 읽기 실패: {e}")
            
            # 데이터 병합
            if existing_data and 'sites' in existing_data:
                # 각 사이트별로 기존 데이터와 새 데이터 병합
                for site_name, new_site_data in dashboard_data['sites'].items():
                    if site_name in existing_data['sites']:
                        # 기존 사이트 데이터가 있으면 병합
                        existing_site = existing_data['sites'][site_name]
                        
                        # 새로운 날짜만 추가
                        for idx, date in enumerate(new_site_data['data']['dates']):
                            if date not in existing_site['data']['dates']:
                                existing_site['data']['dates'].append(date)
                                existing_site['data']['players_online'].append(new_site_data['data']['players_online'][idx])
                                existing_site['data']['cash_players'].append(new_site_data['data']['cash_players'][idx])
                                existing_site['data']['peak_24h'].append(new_site_data['data']['peak_24h'][idx])
                                existing_site['data']['seven_day_avg'].append(new_site_data['data']['seven_day_avg'][idx])
                    else:
                        # 새로운 사이트면 그대로 추가
                        existing_data['sites'][site_name] = new_site_data
                
                # 메타데이터 업데이트
                existing_data['last_updated'] = dashboard_data['last_updated']
                existing_data['dates'] = sorted(list(set(existing_data.get('dates', []) + dashboard_data['dates'])))
                existing_data['summary'] = dashboard_data['summary']
                
                dashboard_data = existing_data
            
            # 메인 대시보드 데이터 저장
            with open(api_data_path, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
            
            # 요약 데이터만 (경량화)
            summary_data = {
                'last_updated': dashboard_data['last_updated'],
                'summary': dashboard_data['summary'],
                'latest_sites': {}
            }
            
            # 각 사이트의 최신 데이터만
            for site_name, site_data in dashboard_data['sites'].items():
                if site_data['data']['dates']:
                    latest_idx = -1
                    summary_data['latest_sites'][site_name] = {
                        'name': site_name,
                        'category': site_data['category'],
                        'players_online': site_data['data']['players_online'][latest_idx],
                        'cash_players': site_data['data']['cash_players'][latest_idx],
                        'peak_24h': site_data['data']['peak_24h'][latest_idx],
                        'seven_day_avg': site_data['data']['seven_day_avg'][latest_idx],
                        'date': site_data['data']['dates'][latest_idx]
                    }
            
            with open(f'{self.output_dir}/api_summary.json', 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
            logger.info("API endpoint files created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ API 파일 생성 실패: {str(e)}")
            return False
    
    def generate_web_dashboard(self, dashboard_data):
        """웹 대시보드 HTML 생성 - 기존 index.html을 덮어쓰지 않음"""
        try:
            # 기존 index.html을 유지하고 API 데이터만 업데이트
            logger.info("Existing index.html preserved, only API data updated")
            return True  # 실제 HTML 생성 건너뛰기
        except Exception as e:
            logger.error(f"❌ 대시보드 보존 실패: {str(e)}")
            return False
        
        # 아래 코드는 실행되지 않음 (기존 HTML 템플릿 코드)
        html_template = f"""
<!DOCTYPE html>
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
            <h1>🎯 GG POKER 모니터링 대시보드</h1>
            <p>실시간 포커 사이트 트래픽 분석 • 자동 업데이트</p>
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
            <h3>📈 사이트별 플레이어 트렌드</h3>
            <div class="chart-wrapper">
                <canvas id="trendChart"></canvas>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>🎯 현재 사이트 현황</h3>
            <div class="chart-wrapper">
                <canvas id="currentChart"></canvas>
            </div>
        </div>
        
        <div class="last-updated">
            마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        </div>
    </div>

    <script>
        const dashboardData = {json.dumps(dashboard_data, ensure_ascii=False)};
        
        // 트렌드 차트
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e'];
        
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
</html>
        """
        
        try:
            with open(f'{self.output_dir}/index.html', 'w', encoding='utf-8') as f:
                f.write(html_template)
            
            logger.info("✅ 웹 대시보드 HTML 생성 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 웹 대시보드 생성 실패: {str(e)}")
            return False
    
    def update_dashboard(self):
        """대시보드 업데이트 실행"""
        logger.info("Starting online dashboard update...")
        
        try:
            # 대시보드 데이터 조회 - 1년치 데이터
            dashboard_data = self.get_dashboard_data(365)
            
            if not dashboard_data:
                logger.error("Failed to retrieve dashboard data")
                return False
            
            # API 파일 생성
            api_success = self.generate_api_endpoints(dashboard_data)
            
            # 웹 대시보드 생성
            web_success = self.generate_web_dashboard(dashboard_data)
            
            if api_success and web_success:
                logger.info("Dashboard update complete")
                logger.info(f"Data: {dashboard_data['summary']['data_points']} points")
                logger.info(f"GG POKER: {dashboard_data['summary']['gg_poker_sites']} sites")
                logger.info(f"Latest Players: {dashboard_data['summary']['latest_total_players']:,} players")
                return True
            else:
                logger.error("Dashboard update partially failed")
                return False
                
        except Exception as e:
            logger.error(f"Dashboard update failed: {str(e)}")
            return False

def main():
    """메인 실행"""
    print("온라인 대시보드 업데이트")
    print("=" * 40)
    
    updater = DashboardUpdater()
    success = updater.update_dashboard()
    
    if success:
        print("[SUCCESS] 대시보드 업데이트 성공")
        sys.exit(0)
    else:
        print("[FAILED] 대시보드 업데이트 실패")
        sys.exit(1)

if __name__ == "__main__":
    main()
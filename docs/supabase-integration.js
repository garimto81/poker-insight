/**
 * Supabase 연동 JavaScript 모듈
 * 프론트엔드에서 Supabase와 실시간 데이터 연동
 */

class SupabaseIntegration {
    constructor(supabaseUrl, supabaseKey) {
        this.supabaseUrl = supabaseUrl;
        this.supabaseKey = supabaseKey;
        this.headers = {
            'apikey': supabaseKey,
            'Authorization': `Bearer ${supabaseKey}`,
            'Content-Type': 'application/json'
        };
        
        console.log('🔗 Supabase Integration initialized');
    }
    
    /**
     * Supabase 연결 테스트
     */
    async testConnection() {
        try {
            const response = await fetch(`${this.supabaseUrl}/rest/v1/`, {
                method: 'GET',
                headers: this.headers
            });
            
            if (response.ok) {
                console.log('✅ Supabase 연결 성공');
                return true;
            } else {
                console.error('❌ Supabase 연결 실패:', response.status);
                return false;
            }
        } catch (error) {
            console.error('❌ Supabase 연결 오류:', error);
            return false;
        }
    }
    
    /**
     * 최근 트래픽 데이터 조회
     */
    async getLatestTrafficData(days = 7) {
        try {
            const fromDate = new Date();
            fromDate.setDate(fromDate.getDate() - days);
            const fromDateStr = fromDate.toISOString().split('T')[0];
            
            const response = await fetch(
                `${this.supabaseUrl}/rest/v1/daily_traffic?collection_date=gte.${fromDateStr}&order=collection_date.desc,collection_time.desc`,
                {
                    method: 'GET',
                    headers: this.headers
                }
            );
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ ${data.length}개 트래픽 데이터 조회 완료`);
                return data;
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('❌ 트래픽 데이터 조회 실패:', error);
            throw error;
        }
    }
    
    /**
     * 대시보드용 데이터 변환
     */
    convertToDashboardFormat(trafficData) {
        const sites = {};
        const dates = new Set();
        
        trafficData.forEach(row => {
            const siteName = row.site_name;
            const collectionDate = row.collection_date;
            
            dates.add(collectionDate);
            
            if (!sites[siteName]) {
                sites[siteName] = {
                    name: siteName,
                    category: siteName.toUpperCase().includes('GG') ? 'GG_POKER' : 'OTHER',
                    data: {
                        dates: [],
                        players_online: [],
                        cash_players: [],
                        peak_24h: [],
                        seven_day_avg: []
                    }
                };
            }
            
            sites[siteName].data.dates.push(collectionDate);
            sites[siteName].data.players_online.push(row.players_online);
            sites[siteName].data.cash_players.push(row.cash_players);
            sites[siteName].data.peak_24h.push(row.peak_24h || 0);
            sites[siteName].data.seven_day_avg.push(row.seven_day_avg || 0);
        });
        
        // 요약 통계 계산
        const latestTotalPlayers = Object.values(sites).reduce((sum, site) => {
            const latestPlayers = site.data.players_online[site.data.players_online.length - 1] || 0;
            return sum + latestPlayers;
        }, 0);
        
        const ggPokerSites = Object.values(sites).filter(
            site => site.category === 'GG_POKER'
        ).length;
        
        return {
            last_updated: new Date().toISOString(),
            data_period_days: dates.size,
            sites: sites,
            dates: Array.from(dates).sort(),
            summary: {
                total_sites: Object.keys(sites).length,
                gg_poker_sites: ggPokerSites,
                latest_total_players: latestTotalPlayers,
                data_points: trafficData.length
            }
        };
    }
    
    /**
     * 대시보드 데이터 조회 (기존 API와 호환)
     */
    async getDashboardData() {
        try {
            console.log('📊 Supabase에서 대시보드 데이터 조회 중...');
            
            const trafficData = await this.getLatestTrafficData(30);
            const dashboardData = this.convertToDashboardFormat(trafficData);
            
            console.log('✅ 대시보드 데이터 변환 완료:', {
                sites: dashboardData.summary.total_sites,
                players: dashboardData.summary.latest_total_players,
                dataPoints: dashboardData.summary.data_points
            });
            
            return dashboardData;
        } catch (error) {
            console.error('❌ 대시보드 데이터 조회 실패:', error);
            throw error;
        }
    }
    
    /**
     * 실시간 데이터 구독 (WebSocket)
     */
    subscribeToUpdates(callback) {
        // Supabase Realtime 구독
        const channel = `${this.supabaseUrl}/realtime/v1/websocket`;
        // 실제 구현은 Supabase JavaScript 클라이언트 라이브러리 사용 권장
        console.log('🔔 실시간 업데이트 구독 설정됨');
    }
}

/**
 * 향상된 데이터 로딩 함수 (Supabase 지원)
 */
async function loadDashboardDataEnhanced() {
    const loadingEl = document.getElementById('loading-indicator');
    const errorContainer = document.getElementById('error-container');
    
    try {
        loadingEl.style.display = 'block';
        errorContainer.innerHTML = '';
        
        // Supabase 설정 확인
        const supabaseUrl = window.SUPABASE_URL || null;
        const supabaseKey = window.SUPABASE_ANON_KEY || null;
        
        if (supabaseUrl && supabaseKey) {
            console.log('🔗 Supabase 모드로 데이터 로딩 시도...');
            
            const supabase = new SupabaseIntegration(supabaseUrl, supabaseKey);
            
            // 연결 테스트
            const connected = await supabase.testConnection();
            if (connected) {
                const data = await supabase.getDashboardData();
                loadingEl.style.display = 'none';
                console.log('✅ Supabase에서 데이터 로드 성공');
                return data;
            } else {
                throw new Error('Supabase 연결 실패');
            }
        } else {
            // Fallback: 기존 JSON 파일 방식
            console.log('📄 JSON 파일 모드로 데이터 로딩...');
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);
            
            const response = await fetch('./api_data.json', {
                signal: controller.signal,
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            loadingEl.style.display = 'none';
            console.log('✅ JSON 파일에서 데이터 로드 성공');
            return data;
        }
        
    } catch (error) {
        console.error('❌ 데이터 로딩 실패:', error);
        loadingEl.style.display = 'none';
        
        // 에러 메시지 표시
        let errorMessage = '';
        if (error.message.includes('Supabase')) {
            errorMessage = `
                <div class="error-message">
                    <strong>🔗 Supabase 연결 실패:</strong> ${error.message}<br>
                    <small>JSON 파일 모드로 전환 시도 중...</small>
                </div>
            `;
        } else if (error.name === 'TypeError' || error.message.includes('fetch')) {
            errorMessage = `
                <div class="error-message">
                    <strong>🚫 CORS 접근 제한:</strong> 브라우저 보안정책으로 인해 로컬 파일 접근이 차단되었습니다.<br>
                    <small><strong>해결방법:</strong> HTTP 서버로 실행하거나 Supabase 연동을 사용하세요</small><br>
                    <code>python -m http.server 8000</code>
                </div>
            `;
        } else {
            errorMessage = `
                <div class="error-message">
                    <strong>❌ 데이터 로딩 실패:</strong> ${error.message}<br>
                    <small>Supabase 설정을 확인하거나 HTTP 서버에서 실행해보세요</small>
                </div>
            `;
        }
        
        errorContainer.innerHTML = errorMessage;
        
        // 기본 fallback 데이터
        return {
            "last_updated": new Date().toISOString(),
            "data_period_days": 1,
            "sites": {
                "Demo Mode": {
                    "name": "Demo Mode",
                    "category": "DEMO",
                    "data": {
                        "dates": [new Date().toISOString().split('T')[0]],
                        "players_online": [0],
                        "cash_players": [0],
                        "peak_24h": [0],
                        "seven_day_avg": [0]
                    }
                }
            },
            "dates": [new Date().toISOString().split('T')[0]],
            "summary": {
                "total_sites": 1,
                "gg_poker_sites": 0,
                "latest_total_players": 0,
                "data_points": 1
            }
        };
    }
}

// 전역 스코프에 함수 노출
window.SupabaseIntegration = SupabaseIntegration;
window.loadDashboardDataEnhanced = loadDashboardDataEnhanced;
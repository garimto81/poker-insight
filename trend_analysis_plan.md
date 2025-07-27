# 포커 트렌드 패턴 분석 계획

## 📊 1. 데이터 수집 주기별 분석

### 시간별 패턴 분석
- **시간대별 트래픽 변화**: 24시간 주기로 플레이어 수 변동 패턴
- **피크 타임 식별**: 가장 활발한 시간대 (예: 저녁 7-11시)
- **데드 타임 분석**: 트래픽이 가장 낮은 시간대

### 요일별 패턴 분석  
- **주중 vs 주말**: 평일과 주말의 트래픽 차이
- **요일별 특성**: 월요일 vs 금요일 vs 일요일 패턴
- **토너먼트 스케줄 영향**: 주요 토너먼트 요일의 트래픽 변화

### 월별/계절별 패턴
- **WSOP 시즌 영향** (6-7월): 온라인 트래픽 감소 vs 증가
- **연말연시 효과**: 12월-1월 트래픽 변화
- **여름휴가철 영향**: 8월 트래픽 패턴

## 📈 2. 사이트별 성장/하락 트렌드

### 성장률 분석
```python
# 7일 이동평균 기반 성장률 계산
growth_rate = ((current_avg - previous_avg) / previous_avg) * 100

# 트렌드 분류
if growth_rate > 10%: "급성장"
elif growth_rate > 5%: "성장"  
elif growth_rate > -5%: "안정"
elif growth_rate > -10%: "하락"
else: "급락"
```

### 시장 점유율 변화
- **상위 10위 사이트 순위 변동** 추적
- **신규 진입 사이트** 모니터링  
- **시장 집중도 변화** (상위 3개 사이트 점유율)

### 네트워크별 트렌드
- **GGNetwork vs PokerStars** 경쟁 구도
- **소규모 네트워크 성장 패턴**
- **지역별 네트워크 트렌드** (유럽 vs 아시아)

## 🔍 3. 뉴스 기반 트렌드 분석

### 키워드 빈도 분석
```python
trending_keywords = {
    "WSOP": 빈도수 + 감정분석,
    "GGPoker": 언급 횟수 + 긍정/부정,
    "PokerStars": 브랜드 언급 트렌드,
    "Tournament": 토너먼트 관련 뉴스 증가율,
    "High Stakes": 하이스테이크 관련 관심도
}
```

### 뉴스 임팩트 분석
- **중요 뉴스 발표 전후** 트래픽 변화
- **신규 프로모션 공지** 효과 측정
- **규제 뉴스 영향도** 분석

### 감정 분석 (Sentiment Analysis)
- **긍정적 뉴스** vs **부정적 뉴스** 비율
- **특정 사이트 관련 뉴스** 감정 추세

## 🎯 4. 방송용 트렌드 지표

### Real-time 변화 감지
```python
# 급격한 변화 알림 시스템
def detect_anomaly(current_traffic, historical_avg):
    if current_traffic > historical_avg * 1.5:
        return "급증 알림"
    elif current_traffic < historical_avg * 0.7:
        return "급락 알림"
```

### 방송 중 언급할 포인트
- **"GGNetwork가 전주 대비 15% 성장"**
- **"PokerStars의 새로운 토너먼트 시리즈 영향으로 트래픽 급증"**
- **"이번 주 가장 핫한 포커 사이트는?"**

## 🔧 5. 기술적 구현 방법

### 데이터 저장 구조
```sql
-- 시간별 스냅샷 테이블
CREATE TABLE hourly_snapshots (
    id INTEGER PRIMARY KEY,
    site_id INTEGER,
    hour_timestamp DATETIME,
    players_count INTEGER,
    day_of_week INTEGER,
    is_weekend BOOLEAN
);

-- 트렌드 분석 결과 테이블  
CREATE TABLE trend_analysis (
    id INTEGER PRIMARY KEY,
    site_id INTEGER,
    analysis_date DATE,
    trend_type STRING, -- 'growth', 'decline', 'stable'
    growth_rate FLOAT,
    confidence_score FLOAT
);
```

### 분석 알고리즘
1. **이동평균 (Moving Average)**: 노이즈 제거
2. **선형 회귀 (Linear Regression)**: 트렌드 방향성
3. **계절성 분해**: 주기적 패턴 식별
4. **이상치 탐지**: 급격한 변화 감지

### 실시간 모니터링
```python
# 매 시간마다 실행되는 트렌드 체크
def hourly_trend_check():
    current_data = get_current_traffic()
    historical_data = get_last_7_days()
    
    trends = analyze_trends(current_data, historical_data)
    
    if trends.has_significant_change():
        send_broadcast_alert(trends.summary)
```

## 📺 6. 방송 활용 시나리오

### 오프닝 멘트용
- **"오늘의 온라인 포커 시장 현황"**
- **"이번 주 가장 주목받는 사이트"**
- **"WSOP 시즌의 온라인 포커 트렌드"**

### 중간 세그먼트용  
- **"실시간 트래픽 변화"** 
- **"시청자들이 관심 있어할 포커 뉴스"**
- **"프로 선수들이 주로 플레이하는 사이트"**

### 마감 코멘트용
- **"오늘의 포커 시장 총평"**
- **"내일 주목할 포인트"**

## 🎨 7. 시각화 계획

### 차트 유형
- **라인 차트**: 시간별 트래픽 변화
- **바 차트**: 사이트별 순위 및 성장률
- **히트맵**: 시간대별 활동 패턴
- **파이 차트**: 시장 점유율

### 색상 코딩
- 🟢 **녹색**: 성장/증가
- 🔴 **빨간색**: 하락/감소  
- 🟡 **노란색**: 안정/주의
- 🔵 **파란색**: 새로운 트렌드

## ⚡ 8. 실시간 알림 시스템

### 브레이킹 뉴스 수준
- **급증/급락 20% 이상**: 즉시 알림
- **새로운 사이트 TOP 10 진입**: 30분 내 알림
- **주요 뉴스 브레이킹**: 15분 내 분석

### 방송진용 대시보드
- **실시간 지표 모니터링**
- **트렌드 변화 알림**
- **언급할 만한 포인트 제안**

이런 방식으로 포커 방송에 실질적으로 도움이 되는 트렌드 분석을 제공할 계획입니다!
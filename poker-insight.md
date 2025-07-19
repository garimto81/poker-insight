# Poker Insight - 포커 사이트 모니터링 대시보드

## 📊 프로젝트 개요
실시간 포커 사이트 트래픽 분석 및 모니터링 대시보드 시스템

## 📅 제작 기간
- **시작일**: 2025-07-19
- **종료일**: 2025-07-20  
- **총 작업 기간**: 2일

## 🎯 주요 기능

### 대시보드
- 📈 4개 독립 차트 (온라인 플레이어, 캐시 플레이어, 24시간 피크, 7일 평균)
- 📊 Top 5 사이트 표시 (가독성 최적화)
- ⏰ 시간 선택 기능 (7일, 1개월, 3개월, 6개월, 1년)
- 🎨 GG 포커 사이트 강조 표시 (빨간색)

### 데이터 수집
- 🕷️ PokerScout 웹 크롤링
- 🗄️ SQLite/PostgreSQL 데이터베이스
- 🔄 자동 스케줄링 시스템
- 📡 RESTful API 엔드포인트

### 배포
- 🌐 GitHub Pages 자동 배포
- 📱 완전 반응형 디자인
- ⚡ Chart.js 기반 실시간 차트

## 🏗️ 기술 스택

### Frontend
- **HTML5**: 시멘틱 마크업
- **CSS3**: 그라데이션 디자인, 반응형 레이아웃
- **JavaScript**: ES6+, 비동기 데이터 로딩
- **Chart.js**: 바형 차트 시각화

### Backend  
- **Python 3.8+**: 메인 개발 언어
- **CloudScraper**: 웹 크롤링 (Cloudflare 우회)
- **SQLite**: 로컬 데이터베이스
- **JSON API**: 데이터 제공

### DevOps
- **GitHub Actions**: CI/CD 파이프라인
- **GitHub Pages**: 정적 사이트 호스팅
- **Git**: 버전 관리

## 📈 성과

### 데이터 현황
- **모니터링 사이트**: 46개
- **GG 포커 네트워크**: 2개 사이트
- **총 플레이어**: 281,028명 (실시간)
- **최대 사이트**: GGNetwork (134,304명)

### 기술적 성과
- ✅ 실시간 데이터 수집 시스템 구축
- ✅ 캐싱 최적화로 빠른 로딩 속도
- ✅ 모바일 친화적 반응형 디자인
- ✅ API 엔드포인트 안정성 확보

## 🔧 주요 해결 과제

### 1. GitHub Pages 캐싱 문제
- **문제**: 변경사항이 실시간 반영되지 않음
- **해결**: 타임스탬프 업데이트로 강제 캐시 새로고침

### 2. 차트 시각화 최적화
- **문제**: 상위/하위 사이트 데이터 격차 (134K vs 10명)
- **해결**: Top 10 → Top 5 축소, 바형 차트 적용

### 3. 데이터 덮어쓰기 방지
- **문제**: 서버 업데이트 시 커스텀 HTML 손실
- **해결**: update_dashboard.py 보호 로직 추가

### 4. API 접근성 확보
- **문제**: .gitignore로 인한 API 파일 누락
- **해결**: docs/*.json 파일 예외 처리

## 📁 프로젝트 구조
```
poker-insight/
├── docs/                    # GitHub Pages 배포 파일
│   ├── index.html          # 메인 대시보드
│   ├── api_data.json       # 전체 데이터 API
│   └── api_summary.json    # 요약 데이터 API
├── crawlers/               # 웹 크롤링 모듈
├── database/               # DB 모델 및 설정
├── config/                 # 환경 설정
└── logs/                   # 로그 파일
```

## 🚀 배포 정보
- **라이브 URL**: https://garimto81.github.io/poker-insight/
- **API 엔드포인트**: `/api_data.json`, `/api_summary.json`
- **버전**: v1.2.2
- **마지막 업데이트**: 2025-07-20

## 🎨 UI/UX 최종 개선 (2025-07-20 추가 작업)

### 대시보드 리브랜딩
- **제목 변경**: "🎯 GG POKER 모니터링 대시보드" → "온라인 포커 사이트 분석"
- **이모지 제거**: 모든 이모지를 제거하고 전문적인 디자인으로 변경
- **통계 카드 축소**: 4개 → 2개 카드로 간소화
  - 유지: 분석 대상 사이트, 전체 접속자 수
  - 삭제: GG POKER 사이트 수, 데이터 수집 기간

### 차트 최적화
- **Top 10 → Top 5**: 가독성 향상을 위해 상위 5개 사이트만 표시
- **GG 사이트 강조**: CSS 배지 시스템으로 [GG] 라벨 추가
- **차트 제목 표준화**: PokerScout 원본 용어 사용
  - Players Online
  - Cash Players  
  - 24 H Peak
  - 7 Day Avg

### 기술적 개선사항
```css
/* GG 사이트 배지 시스템 */
.gg-highlight::before {
    content: "GG";
    background: #e74c3c;
    color: white;
    padding: 2px 6px;
    border-radius: 3px;
}
```

```javascript
// 차트 라벨에 GG 표시
const labels = top5.map(site => site.isGG ? `${site.name} [GG]` : site.name);
```

### 성과
- ✅ Windows 인코딩 문제 해결 (이모지 제거)
- ✅ 전문적이고 깔끔한 UI 완성
- ✅ PokerScout 원본 사이트와 용어 통일
- ✅ 국제적 표준에 맞는 영어 용어 사용

## 🔮 향후 개선 계획
1. **다일 데이터 축적**: 시간 선택 기능 활성화
2. **알림 시스템**: 급격한 플레이어 변동 감지
3. **비교 분석**: 경쟁사 대비 GG 포커 성과 분석
4. **모바일 앱**: PWA 변환 검토

---
*최종 완료: 2025-07-20 (총 작업 기간: 2일)*
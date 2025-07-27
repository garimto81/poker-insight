# 온라인 포커 사이트 분석

실시간 포커 사이트 트래픽 분석 및 모니터링 대시보드 시스템

## 🎯 프로젝트 개요

글로벌 포커 네트워크 모니터링을 위한 자동화된 데이터 수집 및 분석 플랫폼입니다. PokerScout에서 실시간 데이터를 수집하여 46개 포커 사이트의 트래픽을 분석합니다.

## 🚀 라이브 대시보드

**👉 [대시보드 바로가기](https://garimto81.github.io/poker-insight/)**

### 주요 기능
- **Players Online**: 실시간 온라인 플레이어 수
- **Cash Players**: 캐시 게임 참여자 수  
- **24 H Peak**: 24시간 최고 플레이어 수
- **7 Day Avg**: 7일 평균 플레이어 수

## 📊 현재 모니터링 현황

- **분석 대상**: 46개 포커 사이트
- **GG 포커 네트워크**: 2개 사이트 (GGNetwork, GGPoker ON)
- **전체 접속자**: 281,028명 (실시간)
- **최대 사이트**: GGNetwork (134,304명)

## 🛠️ 기술 스택

### Frontend
- **HTML5/CSS3**: 반응형 대시보드 디자인
- **JavaScript ES6+**: 비동기 데이터 로딩
- **Chart.js**: 실시간 차트 시각화

### Backend  
- **Python 3.8+**: 데이터 수집 및 처리
- **CloudScraper**: 웹 크롤링 (Cloudflare 우회)
- **SQLite/PostgreSQL**: 데이터베이스
- **JSON API**: RESTful 데이터 제공

### DevOps
- **GitHub Actions**: 매일 자동 데이터 수집
- **GitHub Pages**: 자동 배포
- **Git**: 버전 관리

## 📈 자동화 기능

### 일일 데이터 수집
- **스케줄**: 매일 UTC 09:00 (한국시간 18:00)
- **수집 대상**: 59개 포커 사이트 실시간 데이터
- **자동 업데이트**: 대시보드 및 API 엔드포인트

### API 엔드포인트
- `/api_data.json`: 전체 사이트 상세 데이터
- `/api_summary.json`: 요약 통계 데이터

## 🏗️ 프로젝트 구조

```
poker-insight/
├── docs/                    # GitHub Pages 배포
│   ├── index.html          # 메인 대시보드
│   ├── api_data.json       # 데이터 API
│   └── api_summary.json    # 요약 API
├── crawlers/               # 웹 크롤링 모듈
├── database/               # DB 모델
├── .github/workflows/      # GitHub Actions
└── logs/                   # 수집 로그
```

## 🔧 로컬 실행

### 환경 설정
```bash
# 저장소 클론
git clone https://github.com/garimto81/poker-insight.git
cd poker-insight

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export DB_TYPE=sqlite
export DATABASE_URL=""
```

### 데이터 수집 실행
```bash
# 수동 데이터 수집
python online_data_collector.py

# 대시보드 업데이트
python update_dashboard.py
```

## 📋 개발 이력

- **시작일**: 2025-07-19
- **완료일**: 2025-07-20
- **총 개발 기간**: 2일
- **버전**: v1.2.2

### 주요 마일스톤
1. **데이터 수집 시스템** 구축
2. **실시간 대시보드** 개발
3. **GitHub Actions** 자동화
4. **UI/UX 리브랜딩** 완료

## 🎨 최근 업데이트 (v1.2.2)

- ✅ **리브랜딩**: "GG POKER 모니터링" → "온라인 포커 사이트 분석"
- ✅ **이모지 제거**: 전문적인 디자인으로 변경
- ✅ **차트 최적화**: Top 10 → Top 5 표시
- ✅ **용어 표준화**: PokerScout 원본 용어 사용
- ✅ **Windows 호환성**: 인코딩 문제 해결

## 📄 상세 문서

프로젝트의 전체 개발 과정과 기술적 세부사항은 [`poker-insight.md`](./poker-insight.md)에서 확인할 수 있습니다.

## 🔮 향후 계획

1. **다일 데이터 축적**: 시간 선택 기능 활성화
2. **알림 시스템**: 급격한 변동 감지
3. **비교 분석**: 경쟁사 대비 성과 분석
4. **모바일 최적화**: PWA 변환

---

**라이브 대시보드**: https://garimto81.github.io/poker-insight/

*최종 업데이트: 2025-07-20*
# 🚀 Supabase 연동 가이드

포커 인사이트 프로젝트에서 Supabase를 연동하여 실시간 데이터베이스 기능을 사용하는 방법입니다.

## 📋 목차

1. [Supabase 프로젝트 설정](#1-supabase-프로젝트-설정)
2. [환경변수 설정](#2-환경변수-설정)
3. [데이터 마이그레이션](#3-데이터-마이그레이션)
4. [프론트엔드 연동](#4-프론트엔드-연동)
5. [GitHub Actions 설정](#5-github-actions-설정)
6. [테스트 및 검증](#6-테스트-및-검증)

## 1. Supabase 프로젝트 설정

### 1.1 Supabase 계정 생성
1. [Supabase](https://supabase.com)에서 계정 생성
2. 새 프로젝트 생성
3. 데이터베이스 패스워드 설정

### 1.2 API 키 확인
프로젝트 생성 후 **Settings > API**에서 다음 정보 확인:
- **URL**: `https://your-project-id.supabase.co`
- **anon public**: 프론트엔드에서 사용할 공개 키
- **service_role**: 백엔드에서 사용할 관리자 키

## 2. 환경변수 설정

### 2.1 로컬 개발 환경
프로젝트 루트에 `.env` 파일 생성:

```bash
# Supabase 설정
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-anon-key
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-service-key

# 기존 설정 (백업용)
DB_TYPE=sqlite
DATABASE_URL=
```

### 2.2 필수 패키지 설치
```bash
pip install -r requirements.txt
```

## 3. 데이터 마이그레이션

### 3.1 테이블 생성 및 데이터 마이그레이션
```bash
# 환경 설정 테스트
python test_supabase_integration.py env

# 연결 테스트
python test_supabase_integration.py connect

# 테이블 생성
python test_supabase_integration.py tables

# 기존 SQLite 데이터 마이그레이션
python migrate_to_supabase.py
```

### 3.2 마이그레이션 확인
```bash
# 전체 테스트 실행
python test_supabase_integration.py
```

## 4. 프론트엔드 연동

### 4.1 설정 파일 생성
```bash
# 프론트엔드 설정 파일 자동 생성
python test_supabase_integration.py frontend
```

### 4.2 HTML 파일 수정
`docs/index.html`에 설정 파일 추가:

```html
<head>
    <!-- 기존 스크립트들 -->
    <script src="./supabase-integration.js"></script>
    <script src="./supabase-config.js"></script>
</head>
```

### 4.3 수동 설정 (선택사항)
`docs/index.html`에서 직접 설정:

```javascript
// Supabase 설정
window.SUPABASE_URL = 'https://your-project-id.supabase.co';
window.SUPABASE_ANON_KEY = 'your-anon-key';
```

## 5. GitHub Actions 설정

### 5.1 GitHub Secrets 추가
Repository Settings > Secrets and variables > Actions에서 추가:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-service-key
```

### 5.2 워크플로우 수정
`.github/workflows/daily-data-collection.yml`에 환경변수 추가:

```yaml
env:
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  DB_TYPE: ${{ secrets.DB_TYPE }}
```

## 6. 테스트 및 검증

### 6.1 로컬 테스트
```bash
# 전체 통합 테스트
python test_supabase_integration.py

# 개별 테스트
python test_supabase_integration.py connect    # 연결 테스트
python test_supabase_integration.py insert     # 데이터 삽입 테스트
python test_supabase_integration.py query      # 데이터 조회 테스트
python test_supabase_integration.py dashboard  # 대시보드 데이터 테스트
```

### 6.2 프론트엔드 테스트
1. HTTP 서버 실행: `python -m http.server 8000`
2. 브라우저에서 `http://localhost:8000` 접속
3. 개발자 도구 Console에서 로그 확인:
   - `🔗 Supabase Integration initialized`
   - `✅ Supabase 연결 성공`
   - `✅ Supabase에서 데이터 로드 성공`

### 6.3 실시간 데이터 확인
Supabase 대시보드에서:
1. **Table Editor**에서 `daily_traffic` 테이블 확인
2. **API** 탭에서 REST API 테스트
3. **Logs** 탭에서 요청 로그 확인

## 🔧 문제 해결

### 연결 실패 시
1. **환경변수 확인**: `.env` 파일의 URL과 키가 정확한지 확인
2. **네트워크 확인**: 방화벽이나 프록시 설정 확인
3. **API 키 권한**: service_role 키의 권한 확인

### 데이터 조회 실패 시
1. **RLS (Row Level Security)**: Supabase에서 테이블의 RLS 설정 확인
2. **테이블 권한**: anon 역할의 테이블 접근 권한 확인
3. **CORS 설정**: Supabase 프로젝트의 CORS 설정 확인

### 프론트엔드 오류 시
1. **브라우저 Console**: JavaScript 오류 메시지 확인
2. **네트워크 탭**: API 요청 상태 확인
3. **HTTPS 요구사항**: GitHub Pages는 HTTPS이므로 Supabase URL도 HTTPS 사용

## 📚 추가 리소스

- [Supabase 공식 문서](https://supabase.com/docs)
- [Supabase JavaScript 클라이언트](https://supabase.com/docs/reference/javascript)
- [Row Level Security 가이드](https://supabase.com/docs/guides/auth/row-level-security)

## 🎯 다음 단계

1. **실시간 구독**: Supabase Realtime으로 실시간 데이터 업데이트
2. **인증 시스템**: Supabase Auth로 사용자 인증 추가
3. **Edge Functions**: 서버리스 함수로 고급 로직 구현
4. **Storage**: 이미지/파일 업로드 기능 추가

## ⚠️ 보안 주의사항

1. **API 키 보안**: 
   - `service_role` 키는 절대 프론트엔드에 노출하지 않기
   - GitHub Secrets 사용하여 환경변수 관리
   
2. **RLS 설정**: 
   - 프로덕션에서는 적절한 Row Level Security 정책 적용
   - anon 역할의 권한 최소화

3. **CORS 설정**: 
   - 허용할 도메인만 CORS에 등록
   - 와일드카드(*) 사용 지양
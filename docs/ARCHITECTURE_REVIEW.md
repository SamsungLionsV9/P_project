# 프로젝트 아키텍처 점검 보고서

**점검일**: 2025-12-10
**점검자**: AI Assistant

---

## 프로젝트 구조

```
used-car-price-predictor/
├── admin-dashboard/     # React 관리자 대시보드 (포트 3001)
│   └── src/
│       ├── pages/       # 페이지 컴포넌트 (8개)
│       └── components/  # 공통 컴포넌트 (4개)
├── flutter_app/         # Flutter 모바일 앱
│   └── lib/
│       ├── services/    # API 서비스
│       ├── models/      # 데이터 모델
│       └── config/      # 환경 설정
├── ml-service/          # FastAPI ML 서비스 (포트 8000)
│   └── services/        # 비즈니스 로직 (15개 서비스)
├── user-service/        # Spring Boot 사용자 서비스 (포트 8080)
├── src/                 # 공통 Python 소스 (groq_advisor 등)
├── config/              # 설정 파일
├── data/                # SQLite 데이터베이스
├── models/              # ML 모델 파일 (.pkl)
└── docker/              # Docker 설정 파일
```

---

## 서비스 구성

| 서비스 | 기술 스택 | 포트 | 역할 |
|:--|:--|:--|:--|
| ML Service | Python/FastAPI | 8000 | 가격 예측, AI 분석 |
| User Service | Java/Spring Boot | 8080 | 인증, 사용자 관리 |
| Admin Dashboard | React/Vite | 3001 | 관리자 대시보드 |
| Flutter App | Dart/Flutter | - | 모바일 앱 |

---

## 발견된 이슈 및 수정 내역

### ✅ 수정 완료

| # | 이슈 | 수정 내용 |
|:--|:--|:--|
| 1 | API_BASE 하드코딩 | `App.jsx`, `EconomicInsightsPage.jsx` → 프록시 사용으로 변경 |
| 2 | Health Check 경로 | `docker-compose.yml` → `/api/health`로 수정 |
| 3 | Vite 프록시 누락 | `/api/economic-insights`, `/api/market-timing` 추가 |
| 4 | 빈 파일 14개 | 삭제 완료 |

### ⚠️ 참고 사항 (수정 불필요)

| # | 항목 | 설명 |
|:--|:--|:--|
| 1 | Groq 모델명 차이 | `llama-3.3-70b-versatile` vs `llama-3.3-70b` (데이터 생성용) |
| 2 | 대용량 임시 파일 | `_Used_Car_*.json` (gitignore에 추가됨) |

---

## API 엔드포인트 목록 (ML Service)

### 기본
- `GET /api/health` - 헬스체크
- `GET /api/health/detailed` - 상세 헬스체크

### 가격 예측
- `POST /api/predict` - 가격 예측
- `POST /api/smart-analysis` - 통합 스마트 분석

### 타이밍
- `POST /api/timing` - 타이밍 분석
- `GET /api/market-timing` - 시장 타이밍 요약
- `GET /api/economic-insights` - 경제 인사이트
- `GET /api/timing-prediction` - 타이밍 예측

### B2B
- `GET /api/b2b/dashboard` - B2B 대시보드
- `GET /api/b2b/market-opportunity` - 시장 기회 지수
- `GET /api/b2b/buying-signals` - 매집 추천
- `GET /api/b2b/sell-signals` - 매각 경고
- `GET /api/b2b/sensitivity` - 민감도 분석
- `GET /api/b2b/forecast-accuracy` - 예측 정확도

### AI
- `GET /api/ai/status` - AI 상태 확인
- `POST /api/ai/negotiation-script` - 네고 대본 생성

### 관리자
- `GET /api/admin/dashboard-stats-extended` - 대시보드 통계
- `GET /api/admin/ai-logs` - AI 로그
- `GET /api/admin/analysis-history` - 분석 이력

---

## 환경 설정

### Flutter App (`lib/config/environment.dart`)
- Android 에뮬레이터: `10.0.2.2:8000`
- iOS/Web/Desktop: `localhost:8000`

### Admin Dashboard (`vite.config.js`)
- 프록시로 Docker 서비스 연결
- ML Service: `http://ml-service:8000`
- User Service: `http://user-service:8080`

### Docker (`docker-compose.yml`)
- 네트워크: `carsentix-network`
- ML Service ↔ User Service 내부 통신

---

## 권장 사항

1. **프로덕션 배포 전**
   - `.env` 파일의 API 키 교체
   - JWT_SECRET 변경
   - HTTPS 설정

2. **코드 품질**
   - API_BASE는 환경변수로 관리 권장
   - 공통 상수는 별도 config 파일로 분리

3. **모니터링**
   - Health check 알림 설정
   - API 응답 시간 모니터링

---

> 마지막 업데이트: 2025-12-10

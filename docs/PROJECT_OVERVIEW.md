# 📖 Car-Sentix 프로젝트 전체 개요

> **최종 업데이트**: 2024년 12월 4일  
> **작성 원칙**: 모든 내용은 **사실에 기반**하여 작성됨

---

## 1. 프로젝트 정의

### 1.1 프로젝트명
**Car-Sentix** (Car + Sentiment + Analytics)

### 1.2 한글명
**"언제 살까?"** - 중고차 구매 의사결정 지원 시스템

### 1.3 핵심 가치 제안
> "단순한 가격 예측을 넘어, **언제 사야 할지**까지 알려주는 통합 어드바이저"

### 1.4 프로젝트 유형
- **학술 프로젝트** (졸업/학기 프로젝트)
- **마이크로서비스 아키텍처** 기반
- **풀스택** (Frontend + Backend + ML)

---

## 2. 비즈니스 목표

### 2.1 사용자 대상

| 대상 | 주요 니즈 | 제공 가치 |
|------|----------|----------|
| **일반 소비자** | 중고차 적정 가격 확인 | 가격 예측, 타이밍 분석 |
| **딜러사 (B2B)** | 매집/매각 타이밍 판단 | 시장 인텔리전스 |
| **금융사 (B2B)** | 담보가치 평가 | 예측 정확도 데이터 |
| **렌터카 (B2B)** | 차량 교체 시점 판단 | 감가 예측 |

### 2.2 차별화 포인트

1. **경제지표 기반 타이밍 분석** (경쟁사에 없는 기능)
   - 한국은행 금리
   - 국제 유가 (WTI)
   - 환율 (USD/KRW)
   - 네이버 검색 트렌드

2. **AI 통합 분석**
   - Groq LLM 기반 네고 대본 생성
   - 허위매물 탐지

3. **B2B 데이터 서비스**
   - API 형태로 데이터 제공
   - 시장 인텔리전스 대시보드

---

## 3. 시스템 구성

### 3.1 서비스 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                        [클라이언트 레이어]                        │
├─────────────────────────────────────────────────────────────────┤
│  📱 Flutter App (3000)     │  🖥️ Admin Dashboard (3001)        │
│  - 모바일/웹 앱            │  - React/Vite                      │
│  - 일반 사용자용           │  - 관리자/B2B용                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        [API 게이트웨이]                          │
├─────────────────────────────────────────────────────────────────┤
│  🟢 ML Service (8000)       │  🔵 User Service (8080)           │
│  - FastAPI/Python           │  - Spring Boot/Java               │
│  - 가격 예측                │  - 인증/인가 (JWT)                │
│  - 타이밍 분석              │  - 소셜 로그인                    │
│  - B2B 인사이트             │  - 즐겨찾기/이력                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        [데이터 레이어]                           │
├─────────────────────────────────────────────────────────────────┤
│  📊 XGBoost Models          │  🗄️ SQLite DB                     │
│  - 국산차 v12               │  - 분석 이력                      │
│  - 수입차 v14               │  - 사용자 정보                    │
│  - 연료별 분리 학습         │  - 즐겨찾기                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        [외부 데이터 소스]                        │
├─────────────────────────────────────────────────────────────────┤
│  Yahoo Finance  │  네이버 데이터랩  │  Groq AI  │  엔카 데이터  │
│  (유가/환율)    │  (검색 트렌드)    │  (LLM)    │  (차량 정보)  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 기술 스택 (사실)

| 구분 | 기술 | 버전/상세 |
|------|------|----------|
| **Frontend** | Flutter | 3.x, Dart |
| **Frontend** | React | Vite, Recharts |
| **Backend** | FastAPI | Python 3.11 |
| **Backend** | Spring Boot | Java 17, Gradle |
| **ML** | XGBoost | scikit-learn |
| **DB** | SQLite | 로컬 파일 |
| **Container** | Docker | docker-compose |
| **AI** | Groq | Llama3-70b-8192 |

---

## 4. 핵심 기능

### 4.1 Track 1: 가격 예측 (XGBoost)

**성능 지표 (사실)**
| 지표 | 국산차 | 수입차 |
|------|--------|--------|
| R² Score | 0.87 | 0.82 |
| MAE | 231만원 | 450만원 |
| 학습 데이터 | 119,343대 | 45,000대 |
| 모델 수 | 253개 | 180개 |

**입력 Feature**
- brand_encoded (브랜드)
- model_encoded (모델)
- year (연식)
- mileage (주행거리)
- fuel_encoded (연료 타입)
- 옵션 (선루프, 네비, 가죽시트 등)

### 4.2 Track 2: 타이밍 분석

**점수 산정 방식 (사실)**
```
타이밍 점수 = 거시경제(40%) + 검색트렌드(30%) + 신차일정(30%)
```

**데이터 소스 (사실)**
| 지표 | 소스 | API/방식 | 상태 |
|------|------|----------|------|
| 기준금리 | 한국은행 | BOK API | 실제 |
| 국제유가 | Yahoo Finance | yfinance | 실제 |
| 환율 | Yahoo Finance | yfinance | 실제 |
| 검색트렌드 | 네이버 | DataLab API | 실제 |
| 신차일정 | CSV | 수동 관리 | 정적 |

### 4.3 Track 3: AI 분석 (Groq)

**기능 목록**
1. 매수/관망 신호등 (Strong Buy ~ Avoid)
2. 허위매물 탐지기 (위험도 0-100)
3. 네고 대본 생성기 (협상 포인트 제시)

**모델**: Llama3-70b-8192 (Groq Cloud)

### 4.4 B2B 인사이트 (신규)

**제공 지표**
- Market Opportunity Index (시장 기회 지수)
- Buying Signals (매집 추천)
- Sell Signals (매각 경고)
- Portfolio ROI (포트폴리오 수익률)
- Macro Sensitivity (민감도 분석)
- Forecast Accuracy (예측 정확도)

---

## 5. 데이터 흐름

### 5.1 가격 예측 흐름

```
[사용자 입력] → [Flutter App] → [ML Service API]
                                      │
                                      ▼
                            [PredictionServiceV12]
                                      │
                        ┌─────────────┴─────────────┐
                        ▼                           ▼
              [국산차 모델 선택]           [수입차 모델 선택]
                        │                           │
                        ▼                           ▼
              [XGBoost Predict]           [XGBoost Predict]
                        │                           │
                        └─────────────┬─────────────┘
                                      ▼
                            [가격 + 신뢰구간 반환]
                                      │
                                      ▼
                            [Flutter 결과 표시]
```

### 5.2 타이밍 분석 흐름

```
[모델명 입력] → [TimingService] 
                     │
    ┌────────────────┼────────────────┐
    ▼                ▼                ▼
[한국은행 API]  [Yahoo Finance]  [네이버 DataLab]
    │                │                │
    ▼                ▼                ▼
[금리 점수]     [유가/환율 점수]  [검색트렌드 점수]
    │                │                │
    └────────────────┴────────────────┘
                     │
                     ▼
              [가중 합산 (40:30:30)]
                     │
                     ▼
              [타이밍 점수 0-100]
```

---

## 6. 프로젝트 구조

```
used-car-price-predictor/
│
├── 📱 flutter_app/              # Flutter 모바일/웹 앱
│   ├── lib/
│   │   ├── main.dart            # 앱 진입점
│   │   ├── home_page.dart       # 홈 화면
│   │   ├── result_page.dart     # 결과 화면
│   │   └── services/
│   │       └── api_service.dart # API 클라이언트
│   └── pubspec.yaml
│
├── 🖥️ admin-dashboard/          # React 관리자 대시보드
│   ├── src/
│   │   ├── pages/
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── B2BMarketIntelligencePage.jsx
│   │   │   └── ...
│   │   └── components/
│   └── package.json
│
├── 🟢 ml-service/               # FastAPI ML 서비스
│   ├── services/
│   │   ├── prediction_v12.py    # 가격 예측
│   │   ├── timing.py            # 타이밍 분석
│   │   ├── enhanced_timing.py   # Phase 3 고도화
│   │   ├── b2b_intelligence.py  # B2B 인사이트
│   │   └── groq_service.py      # AI 분석
│   └── utils/
│
├── 🔵 user-service/             # Spring Boot 사용자 서비스
│   └── src/main/java/
│       ├── controller/
│       ├── service/
│       └── security/
│
├── 📊 models/                   # 학습된 XGBoost 모델
│   ├── domestic_unified_v12_*.pkl
│   └── imported_unified_v14_*.pkl
│
├── 📁 data/                     # 학습 데이터
│   └── encar_*.csv
│
├── 📄 docs/                     # 문서
│   ├── PROJECT_OVERVIEW.md      # (이 문서)
│   ├── DEVELOPMENT_LOG.md       # 작업 일지
│   ├── API_SPECIFICATION.md     # API 명세
│   └── ARCHITECTURE.md          # 아키텍처
│
├── run_server.py                # ML API 서버 진입점
├── docker-compose.yml           # Docker 구성
└── requirements.txt             # Python 의존성
```

---

## 7. 환경 설정

### 7.1 필수 환경 변수 (.env)

```env
# Groq AI
GROQ_API_KEY=gsk_xxx

# 한국은행 API
BOK_API_KEY=xxx

# 네이버 데이터랩
NAVER_CLIENT_ID=xxx
NAVER_CLIENT_SECRET=xxx

# 소셜 로그인 (선택)
NAVER_CLIENT_ID_OAUTH=xxx
KAKAO_CLIENT_ID=xxx
GOOGLE_CLIENT_ID=xxx
```

### 7.2 Docker 실행

```bash
# 전체 서비스 실행
docker compose up -d

# 개별 서비스 실행
docker compose up ml-service -d
docker compose up admin-dashboard -d
docker compose up user-service -d
```

### 7.3 포트 구성

| 서비스 | 포트 | URL |
|--------|------|-----|
| ML Service | 8000 | http://localhost:8000 |
| User Service | 8080 | http://localhost:8080 |
| Admin Dashboard | 3001 | http://localhost:3001 |
| Flutter Web | 3000 | http://localhost:3000 |

---

## 8. 제한사항 및 주의사항

### 8.1 데이터 제한

| 항목 | 상태 | 비고 |
|------|------|------|
| 과거 시세 데이터 | 없음 | 기업 제휴 필요 |
| 실제 거래 가격 | 없음 | 매물 가격만 수집 |
| 딜러 마진 데이터 | 없음 | 추정치 사용 |

### 8.2 시뮬레이션 데이터 (명시)

| 항목 | 생성 방식 |
|------|----------|
| 차종별 ROI | 감가율 + 수요트렌드 규칙 기반 |
| API 호출량 | 일관된 랜덤 값 |
| 예측 정확도 | 시뮬레이션 히스토리 |

### 8.3 면책 사항

> 본 시스템의 가격 예측 및 타이밍 분석은 참고용이며, 
> 실제 거래 가격과 차이가 있을 수 있습니다.
> 투자 결정은 사용자 본인의 판단에 따릅니다.

---

## 9. 향후 계획

### 9.1 데이터 고도화
- [ ] 엔카/KB차차차 API 공식 연동
- [ ] 국토부 자동차365 거래량 데이터 연동
- [ ] 과거 시세 데이터 수집 (기업 제휴)

### 9.2 기능 확장
- [ ] 차량 비교 기능
- [ ] 알림 서비스 (가격 변동, 타이밍 적기)
- [ ] 차량 상태 진단 AI

### 9.3 B2B 확장
- [ ] 유료 API 플랜
- [ ] 기업 전용 대시보드
- [ ] 커스텀 리포트 생성

---

## 10. 연락처

- **프로젝트 담당**: [학생 이름]
- **지도 교수**: [교수님 성함]
- **GitHub**: [Repository URL]

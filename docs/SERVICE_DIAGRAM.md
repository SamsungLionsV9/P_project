# 🚗 Car-Sentix 서비스 구성도

## 1. 전체 시스템 아키텍처

```mermaid
flowchart TB
    subgraph CLIENT["📱 클라이언트 (Flutter App)"]
        APP[Car-Sentix 모바일 앱]
        APP_FUNC["• 간편 조회\n• 상세 입력\n• 결과 분석\n• 즐겨찾기/알림"]
    end

    subgraph GATEWAY["🔀 API Gateway (Spring Boot :8080)"]
        GW_AUTH[인증/인가]
        GW_ROUTE[라우팅]
        GW_RATE[Rate Limiting]
    end

    subgraph CACHE["⚡ 캐시 레이어"]
        REDIS[(Redis Cache)]
        REDIS_FUNC["• 세션 관리\n• API 응답 캐싱\n• Rate Limit 카운터\n• 인기 검색어"]
    end

    subgraph AI_SERVICE["🤖 AI 서비스 서버 (FastAPI :8001)"]
        PREDICT[가격 예측 API]
        TIMING[타이밍 분석 API]
        SMART[통합 분석 API]
        SIMILAR[유사 차량 API]
        
        subgraph MODELS["📦 학습된 모델 (Production)"]
            DOM_MODEL["domestic_v11.pkl\n국산차 MAPE 9.9%"]
            IMP_MODEL["imported_v13.pkl\n외제차 MAPE 12.1%"]
        end
    end

    subgraph USER_SERVICE["👤 사용자 서비스 (Spring Boot :8080)"]
        AUTH[JWT 인증]
        OAUTH[소셜 로그인]
        USER_DB[(MySQL)]
        USER_FUNC["• 회원가입/로그인\n• 프로필 관리\n• 검색 이력\n• 즐겨찾기"]
    end

    subgraph EXTERNAL["🌐 외부 데이터 소스"]
        BOK[한국은행 API\n기준금리]
        NAVER[네이버 데이터랩\n검색트렌드]
        OIL[국제유가 API]
        EXCHANGE[환율 API]
    end

    subgraph AI_TRAIN["🎓 AI 학습 서버 (분리)"]
        JUPYTER[Jupyter Lab]
        TRAIN_SCRIPT["학습 스크립트\n• train_domestic.py\n• train_imported.py"]
        TRAIN_DATA[(학습 데이터\n국산 119K / 외제 49K)]
        TRAIN_OUTPUT["학습 결과물\n• .pkl 모델\n• encoders\n• features"]
    end

    subgraph GROQ["🧠 AI 분석 (Groq LLM)"]
        SIGNAL[매수/관망 신호]
        FRAUD[허위매물 탐지]
        NEGO[네고 대본 생성]
    end

    %% 연결
    APP --> GATEWAY
    GATEWAY --> REDIS
    GATEWAY --> AI_SERVICE
    GATEWAY --> USER_SERVICE
    
    REDIS -.->|캐시 히트| GATEWAY
    
    AI_SERVICE --> MODELS
    AI_SERVICE --> EXTERNAL
    AI_SERVICE --> GROQ
    
    USER_SERVICE --> USER_DB
    USER_SERVICE --> REDIS
    
    TRAIN_DATA --> TRAIN_SCRIPT
    TRAIN_SCRIPT --> TRAIN_OUTPUT
    TRAIN_OUTPUT -.->|배포| MODELS

    classDef client fill:#e1f5fe,stroke:#01579b
    classDef gateway fill:#fff3e0,stroke:#e65100
    classDef cache fill:#ffebee,stroke:#c62828
    classDef ai fill:#e8f5e9,stroke:#2e7d32
    classDef user fill:#f3e5f5,stroke:#7b1fa2
    classDef external fill:#fafafa,stroke:#616161
    classDef train fill:#fff8e1,stroke:#f57f17
    classDef groq fill:#e3f2fd,stroke:#1565c0

    class CLIENT client
    class GATEWAY gateway
    class CACHE cache
    class AI_SERVICE ai
    class USER_SERVICE user
    class EXTERNAL external
    class AI_TRAIN train
    class GROQ groq
```

---

## 2. 데이터 흐름도 (서비스 시나리오)

```mermaid
sequenceDiagram
    autonumber
    participant U as 📱 사용자
    participant F as Flutter App
    participant G as API Gateway
    participant R as Redis Cache
    participant M as ML Service
    participant D as 외부 데이터
    participant AI as Groq AI
    participant DB as MySQL

    rect rgb(240, 248, 255)
        Note over U,DB: 🔍 차량 가격 조회 시나리오
    end

    U->>F: 차량 정보 입력<br/>(브랜드, 모델, 연식, 주행거리)
    F->>G: POST /api/smart-analysis
    
    G->>R: 캐시 조회
    alt 캐시 히트
        R-->>G: 캐시된 결과 반환
        G-->>F: 즉시 응답 (50ms)
    else 캐시 미스
        G->>M: 분석 요청 전달
        
        par 병렬 처리
            M->>M: 🤖 가격 예측<br/>(V11/V13 모델)
        and
            M->>D: 거시경제 데이터 수집
            D-->>M: 금리/환율/유가
        and
            M->>M: 📊 비슷한 차량 분석
        end
        
        M->>M: ⏱️ 타이밍 점수 계산
        
        alt 판매가격 제공됨
            M->>AI: AI 종합 분석 요청
            AI-->>M: 매수신호/허위매물/네고대본
        end
        
        M-->>G: 분석 결과
        G->>R: 결과 캐싱 (TTL: 1시간)
        G-->>F: 응답 (500ms)
    end
    
    F-->>U: 결과 화면 표시

    rect rgb(255, 248, 240)
        Note over U,DB: 💾 검색 이력 저장
    end
    
    F->>G: POST /api/history
    G->>DB: 검색 이력 저장
    DB-->>G: 저장 완료
```

---

## 3. AI 학습 vs AI 서비스 분리 구조

```mermaid
flowchart LR
    subgraph TRAINING["🎓 AI 학습 환경 (오프라인)"]
        direction TB
        RAW["📁 원본 데이터\n• encar_domestic.csv\n• encar_imported.csv"]
        CLEAN["🧹 전처리\n• 이상치 제거\n• 피처 엔지니어링"]
        TRAIN["🔬 모델 학습\n• XGBoost\n• Optuna 튜닝"]
        EVAL["📊 평가\n• MAPE < 10%\n• R² > 0.95"]
        PKL["📦 모델 저장\n• .pkl 파일\n• encoders"]
        
        RAW --> CLEAN --> TRAIN --> EVAL
        EVAL -->|통과| PKL
        EVAL -->|실패| TRAIN
    end

    subgraph DEPLOY["🚀 배포 프로세스"]
        direction TB
        GIT["Git Push\n모델 파일"]
        CI["CI/CD\n자동 배포"]
        VER["버전 관리\n v11 → v12"]
    end

    subgraph SERVING["🤖 AI 서비스 환경 (온라인)"]
        direction TB
        LOAD["📥 모델 로드\n서버 시작 시 1회"]
        API["⚡ API 서비스\n• /predict\n• /timing\n• /smart-analysis"]
        CACHE2["💾 Redis 캐시\n응답 시간 최적화"]
        MON["📈 모니터링\n• 예측 정확도\n• 응답 시간"]
        
        LOAD --> API --> CACHE2
        API --> MON
    end

    PKL --> GIT --> CI --> LOAD

    style TRAINING fill:#fff8e1,stroke:#f57f17
    style DEPLOY fill:#e3f2fd,stroke:#1565c0
    style SERVING fill:#e8f5e9,stroke:#2e7d32
```

---

## 4. 상세 컴포넌트 구성도

```mermaid
flowchart TB
    subgraph FLUTTER["📱 Flutter Client"]
        direction LR
        HOME["🏠 홈 화면"]
        QUICK["⚡ 간편 조회"]
        DETAIL["📝 상세 입력"]
        RESULT["📊 결과 화면"]
        HISTORY["📜 검색 이력"]
        FAVORITE["⭐ 즐겨찾기"]
        ALERT["🔔 가격 알림"]
        
        HOME --> QUICK
        HOME --> DETAIL
        HOME --> HISTORY
        QUICK --> RESULT
        DETAIL --> RESULT
        RESULT --> FAVORITE
        RESULT --> ALERT
    end

    subgraph SPRING["☕ Spring Boot (User Service)"]
        direction TB
        
        subgraph AUTH_MOD["🔐 인증 모듈"]
            JWT_FILTER[JWT Filter]
            OAUTH2[OAuth2 Client]
            SEC_CONFIG[Security Config]
        end
        
        subgraph USER_MOD["👤 사용자 모듈"]
            USER_CTRL[UserController]
            USER_SVC[UserService]
            USER_REPO[UserRepository]
        end
        
        subgraph CAR_MOD["🚗 차량 데이터 모듈"]
            CAR_CTRL[CarDataController]
            CAR_SVC[CarDataService]
            CAR_REPO[CarRepository]
        end
        
        subgraph GW_MOD["🔀 ML Gateway"]
            ML_GW[MLGatewayController]
            REST_TPL[RestTemplate]
        end
    end

    subgraph FASTAPI["🐍 FastAPI (ML Service)"]
        direction TB
        
        subgraph PRED_MOD["💰 예측 모듈"]
            PRED_V11[PredictionServiceV11]
            DOM_ENC[Domestic Encoders]
            IMP_ENC[Imported Encoders]
        end
        
        subgraph TIME_MOD["⏱️ 타이밍 모듈"]
            TIME_SVC[TimingService]
            DATA_COL[DataCollectors]
            REAL_ENGINE[RealTimingEngine]
        end
        
        subgraph GROQ_MOD["🧠 AI 분석 모듈"]
            GROQ_SVC[GroqService]
            SIGNAL_GEN[SignalGenerator]
            FRAUD_DET[FraudDetector]
            NEGO_GEN[NegotiationGenerator]
        end
        
        subgraph HIST_MOD["📜 이력 모듈"]
            HIST_SVC[HistoryService]
            POP_SVC[PopularService]
            SIM_SVC[SimilarService]
        end
    end

    subgraph DATA["💾 데이터 저장소"]
        direction LR
        MYSQL[(MySQL\n사용자/이력)]
        REDIS2[(Redis\n캐시/세션)]
        PKL2["📦 PKL Files\n학습 모델"]
        CSV["📊 CSV Files\n차량 데이터"]
    end

    FLUTTER --> SPRING
    SPRING --> FASTAPI
    SPRING --> MYSQL
    SPRING --> REDIS2
    FASTAPI --> PKL2
    FASTAPI --> CSV
    FASTAPI --> REDIS2

    style FLUTTER fill:#e1f5fe,stroke:#01579b
    style SPRING fill:#fff3e0,stroke:#e65100
    style FASTAPI fill:#e8f5e9,stroke:#2e7d32
    style DATA fill:#fafafa,stroke:#616161
```

---

## 5. Redis 캐싱 전략

```mermaid
flowchart TB
    subgraph REQUEST["📥 요청 처리"]
        REQ[API 요청]
        HASH["캐시 키 생성\nMD5(brand+model+year+mileage)"]
    end

    subgraph CACHE_LOGIC["⚡ 캐시 로직"]
        CHECK{Redis 조회}
        HIT["✅ 캐시 히트\n응답: 50ms"]
        MISS["❌ 캐시 미스"]
        COMPUTE["🔄 계산 수행\n응답: 500ms"]
        STORE["💾 캐시 저장\nTTL: 1시간"]
    end

    subgraph CACHE_TYPES["📦 캐시 유형"]
        PRED_CACHE["🚗 예측 결과\npred:{hash}\nTTL: 1시간"]
        TIME_CACHE["⏱️ 타이밍 분석\ntiming:{model}\nTTL: 30분"]
        POP_CACHE["🔥 인기 차량\npopular:{category}\nTTL: 5분"]
        RATE_CACHE["🚦 Rate Limit\nrate:{ip}\nTTL: 1분"]
        SESSION["🔐 세션\nsession:{token}\nTTL: 24시간"]
    end

    REQ --> HASH --> CHECK
    CHECK -->|HIT| HIT
    CHECK -->|MISS| MISS --> COMPUTE --> STORE
    HIT --> RESPONSE
    STORE --> RESPONSE[📤 응답]

    CACHE_TYPES -.-> CHECK

    style REQUEST fill:#e3f2fd
    style CACHE_LOGIC fill:#fff3e0
    style CACHE_TYPES fill:#ffebee
```

---

## 6. 서비스 효과 요약

```mermaid
mindmap
  root((Car-Sentix))
    📊 데이터 분석
      국산차 119,428건
      외제차 49,114건
      실거래가 기반
    🤖 AI 학습
      XGBoost 모델
      MAPE 9.9%
      Optuna 튜닝
    ⚡ AI 서비스
      실시간 예측
      500ms 응답
      캐시 최적화
    📱 클라이언트
      간편 조회
      AI 분석
      가격 알림
    💡 기대 효과
      허위매물 탐지
      적정가 판단
      협상력 강화
```

---

## 7. 기술 스택 정리

| 레이어 | 기술 | 용도 |
|--------|------|------|
| **Client** | Flutter, Dart | 크로스플랫폼 모바일 앱 |
| **Gateway** | Spring Boot, Java 17 | API Gateway, 인증 |
| **ML Service** | FastAPI, Python 3.11 | 가격 예측, AI 분석 |
| **AI Model** | XGBoost, Scikit-learn | 머신러닝 모델 |
| **LLM** | Groq (Llama 3.1) | 자연어 분석 |
| **Cache** | Redis 7.x | 캐싱, 세션, Rate Limit |
| **Database** | MySQL 8.x | 사용자, 이력 저장 |
| **External API** | 한국은행, 네이버 | 거시경제 데이터 |

---

## 8. 배포 환경

```mermaid
flowchart LR
    subgraph DEV["🔧 개발 환경"]
        LOCAL[localhost]
        DEV_DB[(개발 DB)]
    end

    subgraph STAGE["🧪 스테이징"]
        STAGE_SVR[테스트 서버]
        STAGE_DB[(테스트 DB)]
    end

    subgraph PROD["🚀 운영 환경"]
        LB[Load Balancer]
        APP1[App Server 1]
        APP2[App Server 2]
        PROD_DB[(운영 DB)]
        PROD_REDIS[(Redis Cluster)]
    end

    DEV -->|Git Push| STAGE -->|승인| PROD
    LB --> APP1
    LB --> APP2
    APP1 --> PROD_DB
    APP2 --> PROD_DB
    APP1 --> PROD_REDIS
    APP2 --> PROD_REDIS

    style DEV fill:#e8f5e9
    style STAGE fill:#fff3e0
    style PROD fill:#e3f2fd
```

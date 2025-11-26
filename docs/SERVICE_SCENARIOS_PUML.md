# 🚗 Car-Sentix 서비스 시나리오 (PlantUML)

## 📌 PlantUML 렌더링 방법
- **VS Code**: PlantUML 확장 설치 후 `Alt + D`
- **온라인**: [PlantUML Server](https://www.plantuml.com/plantuml)
- **IntelliJ**: PlantUML Integration 플러그인

---

## 1️⃣ 전체 시스템 아키텍처 (C4 Container)

```plantuml
@startuml Car-Sentix System Architecture
!define ICONURL https://raw.githubusercontent.com/tupadr3/plantuml-icon-font-sprites/v2.4.0
!include ICONURL/common.puml
!include ICONURL/font-awesome-5/mobile_alt.puml
!include ICONURL/font-awesome-5/server.puml
!include ICONURL/font-awesome-5/database.puml
!include ICONURL/font-awesome-5/brain.puml
!include ICONURL/font-awesome-5/cloud.puml
!include ICONURL/font-awesome-5/cogs.puml
!include ICONURL/font-awesome-5/user.puml
!include ICONURL/font-awesome-5/shield_alt.puml
!include ICONURL/font-awesome-5/bolt.puml

skinparam backgroundColor #FEFEFE
skinparam handwritten false
skinparam defaultFontName Malgun Gothic
skinparam shadowing true

title <size:24><b>Car-Sentix AI 중고차 가격 분석 시스템</b></size>\n전체 아키텍처 구성도

' 사용자
actor "사용자" as User #LightBlue
FA5_MOBILE_ALT(mobile, "Flutter App", rectangle, #4FC3F7)

' API Gateway
package "API Gateway Layer" #FFF3E0 {
    FA5_SHIELD_ALT(gateway, "Spring Boot\nAPI Gateway\n:8080", rectangle, #FF9800)
    FA5_BOLT(redis, "Redis Cache\n세션/캐시", rectangle, #F44336)
}

' AI Service Layer
package "AI Service Layer" #E8F5E9 {
    FA5_BRAIN(mlservice, "FastAPI\nML Service\n:8001", rectangle, #4CAF50)
    FA5_COGS(prediction, "가격 예측\nV11/V13", rectangle, #8BC34A)
    FA5_COGS(timing, "타이밍 분석\n실시간 데이터", rectangle, #8BC34A)
    FA5_COGS(groq, "Groq AI\n자연어 분석", rectangle, #8BC34A)
}

' AI Training Layer (분리)
package "AI Training Layer (Offline)" #FFF8E1 {
    FA5_SERVER(trainserver, "학습 서버\nJupyter Lab", rectangle, #FFC107)
    database "학습 데이터\n국산 119K\n외제 49K" as traindata #FFE082
    file "학습 결과\n.pkl 모델" as pklfile #FFECB3
}

' Data Layer
package "Data Layer" #E3F2FD {
    FA5_DATABASE(mysql, "MySQL\n사용자/이력", rectangle, #2196F3)
    FA5_DATABASE(csvdata, "CSV 데이터\n차량 정보", rectangle, #64B5F6)
}

' External APIs
package "External APIs" #FAFAFA {
    FA5_CLOUD(bok, "한국은행\n기준금리", rectangle, #9E9E9E)
    FA5_CLOUD(naver, "네이버\n검색트렌드", rectangle, #9E9E9E)
    FA5_CLOUD(oil, "유가/환율\nAPI", rectangle, #9E9E9E)
}

' Connections
User --> mobile : 앱 사용
mobile --> gateway : HTTPS 요청
gateway --> redis : 캐시 조회
gateway --> mlservice : ML API 호출
gateway --> mysql : 사용자 조회

mlservice --> prediction
mlservice --> timing
mlservice --> groq
mlservice --> csvdata : 차량 데이터

timing --> bok : 금리 조회
timing --> naver : 트렌드 조회
timing --> oil : 유가 조회

trainserver --> traindata : 데이터 학습
trainserver --> pklfile : 모델 저장
pklfile ..> prediction : <b>배포</b>\n(오프라인→온라인)

legend right
  |= 구분 |= 설명 |
  | <#4FC3F7> 클라이언트 | Flutter 모바일 앱 |
  | <#FF9800> Gateway | 인증/라우팅/Rate Limit |
  | <#4CAF50> AI 서비스 | 실시간 예측 API |
  | <#FFC107> AI 학습 | 오프라인 모델 학습 |
  | <#2196F3> 저장소 | MySQL, Redis, CSV |
endlegend

@enduml
```

---

## 2️⃣ 가격 예측 시나리오 (Sequence Diagram)

```plantuml
@startuml Price Prediction Scenario
!define ICONURL https://raw.githubusercontent.com/tupadr3/plantuml-icon-font-sprites/v2.4.0
!include ICONURL/common.puml
!include ICONURL/font-awesome-5/mobile_alt.puml
!include ICONURL/font-awesome-5/server.puml
!include ICONURL/font-awesome-5/brain.puml
!include ICONURL/font-awesome-5/database.puml

skinparam backgroundColor #FEFEFE
skinparam handwritten false
skinparam defaultFontName Malgun Gothic
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true

title <size:20><b>시나리오 1: 중고차 가격 예측</b></size>\n사용자가 차량 정보를 입력하고 AI 예측 결과를 받는 과정

actor "👤 사용자" as User #LightBlue
participant "📱 Flutter App" as App #E1F5FE
participant "🔀 API Gateway\n(Spring Boot)" as Gateway #FFF3E0
participant "⚡ Redis Cache" as Redis #FFEBEE
participant "🤖 ML Service\n(FastAPI)" as ML #E8F5E9
participant "🧠 XGBoost\nModel" as Model #C8E6C9
participant "📊 Groq AI" as Groq #E3F2FD

autonumber

== 차량 정보 입력 ==
User -> App : 차량 정보 입력\n(브랜드, 모델, 연식, 주행거리)
activate App #E1F5FE

App -> Gateway : POST /api/smart-analysis\n{brand, model, year, mileage}
activate Gateway #FFF3E0

== 캐시 확인 ==
Gateway -> Redis : GET cache:predict:{hash}
activate Redis #FFEBEE

alt 캐시 히트 (HIT)
    Redis --> Gateway : 캐시된 결과 반환
    Gateway --> App : 200 OK (50ms)
    App --> User : 결과 화면 표시
else 캐시 미스 (MISS)
    Redis --> Gateway : null
    deactivate Redis

    == AI 예측 수행 ==
    Gateway -> ML : 예측 요청 전달
    activate ML #E8F5E9
    
    ML -> Model : 피처 생성 & 예측
    activate Model #C8E6C9
    note right of Model
        국산차: domestic_v11.pkl
        외제차: imported_v13.pkl
        MAPE: 9.9% ~ 12.1%
    end note
    Model --> ML : predicted_price: 2,628만원\nprice_range: [2,368, 2,888]
    deactivate Model

    == AI 분석 (옵션) ==
    opt 판매가격 제공 시
        ML -> Groq : AI 종합 분석 요청
        activate Groq #E3F2FD
        Groq --> ML : signal: "매수"\nfraud_score: 15\nnegotiation_script
        deactivate Groq
    end

    ML --> Gateway : 분석 결과 반환
    deactivate ML

    == 캐시 저장 ==
    Gateway -> Redis : SET cache:predict:{hash}\nTTL: 3600s
    activate Redis #FFEBEE
    Redis --> Gateway : OK
    deactivate Redis

    Gateway --> App : 200 OK (500ms)
    deactivate Gateway
    
    App --> User : 📊 결과 화면 표시
    deactivate App
end

note over User, Groq #FFFDE7
    <b>🎯 기대 효과</b>
    • 실시간 AI 가격 예측 (MAPE < 10%)
    • 적정가 대비 판매가 비교
    • 매수/관망/회피 신호 제공
    • 협상 대본 자동 생성
end note

@enduml
```

---

## 3️⃣ AI 학습 서버 vs AI 서비스 분리 구조

```plantuml
@startuml AI Training vs Serving
!define ICONURL https://raw.githubusercontent.com/tupadr3/plantuml-icon-font-sprites/v2.4.0
!include ICONURL/common.puml
!include ICONURL/font-awesome-5/graduation_cap.puml
!include ICONURL/font-awesome-5/rocket.puml
!include ICONURL/font-awesome-5/database.puml
!include ICONURL/font-awesome-5/cogs.puml
!include ICONURL/font-awesome-5/check_circle.puml
!include ICONURL/font-awesome-5/sync.puml

skinparam backgroundColor #FEFEFE
skinparam handwritten false
skinparam defaultFontName Malgun Gothic

title <size:20><b>AI 학습 서버 vs AI 서비스 분리 구조</b></size>\n오프라인 학습 → 배포 → 온라인 서비스

' Training Environment
rectangle "🎓 AI 학습 환경 (Offline)" as TrainEnv #FFF8E1 {
    
    rectangle "📁 원본 데이터" as RawData #FFE082 {
        file "encar_domestic.csv\n119,428건" as DomCSV
        file "encar_imported.csv\n49,114건" as ImpCSV
    }
    
    rectangle "🔬 학습 파이프라인" as Pipeline #FFECB3 {
        rectangle "전처리" as Preprocess #FFF59D {
            card "결측치 처리" as M1
            card "이상치 제거" as M2
            card "피처 엔지니어링" as M3
        }
        
        rectangle "모델 학습" as Training #FFF59D {
            card "XGBoost" as XGB
            card "Optuna 튜닝" as Optuna
            card "교차 검증" as CV
        }
        
        rectangle "평가" as Eval #FFF59D {
            card "MAPE < 10%" as MAPE
            card "R² > 0.95" as R2
        }
    }
    
    rectangle "📦 학습 결과물" as Output #FFE082 {
        file "domestic_v11.pkl\n(7.4MB)" as DomModel
        file "imported_v13.pkl\n(5.2MB)" as ImpModel
        file "encoders.pkl" as Encoders
    }
}

' Deployment
rectangle "🚀 배포 프로세스" as Deploy #E3F2FD {
    card "Git Push" as Git #90CAF9
    card "CI/CD\nGitHub Actions" as CICD #90CAF9
    card "버전 관리\nv11 → v12" as Version #90CAF9
}

' Serving Environment
rectangle "🤖 AI 서비스 환경 (Online)" as ServeEnv #E8F5E9 {
    
    rectangle "⚡ FastAPI 서버 (:8001)" as Server #A5D6A7 {
        rectangle "모델 로딩" as Load #C8E6C9 {
            card "서버 시작 시\n1회 로드" as LoadOnce
        }
        
        rectangle "API 엔드포인트" as API #C8E6C9 {
            card "POST /predict" as Predict
            card "POST /timing" as Timing
            card "POST /smart-analysis" as Smart
        }
        
        rectangle "최적화" as Optimize #C8E6C9 {
            card "Redis 캐싱" as Cache
            card "배치 처리" as Batch
        }
    }
    
    rectangle "📈 모니터링" as Monitor #A5D6A7 {
        card "예측 정확도" as AccMon
        card "응답 시간" as LatMon
        card "에러율" as ErrMon
    }
}

' Connections
RawData --> Pipeline
Pipeline --> Output

Output --> Deploy
Deploy --> Server

DomCSV --> Preprocess
ImpCSV --> Preprocess
Preprocess --> Training
Training --> Eval
Eval --> DomModel
Eval --> ImpModel

' Notes
note right of TrainEnv #FFFDE7
    <b>🔒 오프라인 환경</b>
    • GPU 서버 또는 Colab
    • 대용량 데이터 처리
    • 하이퍼파라미터 튜닝
    • 주기: 월 1회 재학습
end note

note right of ServeEnv #E8F5E9
    <b>⚡ 온라인 환경</b>
    • CPU 서버 (경량화)
    • 실시간 예측 (<500ms)
    • 고가용성 (HA)
    • 24/7 서비스
end note

legend right
|= 단계 |= 소요시간 |= 주기 |
| 데이터 수집 | 1일 | 월 1회 |
| 모델 학습 | 2-4시간 | 월 1회 |
| 배포 | 10분 | 필요시 |
| 예측 서비스 | 500ms | 실시간 |
endlegend

@enduml
```

---

## 4️⃣ 타이밍 분석 시나리오 (실시간 데이터)

```plantuml
@startuml Timing Analysis Scenario
!define ICONURL https://raw.githubusercontent.com/tupadr3/plantuml-icon-font-sprites/v2.4.0
!include ICONURL/common.puml
!include ICONURL/font-awesome-5/clock.puml
!include ICONURL/font-awesome-5/chart_line.puml
!include ICONURL/font-awesome-5/cloud.puml

skinparam backgroundColor #FEFEFE
skinparam handwritten false
skinparam defaultFontName Malgun Gothic
skinparam sequenceMessageAlign center

title <size:20><b>시나리오 2: 매수 타이밍 분석</b></size>\n실시간 거시경제 데이터 기반 분석

actor "👤 사용자" as User #LightBlue
participant "📱 Flutter App" as App #E1F5FE
participant "🤖 ML Service" as ML #E8F5E9
participant "🏦 한국은행\nAPI" as BOK #FFF3E0
participant "🔍 네이버\n데이터랩" as Naver #E8F5E9
participant "🛢️ 유가/환율\nAPI" as Oil #FFEBEE
database "📅 신차 일정\nDB" as NewCar #E3F2FD

autonumber

User -> App : 타이밍 분석 요청\n(모델명: 그랜저)
activate App

App -> ML : POST /api/timing\n{model: "그랜저"}
activate ML

== 병렬 데이터 수집 ==
par 거시경제 데이터
    ML -> BOK : 기준금리 조회
    activate BOK
    BOK --> ML : rate: 2.5%\ntrend: stable
    deactivate BOK
else 검색 트렌드
    ML -> Naver : 검색량 조회
    activate Naver
    Naver --> ML : change: -11.2%\ntrend: stable
    deactivate Naver
else 유가/환율
    ML -> Oil : 국제유가, 환율 조회
    activate Oil
    Oil --> ML : oil: $57.24\nexchange: 1,467원
    deactivate Oil
else 신차 일정
    ML -> NewCar : 출시 예정 조회
    activate NewCar
    NewCar --> ML : upcoming: 0건
    deactivate NewCar
end

== 타이밍 점수 계산 ==
ML -> ML : 점수 계산 (100점 만점)
note right of ML #FFFDE7
    <b>점수 구성</b>
    • 금리 (25점): 낮을수록 유리
    • 유가 (20점): 낮을수록 유리
    • 환율 (20점): 낮을수록 유리
    • 검색량 (20점): 적을수록 유리
    • 신차 (15점): 출시 전 유리
end note

ML --> App : 분석 결과 반환
deactivate ML

App --> User : 📊 타이밍 결과 표시
deactivate App

note over User, NewCar #E8F5E9
    <b>📊 분석 결과 예시</b>
    ━━━━━━━━━━━━━━━━━━━━
    ⏱️ 타이밍 점수: <b>64/100</b>
    🚦 판단: <b>🟡 관망</b>
    
    • 금리 2.5% (안정) → 18/25
    • 유가 $57 (하락중) → 16/20
    • 환율 1,467원 (안정) → 14/20
    • 검색량 -11% (감소) → 12/20
    • 신차 없음 → 4/15
end note

@enduml
```

---

## 5️⃣ 사용자 인증 플로우 (OAuth2 소셜 로그인)

```plantuml
@startuml OAuth2 Social Login
!define ICONURL https://raw.githubusercontent.com/tupadr3/plantuml-icon-font-sprites/v2.4.0
!include ICONURL/common.puml
!include ICONURL/font-awesome-5/user.puml
!include ICONURL/font-awesome-5/key.puml
!include ICONURL/font-awesome-5/shield_alt.puml

skinparam backgroundColor #FEFEFE
skinparam handwritten false
skinparam defaultFontName Malgun Gothic
skinparam sequenceMessageAlign center

title <size:20><b>시나리오 3: 소셜 로그인 (카카오)</b></size>\nOAuth2 인증 플로우

actor "👤 사용자" as User #LightBlue
participant "📱 Flutter App" as App #E1F5FE
participant "🔐 Spring Boot\nAuth Server" as Auth #FFF3E0
participant "🟡 카카오\nOAuth2" as Kakao #FFF59D
database "👥 MySQL\nUser DB" as DB #E3F2FD
participant "⚡ Redis\nSession" as Redis #FFEBEE

autonumber

User -> App : 카카오 로그인 버튼 클릭
activate App

App -> Kakao : OAuth2 인증 요청\n(client_id, redirect_uri)
activate Kakao

Kakao --> User : 카카오 로그인 화면
User -> Kakao : 이메일/비밀번호 입력
Kakao -> Kakao : 인증 확인

Kakao --> App : Authorization Code
deactivate Kakao

App -> Auth : POST /oauth2/callback/kakao\n{code: "abc123"}
activate Auth

Auth -> Kakao : Access Token 요청\n(code, client_secret)
activate Kakao
Kakao --> Auth : access_token, refresh_token
deactivate Kakao

Auth -> Kakao : 사용자 정보 요청\n(access_token)
activate Kakao
Kakao --> Auth : {email, nickname, profile_image}
deactivate Kakao

Auth -> DB : 사용자 조회/생성
activate DB
alt 기존 사용자
    DB --> Auth : 사용자 정보 반환
else 신규 사용자
    Auth -> DB : INSERT user
    DB --> Auth : 생성 완료
end
deactivate DB

Auth -> Auth : JWT 토큰 생성
note right of Auth
    JWT Payload:
    {
      sub: "user123",
      email: "user@kakao.com",
      exp: 1732633200
    }
end note

Auth -> Redis : 세션 저장 (TTL: 24h)
activate Redis
Redis --> Auth : OK
deactivate Redis

Auth --> App : 200 OK\n{jwt_token, user_info}
deactivate Auth

App -> App : 토큰 저장 (SecureStorage)
App --> User : 🏠 홈 화면 이동
deactivate App

note over User, Redis #E8F5E9
    <b>🔐 보안 특징</b>
    • JWT 토큰 (24시간 유효)
    • Redis 세션 관리
    • HTTPS 통신
    • SecureStorage 저장
end note

@enduml
```

---

## 6️⃣ 전체 서비스 효과 다이어그램

```plantuml
@startuml Service Effects
!define ICONURL https://raw.githubusercontent.com/tupadr3/plantuml-icon-font-sprites/v2.4.0
!include ICONURL/common.puml
!include ICONURL/font-awesome-5/car.puml
!include ICONURL/font-awesome-5/chart_line.puml
!include ICONURL/font-awesome-5/shield_alt.puml
!include ICONURL/font-awesome-5/comments.puml
!include ICONURL/font-awesome-5/bell.puml

skinparam backgroundColor #FEFEFE
skinparam handwritten false
skinparam defaultFontName Malgun Gothic

title <size:20><b>Car-Sentix 서비스 효과</b></size>

left to right direction

' 입력
rectangle "📥 입력" as Input #E3F2FD {
    card "차량 정보\n(브랜드, 모델, 연식)" as I1
    card "주행거리\n옵션 사항" as I2
    card "판매자 제시가\n(옵션)" as I3
}

' AI 처리
rectangle "🤖 AI 처리" as Process #E8F5E9 {
    rectangle "가격 예측\n(XGBoost)" as Predict #C8E6C9
    rectangle "타이밍 분석\n(실시간 데이터)" as Timing #C8E6C9
    rectangle "AI 분석\n(Groq LLM)" as AI #C8E6C9
}

' 출력
rectangle "📤 출력" as Output #FFF3E0 {
    card "💰 예상 시세\n2,628만원\n(±10%)" as O1 #FFE082
    card "📊 가격 분포\n상위 30%" as O2 #FFE082
    card "⏱️ 타이밍 점수\n64점 (관망)" as O3 #FFE082
    card "🚦 매수 신호\n매수/관망/회피" as O4 #FFE082
    card "🔍 허위매물\n의심도 15%" as O5 #FFE082
    card "💬 네고 대본\n자동 생성" as O6 #FFE082
}

' 효과
rectangle "🎯 기대 효과" as Effect #FFEBEE {
    card "✅ 호갱 방지\n적정가 파악" as E1 #FFCDD2
    card "✅ 시간 절약\n즉시 분석" as E2 #FFCDD2
    card "✅ 협상력 강화\n데이터 근거" as E3 #FFCDD2
    card "✅ 사기 예방\n허위매물 탐지" as E4 #FFCDD2
}

Input --> Process
Process --> Output
Output --> Effect

I1 --> Predict
I2 --> Predict
I3 --> AI

Predict --> O1
Predict --> O2
Timing --> O3
AI --> O4
AI --> O5
AI --> O6

@enduml
```

---

## 📋 사용 방법

### VS Code에서 보기
```bash
# PlantUML 확장 설치
ext install jebbs.plantuml

# Java 설치 필요 (PlantUML 렌더링)
# 또는 PlantUML Server 설정
```

### 온라인에서 보기
1. [PlantUML Server](https://www.plantuml.com/plantuml) 접속
2. 코드 붙여넣기
3. PNG/SVG 다운로드

### 이미지 생성 명령
```bash
# PlantUML CLI 사용 시
java -jar plantuml.jar SERVICE_SCENARIOS_PUML.md -tpng
```

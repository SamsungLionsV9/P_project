# 📱 CarSentix 앱 사용자 흐름 및 기술 문서

> **버전**: 1.0.0  
> **최종 업데이트**: 2025-12-12  
> **앱 이름**: 언제 살까? (CarSentix)

---

## 📋 목차

1. [앱 개요](#앱-개요)
2. [기술 스택](#기술-스택)
3. [메뉴 구조](#메뉴-구조)
4. [1. 홈 탭](#1-홈-탭)
5. [2. 내 차 찾기 탭](#2-내-차-찾기-탭)
6. [3. 추천 탭](#3-추천-탭)
7. [4. 마이 탭](#4-마이-탭)
8. [5. 설정 탭](#5-설정-탭)
9. [데이터 흐름도](#데이터-흐름도)
10. [API 엔드포인트 정리](#api-엔드포인트-정리)

---

## 앱 개요

**CarSentix**는 AI 기반 중고차 구매 타이밍 분석 앱입니다.

### 핵심 차별점
- 단순 시세 조회가 아닌 **"언제 사야 하는지"** 타이밍 분석
- 경제지표(금리, 유가, 신차출시) 기반 구매 적기 판단
- AI(Groq Llama 3.3 70B)를 활용한 네고 대본 생성

### 주요 기능
| 기능 | 설명 |
|:--|:--|
| 가격 예측 | XGBoost 모델 기반 중고차 적정 가격 예측 |
| 타이밍 분석 | 경제지표 기반 구매 적기 점수(0~100) |
| 허위매물 감지 | 가격 이상치 탐지로 사기 매물 경고 |
| 찜/비교 | 관심 차량 저장 및 최대 3대 비교 |
| AI 네고 대본 | 딜러 협상용 맞춤 스크립트 생성 |

---

## 기술 스택

### Frontend (Flutter 앱)
```
📦 flutter_app/lib/
├── main.dart              # 앱 진입점, 메인 화면
├── car_info_input_page.dart   # 차량 정보 입력
├── result_page.dart       # 분석 결과 화면
├── recommendation_page.dart   # 추천 탭
├── mypage.dart            # 마이페이지
├── settings_page.dart     # 설정
├── services/
│   ├── api_service.dart   # ML 서비스 API 클라이언트
│   └── auth_service.dart  # 인증 서비스 (JWT)
├── providers/
│   ├── comparison_provider.dart   # 비교 목록 상태
│   ├── recent_views_provider.dart # 최근 조회 상태
│   └── popular_cars_provider.dart # 인기 차량 상태
└── models/                # 데이터 모델 클래스
```

| 패키지 | 용도 |
|:--|:--|
| `provider` | 상태 관리 |
| `http` | REST API 통신 |
| `shared_preferences` | 로컬 저장소 |
| `url_launcher` | 외부 앱 실행 |
| `flutter_screenutil` | 반응형 UI |

### Backend (ML Service - FastAPI)
```
📦 run_server.py + ml-service/services/
├── prediction_v12.py      # 가격 예측 (XGBoost)
├── timing_analyzer.py     # 타이밍 분석
├── fraud_detector.py      # 허위매물 감지
├── groq_service.py        # AI 네고 대본 (Groq API)
├── database_service.py    # SQLite DB 관리
└── encar_data_service.py  # 엔카 실매물 데이터
```

### Backend (User Service - Spring Boot)
```
📦 user-service/
├── AuthController         # 로그인/회원가입
├── OAuthController        # 소셜 로그인 (카카오, 네이버, 구글)
└── UserRepository         # 사용자 DB (MySQL/H2)
```

---

## 메뉴 구조

```
┌─────────────────────────────────────────────────────────────┐
│                        CarSentix 앱                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────┐  ┌─────────┐  ┌─────┐  ┌─────┐  ┌─────┐          │
│  │ 홈  │  │내 차 찾기│  │ 추천 │  │ 마이 │  │ 설정 │          │
│  └──┬──┘  └────┬────┘  └──┬──┘  └──┬──┘  └──┬──┘          │
│     │          │          │        │        │              │
│     ▼          ▼          ▼        ▼        ▼              │
│  타이밍     차량정보     인기모델   찜목록    다크모드        │
│  분석       입력        추천차량   분석이력   알림설정        │
│  로그인     분석결과     최근조회   가격알림   AI상태         │
│  최근조회   AI네고대본              비교하기   문의하기        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. 홈 탭

### 📍 위치
`flutter_app/lib/main.dart` → `HomePageContent` 클래스

### 화면 구성

```
┌────────────────────────────────────┐
│  AI 기반 중고차 구매 타이밍 분석      │  ← Hero Section
│  언제 살까?                         │
│  지금이 적기인지 확인하세요           │
│                                    │
│  [구매 타이밍 분석하기 →]            │  ← 내 차 찾기로 이동
│                                    │
│  user@email.com님    로그아웃        │  ← 로그인 상태
└────────────────────────────────────┘
┌────────────────────────────────────┐
│  🕐 오늘의 구매 타이밍               │
│  경제지표 기반 AI 분석               │
│                                    │
│      63 / 100    [괜찮은 시기]       │  ← 타이밍 점수
│                                    │
│  📊 경제지표 현황                    │
│  금리      ────────────── ▶ 좋음    │
│  유가      ────────────── ▶ 주의    │
│  신차출시   ────────────── — 보통    │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│  최근 조회 차량                      │  ← Provider 연동
│  [그랜저] [K5] [소나타]              │
├────────────────────────────────────┤
│  인기 모델 추천                      │  ← 엔카 데이터
│  [그랜저 2,450만] [카니발 3,200만]   │
└────────────────────────────────────┘
```

### 데이터 흐름

```
┌──────────────┐      HTTP GET       ┌──────────────┐
│   Flutter    │ ─────────────────► │  ML Service  │
│  HomeScreen  │  /api/market-timing │   :8000      │
└──────────────┘ ◄───────────────── └──────────────┘
                   JSON Response
                   {
                     score: 63,
                     label: "괜찮은 시기",
                     indicators: [...]
                   }
```

### 기술 상세

| 구성요소 | 파일 | 설명 |
|:--|:--|:--|
| Hero Section | `main.dart` `_buildHeroSection()` | 딥블루 배경, CTA 버튼 |
| 타이밍 카드 | `widgets/professional_timing_card.dart` | 경제지표 시각화 |
| 로그인 폼 | `main.dart` `_buildLoginForm()` | 이메일/소셜 로그인 |
| 최근 조회 | `providers/recent_views_provider.dart` | SharedPreferences 캐시 |

### API 호출

```dart
// api_service.dart
Future<MarketTimingResult> getMarketTiming() async {
  final response = await http.get(
    Uri.parse('$_baseUrl/market-timing'),
  ).timeout(Duration(seconds: 10));
  return MarketTimingResult.fromJson(jsonDecode(response.body));
}
```

### 백엔드 처리

```python
# run_server.py
@app.get("/api/market-timing")
async def get_market_timing():
    """경제지표 기반 구매 타이밍 분석"""
    indicators = economic_service.get_indicators()
    score = timing_analyzer.calculate_score(indicators)
    return {
        "score": score,
        "label": get_label(score),  # 좋은 시기/괜찮은 시기/주의 필요
        "indicators": indicators
    }
```

---

## 2. 내 차 찾기 탭

### 📍 위치
`flutter_app/lib/car_info_input_page.dart`

### 화면 구성

```
┌────────────────────────────────────┐
│         차량 정보 입력              │
├────────────────────────────────────┤
│  기본 정보                          │
│  ┌────────────┐ ┌────────────┐    │
│  │ 브랜드 선택 │ │ 모델 선택   │    │
│  └────────────┘ └────────────┘    │
│  ┌─────────────────────────────┐  │
│  │ 2024년 ▼                    │  │
│  └─────────────────────────────┘  │
│  ┌─────────────────────────────┐  │
│  │ 주행거리 (km)               │  │
│  └─────────────────────────────┘  │
│  연료: [가솔린] [디젤] [LPG] [전기] │
├────────────────────────────────────┤
│  옵션 선택                          │
│  ☐ 선루프  ☐ 네비게이션  ☐ 가죽시트 │
│  ☐ 스마트키 ☐ 후방카메라           │
├────────────────────────────────────┤
│  성능점검 등급                      │
│  ★★★★☆ (4/5)                     │
├────────────────────────────────────┤
│  [               분석하기          ]│
└────────────────────────────────────┘
```

### 데이터 흐름

```
┌──────────────┐                    ┌──────────────┐
│   사용자     │  차량 정보 입력      │   Flutter    │
│   입력       │ ──────────────────► │   앱         │
└──────────────┘                    └──────┬───────┘
                                          │
                                          │ POST /api/smart-analysis
                                          ▼
┌──────────────┐                    ┌──────────────┐
│   결과       │  분석 결과 반환      │  ML Service  │
│   페이지     │ ◄────────────────── │   :8000      │
└──────────────┘                    └──────────────┘
```

### 입력 데이터 구조

```dart
{
  "brand": "현대",
  "model": "그랜저",
  "year": 2022,
  "mileage": 35000,
  "fuel": "가솔린",
  "has_sunroof": true,
  "has_navigation": true,
  "has_leather_seat": false,
  "has_smart_key": true,
  "has_rear_camera": true,
  "inspection_grade": "good"  // normal/good/excellent
}
```

### 분석 결과 → result_page.dart

```
┌────────────────────────────────────┐
│  현대 그랜저 2022년식               │
│  ────────────────────────────────  │
│  💰 예측 가격: 2,450만원            │
│  📊 시세 범위: 2,300 ~ 2,600만원    │
│  ⚠️ 허위매물 위험: 낮음             │
├────────────────────────────────────┤
│  [예측가격] [타이밍분석] [실매물]    │  ← TabBar
├────────────────────────────────────┤
│  📈 타이밍 분석                     │
│  종합 점수: 72점 (좋은 시기)        │
│                                    │
│  - 금리 하락 추세 → 유리            │
│  - 신차 출시 임박 → 가격 하락 예상  │
├────────────────────────────────────┤
│  [🤖 AI 네고 대본 받기]             │
└────────────────────────────────────┘
```

### 백엔드 스마트 분석

```python
# run_server.py
@app.post("/api/smart-analysis")
async def smart_analysis(request: SmartAnalysisRequest):
    """통합 스마트 분석 (가격 + 타이밍 + 허위매물)"""
    
    # 1. 가격 예측 (XGBoost)
    prediction = prediction_service.predict(
        brand=request.brand,
        model=request.model,
        year=request.year,
        mileage=request.mileage,
        fuel=request.fuel,
        options=request.options
    )
    
    # 2. 타이밍 분석
    timing = timing_analyzer.analyze(request.model)
    
    # 3. 허위매물 감지
    fraud_risk = fraud_detector.check(
        predicted_price=prediction.price,
        actual_price=request.asking_price  # 있으면
    )
    
    return {
        "prediction": prediction,
        "timing": timing,
        "fraud_risk": fraud_risk,
        "similar_cars": get_similar(...)
    }
```

---

## 3. 추천 탭

### 📍 위치
`flutter_app/lib/recommendation_page.dart`

### 화면 구성

```
┌────────────────────────────────────┐
│  차량 추천                          │
│  [인기 모델] [추천 차량] [최근 조회]  │  ← TabBar
├────────────────────────────────────┤
│  🏆 인기 모델 (국산차)              │
│  ┌──────────────────────────────┐ │
│  │ 🚗 그랜저 IG                  │ │
│  │ 평균가: 2,450만 | 매물: 1,240 │ │
│  │ 시세 추이: ▼ 3.2% (1개월)    │ │
│  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐ │
│  │ 🚗 K5 DL3                    │ │
│  │ 평균가: 2,180만 | 매물: 892  │ │
│  └──────────────────────────────┘ │
├────────────────────────────────────┤
│  🌍 인기 모델 (수입차)              │
│  [벤츠 E클래스] [BMW 5시리즈]       │
└────────────────────────────────────┘
```

### 데이터 흐름

```
┌──────────────┐      GET /api/popular-cars     ┌──────────────┐
│  추천 탭     │ ───────────────────────────► │  ML Service  │
│              │                               │              │
│              │ ◄─────────────────────────── │  (엔카 데이터) │
│              │      인기 모델 목록            │              │
└──────────────┘                               └──────────────┘
        │
        │ 차량 클릭
        ▼
┌──────────────┐      GET /api/model-deals     ┌──────────────┐
│ 모델 상세    │ ───────────────────────────► │  ML Service  │
│ 모달         │                               │              │
│              │ ◄─────────────────────────── │              │
│              │      실매물 목록              │              │
└──────────────┘                               └──────────────┘
```

### 찜하기 기능

```dart
// recommendation_page.dart
Future<void> _toggleFavorite(RecommendedCar car) async {
  // 1. 로그인 체크
  if (!auth.isLoggedIn) {
    _showSnackBar('로그인 후 찜 기능을 이용할 수 있습니다.');
    return;
  }
  
  // 2. Optimistic UI 업데이트
  setState(() {
    if (isCurrentlyFavorite) {
      _favorites.removeWhere((f) => f.isSameDeal(car));
    } else {
      _favorites.add(Favorite.fromCar(car));
    }
  });
  
  // 3. 서버 동기화
  await _api.toggleFavorite(car);
}
```

### 백엔드 API

```python
# run_server.py
@app.get("/api/popular-cars")
async def get_popular_cars():
    """인기 모델 조회 (엔카 데이터 기반)"""
    return {
        "domestic": encar_service.get_popular_domestic(),
        "imported": encar_service.get_popular_imported()
    }

@app.get("/api/model-deals/{brand}/{model}")
async def get_model_deals(brand: str, model: str, limit: int = 10):
    """특정 모델의 실매물 조회"""
    return encar_service.get_deals(brand, model, limit)
```

---

## 4. 마이 탭

### 📍 위치
`flutter_app/lib/mypage.dart`

### 화면 구성

```
┌────────────────────────────────────┐
│  마이페이지                         │
│  [찜한 차량] [분석 이력]            │  ← TabBar
├────────────────────────────────────┤
│  ❤️ 찜한 차량 (3)                   │
│  ┌──────────────────────────────┐ │
│  │ 🚗 그랜저 2022  2,450만       │ │
│  │ [비교담기 0/3] [❤️]           │ │
│  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐ │
│  │ 🚗 K5 2023  2,180만          │ │
│  │ [비교담기 1/3] [❤️]           │ │
│  └──────────────────────────────┘ │
├────────────────────────────────────┤
│  ⚖️ 비교하기 (2/3)                  │
│  [비교 페이지로 이동 →]             │
└────────────────────────────────────┘
```

### 비교하기 기능

```dart
// providers/comparison_provider.dart
class ComparisonProvider extends ChangeNotifier {
  static const int maxCompareCount = 3;  // 최대 3대
  final List<CarData> _compareList = [];
  
  void toggleCompare(CarData car) {
    if (_compareList.any((c) => c.id == car.id)) {
      _compareList.removeWhere((c) => c.id == car.id);
    } else if (_compareList.length < maxCompareCount) {
      _compareList.add(car);
    }
    notifyListeners();
  }
}
```

### 비교 페이지 (comparison_page.dart)

```
┌────────────────────────────────────────────────────┐
│  차량 비교 (2/3)                                    │
├──────────────┬──────────────┬──────────────────────┤
│   그랜저      │     K5       │                      │
├──────────────┼──────────────┼──────────────────────┤
│ 가격: 2,450만 │ 가격: 2,180만 │                      │
│ 연식: 2022   │ 연식: 2023   │                      │
│ 주행: 35,000 │ 주행: 28,000 │                      │
│ 연료: 가솔린  │ 연료: 가솔린  │                      │
├──────────────┼──────────────┼──────────────────────┤
│ ⭐ 옵션       │ ⭐ 옵션       │                      │
│ ✓ 선루프     │ ✓ 선루프     │                      │
│ ✓ 네비       │ ✗ 네비       │                      │
│ ✓ 가죽시트   │ ✓ 가죽시트   │                      │
└──────────────┴──────────────┴──────────────────────┘
```

### 백엔드 API

```python
# run_server.py
@app.get("/api/favorites")
async def get_favorites(user_id: str = Query(...)):
    """사용자의 찜 목록 조회"""
    return db_service.get_favorites(user_id)

@app.post("/api/favorites")
async def add_favorite(request: FavoriteRequest):
    """찜 추가"""
    return db_service.add_favorite(request.user_id, request.car_data)

@app.delete("/api/favorites/{favorite_id}")
async def remove_favorite(favorite_id: int):
    """찜 삭제"""
    return db_service.remove_favorite(favorite_id)
```

---

## 5. 설정 탭

### 📍 위치
`flutter_app/lib/settings_page.dart`

### 화면 구성

```
┌────────────────────────────────────┐
│              설정                   │
├────────────────────────────────────┤
│  일반                               │
│  ┌──────────────────────────────┐ │
│  │ 다크 모드              [🔘]  │ │
│  ├──────────────────────────────┤ │
│  │ 알림 설정     허위매물 경고 켜짐 │ │  ← 하단 시트 모달
│  └──────────────────────────────┘ │
├────────────────────────────────────┤
│  AI 엔진                            │
│  ┌──────────────────────────────┐ │
│  │ Groq AI 연결 상태            │ │
│  │ Llama 3.3 70B 연결됨 [✓연결됨]│ │
│  ├──────────────────────────────┤ │
│  │ API 키 설정 (선택)            │ │
│  │ 기본 엔진 사용 중             │ │
│  └──────────────────────────────┘ │
├────────────────────────────────────┤
│  지원 및 정보                       │
│  ┌──────────────────────────────┐ │
│  │ 기록 삭제                     │ │  ← 빨간색
│  ├──────────────────────────────┤ │
│  │ 문의하기    admin@carsentix.com│ │  ← 이메일 앱 열기
│  ├──────────────────────────────┤ │
│  │ 버전 정보              v1.0.0 │ │
│  └──────────────────────────────┘ │
└────────────────────────────────────┘
```

### 알림 설정 모달

```
┌────────────────────────────────────┐
│  🔔 알림 설정                       │
├────────────────────────────────────┤
│  허위매물 경고                      │
│  고위험 매물 감지 시 알림     [🔘]  │
│                                    │
│  ℹ️ 허위매물 경고는 분석 시          │
│     자동으로 확인됩니다             │
└────────────────────────────────────┘
```

### 기술 상세

```dart
// settings_page.dart
class _SettingsPageState extends State<SettingsPage> {
  static const String _adminEmail = 'admin@carsentix.com';
  static const String _prefKeyFraudAlert = 'notification_fraud_alert';
  
  bool _fraudAlertEnabled = true;
  
  // 알림 설정 저장 (SharedPreferences)
  Future<void> _setFraudAlertEnabled(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_prefKeyFraudAlert, value);
    setState(() => _fraudAlertEnabled = value);
  }
  
  // 문의하기 (이메일 앱 열기)
  Future<void> _openEmailApp() async {
    final emailUrl = 'mailto:$_adminEmail?subject=...';
    await launchUrl(Uri.parse(emailUrl), 
      mode: LaunchMode.externalApplication);
  }
}
```

### AI 상태 확인 API

```python
# run_server.py
@app.get("/api/ai/status")
async def get_ai_status():
    """AI 엔진 상태 확인"""
    return {
        "groq_available": groq_service.is_available(),
        "model": "llama-3.3-70b-versatile" if available else None,
        "status": "connected" if available else "disconnected"
    }
```

---

## 데이터 흐름도

### 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                           사용자 (User)                              │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Flutter App (Mobile)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │ ApiService  │  │ AuthService │  │  Providers  │                 │
│  └──────┬──────┘  └──────┬──────┘  └─────────────┘                 │
└─────────┼────────────────┼──────────────────────────────────────────┘
          │                │
          │ HTTP           │ HTTP
          │ :8000          │ :8080
          ▼                ▼
┌─────────────────┐  ┌─────────────────┐
│   ML Service    │  │  User Service   │
│   (FastAPI)     │  │  (Spring Boot)  │
│                 │  │                 │
│ ┌─────────────┐ │  │ ┌─────────────┐ │
│ │ Prediction  │ │  │ │    Auth     │ │
│ │  (XGBoost)  │ │  │ │   (JWT)     │ │
│ ├─────────────┤ │  │ ├─────────────┤ │
│ │   Timing    │ │  │ │   OAuth     │ │
│ │  Analyzer   │ │  │ │ (카카오 등)  │ │
│ ├─────────────┤ │  │ └─────────────┘ │
│ │    Groq     │ │  └─────────────────┘
│ │  (AI 네고)   │ │
│ ├─────────────┤ │
│ │   SQLite    │ │
│ │  (데이터)    │ │
│ └─────────────┘ │
└─────────────────┘
```

### 로그인 흐름

```
┌──────────┐     ┌──────────┐     ┌──────────────┐     ┌──────────┐
│ 사용자    │     │ Flutter  │     │ User Service │     │ OAuth    │
│          │     │   App    │     │  (Spring)    │     │ Provider │
└────┬─────┘     └────┬─────┘     └──────┬───────┘     └────┬─────┘
     │                │                   │                  │
     │ 1. 로그인 클릭  │                   │                  │
     │───────────────►│                   │                  │
     │                │                   │                  │
     │                │ 2. OAuth URL 요청  │                  │
     │                │──────────────────►│                  │
     │                │                   │                  │
     │                │ 3. Redirect URL   │                  │
     │                │◄──────────────────│                  │
     │                │                   │                  │
     │ 4. WebView 표시 │                   │                  │
     │◄───────────────│                   │                  │
     │                │                   │                  │
     │ 5. 로그인 완료  │                   │ 6. 인증 코드     │
     │───────────────►│──────────────────────────────────────►│
     │                │                   │                  │
     │                │                   │ 7. 토큰 발급     │
     │                │◄──────────────────────────────────────│
     │                │                   │                  │
     │                │ 8. JWT 토큰       │                  │
     │                │◄──────────────────│                  │
     │                │                   │                  │
     │ 9. 로그인 성공  │                   │                  │
     │◄───────────────│                   │                  │
```

---

## API 엔드포인트 정리

### ML Service (포트 8000)

| 메서드 | 엔드포인트 | 설명 | 사용 화면 |
|:--|:--|:--|:--|
| GET | `/api/health` | 서버 상태 확인 | - |
| GET | `/api/market-timing` | 구매 타이밍 분석 | 홈 |
| POST | `/api/predict` | 가격 예측 | 내 차 찾기 |
| POST | `/api/smart-analysis` | 통합 분석 | 내 차 찾기 |
| GET | `/api/popular-cars` | 인기 모델 | 추천 |
| GET | `/api/model-deals/{brand}/{model}` | 모델별 매물 | 추천 |
| GET | `/api/favorites` | 찜 목록 | 마이 |
| POST | `/api/favorites` | 찜 추가 | 추천/마이 |
| DELETE | `/api/favorites/{id}` | 찜 삭제 | 마이 |
| GET | `/api/ai/status` | AI 연결 상태 | 설정 |
| POST | `/api/ai/negotiation` | AI 네고 대본 | 분석결과 |

### User Service (포트 8080)

| 메서드 | 엔드포인트 | 설명 |
|:--|:--|:--|
| POST | `/api/auth/login` | 이메일 로그인 |
| POST | `/api/auth/register` | 회원가입 |
| GET | `/api/oauth/{provider}/login` | 소셜 로그인 URL |
| POST | `/api/oauth/{provider}/callback` | OAuth 콜백 |
| POST | `/api/auth/logout` | 로그아웃 |

---

## 용어 정리

| 용어 | 설명 |
|:--|:--|
| **타이밍 점수** | 0~100점, 경제지표 기반 구매 적기 판단 |
| **허위매물 위험** | 가격 이상치 기반 사기 매물 확률 |
| **XGBoost** | 머신러닝 모델 (가격 예측용) |
| **Groq** | AI API 서비스 (네고 대본 생성용) |
| **JWT** | JSON Web Token (인증 방식) |
| **Provider** | Flutter 상태 관리 라이브러리 |
| **엔카 데이터** | 중고차 실매물 데이터 소스 |

---

> 📝 **문서 작성**: Cascade AI  
> 📅 **최종 수정**: 2025-12-12

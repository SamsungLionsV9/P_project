# 🚗 Car-Sentix: 중고차 구매 의사결정 지원 시스템

**Track 1**: 가격 예측 (XGBoost)  
**Track 2**: 타이밍 분석 (100% 실제 데이터)

> 단순한 가격 예측을 넘어, **언제 사야 할지**까지 알려주는 통합 어드바이저

## ⚡ NEW: Groq AI 통합 (v3.0) 🤖

**데이터 분석 + LLM의 완벽한 조합!**

**3대 킬러 기능:**
1. 🚦 **AI 매수/관망 신호등** - 주식처럼 매수/관망/회피 판단
2. 🚨 **허위 매물 탐지기** - 딜러 설명글 vs 성능기록부 자동 대조
3. 💬 **네고 대본 생성기** - AI가 깎는 방법까지 알려줌

```bash
# 스마트 어드바이저 (데이터 + Groq AI)
python src/smart_advisor.py 현대 그랜저 2022 35000 가솔린 3200
```

📖 **Groq 가이드**: [docs/GROQ_AI_FEATURES.md](docs/GROQ_AI_FEATURES.md)

---

## 💎 실제 데이터 버전 (v2.0)

**100% 객관적 데이터만 사용하는 신뢰성 높은 버전!**

```bash
# 실제 데이터 기반 타이밍 분석
python src/car_sentix_real.py 그랜저

# 통합 분석 (가격 + 타이밍)
python src/integrated_advisor_real.py 현대 그랜저 2022 50000 가솔린
```

📖 **상세 가이드**: [docs/REAL_DATA_USAGE.md](docs/REAL_DATA_USAGE.md)

---

## 🎯 시스템 개요

### Track 1: 가격 예측 (XGBoost)

| 지표 | 값 |
|------|-----|
| **R² Score** | **0.87** |
| **MAE** | 231만원 |
| **데이터** | 119,343대 |
| **모델 수** | 253개 (고신뢰도) |

### Track 2: 타이밍 분석 (실제 데이터 버전 ⭐)

| 지표 | 데이터 소스 | 객관성 |
|------|-------------|--------|
| **거시경제** | 한국은행 API + Yahoo Finance | ✅ 100% |
| **검색 트렌드** | 네이버 데이터랩 API | ✅ 100% |
| **신차 일정** | CSV 데이터 | 수동 관리 |
| **커뮤니티 감성** | ~~제외~~ | 크롤링 불가 |

**가중치**: 거시경제 40% + 검색 트렌드 30% + 신차 일정 30%

## 🎯 주요 특징

✅ **통합 모델**: 하나의 모델이 모든 브랜드/모델 동시 학습  
✅ **고성능**: R² 0.87 (Kaggle 우승 수준)  
✅ **빠른 학습**: 11만 데이터 20분  
✅ **해석 가능**: Feature Importance 확인 가능  
✅ **실용적**: 실시간 예측 가능

## 📂 프로젝트 구조

```
used-car-price-predictor/
├── src/                                 # 소스 코드
│   ├── predict_car_price.py             # Track 1: 가격 예측
│   │
│   ├── smart_advisor.py                 # 🤖 스마트 어드바이저 (Groq AI)
│   ├── groq_advisor.py                  # 🤖 Groq LLM 기능 (3대 킬러)
│   │
│   ├── car_sentix_real.py              # ⭐ Track 2: 타이밍 분석 (실제 데이터)
│   ├── integrated_advisor_real.py       # ⭐ 통합 어드바이저 (실제 데이터)
│   ├── timing_engine_real.py            # ⭐ 타이밍 엔진 (3요소)
│   ├── data_collectors_real_only.py     # ⭐ 실제 데이터 수집기
│   │
│   ├── car_sentix.py                    # (구버전) 타이밍 분석
│   ├── integrated_advisor.py            # (구버전) 통합 어드바이저
│   ├── timing_engine.py                 # (구버전) 타이밍 엔진
│   ├── data_collectors_complete.py      # (구버전) 데이터 수집
│   ├── bobaedream_scraper.py            # 보배드림 크롤러
│   ├── sentiment_database.py            # 정적 감성 DB
│   └── train_model_improved.py          # 모델 학습
│
├── models/                              # 학습된 모델
│   └── improved_car_price_model.pkl
│
├── data/                         # 데이터
│   ├── processed_encar_data.csv  # 중고차 데이터 (119,343대)
│   └── new_car_schedule.csv      # 신차 출시 일정
│
├── docs/                                 # 문서
│   ├── GROQ_AI_FEATURES.md              # 🤖 Groq AI 킬러 기능 가이드
│   ├── REAL_DATA_USAGE.md               # ⭐ 실제 데이터 사용 가이드
│   ├── TIMING_ADVISOR_PLAN.md            # 타이밍 시스템 설계
│   ├── API_SETUP_GUIDE.md                # API 설정 가이드
│   └── IMPLEMENTATION_STATUS.md          # 구현 현황
│
├── .env                          # API 키 (gitignore)
├── requirements.txt              # 의존성
└── README.md                     # 이 문서
```

## 🚀 사용 방법

### 1. 설치
```bash
pip install -r requirements.txt
```

### 2. API 키 설정 (.env 파일)
```bash
# .env 파일 생성
BOK_API_KEY=your_bok_api_key              # 한국은행 API
NAVER_CLIENT_ID=your_naver_client_id      # 네이버 데이터랩
NAVER_CLIENT_SECRET=your_naver_secret     # 네이버 시크릿
```

**API 발급 방법:** `docs/API_SETUP_GUIDE.md` 참조

### 3. Track 1: 가격 예측만
```bash
cd src
python predict_car_price.py "현대" "그랜저" 2022 50000 "가솔린"
```

**출력:**
```
💰 예상 가격: 3,200만원
```

### 4. Track 2: 타이밍 분석만
```bash
cd src
python car_sentix.py 그랜저
```

**출력:**
```
📊 타이밍 점수: 54.8점 / 100점
판단: 🔴 대기
이유:
  ✅ 저금리 2.5%
  ✅ 저유가 $58
  ❌ 신차 3.2개월 후 출시
```

### 5. 통합 분석 (가격 + 타이밍)
```bash
cd src
python integrated_advisor.py 현대 그랜저 2022 50000 가솔린
```

**출력:**
```
💰 예상 가격: 3,200만원
📊 타이밍 점수: 54.8점 (대기)

✨ 최종 조언:
🔴 구매를 미루시는 것을 권장합니다
   - 만약 구매 시: 2,720만원 이하
   - 추천: 1-2개월 후 재검토
```

### 6. 여러 차량 비교
```bash
cd src
python car_sentix.py 그랜저 아반떼 K5
```

**출력:**
```
📊 비교 요약
순위   차량    점수       판단
1    K5      56.8점  🟡 관망
2    아반떼   55.8점  🟡 관망
3    그랜저   54.8점  🔴 대기
```

## 🔄 데이터 수집 (선택사항)

새로운 데이터로 재학습하려면:

### 1. 데이터 수집
```bash
python scrape_encar_partitioned.py
```
*약 10-15분 소요*

### 2. 전처리
```bash
python preprocess_encar.py
```

### 3. 모델 재학습
```bash
python train_model_improved.py
```
*약 20-30분 소요*

## ⚠️ 모델 생성 안내 (필독)

GitHub 저장소 용량 제한으로 인해 **학습된 모델(.pkl)과 대용량 데이터(.csv)는 포함되지 않았습니다.**
프로젝트를 처음 실행하실 때는 아래 명령어로 모델을 직접 생성해주셔야 합니다:

```bash
# 모델 학습 및 생성 (약 1-2분 소요)
cd src
python train_model_improved.py
```

## 📖 상세 문서

### 모델 설명
**MODEL_EXPLANATION.md** 파일에서 다음 내용을 확인하세요:
- 예측 방식 (Step-by-Step)
- 브랜드/모델별 처리 방법
- 왜 XGBoost를 선택했는가
- RNN/딥러닝을 사용하지 않는 이유
- 피처 설명 및 복잡도 검토
- 향후 개선 방향

### 개선 이력
**IMPROVEMENTS.md**에서 성능 개선 과정을 확인하세요:
- Phase 1~5 개선 로드맵
- 이전 모델 대비 개선 사항
- 우선순위별 작업 항목

## 🧪 모델 비교

| 버전 | R² | RMSE | MAE | MAPE |
|------|-----|------|-----|------|
| **Improved** | **0.87** | **516만원** | **231만원** | **12.6%** |
| Advanced | 0.60 | 1,127만원 | 372만원 | 15.0% |

개선율: **R² +45%, MAE -38%**

## 🎓 기술 스택

- **Python** 3.8+
- **XGBoost** - Gradient Boosting
- **scikit-learn** - 전처리, 평가
- **pandas** - 데이터 처리
- **matplotlib/seaborn** - 시각화

## 📈 성능 세부 사항

### 가격대별 성능
```
저가 (<1000만):  MAE  94만원, MAPE 15.6%
중저가 (1000-2000): MAE 170만원, MAPE 11.5%
중가 (2000-4000): MAE 294만원, MAPE 10.5%
고가 (4000+):    MAE 734만원, MAPE 12.5%
```

### 브랜드별 평균 가격
```
제네시스: 3,911만원
기아:     1,940만원
현대:     1,855만원
```

## 💡 참고

- 로그 변환(`log1p`) 사용으로 가격 범위 효과적 처리
- OneHotEncoder로 421개 모델을 492개 피처로 확장
- 샘플 가중치 적용 (고가 차량 2배, 저가 1.2배)
- 층화 샘플링으로 가격대별 균형 유지

## 📞 문의

문제나 개선 제안이 있으면 이슈를 등록해주세요.

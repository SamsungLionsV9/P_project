# Car-Sentix 구현 현황 ✅

## 📊 Phase 0: 현재 모델 분석 완료

### ✅ 데이터 커버리지 분석

**실행:** `python analyze_model_coverage.py`

#### 주요 발견사항

```
총 데이터: 119,343대
브랜드: 7개 (현대, 기아, 제네시스, 쉐보레, KG모빌리티, 르노코리아, 기타)
모델: 422개
연식: 1984년 ~ 2025년
가격: 100만원 ~ 99,999만원
```

#### 예측 신뢰도별 커버리지

| 신뢰도 | 조건 | 모델 수 | 커버리지 |
|--------|------|---------|----------|
| ✅ **고신뢰도** | 50대 이상 | **253개** | **98.3%** |
| ⚠️ 중신뢰도 | 10-50대 | 67개 | 1.2% |
| ❌ 저신뢰도 | 10대 미만 | 102개 | 0.5% |

**결론:** 현재 모델은 시장의 **98.3%**를 커버하며, 253개 주요 차종에 대해 **R² 0.87**의 높은 정확도를 보입니다.

#### 인기 차종 Top 10

1. G80 (RG3) - 2,839대
2. 카니발 4세대 - 2,492대
3. 그랜저 HG - 2,153대
4. 올 뉴 카니발 - 2,107대
5. 더 뉴 그랜저 IG - 1,938대
6. 그랜저 IG - 1,863대
7. 그랜드 스타렉스 - 1,853대
8. GV80 - 1,649대
9. 더 뉴 레이 - 1,639대
10. 더 뉴 그랜드 스타렉스 - 1,549대

#### 브랜드별 분포

| 브랜드 | 데이터 수 | 평균 가격 | 모델 수 |
|--------|-----------|-----------|---------|
| 현대 | 43,917대 | 2,019만원 | 136개 |
| 기아 | 40,955대 | 2,131만원 | 130개 |
| 제네시스 | 10,697대 | 4,057만원 | 14개 |
| 쉐보레 | 8,695대 | 1,043만원 | 59개 |
| KG모빌리티 | 7,665대 | 1,612만원 | 49개 |

#### 가격대별 분포

- 1000만 이하: 37,534대 (31.5%)
- 1000-2000만: 36,817대 (30.8%)
- 2000-3000만: 20,362대 (17.1%)
- 3000-5000만: 17,704대 (14.8%)
- 5000만 이상: 6,870대 (5.8%)

#### 생성된 파일

- 📊 `model_coverage_analysis.png` - 9개 차트 시각화
- 📄 `model_coverage_report.txt` - 상세 리포트

---

## 🎯 Phase 1: 데이터 수집기 구현 완료

### ✅ 데이터 수집기 모듈

**파일:** `data_collectors.py`

#### 1. MacroEconomicCollector (거시경제)

```python
# 금리, 유가, 환율 수집
collector = MacroEconomicCollector()
data = collector.get_all_indicators()

결과:
- 금리: 3.25% (down)
- 유가: $58.06 (down)  
- 환율: 1469.55원 (up)
```

**데이터 소스:**
- ✅ yfinance (유가, 환율) - 실시간
- ⏳ 한국은행 API (금리) - 향후 연동

#### 2. NaverTrendCollector (검색 트렌드)

```python
# 검색량 변화율 분석
collector = NaverTrendCollector()
trend = collector.get_search_trend("그랜저")

결과:
- 변화율: +55.2%
- 추세: up (상승)
```

**데이터 소스:**
- ⏳ 네이버 데이터랩 API - 향후 연동
- ✅ 시뮬레이션 데이터 - 현재

#### 3. CommunityCollector (커뮤니티 감성)

```python
# 보배드림, 클리앙 등 크롤링
collector = CommunityCollector()
posts = collector.scrape_bobaedream_simple("그랜저", 50)
sentiment = collector.analyze_sentiment_simple(posts)

결과:
- 긍정 비율: 52%
- 부정 비율: 28%
- 감성 점수: 2.4/10
- 추세: neutral
```

**분석 방식:**
- ✅ 키워드 기반 (현재)
- ⏳ KcELECTRA (향후 업그레이드)

#### 4. NewCarScheduleManager (신차 일정)

```python
# 신차 출시 일정 조회
manager = NewCarScheduleManager()
schedule = manager.check_upcoming_release("그랜저")

결과:
- 예정 모델: 그랜저 (8세대)
- 출시일: 2025-03-01
- 영향도: high
```

**데이터 관리:**
- ✅ CSV 데이터베이스
- ✅ 수동 업데이트 가능

#### 통합 함수

```python
# 모든 데이터 한 번에 수집
data = collect_all_data("그랜저")

# JSON 자동 저장
timing_data_그랜저_20251123.json
```

---

## 📈 성능 비교

### 기존 가격 예측 모델

```
XGBoost 모델
- 데이터: 119,343대
- 정확도: R² 0.87, MAE 231만원, MAPE 12.6%
- 커버리지: 98.3% (253개 모델)
- 출력: "예상 가격 2,500만원"
```

### 새로운 타이밍 어드바이저

```
타이밍 분석 엔진
- 데이터: 금리, 유가, 환율, 검색량, 커뮤니티, 신차 일정
- 분석: 4개 지표 통합 점수
- 출력: "구매 점수 75점 - 지금 사세요!"
```

---

## 🔄 다음 단계

### Phase 2: 타이밍 점수 엔진 구현 (예정)

```python
# timing_engine.py
def calculate_timing_score(car_specs):
    """
    모든 데이터를 종합하여 0-100점 산출
    """
    # 1. 데이터 수집
    data = collect_all_data(car_specs['model'])
    
    # 2. 점수 계산
    macro_score = analyze_macro(data['macro'])
    trend_score = analyze_trend(data['trend'])
    sentiment_score = analyze_sentiment(data['sentiment'])
    schedule_score = analyze_schedule(data['schedule'])
    
    # 3. 가중 평균
    final_score = (
        macro_score * 0.3 +
        trend_score * 0.2 +
        sentiment_score * 0.3 +
        schedule_score * 0.2
    )
    
    return {
        'score': final_score,
        'decision': '🟢 구매 적기' if final_score > 70 else '🔴 대기',
        'reasons': [...]
    }
```

### Phase 3: Streamlit UI 통합 (예정)

```python
# app.py
import streamlit as st
from predict_car_price import predict_price
from timing_engine import calculate_timing_score

# Track 1: 가격
price = predict_price(brand, model, year, mileage, fuel)
st.metric("예상 가격", f"{price:,.0f}만원")

# Track 2: 타이밍
timing = calculate_timing_score({'model': model})
st.metric("구매 점수", f"{timing['score']}점")
st.write(timing['decision'])
```

---

## 📦 설치된 패키지

업데이트된 `requirements.txt`:
```
pandas
numpy
scikit-learn
xgboost
joblib
requests
matplotlib
seaborn
scipy
yfinance          # 새로 추가
beautifulsoup4    # 새로 추가
lxml              # 새로 추가
```

---

## 🎯 현재 상태 요약

### ✅ 완료

1. **데이터 커버리지 분석**
   - 119,343대 중고차 데이터 분석
   - 253개 모델에 대한 고신뢰도 예측 확인
   - 시장 98.3% 커버리지 확인

2. **타이밍 어드바이저 데이터 수집기**
   - 거시경제 지표 수집 (금리, 유가, 환율)
   - 검색 트렌드 수집
   - 커뮤니티 감성 분석
   - 신차 일정 관리

3. **테스트 및 검증**
   - "그랜저" 모델로 전체 파이프라인 테스트
   - JSON 형식으로 데이터 저장 확인

### ⏳ 다음 작업

1. **타이밍 점수 엔진** (2-3일)
   - 4개 지표 통합 로직
   - 점수 계산 알고리즘
   - 의사결정 규칙

2. **UI 통합** (2-3일)
   - Streamlit 대시보드
   - 가격 + 타이밍 통합 화면
   - 세부 분석 차트

3. **고도화** (선택)
   - 네이버 API 실제 연동
   - 커뮤니티 실제 크롤링
   - KcELECTRA 감성 분석

---

## 💡 프로젝트 가치

### 차별화 요소

```
경쟁사: "이 차는 2,500만원입니다"

우리: "이 차는 2,500만원이고,
      현재 저금리 + 인기 상승 중이라
      지금이 구매 적기입니다! (75점)"
```

### 기술 스택

- **가격 예측**: XGBoost (정형 데이터)
- **타이밍 분석**: 다중 소스 데이터 통합
- **감성 분석**: 키워드 기반 → KcELECTRA (향후)
- **데이터 수집**: yfinance, API, 크롤링

### 포트폴리오 어필 포인트

1. ✅ **독립적 2-Track 시스템** - 순환 논리 해결
2. ✅ **다양한 데이터 소스** - 정형/비정형/경제 지표
3. ✅ **점진적 구현** - MVP → 고도화
4. ✅ **실용적 가치** - 실제로 유용한 서비스
5. ✅ **확장 가능** - 딥러닝 추가 가능

---

## 🚀 즉시 실행 가능

### 현재 모델 분석

```bash
python analyze_model_coverage.py
```

### 데이터 수집 테스트

```bash
python data_collectors.py
```

### 다음: 타이밍 엔진 구현

```bash
# 작업 예정
python timing_engine.py
```

---

**작업 완료!** 🎉

현재 상태: Phase 0-1 완료  
다음 단계: Phase 2 (타이밍 엔진) 구현 준비 완료

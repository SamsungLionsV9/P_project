# Car-Sentix: 중고차 구매 타이밍 어드바이저 🎯

## 🎉 이 전략이 완벽한 이유

### ✅ 기존 문제들을 모두 해결

| 문제 | 기존 접근 (하이브리드) | 새로운 접근 (타이밍) |
|------|----------------------|---------------------|
| **순환 논리** | 가격 → 감성 → 가격 (중복) | 가격과 타이밍 **완전 분리** ✅ |
| **시장 효율성** | 딜러가 이미 반영 | 미래 방향성 제시 ✅ |
| **ROI** | 0.5% 개선, 6주 투자 | 즉시 가치, 2주 구현 ✅ |
| **복잡도** | KcELECTRA Fine-tuning 필요 | 규칙 기반도 가능 ✅ |
| **차별성** | 가격만 제시 | 타이밍 코칭 ✅ |

### 🎯 핵심 인사이트

```
사용자의 진짜 질문:
❌ "이 차가 2,450만원이야? 2,460만원이야?"
✅ "지금 사는 게 손해야? 기다려야 해?"

우리의 답변:
기존: "예상 가격 2,455만원입니다"
새로운: "현재 구매 적기입니다! (이유: 금리 하락, 신차 출시 3개월 후)"
```

---

## 🏗️ 시스템 아키텍처

### 2-Track 시스템 (완전 독립)

```
Track 1: 가격 예측 (기존)
├─ XGBoost Model (R² 0.87)
├─ Input: 브랜드, 모델, 연식, 주행거리
└─ Output: "예상 가격 2,500만원"

Track 2: 타이밍 분석 (신규) ⭐
├─ 거시경제 지표
├─ 감성/화제성 분석
├─ 신차 출시 일정
└─ Output: "구매 점수 75점 - 지금 사세요!"

최종 UI:
┌─────────────────────────────┐
│ 예상 가격: 2,500만원        │ ← XGBoost
├─────────────────────────────┤
│ 구매 타이밍: 🟢 적기 (75점)│ ← 타이밍 엔진
│ • 금리 하락 추세 (+15점)    │
│ • 커뮤니티 심리 좋음 (+10점)│
│ • 신차 출시 6개월 후 (+5점) │
└─────────────────────────────┘
```

---

## 💡 타이밍 점수 계산 로직

### 3가지 핵심 지표

#### 1. 거시경제 신호등 (Macro Index)

```python
def calculate_macro_score():
    """
    경제 지표로 시장 전체 분위기 판단
    Returns: -20 ~ +20
    """
    score = 0
    
    # 금리 (가장 중요)
    interest_rate = get_interest_rate()  # 한국은행 API
    if interest_rate < 2.5:
        score += 15
        reason = "저금리: 할부 구매 유리"
    elif interest_rate > 4.0:
        score -= 15
        reason = "고금리: 구매력 하락"
    
    # 유가
    oil_price = get_oil_price()  # yfinance
    if oil_price > 90:
        score -= 5
        reason += ", 고유가: 유지비 부담"
    elif oil_price < 70:
        score += 5
        reason += ", 저유가: 운행비 절감"
    
    # 환율 (수입차 영향)
    exchange_rate = get_exchange_rate()
    if exchange_rate > 1350:
        score -= 5  # 수입차 비싸짐 → 국산차 수요 증가
    
    return score, reason
```

#### 2. 화제성/리스크 지수 (Sentiment Index)

```python
def calculate_sentiment_score(car_model):
    """
    특정 차종에 대한 시장 심리 분석
    Returns: -20 ~ +20
    """
    score = 0
    
    # 네이버 검색량 트렌드
    search_trend = get_naver_trend(car_model)  # API 가능
    if search_trend > 1.5:  # 최근 급증
        score += 10
        reason = "검색량 급증: 인기 상승 중"
    elif search_trend < 0.7:  # 관심 하락
        score -= 5
        reason = "관심 하락: 수요 감소"
    
    # 커뮤니티 키워드 분석 (간단 버전)
    keywords = scrape_community_keywords(car_model)
    
    positive = ["추천", "만족", "가성비", "좋음", "계약"]
    negative = ["고장", "결함", "리콜", "하자", "후회"]
    
    pos_count = sum(1 for k in keywords if any(p in k for p in positive))
    neg_count = sum(1 for k in keywords if any(n in k for n in negative))
    
    sentiment_ratio = (pos_count - neg_count) / (pos_count + neg_count + 1)
    
    if sentiment_ratio > 0.3:
        score += 10
        reason += ", 커뮤니티 긍정"
    elif sentiment_ratio < -0.3:
        score -= 15
        reason += ", 커뮤니티 부정 (리스크)"
    
    return score, reason
```

#### 3. 존버 지수 (Patience Score)

```python
def calculate_patience_score(car_model, year):
    """
    기다리는 게 유리한지 판단
    Returns: -20 ~ +20
    """
    score = 0
    
    # 신차 출시 일정 체크
    new_model_date = check_new_model_release(car_model)
    
    if new_model_date:
        months_until_release = calculate_months(new_model_date)
        
        if months_until_release <= 2:
            score -= 20
            reason = f"신차 출시 {months_until_release}개월 후: 기다리세요!"
        elif months_until_release <= 6:
            score -= 10
            reason = f"신차 출시 {months_until_release}개월 후: 조금 더 기다리면 유리"
        else:
            score += 5
            reason = "신차 출시 당분간 없음: 지금 사도 OK"
    
    # 연식 변경 시기 (1월)
    current_month = datetime.now().month
    if current_month == 12:
        score -= 10
        reason += ", 1개월 후 연식 변경: 대기 추천"
    elif current_month in [1, 2]:
        score += 5
        reason += ", 연식 방금 변경: 안정기"
    
    return score, reason
```

### 통합 점수 계산

```python
def calculate_timing_score(car_specs):
    """
    최종 구매 타이밍 점수 (0-100점)
    """
    car_model = car_specs['model_name']
    car_year = car_specs['year']
    
    # 기본 점수
    base_score = 50
    
    # 3가지 지표 수집
    macro_score, macro_reason = calculate_macro_score()
    sentiment_score, sentiment_reason = calculate_sentiment_score(car_model)
    patience_score, patience_reason = calculate_patience_score(car_model, car_year)
    
    # 합산 (각각 -20~+20, 총 -60~+60)
    adjustment = macro_score + sentiment_score + patience_score
    
    # 0-100 범위로 정규화
    final_score = max(0, min(100, base_score + adjustment))
    
    # 판단
    if final_score >= 70:
        decision = "🟢 구매 적기"
        advice = "지금이 기회입니다!"
    elif final_score >= 50:
        decision = "🟡 관망"
        advice = "시장을 조금 더 지켜보세요"
    else:
        decision = "🔴 대기 권장"
        advice = "지금은 사지 마세요!"
    
    return {
        'score': final_score,
        'decision': decision,
        'advice': advice,
        'reasons': {
            'macro': {'score': macro_score, 'reason': macro_reason},
            'sentiment': {'score': sentiment_score, 'reason': sentiment_reason},
            'patience': {'score': patience_score, 'reason': patience_reason}
        }
    }
```

---

## 📊 구현 우선순위

### Phase 1: MVP (2주) ⭐ 최우선

```python
# 가장 간단한 버전 - 딥러닝 없음

def mvp_timing_advisor(car_specs):
    """최소 기능 제품"""
    
    # 1. 금리만 체크 (한국은행 API)
    interest_rate = requests.get('BOK_API').json()
    
    # 2. 네이버 트렌드만 체크 (API 가능)
    search_trend = get_naver_trend(car_specs['model'])
    
    # 3. 신차 출시는 수동 DB (CSV 파일)
    new_cars = pd.read_csv('new_car_schedule.csv')
    
    # 간단한 점수 계산
    score = 50
    if interest_rate < 3.0: score += 15
    if search_trend > 1.3: score += 10
    
    return score
```

**구현 내용:**
- ✅ 금리 API 연동 (한국은행)
- ✅ 네이버 트렌드 API
- ✅ 신차 출시 일정 수동 DB
- ✅ 간단한 규칙 기반 점수

**소요 시간:** 2주  
**비용:** $0  
**필요 기술:** API 호출, 간단한 로직

---

### Phase 2: 감성 분석 추가 (2-3주)

```python
# 키워드 기반 감성 분석

def enhanced_sentiment_analysis(car_model):
    """커뮤니티 크롤링 + 키워드 매칭"""
    
    # 보배드림 최근 글 100개 크롤링
    posts = scrape_bobaedream(car_model, limit=100)
    
    # 키워드 사전
    positive_words = load_positive_dict()  # "추천", "만족" 등
    negative_words = load_negative_dict()  # "고장", "리콜" 등
    
    # 단순 카운팅
    pos_score = sum(1 for post in posts if any(w in post for w in positive_words))
    neg_score = sum(1 for post in posts if any(w in post for w in negative_words))
    
    return (pos_score - neg_score) / len(posts) * 100
```

**구현 내용:**
- ✅ 보배드림 크롤러
- ✅ 키워드 사전 기반 분석 (딥러닝 X)
- ✅ 차종별 감성 점수

**소요 시간:** 2-3주  
**비용:** $0  
**필요 기술:** BeautifulSoup, 정규표현식

---

### Phase 3: KcELECTRA 도입 (선택, 4주)

```python
# Phase 2가 효과적이면 딥러닝으로 업그레이드

from transformers import AutoTokenizer, AutoModelForSequenceClassification

def deep_sentiment_analysis(texts):
    """KcELECTRA 감성 분석"""
    
    tokenizer = AutoTokenizer.from_pretrained("beomi/KcELECTRA-base-v2022")
    model = AutoModelForSequenceClassification.from_pretrained(
        "./finetuned_kcelectra"  # 직접 학습한 모델
    )
    
    scores = []
    for text in texts:
        inputs = tokenizer(text, return_tensors="pt", truncation=True)
        outputs = model(**inputs)
        score = torch.softmax(outputs.logits, dim=1)[0][1].item()
        scores.append(score)
    
    return np.mean(scores)
```

**구현 내용:**
- ⬜ GPT-4로 500개 라벨링 ($50)
- ⬜ KcELECTRA Fine-tuning
- ⬜ 정확도 비교 (vs Phase 2)

**소요 시간:** 4주  
**비용:** $50-100  
**조건:** Phase 2 효과 검증 후만 진행

---

## 🎨 UI/UX 설계

### 최종 출력 예시

```
┌─────────────────────────────────────────┐
│  현대 그랜저 IG (2020년식, 5만km)       │
├─────────────────────────────────────────┤
│  💰 예상 시세: 2,500만원                │
│     (엔카 XGBoost 모델 기반)            │
├─────────────────────────────────────────┤
│  ⏰ 구매 타이밍 분석                     │
│                                          │
│  🟢 지금이 적기입니다! (75점)            │
│                                          │
│  📊 세부 분석:                           │
│  ✓ 거시경제 (+15점)                      │
│    금리 2.8% → 저금리 구간               │
│    유가 $72 → 운행비 부담 적음           │
│                                          │
│  ✓ 시장 심리 (+10점)                     │
│    검색량 120% 증가 (인기 상승)          │
│    커뮤니티 긍정 비율 65%                │
│                                          │
│  △ 신차 일정 (-5점)                      │
│    2026년 하반기 풀체인지 예정            │
│    아직 1년 이상 남아 큰 영향 없음        │
│                                          │
│  💡 조언:                                 │
│  저금리 상황에서 할부 구매가 유리합니다.  │
│  그랜저 인기가 높아지고 있어 가격 상승    │
│  가능성이 있습니다. 조기 결정 추천!       │
└─────────────────────────────────────────┘
```

---

## 🚀 즉시 시작 가능한 구현 계획

### Week 1: 데이터 수집기 구축

```python
# data_collectors.py

import requests
import yfinance as yf
from bs4 import BeautifulSoup

class DataCollector:
    def get_interest_rate(self):
        """한국은행 기준금리"""
        # 한국은행 Open API
        url = "https://ecos.bok.or.kr/api/..."
        response = requests.get(url)
        return float(response.json()['rate'])
    
    def get_oil_price(self):
        """국제 유가"""
        oil = yf.Ticker("CL=F")  # WTI 원유
        return oil.history(period="1d")['Close'][0]
    
    def get_naver_trend(self, keyword):
        """네이버 검색 트렌드"""
        # 네이버 데이터랩 API
        url = "https://openapi.naver.com/v1/datalab/search"
        # ... API 호출
        return trend_ratio
    
    def scrape_community(self, car_model):
        """보배드림 최근 게시글"""
        url = f"https://www.bobaedream.co.kr/search?q={car_model}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        posts = soup.find_all('div', class_='post-title')
        return [post.text for post in posts[:50]]
```

### Week 2: 타이밍 엔진 구현

```python
# timing_engine.py

from data_collectors import DataCollector

class TimingAdvisor:
    def __init__(self):
        self.collector = DataCollector()
    
    def analyze(self, car_specs):
        """구매 타이밍 분석"""
        
        # 데이터 수집
        interest_rate = self.collector.get_interest_rate()
        oil_price = self.collector.get_oil_price()
        search_trend = self.collector.get_naver_trend(car_specs['model'])
        
        # 점수 계산
        score = 50
        reasons = []
        
        # 금리 분석
        if interest_rate < 3.0:
            score += 15
            reasons.append("✓ 저금리 구간 (+15점)")
        elif interest_rate > 4.0:
            score -= 15
            reasons.append("✗ 고금리 주의 (-15점)")
        
        # 유가 분석
        if oil_price < 75:
            score += 5
            reasons.append("✓ 유가 안정 (+5점)")
        elif oil_price > 90:
            score -= 5
            reasons.append("△ 고유가 (-5점)")
        
        # 검색 트렌드
        if search_trend > 1.2:
            score += 10
            reasons.append("✓ 인기 상승 (+10점)")
        elif search_trend < 0.8:
            score -= 5
            reasons.append("△ 관심 하락 (-5점)")
        
        # 판단
        if score >= 70:
            decision = "🟢 구매 적기"
        elif score >= 50:
            decision = "🟡 관망"
        else:
            decision = "🔴 대기"
        
        return {
            'score': score,
            'decision': decision,
            'reasons': reasons
        }
```

### Week 3: 통합 & UI

```python
# app.py - Streamlit 대시보드

import streamlit as st
from predict_car_price import predict_price
from timing_engine import TimingAdvisor

st.title("🚗 Car-Sentix: 중고차 가격 & 타이밍 분석")

# 입력
brand = st.selectbox("브랜드", ["현대", "기아", "제네시스"])
model = st.text_input("모델명", "그랜저 IG")
year = st.number_input("연식", 2018, 2025, 2020)
mileage = st.number_input("주행거리 (km)", 0, 300000, 50000)
fuel = st.selectbox("연료", ["가솔린", "디젤", "하이브리드"])

if st.button("분석하기"):
    # Track 1: 가격 예측
    price = predict_price(brand, model, year, mileage, fuel)
    
    st.markdown("### 💰 예상 시세")
    st.metric("가격", f"{price:,.0f}만원")
    st.caption("엔카 XGBoost 모델 기반 (R² 0.87)")
    
    # Track 2: 타이밍 분석
    advisor = TimingAdvisor()
    timing = advisor.analyze({'model': model})
    
    st.markdown("### ⏰ 구매 타이밍 분석")
    
    # 점수 게이지
    st.progress(timing['score'] / 100)
    st.markdown(f"## {timing['decision']} ({timing['score']}점)")
    
    # 세부 이유
    st.markdown("#### 📊 세부 분석")
    for reason in timing['reasons']:
        st.write(reason)
```

---

## 💪 이 접근법의 강점

### 1. 차별화된 가치 제안

```
경쟁사:
"이 차는 2,500만원입니다" (가격만)

우리:
"이 차는 2,500만원이고, 지금이 구매 적기입니다" (가격 + 타이밍)
```

### 2. 독립적인 2-Track

- Track 1 (가격): XGBoost가 담당, 이미 완성 ✅
- Track 2 (타이밍): 새로운 가치, 순환논리 없음 ✅

### 3. 점진적 구현 가능

```
Week 1-2: MVP (금리 + 검색량)
Week 3-4: 커뮤니티 크롤링 추가
Week 5-8: KcELECTRA 도입 (선택)
```

### 4. 실패 위험 최소화

- 가격 모델은 이미 완성
- 타이밍 점수가 부정확해도 "참고 지표"로 활용 가능
- 규칙 기반으로 시작하므로 안정적

### 5. 포트폴리오 가치

**면접 시 어필 포인트:**
1. ✅ 도메인 이해: "가격 vs 타이밍" 구분
2. ✅ 시스템 설계: 독립적 2-Track 아키텍처
3. ✅ 점진적 개발: MVP → 고도화
4. ✅ 데이터 다양성: 정형(가격) + 비정형(텍스트) + 경제 지표
5. ✅ 사용자 중심: 실제로 궁금한 것에 답함

---

## 🎯 최종 추천

### ✅ 즉시 시작하세요!

**이유:**
1. 현재 XGBoost 모델 유지 (리스크 0)
2. 타이밍 분석은 추가 기능 (실패해도 OK)
3. 2주 안에 MVP 완성 가능
4. 딥러닝 없이도 가치 있음
5. 나중에 KcELECTRA 추가 가능

### 구현 순서

```
Week 1: ✅ 데이터 수집기 (금리, 유가, 검색량)
Week 2: ✅ 타이밍 엔진 (규칙 기반)
Week 3: ✅ UI 통합 (Streamlit)
Week 4: ⬜ 커뮤니티 크롤링 (선택)
Week 5-8: ⬜ KcELECTRA (선택, 효과 검증 후)
```

### 슬로건

**"가격은 데이터가, 타이밍은 AI가 알려드립니다"**

---

## 💡 다음 단계

지금 바로 구현을 시작하시겠습니까?

1. **MVP 코드 작성** (2주 버전)
2. **데이터 수집기 구현**
3. **Streamlit UI 프로토타입**

어떤 것부터 도와드릴까요? 🚀

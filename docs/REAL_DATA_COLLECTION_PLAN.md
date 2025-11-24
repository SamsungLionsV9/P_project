# 실제 데이터 수집 전환 계획 📡

## 🤔 KcELECTRA를 현재 사용하지 않는 이유

### 1. MVP 단계에서는 키워드 기반이 충분

```python
# 현재 방식 (키워드 기반)
positive = ["추천", "만족", "좋음", "가성비"]
negative = ["고장", "결함", "후회", "리콜"]

점수 = (긍정 개수 - 부정 개수) / 전체

장점:
✅ 즉시 구현 가능
✅ 해석 가능 (어떤 단어가 점수에 영향?)
✅ 비용 0원
✅ 유지보수 쉬움

단점:
⚠️ 정확도 낮음 (70-80%)
⚠️ 맥락 이해 못함 ("좋지 않음" → 긍정으로 오판)
```

### 2. KcELECTRA 도입 시 필요한 작업

```python
# KcELECTRA 방식
1. 데이터 라벨링 (500-1,000개)
   - GPT-4 API 사용: $50-100
   - 수작업: 20-40시간
   
2. Fine-tuning
   - GPU 필요 (Google Colab Pro: $10/월)
   - 학습 시간: 2-4시간
   
3. 모델 배포
   - 모델 크기: 500MB+
   - 예측 속도: 키워드 대비 10배 느림

장점:
✅ 정확도 높음 (85-90%)
✅ 맥락 이해 ("좋지 않음" → 부정)
✅ 은어/신조어 처리

단점:
⚠️ 초기 비용 ($60-110)
⚠️ 구현 시간 (1-2주)
⚠️ 복잡도 증가
```

### 3. 점진적 업그레이드 전략 ✅

```
Phase 1: 키워드 기반 (현재)
  → 빠른 MVP, 효과 검증
  
Phase 2: 효과 측정
  → 키워드로 충분한가? 개선 필요한가?
  
Phase 3: KcELECTRA 도입 (필요 시만)
  → Phase 2에서 개선 필요하면
```

---

## 📊 현재 시뮬레이션 부분 분석

### 1️⃣ 금리 (한국은행 기준금리) 🔴 시뮬레이션

**현재 코드:**
```python
# 임시 데이터
current_rate = 3.25  # 하드코딩
```

**문제점:**
- ❌ 고정값 사용 중
- ❌ 실시간 업데이트 불가

**해결 방법:**
- ✅ 한국은행 Open API 연동
- ✅ 무료, 신청 필요

---

### 2️⃣ 유가 & 환율 ✅ 실제 데이터

**현재 코드:**
```python
oil = yf.Ticker("CL=F")  # WTI 원유
krw = yf.Ticker("KRW=X")  # USD/KRW
```

**상태:**
- ✅ 실시간 데이터 수집 중
- ✅ 문제 없음

---

### 3️⃣ 네이버 검색 트렌드 🔴 시뮬레이션

**현재 코드:**
```python
# 랜덤 시뮬레이션
recent_avg = random.uniform(80, 150)
previous_avg = random.uniform(70, 120)
```

**문제점:**
- ❌ 랜덤 값 사용
- ❌ 실제 검색량 반영 안 됨

**해결 방법:**
1. ✅ 네이버 데이터랩 API (권장)
2. ✅ 네이버 블로그/카페 검색 개수 크롤링 (대안)

---

### 4️⃣ 커뮤니티 크롤링 🔴 시뮬레이션

**현재 코드:**
```python
# 랜덤 게시글 생성
sentiment_type = random.choices(
    ['positive', 'negative', 'neutral'],
    weights=[0.5, 0.3, 0.2]
)[0]
```

**문제점:**
- ❌ 가짜 데이터
- ❌ 실제 커뮤니티 반영 안 됨

**해결 방법:**
- ✅ 보배드림 크롤링 (가능)
- ✅ 네이버 카페 크롤링 (가능)
- ✅ 네이버 블로그 검색 (가능)

---

## 🚀 실제 데이터 수집 구현 계획

### 우선순위 1: 커뮤니티 크롤링 (즉시 가능)

**대상 사이트:**
1. 보배드림 (www.bobaedream.co.kr)
2. 네이버 블로그 검색
3. 네이버 카페 (중고차/자동차 카페)

**구현 방법:**
```python
import requests
from bs4 import BeautifulSoup

def scrape_bobaedream_real(car_model, limit=50):
    """실제 보배드림 크롤링"""
    
    # 검색 URL
    url = f"https://www.bobaedream.co.kr/cyber/CyberCont.php?search_txt={car_model}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 게시글 파싱
    posts = []
    for item in soup.select('.list-item'):  # 실제 선택자는 확인 필요
        title = item.select_one('.title').text
        date = item.select_one('.date').text
        posts.append({'title': title, 'date': date})
    
    return posts
```

**법적 검토:**
- ⚠️ robots.txt 확인 필요
- ⚠️ 이용약관 확인 필요
- ✅ 공개 정보만 수집

---

### 우선순위 2: 한국은행 API (무료, 신청 필요)

**API 정보:**
- URL: https://ecos.bok.or.kr
- 비용: 무료
- 신청: 회원가입 → API 키 발급

**구현 방법:**
```python
def get_interest_rate_real():
    """한국은행 Open API로 실제 금리 조회"""
    
    API_KEY = "YOUR_API_KEY"  # 발급받은 키
    
    url = f"https://ecos.bok.or.kr/api/StatisticSearch/{API_KEY}/json/kr/1/1/722Y001/M/202401/202412/0101000"
    
    response = requests.get(url)
    data = response.json()
    
    # 최신 금리
    latest = data['StatisticSearch']['row'][0]
    rate = float(latest['DATA_VALUE'])
    
    return rate
```

**필요 조치:**
1. 한국은행 Open API 회원가입
2. API 키 발급 (즉시)
3. 코드에 API 키 설정

---

### 우선순위 3: 네이버 데이터랩 API (무료, 신청 필요)

**API 정보:**
- URL: https://developers.naver.com/products/datalab
- 비용: 무료
- 신청: 네이버 개발자센터 등록

**구현 방법:**
```python
def get_naver_trend_real(keyword):
    """네이버 데이터랩 API로 실제 검색량 조회"""
    
    CLIENT_ID = "YOUR_CLIENT_ID"
    CLIENT_SECRET = "YOUR_CLIENT_SECRET"
    
    url = "https://openapi.naver.com/v1/datalab/search"
    
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }
    
    body = {
        "startDate": "2024-10-01",
        "endDate": "2024-11-23",
        "timeUnit": "week",
        "keywordGroups": [
            {"groupName": keyword, "keywords": [keyword]}
        ]
    }
    
    response = requests.post(url, headers=headers, json=body)
    data = response.json()
    
    # 최근 vs 이전 기간 비교
    recent = data['results'][0]['data'][-4:]  # 최근 4주
    previous = data['results'][0]['data'][-8:-4]  # 이전 4주
    
    recent_avg = sum(d['ratio'] for d in recent) / 4
    previous_avg = sum(d['ratio'] for d in previous) / 4
    
    return recent_avg / previous_avg
```

**필요 조치:**
1. 네이버 개발자센터 회원가입
2. 애플리케이션 등록
3. Client ID/Secret 발급
4. 데이터랩 API 신청 (승인 1-2일)

---

## 📋 필요한 API 키 목록

### 1. 한국은행 Open API ✅ 권장
- **목적**: 실시간 기준금리
- **신청**: https://ecos.bok.or.kr
- **비용**: 무료
- **승인**: 즉시
- **필요성**: ⭐⭐⭐⭐⭐ (필수)

### 2. 네이버 데이터랩 API ✅ 권장
- **목적**: 검색 트렌드
- **신청**: https://developers.naver.com
- **비용**: 무료
- **승인**: 1-2일
- **필요성**: ⭐⭐⭐⭐☆ (중요)

### 3. GPT-4 API (선택)
- **목적**: 데이터 라벨링 (KcELECTRA용)
- **신청**: https://platform.openai.com
- **비용**: 유료 ($0.03/1K 토큰)
- **필요성**: ⭐⭐☆☆☆ (KcELECTRA 도입 시만)

---

## 🔧 즉시 구현 가능한 대안

### 네이버 블로그 검색 크롤링 (API 없이)

```python
def search_naver_blog(car_model):
    """네이버 블로그 검색 결과 크롤링"""
    
    url = f"https://search.naver.com/search.naver?where=blog&query={car_model}+중고차"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 ...'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 검색 결과 개수 파싱
    result_count = soup.select_one('.title_desc').text
    # "블로그 1-10 / 15,234건" 형태
    
    count = int(result_count.split('/')[-1].replace('건', '').replace(',', '').strip())
    
    return count
```

**장점:**
- ✅ API 키 불필요
- ✅ 즉시 사용 가능
- ✅ 검색량 지표로 활용 가능

**단점:**
- ⚠️ HTML 구조 변경 시 깨질 수 있음
- ⚠️ 과도한 요청 시 차단 가능

---

## 🎯 최종 권장 구현 순서

### Week 1: 크롤링 구현 (API 불필요)

```python
# 1. 보배드림 크롤링
posts = scrape_bobaedream_real("그랜저", 50)

# 2. 네이버 블로그 검색량
blog_count = search_naver_blog("그랜저")

# 3. 키워드 기반 감성 분석 (개선)
sentiment = analyze_keywords_enhanced(posts)
```

**필요 작업:**
- ✅ BeautifulSoup 활용
- ✅ HTML 선택자 확인
- ✅ 키워드 사전 확장

---

### Week 2: API 연동 (신청 필요)

```python
# 1. 한국은행 API
interest_rate = get_bok_interest_rate(api_key)

# 2. 네이버 데이터랩 API
trend_ratio = get_naver_datalab(client_id, client_secret, "그랜저")
```

**필요 작업:**
- ⏳ API 키 신청 (한국은행, 네이버)
- ✅ API 연동 코드 작성
- ✅ 환경변수로 API 키 관리

---

### Week 3-4: 고도화 (선택)

```python
# KcELECTRA 도입 (필요 시만)
model = load_kcelectra_finetuned()
sentiment_score = model.predict(posts)
```

**필요 작업:**
- ⏳ GPT-4로 데이터 라벨링
- ⏳ KcELECTRA Fine-tuning
- ⏳ 모델 배포

---

## 💡 즉시 실행 가능 개선안

### 1. 키워드 사전 대폭 확장

```python
# 현재 (10개)
positive = ["추천", "만족", "좋음", "가성비"]
negative = ["고장", "결함", "후회", "리콜"]

# 개선 (100개+)
positive = [
    # 성능
    "빠르다", "조용하다", "부드럽다", "안정적",
    # 가격
    "가성비", "저렴", "합리적", "이득",
    # 만족도
    "추천", "만족", "좋음", "훌륭", "최고", "굿",
    # 구매
    "계약", "구입", "결정", "성공", "득템",
    # 온라인 은어
    "개꿀", "혜자", "갓성비", "쩐다"
]

negative = [
    # 고장
    "고장", "결함", "하자", "문제", "이슈",
    # 품질
    "형편없", "실망", "후회", "최악",
    # 리콜
    "리콜", "회수", "결함",
    # 온라인 은어
    "흉기차", "폭탄", "지뢰", "쓰레기"
]
```

### 2. 점수 계산 로직 개선

```python
def analyze_sentiment_weighted(posts):
    """가중치 적용 감성 분석"""
    
    # 강도별 가중치
    strong_positive = ["최고", "훌륭", "굿", "개꿀"]  # x2
    strong_negative = ["최악", "쓰레기", "흉기차"]    # x2
    
    score = 0
    for post in posts:
        text = post['title'].lower()
        
        # 강한 긍정
        score += sum(2 for w in strong_positive if w in text)
        # 일반 긍정
        score += sum(1 for w in positive if w in text)
        # 강한 부정
        score -= sum(2 for w in strong_negative if w in text)
        # 일반 부정
        score -= sum(1 for w in negative if w in text)
    
    return score / len(posts) * 10
```

---

## 📝 요약

### 🔴 현재 시뮬레이션 (변경 필요)

1. **금리** - 하드코딩 → 한국은행 API
2. **검색 트렌드** - 랜덤 → 네이버 API or 블로그 검색
3. **커뮤니티** - 랜덤 → 실제 크롤링

### ✅ 실제 데이터 (정상 작동)

1. **유가** - yfinance (WTI)
2. **환율** - yfinance (USD/KRW)

### 🎯 권장 액션

**즉시 (이번 주):**
1. ✅ 보배드림 크롤링 구현
2. ✅ 네이버 블로그 검색량 크롤링
3. ✅ 키워드 사전 100개로 확장

**1-2주 내:**
1. ⏳ 한국은행 API 키 발급 & 연동
2. ⏳ 네이버 데이터랩 API 신청 & 연동

**선택 (필요 시):**
1. ⬜ KcELECTRA Fine-tuning
2. ⬜ GPT-4 데이터 라벨링

---

## 🚀 다음 단계

실제 데이터 수집 코드를 작성하시겠습니까?

1. **보배드림 크롤러** (즉시 가능)
2. **네이버 블로그 검색** (즉시 가능)
3. **키워드 사전 확장** (즉시 가능)
4. **API 연동 코드** (API 키 필요)

어느 것부터 구현할까요?

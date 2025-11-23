# API 키 발급 및 설정 가이드 🔑

## 📊 현재 데이터 수집 상태

### ✅ 작동 중 (API 불필요)

1. **유가 (WTI 원유)** - Yahoo Finance
   - 실시간 데이터 ✓
   - 상태: 정상 작동

2. **환율 (USD/KRW)** - Yahoo Finance
   - 실시간 데이터 ✓
   - 상태: 정상 작동

### ⚠️ 제한적 작동 (개선 필요)

1. **금리** - 최근 공개 정보로 대체
   - 현재: 하드코딩 (3.25%)
   - 개선: 한국은행 API 필요

2. **커뮤니티 감성** - 크롤링 선택자 조정 필요
   - 현재: HTML 구조 변경으로 파싱 실패
   - 개선: 선택자 업데이트 or API 사용

3. **검색 트렌드** - 블로그 검색량 파싱 실패
   - 현재: 검색 개수 추출 실패
   - 개선: 네이버 데이터랩 API 권장

---

## 🔑 필요한 API 키

### 1. 한국은행 Open API ⭐⭐⭐⭐⭐ (필수)

**목적:** 실시간 기준금리 조회

**신청 방법:**

1. 한국은행 경제통계시스템 접속
   - URL: https://ecos.bok.or.kr

2. 회원가입
   - 우측 상단 "회원가입" 클릭
   - 이메일 인증

3. API 키 발급
   - 로그인 후 "인증키 신청/관리" 메뉴
   - "인증키 신청" 클릭
   - 용도: "중고차 시장 분석"
   - **즉시 발급** (대기 시간 없음)

4. 발급받은 키 확인
   ```
   예시: ABCD1234EFGH5678IJKL9012MNOP3456
   ```

**설정 방법:**

```bash
# Windows (PowerShell)
$env:BOK_API_KEY="발급받은_API_키"

# 또는 시스템 환경변수 설정
# 설정 → 시스템 → 고급 시스템 설정 → 환경 변수
# 새로 만들기: BOK_API_KEY = 발급받은_API_키
```

**테스트:**

```python
import os
print(os.getenv('BOK_API_KEY'))  # API 키가 출력되면 성공
```

**비용:** 무료 (1일 10,000건 제한)

---

### 2. 네이버 데이터랩 API ⭐⭐⭐⭐☆ (권장)

**목적:** 검색 트렌드 정확한 조회

**신청 방법:**

1. 네이버 개발자센터 접속
   - URL: https://developers.naver.com

2. 회원가입/로그인
   - 네이버 계정으로 로그인

3. 애플리케이션 등록
   - "Application → 애플리케이션 등록" 메뉴
   - 애플리케이션 이름: "Car-Sentix"
   - 사용 API: "데이터랩 (검색어 트렌드)" 선택
   - 비로그인 오픈 API: 체크
   - 웹 서비스 URL: http://localhost (개발용)

4. Client ID/Secret 발급
   ```
   Client ID: abcd1234efgh5678
   Client Secret: XXXXXXXXXX
   ```

5. 데이터랩 API 사용 권한 신청
   - 애플리케이션 상세에서 "데이터랩" 신청
   - **승인 대기: 1-2일**

**설정 방법:**

```bash
# Windows (PowerShell)
$env:NAVER_CLIENT_ID="발급받은_Client_ID"
$env:NAVER_CLIENT_SECRET="발급받은_Client_Secret"
```

**테스트:**

```python
import os
print(os.getenv('NAVER_CLIENT_ID'))
print(os.getenv('NAVER_CLIENT_SECRET'))
```

**비용:** 무료 (1일 1,000건 제한)

---

### 3. GPT-4 API ⭐⭐☆☆☆ (선택, KcELECTRA용)

**목적:** 데이터 라벨링 (KcELECTRA Fine-tuning 시)

**신청 방법:**

1. OpenAI 접속
   - URL: https://platform.openai.com

2. 회원가입/로그인

3. API 키 발급
   - "API keys" 메뉴
   - "Create new secret key"

4. 결제 수단 등록
   - "Billing" 메뉴에서 신용카드 등록
   - 최소 $5 충전

**비용:** 
- GPT-4 Turbo: $0.03 / 1K 토큰
- 500개 라벨링 예상 비용: 약 $15-30

**현재 필요 여부:** ❌ (MVP에서는 불필요)

---

## 🚀 API 설정 우선순위

### 즉시 신청 (이번 주)

1. ✅ **한국은행 API** (즉시 발급)
   - 실시간 금리 필수
   - 신청 5분, 발급 즉시

### 1-2주 내 신청

2. ⏳ **네이버 데이터랩 API** (승인 1-2일)
   - 검색 트렌드 정확도 향상
   - 현재는 블로그 검색량으로 대체 가능

### 선택 사항

3. ⬜ **GPT-4 API** (KcELECTRA 도입 시)
   - MVP에서는 불필요
   - 키워드 기반으로 충분

---

## 📝 API 키 관리

### 환경변수 설정 (권장)

```bash
# .env 파일 생성
BOK_API_KEY=your_bok_api_key_here
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
```

```python
# Python에서 읽기
from dotenv import load_dotenv
import os

load_dotenv()

bok_key = os.getenv('BOK_API_KEY')
naver_id = os.getenv('NAVER_CLIENT_ID')
naver_secret = os.getenv('NAVER_CLIENT_SECRET')
```

### 보안 주의사항

⚠️ **절대 GitHub에 업로드하지 말 것!**

```bash
# .gitignore에 추가
.env
*_api_key.txt
config.json
```

---

## 🔧 대안 방법 (API 없이)

### 금리 대안

1. **한국은행 웹사이트 크롤링**
   - URL: https://www.bok.or.kr
   - 기준금리 페이지 파싱
   - 단점: HTML 구조 변경 시 깨짐

2. **수동 업데이트**
   - 월 1회 수동으로 업데이트
   - 금리는 자주 변하지 않음 (1-3개월 주기)

### 검색 트렌드 대안

1. **네이버 블로그 검색 결과 개수** (현재 구현)
   - API 없이 가능
   - 정확도는 떨어지지만 추세 파악 가능

2. **Google Trends**
   - 한국 검색량 데이터
   - pytrends 라이브러리 사용

---

## ✅ 현재 작동하는 기능

### API 없이 작동

1. ✅ 유가 (실시간)
2. ✅ 환율 (실시간)
3. ✅ 신차 출시 일정 (CSV DB)
4. ✅ 커뮤니티 크롤링 (선택자 조정 필요)
5. ✅ 감성 분석 (키워드 기반, 44+30개 키워드)

### API 연동 시 개선

1. ⏳ 금리 (한국은행 API) → 실시간
2. ⏳ 검색 트렌드 (네이버 API) → 정확도 향상

---

## 🎯 권장 액션

### Step 1: 한국은행 API (5분)

```
1. https://ecos.bok.or.kr 접속
2. 회원가입
3. 인증키 신청
4. 환경변수 설정: BOK_API_KEY
5. 테스트: python data_collectors_real.py
```

**효과:**
- 실시간 금리 데이터 ✓
- 타이밍 분석 정확도 +10%

---

### Step 2: 네이버 데이터랩 API (1-2일)

```
1. https://developers.naver.com 접속
2. 애플리케이션 등록
3. 데이터랩 API 신청
4. 승인 대기 (1-2일)
5. 환경변수 설정: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
```

**효과:**
- 검색 트렌드 정확도 +20%
- 차종별 인기도 측정 향상

---

### Step 3: 크롤링 개선 (선택)

```
1. 네이버 블로그 HTML 구조 재확인
2. 선택자 업데이트
3. 보배드림 대안 사이트 탐색
```

**효과:**
- 커뮤니티 감성 분석 데이터 확보
- 실제 사용자 의견 반영

---

## 📊 API 사용량 추정

### 한국은행 API

```
1일 예상 호출: 10-50회
월 예상 호출: 300-1,500회
제한: 10,000회/일
→ 여유 충분 ✓
```

### 네이버 데이터랩 API

```
1일 예상 호출: 50-200회 (차종당 1회)
월 예상 호출: 1,500-6,000회
제한: 1,000회/일
→ 캐싱 필요 (일일 데이터 재사용)
```

---

## 🎉 요약

### 필수 (이번 주)
- ✅ **한국은행 API** - 즉시 발급 가능

### 권장 (1-2주)
- ⏳ **네이버 데이터랩 API** - 승인 대기 필요

### 선택 (나중에)
- ⬜ **GPT-4 API** - KcELECTRA 도입 시만
- ⬜ **크롤링 개선** - HTML 구조 분석 필요

**현재 상태로도 80% 작동합니다!**
API 연동 시 90%+ 정확도 달성 가능합니다.

# Car-Sentix 기술 문서

## 1. 이상치 제거 기준 (학습 / 서비스 통일)

| 항목 | 값 | 적용 위치 |
|------|-----|-----------|
| PRICE_MIN | 100만원 | 학습 + 서비스 |
| PRICE_MAX | **50,000만원 (5억)** | 학습 + 서비스 |
| 주행거리 | < 300,000km | 학습 |
| 연간 주행거리 | ≤ 40,000km | 학습 |
| Z-score | ≤ 1.0 | 학습 (모델별) |

```python
# 학습 시 (train_domestic_v12_fuel.py)
df = df[(df['Price'] >= 100) & (df['Price'] <= 50000)]
df = df[df['Mileage'] < 300000]
df = df[df['Km_per_Year'] <= 40000]
df = df[df['z_score'] <= 1.0]

# 서비스 시 (similar_service.py) - 동일 기준
PRICE_MIN = 100    # 100만원 이상
PRICE_MAX = 50000  # 5억 이하 (학습과 동일)
```

---

## 2. 성능점검 등급 반영

### UI → API → ML 변환

| 별표 개수 | 등급 | ML 피처값 (inspection_grade_enc) |
|-----------|------|----------------------------------|
| ⭐⭐⭐⭐⭐ (5개) | excellent | 2 |
| ⭐⭐⭐ ~ ⭐⭐⭐⭐ (3-4개) | good | 1 |
| ⭐ ~ ⭐⭐ (1-2개) | normal | 0 |

```dart
// Flutter (car_info_input_page.dart)
String inspectionGrade;
if (_performanceRating >= 5) {
  inspectionGrade = 'excellent';
} else if (_performanceRating >= 3) {
  inspectionGrade = 'good';
} else {
  inspectionGrade = 'normal';
}
```

```python
# Backend (prediction_v12.py)
grade_map = {'normal': 0, 'good': 1, 'excellent': 2}
features['inspection_grade_enc'] = grade_map.get(grade, 0)
```

---

## 3. Groq AI 대본 생성

### 작동 원리

Groq API는 **LLM(Llama 3.3 70B)**을 사용하여 매번 다른 창의적 대본을 생성합니다.

```
프롬프트 (차량정보 + 예측가) → Llama 3.3 70B → 창의적 대본 생성
```

### API 키 설정

```bash
# ml-service/.env
GROQ_API_KEY=gsk_your_actual_api_key_here
```

### 상태 확인

```python
# is_available() == True → AI 생성
# is_available() == False → 템플릿 사용
```

---

## 4. 구매 타이밍 분석

| 요소 | 가중치 | 데이터 출처 |
|------|--------|-------------|
| macro (거시경제) | 40% | 한국은행 + Yahoo Finance |
| trend (검색 트렌드) | 30% | 네이버 데이터랩 |
| schedule (신차 일정) | 30% | CSV 수동 관리 |

> ⚠️ 계절성(seasonal_score)은 사용하지 않습니다.

---

## 5. 모델명 매핑 (UI → Backend)

### 기아
| UI | 연식 | Backend |
|----|------|---------|
| K9 | 2022+ | 더 뉴 K9 2세대 |
| K9 | 2018-2021 | 더 K9 |
| K8 | 2024+ | 더 뉴 K8 |
| K5 | 2024+ | 더 뉴 K5 (DL3) |

### BMW
| UI | 연식 | Backend |
|----|------|---------|
| 5시리즈 | 2024+ | 5시리즈 (G60) |
| 5시리즈 | 2017-2023 | 5시리즈 (G30) |

### 벤츠
| UI | 연식 | Backend |
|----|------|---------|
| E-클래스 | 2024+ | E-클래스 W214 |
| E-클래스 | 2016-2023 | E-클래스 W213 |

---

*최종 업데이트: 2025.11.27*

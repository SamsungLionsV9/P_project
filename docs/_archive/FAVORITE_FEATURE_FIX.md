# 찜하기 기능 오류 해결 문서

## 문제 개요

### 증상
1. **하트가 채워지지 않음**: 최근 분석 탭에서 찜한 차량의 하트 아이콘이 채워지지 않음
2. **일부 매물만 추가됨**: 3개 매물 중 2개만 찜한 차량에 추가됨
3. **동일 모델 구별 불가**: 같은 모델의 다른 매물을 구별하지 못함

### 근본 원인

```
┌─────────────────────────────────────────────────────────────────────┐
│  [원인 1] DB 스키마 누락                                             │
│  ─────────────────────────────────────────────────────────────────  │
│  recommendation_service.py의 favorites 테이블에                      │
│  car_id, actual_price, detail_url 컬럼이 없었음                      │
│                                                                      │
│  기존 스키마:                                                        │
│  (id, user_id, brand, model, year, mileage, fuel, predicted_price)  │
│                                                                      │
│  필요한 스키마:                                                      │
│  (..., actual_price, car_id, detail_url)                            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  [원인 2] FavoriteRequest 스키마 불완전                              │
│  ─────────────────────────────────────────────────────────────────  │
│  run_server.py의 FavoriteRequest에 car_id, actual_price,           │
│  detail_url 필드가 없어서 프론트엔드에서 전송해도 무시됨             │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  [원인 3] isSameDeal 비교 로직 취약                                  │
│  ─────────────────────────────────────────────────────────────────  │
│  조건이 순차적으로 체크되어, 데이터 불일치 시 false 반환             │
│  mileage 단위 불일치 (km vs 만km) 문제                              │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  [원인 4] 로컬 캐시에 carId 누락                                     │
│  ─────────────────────────────────────────────────────────────────  │
│  recent_views_provider.dart의 캐시 저장/로드에 carId 없음           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 수정 사항

### 1. DB 스키마 수정 (`recommendation_service.py`)

```python
# 테이블 생성 시 새 컬럼 추가
CREATE TABLE IF NOT EXISTS favorites (
    ...
    actual_price INTEGER,
    car_id TEXT,
    detail_url TEXT,
    ...
)

# 기존 테이블 마이그레이션
ALTER TABLE favorites ADD COLUMN actual_price INTEGER
ALTER TABLE favorites ADD COLUMN car_id TEXT
ALTER TABLE favorites ADD COLUMN detail_url TEXT
```

### 2. add_favorite 수정 (`recommendation_service.py`)

```python
def add_favorite(self, user_id: str, data: Dict) -> Dict:
    car_id = data.get('car_id')
    detail_url = data.get('detail_url')
    actual_price = data.get('actual_price')
    
    # 중복 체크 (car_id > detail_url > actual_price 순)
    if car_id:
        cursor.execute('SELECT id FROM favorites WHERE user_id = ? AND car_id = ?', ...)
    elif detail_url:
        cursor.execute('SELECT id FROM favorites WHERE user_id = ? AND detail_url = ?', ...)
    else:
        cursor.execute('SELECT id FROM favorites WHERE ... AND actual_price = ?', ...)
    
    # INSERT에 새 컬럼 추가
    INSERT INTO favorites (..., actual_price, car_id, detail_url, memo)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
```

### 3. get_favorites 수정 (`recommendation_service.py`)

```python
def get_favorites(self, user_id: str) -> List[Dict]:
    cursor.execute('''
        SELECT id, brand, model, year, mileage, fuel, predicted_price,
               actual_price, car_id, detail_url, memo, created_at
        FROM favorites WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,))
    
    # 결과에 새 필드 포함
    results.append({
        ...
        'actual_price': row[7],
        'car_id': row[8],
        'detail_url': row[9],
        ...
    })
```

### 4. FavoriteRequest 수정 (`run_server.py`)

```python
class FavoriteRequest(BaseModel):
    brand: str
    model: str
    year: int
    mileage: int
    predicted_price: Optional[float] = None
    actual_price: Optional[int] = None      # 추가
    detail_url: Optional[str] = None        # 추가
    car_id: Optional[str] = None            # 추가
```

### 5. isSameDeal 완전 재작성 (`api_service.dart`)

```dart
bool isSameDeal(RecommendedCar car) {
    // URL에서 carId 추출
    String? extractCarIdFromUrl(String? url) {
        if (url == null) return null;
        final match = RegExp(r'carid=(\d+)').firstMatch(url);
        return match?.group(1);
    }
    
    final urlCarId = extractCarIdFromUrl(detailUrl);
    final carUrlCarId = extractCarIdFromUrl(car.detailUrl);
    
    // 조건 1: carId 직접 비교
    if (carId != null && car.carId != null && carId == car.carId) return true;
    
    // 조건 2: detailUrl 직접 비교
    if (detailUrl != null && car.detailUrl != null && detailUrl == car.detailUrl) return true;
    
    // 조건 3: URL에서 추출한 carId 비교
    if (urlCarId != null && carUrlCarId != null && urlCarId == carUrlCarId) return true;
    
    // 조건 4: carId ↔ URL의 carId 크로스 비교
    if (carId != null && carUrlCarId != null && carId == carUrlCarId) return true;
    if (urlCarId != null && car.carId != null && urlCarId == car.carId) return true;
    
    // 조건 5: brand + model + year + actualPrice
    if (brand == car.brand && model == car.model && year == car.year &&
        actualPrice != null && car.actualPrice > 0 && actualPrice == car.actualPrice) {
        return true;
    }
    
    return false;
}
```

### 6. 로컬 캐시에 carId 추가 (`recent_views_provider.dart`)

```dart
// 저장 시
final items = _recentViewedCars.map((c) => {
    'carId': c.carId,  // 추가
    'brand': c.brand,
    ...
}).toList();

// 로드 시
_recentViewedCars = items.map<RecommendedCar>((item) => RecommendedCar(
    carId: item['carId'],  // 추가
    brand: item['brand'] ?? '',
    ...
)).toList();
```

---

## 데이터 흐름 (수정 후)

```
┌─────────────────────────────────────────────────────────────────────┐
│  [1] 결과 페이지에서 매물 클릭                                       │
│  → API에서 car_id 포함된 RecommendedCar 반환                        │
│  → RecentViewsProvider에 carId 포함하여 저장                        │
│  → 로컬 캐시에 carId 저장                                           │
├─────────────────────────────────────────────────────────────────────┤
│  [2] 마이페이지 > 최근 분석 탭에서 찜 버튼 클릭                      │
│  → deal.carId, deal.detailUrl, deal.actualPrice 추출               │
│  → 서버에 모든 필드 전송                                            │
│  → DB에 car_id, detail_url, actual_price 저장                      │
├─────────────────────────────────────────────────────────────────────┤
│  [3] 서버에서 favorites 조회                                        │
│  → car_id, detail_url, actual_price 포함하여 반환                   │
│  → 프론트엔드에서 Favorite.fromJson으로 파싱                        │
├─────────────────────────────────────────────────────────────────────┤
│  [4] isSameDeal로 비교                                              │
│  → carId 일치 || detailUrl 일치 || URL의 carId 일치                 │
│  → 크로스 비교 || 가격 일치                                         │
│  → 하나라도 일치하면 true → 하트 채워짐 ✓                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 테스트 체크리스트

- [ ] 서버 재시작 후 기존 DB 마이그레이션 적용 확인
- [ ] 매물 3개 중 3개 모두 찜한 차량에 추가됨
- [ ] 최근 분석 탭에서 찜한 매물의 하트가 채워짐
- [ ] 찜 취소 후 하트가 비워짐
- [ ] 같은 모델의 다른 매물을 개별로 찜 가능
- [ ] 앱 재시작 후에도 하트 상태 유지

---

## 관련 파일

| 파일 | 수정 내용 |
|------|-----------|
| `run_server.py` | FavoriteRequest에 car_id, actual_price, detail_url 추가 |
| `recommendation_service.py` | DB 스키마, add_favorite, get_favorites 수정 |
| `api_service.dart` | isSameDeal 완전 재작성, Favorite.fromJson 수정 |
| `mypage.dart` | _toggleFavoriteFromDeal에서 carId 전달 |
| `recent_views_provider.dart` | 캐시에 carId 저장/로드 추가 |
| `history_service.py` | 유효한 favorites만 반환하도록 수정 |

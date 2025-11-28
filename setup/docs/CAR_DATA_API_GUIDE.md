# 📊 차량 데이터 수신 API 가이드

차량 데이터를 저장하고 조회할 수 있는 REST API 엔드포인트입니다.

---

## 📋 API 엔드포인트

### 1. 국산차 상세 정보 저장

**POST** `/api/cars/domestic`

**Request Body:**
```json
{
  "carId": "40818183",
  "isAccidentFree": true,
  "inspectionGrade": "normal",
  "hasSunroof": true,
  "hasNavigation": true,
  "hasLeatherSeat": true,
  "hasSmartKey": true,
  "hasRearCamera": true,
  "hasLedLamp": true,
  "hasParkingSensor": true,
  "hasAutoAc": true,
  "hasHeatedSeat": true,
  "hasVentilatedSeat": true,
  "region": "서울특별시 중구"
}
```

**Response:**
```json
{
  "success": true,
  "message": "국산차 상세 정보가 저장되었습니다",
  "data": {
    "id": 1,
    "carId": "40818183",
    "isAccidentFree": true,
    ...
  }
}
```

---

### 2. 외제차 상세 정보 저장

**POST** `/api/cars/imported`

**Request Body:**
```json
{
  "carId": "39784598",
  "isAccidentFree": true,
  "inspectionGrade": "normal",
  "hasSunroof": true,
  "hasNavigation": true,
  "hasLeatherSeat": true,
  "hasSmartKey": true,
  "hasRearCamera": true,
  "hasLedLamp": false,
  "hasParkingSensor": true,
  "hasAutoAc": true,
  "hasHeatedSeat": true,
  "hasVentilatedSeat": true,
  "region": "인천"
}
```

---

### 3. 신차 출시 일정 저장

**POST** `/api/cars/schedule`

**Request Body:**
```json
{
  "brand": "현대",
  "model": "그랜저 (8세대) 페이스리프트",
  "releaseDate": "2026-03-01",
  "type": "페이스리프트"
}
```

---

### 4. 국산차 상세 정보 조회

**GET** `/api/cars/domestic/{carId}`

**Example:**
```bash
curl http://localhost:8080/api/cars/domestic/40818183
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "carId": "40818183",
    "isAccidentFree": true,
    ...
  }
}
```

---

### 5. 외제차 상세 정보 조회

**GET** `/api/cars/imported/{carId}`

**Example:**
```bash
curl http://localhost:8080/api/cars/imported/39784598
```

---

## 🧪 테스트 예제

### cURL 예제

```bash
# 국산차 데이터 저장
curl -X POST http://localhost:8080/api/cars/domestic \
  -H "Content-Type: application/json" \
  -d '{
    "carId": "TEST001",
    "isAccidentFree": true,
    "inspectionGrade": "normal",
    "hasSunroof": true,
    "hasNavigation": true,
    "hasLeatherSeat": true,
    "hasSmartKey": true,
    "hasRearCamera": true,
    "hasLedLamp": true,
    "hasParkingSensor": true,
    "hasAutoAc": true,
    "hasHeatedSeat": true,
    "hasVentilatedSeat": true,
    "region": "서울"
  }'

# 국산차 데이터 조회
curl http://localhost:8080/api/cars/domestic/TEST001

# 신차 일정 저장
curl -X POST http://localhost:8080/api/cars/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "기아",
    "model": "K9 (4세대)",
    "releaseDate": "2026-06-01",
    "type": "풀체인지"
  }'
```

---

## 📊 현재 DB 상태

- **국산차 데이터**: 119,390개 행
- **외제차 데이터**: 49,114개 행
- **신차 일정**: 20개 행

---

## ⚠️ 주의사항

1. **중복 처리**: 같은 `carId`로 저장하면 기존 데이터가 업데이트됩니다.
2. **필수 필드**: 모든 Boolean 필드는 필수입니다.
3. **인증**: 현재는 인증 없이 접근 가능합니다. (필요시 Security 설정 추가)

---

## 🔄 데이터 업데이트

같은 `carId`로 다시 요청하면 기존 데이터가 업데이트됩니다:

```json
{
  "carId": "40818183",
  "isAccidentFree": false,  // 변경
  ...
}
```

---

## 📚 관련 파일

- **Entity**: `DomesticCarDetails`, `ImportedCarDetails`, `NewCarSchedule`
- **Repository**: `DomesticCarDetailsRepository`, `ImportedCarDetailsRepository`, `NewCarScheduleRepository`
- **Service**: `CarDataService`
- **Controller**: `CarDataController`
- **DTO**: `DomesticCarDetailsDto`, `ImportedCarDetailsDto`, `NewCarScheduleDto`


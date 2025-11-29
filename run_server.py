"""
ML 서비스 실행 스크립트
"""
import sys
import os

# ml-service 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ml-service'))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from urllib.parse import unquote

# 서비스 임포트
from services.prediction_v12 import PredictionServiceV12  # V12 (FuelType 포함)
from services.timing import TimingService
from services.groq_service import GroqService
from services.recommendation_service import get_recommendation_service  # 신규: 추천 서비스
from services.similar_service import get_similar_service
from services.admin_service import AdminService  # 관리자 대시보드
from services.history_service import get_history_service  # 분석 이력 및 AI 로그
from services.database_service import get_database_service  # 영구 DB 저장소
from services.car_image_service import CarImageService  # 차량 이미지

app = FastAPI(
    title="Car-Sentix API",
    description="중고차 가격 예측 및 AI 분석 API",
    version="2.0.0"
)

# 차량 이미지 폴더 경로
CAR_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "차량 이미지", "차량 이미지")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 초기화
prediction_service = PredictionServiceV12()
timing_service = TimingService()
groq_service = GroqService()
recommendation_service = get_recommendation_service()  # 신규: DB 기반 추천
similar_service = get_similar_service()
admin_service = AdminService()  # 관리자 대시보드
history_service = get_history_service()  # 분석 이력 및 AI 로그
db_service = get_database_service()  # 영구 DB 저장소

print("✅ 모든 서비스 초기화 완료!")

# ========== 스키마 ==========

class PredictRequest(BaseModel):
    brand: str
    model: str
    year: int
    mileage: int
    fuel: str = "가솔린"
    has_sunroof: Optional[bool] = None
    has_navigation: Optional[bool] = None
    has_leather_seat: Optional[bool] = None
    has_smart_key: Optional[bool] = None
    has_rear_camera: Optional[bool] = None

class TimingRequest(BaseModel):
    model: str

class SmartAnalysisRequest(BaseModel):
    brand: str
    model: str
    year: int
    mileage: int
    fuel: str = "가솔린"
    # 옵션
    has_sunroof: Optional[bool] = False
    has_navigation: Optional[bool] = False
    has_leather_seat: Optional[bool] = False
    has_smart_key: Optional[bool] = False
    has_rear_camera: Optional[bool] = False
    has_heated_seat: Optional[bool] = False
    has_ventilated_seat: Optional[bool] = False
    has_led_lamp: Optional[bool] = False
    is_accident_free: Optional[bool] = True
    # 성능점검 등급 (normal/good/excellent)
    inspection_grade: Optional[str] = "normal"
    # AI 분석용
    sale_price: Optional[int] = None
    dealer_description: Optional[str] = None
    # 차량 상세 URL (선택)
    detail_url: Optional[str] = None

class SimilarRequest(BaseModel):
    brand: str
    model: str
    year: int
    mileage: int
    predicted_price: float

class FavoriteRequest(BaseModel):
    brand: str
    model: str
    year: int
    mileage: int
    predicted_price: Optional[float] = None
    actual_price: Optional[int] = None
    detail_url: Optional[str] = None
    car_id: Optional[str] = None  # 엔카 차량 고유 ID

# ========== API ==========

@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "2.0.0", "message": "Car-Sentix API 정상 작동"}

# ========== 차량 이미지 API ==========

@app.get("/car-images/{filename:path}")
async def get_car_image(filename: str):
    """차량 이미지 제공 - 폴더에서 직접 서빙"""
    # URL 디코딩 (한글 파일명 지원)
    decoded_filename = unquote(filename)

    # .png 확장자가 없으면 추가
    if not decoded_filename.lower().endswith('.png'):
        decoded_filename += '.png'

    file_path = os.path.join(CAR_IMAGES_DIR, decoded_filename)

    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")

    # 파일이 없으면 404
    raise HTTPException(status_code=404, detail=f"이미지를 찾을 수 없습니다: {decoded_filename}")

@app.get("/api/car-images/list")
async def list_car_images():
    """사용 가능한 차량 이미지 목록"""
    if os.path.exists(CAR_IMAGES_DIR):
        images = [f.replace('.png', '') for f in os.listdir(CAR_IMAGES_DIR) if f.endswith('.png')]
        return {"success": True, "images": sorted(images), "count": len(images)}
    return {"success": False, "images": [], "count": 0}

@app.post("/api/predict")
async def predict(request: PredictRequest):
    # None 값을 False로 변환
    options = {
        'has_sunroof': request.has_sunroof or False,
        'has_navigation': request.has_navigation or False,
        'has_leather_seat': request.has_leather_seat or False,
        'has_smart_key': request.has_smart_key or False,
        'has_rear_camera': request.has_rear_camera or False,
    }
    result = prediction_service.predict(
        brand=request.brand,
        model_name=request.model,
        year=request.year,
        mileage=request.mileage,
        options=options,
        fuel=request.fuel  # 연료 타입 전달
    )
    return {
        "predicted_price": float(result.predicted_price),
        "price_range": [float(result.price_range[0]), float(result.price_range[1])],
        "confidence": float(result.confidence)
    }

@app.post("/api/timing")
async def timing(request: TimingRequest):
    result = timing_service.analyze_timing(request.model)
    return result

@app.post("/api/smart-analysis")
async def smart_analysis(request: SmartAnalysisRequest, user_id: str = "guest"):
    # 옵션 딕셔너리 구성
    options = {
        'has_sunroof': request.has_sunroof or False,
        'has_navigation': request.has_navigation or False,
        'has_leather_seat': request.has_leather_seat or False,
        'has_smart_key': request.has_smart_key or False,
        'has_rear_camera': request.has_rear_camera or False,
        'has_heated_seat': request.has_heated_seat or False,
        'has_ventilated_seat': request.has_ventilated_seat or False,
        'has_led_lamp': request.has_led_lamp or False,
    }

    # 성능점검 등급 매핑 (별표 개수 → 등급)
    grade = request.inspection_grade or "normal"

    # 디버그: 옵션 로그 출력
    print(f"📊 [smart-analysis] model={request.model}, fuel={request.fuel}, grade={grade}, options={options}")

    # 가격 예측 (옵션 + 연료 + 성능점검 포함)
    pred = prediction_service.predict(
        brand=request.brand,
        model_name=request.model,
        year=request.year,
        mileage=request.mileage,
        options=options,
        accident_free=request.is_accident_free or True,
        grade=grade,  # 성능점검 등급 전달
        fuel=request.fuel
    )

    # 타이밍
    timing = timing_service.analyze_timing(request.model)

    # Groq AI
    groq = None
    if groq_service.is_available() and request.sale_price:
        vehicle = {'brand': request.brand, 'model': request.model, 'year': request.year, 'mileage': request.mileage, 'sale_price': request.sale_price}
        prediction = {'predicted_price': pred.predicted_price}
        timing_data = {'final_score': timing['timing_score'], 'decision': timing['decision']}

        groq = {}
        try:
            groq['signal'] = groq_service.generate_signal_report(vehicle, prediction, timing_data)
        except: pass
        try:
            if request.dealer_description:
                groq['fraud_check'] = groq_service.detect_fraud(request.dealer_description, None)
        except: pass
        try:
            groq['negotiation'] = groq_service.generate_negotiation_script(vehicle, prediction, [])
        except: pass

    # 분석 이력 저장 (admin dashboard 통계용)
    admin_service.record_request(request.model)

    # 사용자별 검색 이력 저장
    history_service.add_history(user_id, {
        'brand': request.brand,
        'model': request.model,
        'year': request.year,
        'mileage': request.mileage,
        'fuel': request.fuel,
        'predicted_price': float(pred.predicted_price),
    })

    # 영구 DB에 분석 결과 저장 (통계용)
    signal_value = None
    if groq and isinstance(groq, dict) and groq.get('signal'):
        signal_data = groq.get('signal')
        if isinstance(signal_data, dict):
            signal_value = signal_data.get('signal')

    db_service.save_analysis({
        'user_id': user_id,
        'brand': request.brand,
        'model': request.model,
        'year': request.year,
        'mileage': request.mileage,
        'fuel_type': request.fuel,
        'predicted_price': float(pred.predicted_price),
        'confidence': float(pred.confidence),
        'timing_score': timing.get('timing_score') if timing else None,
        'signal': signal_value,
        'detail_url': request.detail_url,
        'request': request.model_dump(),
        'response': {
            'prediction': {'predicted_price': float(pred.predicted_price)},
            'timing': timing,
        }
    })

    return {
        "prediction": {
            "predicted_price": float(pred.predicted_price),
            "price_range": [float(pred.price_range[0]), float(pred.price_range[1])],
            "confidence": float(pred.confidence)
        },
        "timing": timing,
        "groq_analysis": groq
    }

@app.post("/api/similar")
async def similar(request: SimilarRequest):
    return similar_service.get_similar_distribution(
        brand=request.brand,
        model=request.model,
        year=request.year,
        mileage=request.mileage,
        predicted_price=request.predicted_price
    )

@app.get("/api/popular")
async def popular(category: str = "all", limit: int = 5):
    """엔카 데이터 기반 인기 모델"""
    return {"models": recommendation_service.get_popular_models(category, limit)}

@app.get("/api/trending")
async def trending(days: int = 7, limit: int = 10):
    """최근 N일간 인기 검색 모델"""
    return {"trending": recommendation_service.get_trending_models(days, limit)}

@app.get("/api/recommendations")
async def recommendations(user_id: str = "guest", category: str = "all",
                          budget_min: int = None, budget_max: int = None, limit: int = 10):
    """예측 가격 기반 추천 차량"""
    return {
        "recommendations": recommendation_service.get_recommended_vehicles(
            user_id=user_id, category=category,
            budget_min=budget_min, budget_max=budget_max, limit=limit
        )
    }

@app.get("/api/good-deals")
async def good_deals(category: str = "all", limit: int = 10):
    """가성비 좋은 차량 (예측가 > 실제가)"""
    return {"deals": recommendation_service.get_good_deals(category, limit)}

@app.get("/api/model-deals")
async def model_deals(brand: str, model: str, limit: int = 10):
    """특정 모델의 가성비 좋은 매물"""
    deals = recommendation_service.get_model_deals(brand, model, limit)
    return {"brand": brand, "model": model, "deals": deals}

@app.post("/api/analyze-deal")
async def analyze_deal(request: Request):
    """
    개별 매물 상세 분석 (자동 AI 분석 포함)
    - 가격 적정성
    - 허위매물 위험도 (자동 분석 + DB 저장)
    - 시그널 분석 (자동 분석 + DB 저장)
    - 네고 포인트
    """
    data = await request.json()

    brand = data.get('brand', '')
    model = data.get('model', '')
    year = int(data.get('year', 2020))
    mileage = int(data.get('mileage', 50000))
    actual_price = int(data.get('actual_price', 0))
    predicted_price = int(data.get('predicted_price', 0))
    fuel = data.get('fuel', '가솔린')
    dealer_description = data.get('dealer_description', '')
    car_id = data.get('car_id', '')

    # 예측가가 없으면 직접 예측
    confidence = 0
    if predicted_price == 0:
        try:
            result = prediction_service.predict(brand, model, year, mileage, fuel=fuel)
            predicted_price = result.predicted_price
            confidence = result.confidence
        except:
            predicted_price = actual_price  # 예측 실패 시 실제가 사용

    analysis = recommendation_service.analyze_deal(
        brand=brand,
        model=model,
        year=year,
        mileage=mileage,
        actual_price=actual_price,
        predicted_price=predicted_price,
        fuel=fuel
    )

    # 시그널 분석 (자동 실행)
    signal_result = None
    if groq_service.is_available():
        try:
            signal_result = groq_service.analyze_signal(
                brand=brand,
                model=model,
                year=year,
                mileage=mileage,
                predicted_price=predicted_price,
                actual_price=actual_price
            )
        except:
            pass

    # 시그널 분석 결과 DB 저장
    if signal_result:
        db_service.save_ai_log("signal", {
            "user_id": "guest",
            "car_info": f"{brand} {model} {year}년",
            "car_id": car_id,
            "request": {
                "brand": brand,
                "model": model,
                "year": year,
                "mileage": mileage,
                "predicted_price": predicted_price,
                "actual_price": actual_price,
            },
            "response": signal_result,
            "success": True,
            "ai_model": "Llama 3.3 70B"
        })

    # 허위매물 탐지 (자동 실행)
    fraud_result = None
    if groq_service.is_available() and dealer_description:
        try:
            fraud_result = groq_service.detect_fraud(
                brand=brand,
                model=model,
                year=year,
                mileage=mileage,
                price=actual_price,
                description=dealer_description
            )
        except:
            pass

    # 허위매물 탐지 결과 DB 저장
    if fraud_result:
        db_service.save_ai_log("fraud_detection", {
            "user_id": "guest",
            "car_info": f"{brand} {model} {year}년",
            "car_id": car_id,
            "request": {
                "brand": brand,
                "model": model,
                "year": year,
                "mileage": mileage,
                "price": actual_price,
                "description": dealer_description[:100] if dealer_description else "",
            },
            "response": fraud_result,
            "success": True,
            "ai_model": "Llama 3.3 70B"
        })

    return {
        "brand": brand,
        "model": model,
        "year": year,
        "mileage": mileage,
        "fuel": fuel,
        "signal_analysis": signal_result,
        "fraud_detection": fraud_result,
        **analysis
    }

@app.get("/api/brands")
async def brands():
    return {"brands": ["현대", "기아", "제네시스", "쉐보레", "르노코리아", "KG모빌리티", "벤츠", "BMW", "아우디", "폭스바겐", "볼보", "렉서스", "포르쉐", "테슬라"]}

@app.get("/api/models/{brand}")
async def models(brand: str):
    brand_models = {
        "현대": ["그랜저", "쏘나타", "아반떼", "투싼", "싼타페", "팰리세이드", "코나", "아이오닉5"],
        "기아": ["K5", "K8", "쏘렌토", "카니발", "스포티지", "니로", "EV6", "모닝"],
        "벤츠": ["E-클래스", "C-클래스", "S-클래스", "GLC", "GLE", "A-클래스"],
        "BMW": ["3시리즈", "5시리즈", "7시리즈", "X3", "X5", "X7"],
    }
    return {"brand": brand, "models": brand_models.get(brand, [])}

@app.get("/api/history")
async def history(user_id: str = "guest", limit: int = 10):
    """사용자 검색 이력 (DB 저장)"""
    return {"history": recommendation_service.get_search_history(user_id, limit)}

@app.get("/api/favorites")
async def favorites(user_id: str = "guest"):
    """사용자 즐겨찾기 목록 (DB 기반)"""
    return {"favorites": recommendation_service.get_favorites(user_id)}

@app.post("/api/favorites")
async def add_favorite(request: FavoriteRequest, user_id: str = "guest"):
    """즐겨찾기 추가 (DB 기반)"""
    result = recommendation_service.add_favorite(user_id, {
        'brand': request.brand,
        'model': request.model,
        'year': request.year,
        'mileage': request.mileage,
        'predicted_price': request.predicted_price,
        'actual_price': request.actual_price,
        'detail_url': request.detail_url,
        'car_id': request.car_id,  # 엔카 차량 고유 ID
    })
    return result

@app.delete("/api/favorites/{favorite_id}")
async def remove_favorite(favorite_id: int, user_id: str = "guest"):
    """즐겨찾기 삭제"""
    success = recommendation_service.remove_favorite(user_id, favorite_id)
    return {"success": success}

@app.post("/api/history")
async def add_history(request: SimilarRequest, user_id: str = "guest"):
    """검색 이력 저장"""
    result = recommendation_service.add_search_history(user_id, {
        'brand': request.brand,
        'model': request.model,
        'year': request.year,
        'mileage': request.mileage,
        'predicted_price': request.predicted_price
    })
    return {"success": True, "history": result}

@app.delete("/api/history/{history_id}")
async def remove_history(history_id: int, user_id: str = "guest"):
    """검색 이력 삭제"""
    success = recommendation_service.remove_search_history(user_id, history_id)
    return {"success": success}

@app.delete("/api/history")
async def clear_history(user_id: str = "guest"):
    """검색 이력 전체 삭제"""
    deleted_count = recommendation_service.clear_search_history(user_id)
    return {"success": True, "deleted_count": deleted_count}

# ========== 가격 알림 API ==========

class AlertRequest(BaseModel):
    brand: str
    model: str
    year: int
    target_price: float

@app.get("/api/alerts")
async def get_alerts(user_id: str = "guest"):
    """가격 알림 목록"""
    return {"alerts": recommendation_service.get_alerts(user_id)}

@app.post("/api/alerts")
async def add_alert(request: AlertRequest, user_id: str = "guest"):
    """가격 알림 추가"""
    result = recommendation_service.add_price_alert(user_id, request.model_dump())
    return result

@app.put("/api/alerts/{alert_id}/toggle")
async def toggle_alert(alert_id: int, user_id: str = "guest"):
    """알림 활성화/비활성화"""
    result = recommendation_service.toggle_alert(user_id, alert_id)
    return result

@app.delete("/api/alerts/{alert_id}")
async def remove_alert(alert_id: int, user_id: str = "guest"):
    """알림 삭제"""
    success = recommendation_service.remove_alert(user_id, alert_id)
    return {"success": success}

# ========== 네고 대본 생성 API (Groq AI) ==========

class NegotiationRequest(BaseModel):
    car_name: str
    price: str  # 실제 판매가 (문자열)
    info: str
    checkpoints: List[str] = []
    # 고도화: 정확한 가격 정보
    actual_price: Optional[int] = None  # 실제 판매가 (숫자)
    predicted_price: Optional[int] = None  # AI 예측가 (숫자)
    year: Optional[int] = None  # 연식
    mileage: Optional[int] = None  # 주행거리

@app.post("/api/negotiation/generate")
async def generate_negotiation(request: NegotiationRequest):
    """Groq AI로 네고 대본 생성 (고도화)"""
    try:
        # 가격 결정: 새 필드 우선, 없으면 기존 방식
        if request.actual_price is not None:
            sale_price = request.actual_price
        else:
            sale_price = int(''.join(filter(str.isdigit, request.price)) or 0)
        
        # 예측가 결정: 새 필드 우선, 없으면 판매가 기준 추정
        if request.predicted_price is not None:
            predicted_price = request.predicted_price
        else:
            # 예측가가 없으면 판매가의 105%로 추정 (협상 여지)
            predicted_price = int(sale_price * 1.05)
        
        # car_name 파싱 (브랜드와 모델 분리)
        car_name = request.car_name or '차량'
        parts = car_name.split(' ', 1)
        brand = parts[0] if parts else '알 수 없음'
        model_part = parts[1] if len(parts) > 1 else car_name
        
        # 연식 추출 (car_name에서 또는 별도 필드)
        year = request.year
        if not year and '년' in model_part:
            # "쏘나타 2023년식" → year=2023
            import re
            year_match = re.search(r'(\d{4})년', model_part)
            if year_match:
                year = int(year_match.group(1))
                model_part = model_part.replace(year_match.group(0), '').strip()
        
        vehicle_data = {
            'brand': brand,
            'model': model_part,
            'year': year,
            'mileage': request.mileage or 0,
            'sale_price': sale_price,
            'info': request.info
        }
        
        prediction_data = {
            'predicted_price': predicted_price
        }
        
        # Groq 서비스 호출
        result = groq_service.generate_negotiation_script(
            vehicle_data=vehicle_data,
            prediction_data=prediction_data,
            issues=request.checkpoints,
            style='balanced'
        )
        
        # 프론트엔드 형식에 맞게 변환
        phone_script = result.get('phone_script', [])
        if isinstance(phone_script, str):
            phone_script = [phone_script]
        
        # 전화 대본 형식화 (리스트면 그대로, 아니면 단계별로)
        if phone_script and len(phone_script) >= 3:
            phone_scripts = [
                f"1️⃣ 인사: {phone_script[0]}",
                f"2️⃣ 시세 언급: {phone_script[1]}",
                f"3️⃣ 가격 제안: {phone_script[2]}",
            ]
            if len(phone_script) > 3:
                phone_scripts.append(f"4️⃣ 마무리: {phone_script[3]}")
        else:
            phone_scripts = [
                f"1️⃣ 인사: 안녕하세요, {request.car_name} 매물 보고 연락드렸습니다.",
                f"2️⃣ 시세 언급: 비슷한 매물들 비교해봤는데요.",
                f"3️⃣ 가격 제안: {result.get('target_price', sale_price):,}만원 정도에 가능하시면 바로 보러가겠습니다.",
                "4️⃣ 마무리: 연락 기다리겠습니다. 감사합니다."
            ]
        
        response = {
            'message_script': result.get('message_script', ''),
            'phone_script': phone_scripts,
            'tip': result.get('tips', ['자신감 있게, 하지만 정중하게 협상하세요'])[0] if result.get('tips') else '자신감 있게 협상하세요',
            'checkpoints': request.checkpoints,
            'target_price': result.get('target_price', sale_price),
            'key_arguments': result.get('key_arguments', []),
            'price_situation': result.get('price_situation', 'fair'),
            'actual_price': sale_price,
            'predicted_price': predicted_price
        }

        # AI 로그 기록 (메모리 + DB 영구 저장)
        log_data = {
            "user_id": "guest",
            "car_info": f"{brand} {model_part} {year or ''}년",
            "request": {
                "brand": brand,
                "model": model_part,
                "year": year,
                "predicted_price": predicted_price,
                "sale_price": sale_price,
            },
            "response": {
                "success": True,
                "script": response.get('message_script'),
                "target_price": response.get('target_price'),
            },
            "success": True,
            "ai_model": "Llama 3.3 70B" if groq_service.is_available() else "Fallback"
        }

        # 메모리 저장 (하위호환)
        history_service.add_ai_log(
            log_type="negotiation",
            user_id="guest",
            request_data=log_data["request"],
            response_data=log_data["response"],
            ai_model=log_data["ai_model"]
        )

        # DB 영구 저장
        db_service.save_ai_log("negotiation", log_data)

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"네고 대본 생성 실패: {str(e)}")

# ========== AI 상태 확인 ==========

@app.get("/api/ai/status")
async def get_ai_status():
    """AI 엔진 상태 확인 (Groq API 연결 여부)"""
    return {
        'groq_available': groq_service.is_available(),
        'model': 'Llama 3.3 70B' if groq_service.is_available() else None,
        'status': 'connected' if groq_service.is_available() else 'disconnected'
    }


# ========== 관리자 대시보드 API ==========

@app.get("/api/admin/dashboard-stats", tags=["Admin"])
async def get_dashboard_stats():
    """대시보드 통계 (오늘 조회수, 전체 조회수, 인기 모델) - DB 기반"""
    # DB에서 실제 데이터 조회
    db_stats = db_service.get_dashboard_stats()

    # DB에 데이터가 없으면 admin_service fallback
    if db_stats.get('totalCount', 0) == 0:
        return admin_service.get_dashboard_stats()

    return db_stats


@app.get("/api/admin/daily-requests", tags=["Admin"])
async def get_daily_requests(days: int = 7):
    """일별 요청 통계 - DB 기반"""
    # DB에서 실제 데이터 조회
    db_data = db_service.get_daily_requests(days)

    # DB에 데이터가 없으면 admin_service fallback
    if not db_data.get('data') or all(d['count'] == 0 for d in db_data['data']):
        return admin_service.get_daily_requests(days)

    return db_data


@app.get("/api/admin/vehicle-stats", tags=["Admin"])
async def get_vehicle_stats():
    """차량 데이터 통계 (국산/수입 대수)"""
    return admin_service.get_vehicle_stats()


@app.get("/api/admin/vehicles", tags=["Admin"])
async def get_vehicles(
    brand: str = None,
    model: str = None,
    category: str = "all",
    limit: int = 50
):
    """차량 목록 조회"""
    return admin_service.get_vehicles(brand, model, category, limit)


@app.get("/api/admin/history", tags=["Admin"])
async def get_admin_history(limit: int = 50):
    """분석 이력 목록"""
    return admin_service.get_history_list(limit)


@app.get("/api/admin/vehicle/{car_id}", tags=["Admin"])
async def get_vehicle_detail(car_id: int, category: str = "domestic"):
    """차량 상세정보 (옵션, 사고이력 포함)"""
    return admin_service.get_vehicle_detail(car_id, category)


@app.get("/api/admin/ai-logs", tags=["Admin"])
async def get_ai_logs(log_type: str = None, limit: int = 50):
    """AI 분석 로그 조회 (네고 대본 생성 기록 등) - DB 기반"""
    # DB에서 조회 우선
    db_logs = db_service.get_ai_logs(log_type, limit)
    db_stats = db_service.get_ai_stats()

    # DB에 데이터가 없으면 메모리 fallback
    if not db_logs:
        logs = history_service.get_ai_logs(log_type, limit)
        stats = history_service.get_ai_stats()
        return {
            "success": True,
            "logs": logs,
            "stats": stats,
            "total": len(logs)
        }

    return {
        "success": True,
        "logs": db_logs,
        "stats": db_stats,
        "total": len(db_logs)
    }


@app.get("/api/admin/analysis-history", tags=["Admin"])
async def get_analysis_history(user_id: str = None, limit: int = 50):
    """분석 이력 조회 (예측 결과 포함) - DB 기반"""
    history = db_service.get_analysis_history(user_id, limit)
    return {
        "success": True,
        "history": history,
        "total": len(history)
    }


# 차량 이미지 API
@app.get("/api/car-image", tags=["Utils"])
async def get_car_image(brand: str, model: str):
    """차량 모델별 이미지 URL 반환"""
    return CarImageService.get_image_with_fallback(brand, model)


if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Car-Sentix API 서버 시작...")
    print("📍 http://localhost:8000")
    print("📖 API 문서: http://localhost:8000/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)

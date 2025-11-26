"""
ML 서비스 실행 스크립트
"""
import sys
import os

# ml-service 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ml-service'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict

# 서비스 임포트
from services.prediction_v12 import PredictionServiceV12  # V12 (FuelType 포함)
from services.timing import TimingService
from services.groq_service import GroqService
from services.recommendation_service import get_recommendation_service  # 신규: 추천 서비스
from services.similar_service import get_similar_service

app = FastAPI(
    title="Car-Sentix API",
    description="중고차 가격 예측 및 AI 분석 API",
    version="2.0.0"
)

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
    # AI 분석용
    sale_price: Optional[int] = None
    dealer_description: Optional[str] = None

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

# ========== API ==========

@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "2.0.0", "message": "Car-Sentix API 정상 작동"}

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
async def smart_analysis(request: SmartAnalysisRequest):
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
    
    # 디버그: 옵션 로그 출력
    print(f"📊 [smart-analysis] model={request.model}, fuel={request.fuel}, options={options}")
    
    # 가격 예측 (옵션 + 연료 포함)
    pred = prediction_service.predict(
        brand=request.brand,
        model_name=request.model,
        year=request.year,
        mileage=request.mileage,
        options=options,
        accident_free=request.is_accident_free or True,
        fuel=request.fuel  # 연료 타입 전달
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
        'predicted_price': request.predicted_price
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
    result = recommendation_service.add_price_alert(user_id, request.dict())
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

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Car-Sentix API 서버 시작...")
    print("📍 http://localhost:8001")
    print("📖 API 문서: http://localhost:8001/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=8001)

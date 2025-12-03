"""
ML 서비스 실행 스크립트
"""
import sys
import os
import logging
import time
from datetime import datetime
from functools import lru_cache
from dotenv import load_dotenv

# .env 파일 로드 (API 키 등)
load_dotenv()

# ml-service 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ml-service'))

# 로깅 설정
from utils.logger import get_logger
logger = get_logger('server')

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal, Dict, Any
from urllib.parse import unquote
from io import BytesIO

# 이미지 압축용 (선택적)
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL not available - images will be served without compression")

# ========== 간단한 TTL 캐시 ==========
class SimpleCache:
    """TTL 기반 간단한 캐시"""
    def __init__(self, ttl_seconds: int = 60):
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._ttl = ttl_seconds
    
    def get(self, key: str) -> Any:
        if key in self._cache:
            if time.time() - self._timestamps[key] < self._ttl:
                return self._cache[key]
            else:
                del self._cache[key]
                del self._timestamps[key]
        return None
    
    def set(self, key: str, value: Any):
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def clear(self):
        self._cache.clear()
        self._timestamps.clear()

# 차량 목록 캐시 (60초 TTL)
vehicle_cache = SimpleCache(ttl_seconds=60)
# 대시보드 통계 캐시 (30초 TTL)
stats_cache = SimpleCache(ttl_seconds=30)

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
CAR_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "차량 이미지", "차량 이미지")  # 국산차
CAR_IMAGES_IMPORTED_DIR = os.path.join(os.path.dirname(__file__), "차량 이미지", "외제차 이미지")  # 외제차

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

logger.info("All services initialized successfully")

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
    """통합 분석 요청 스키마 (검증 포함)"""
    brand: str = Field(..., min_length=1, description="제조사")
    model: str = Field(..., min_length=1, description="모델명")
    year: int = Field(..., ge=1990, le=2026, description="연식")
    mileage: int = Field(..., ge=0, le=1000000, description="주행거리(km)")
    fuel: Literal["가솔린", "디젤", "LPG", "하이브리드", "전기", "가솔린+전기", "디젤+전기"] = "가솔린"
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
    # 성능점검 등급
    inspection_grade: Literal["normal", "good", "excellent"] = "normal"
    # AI 분석용
    sale_price: Optional[int] = Field(None, ge=0, le=500000000, description="판매가(만원)")
    dealer_description: Optional[str] = None
    # 차량 상세 URL
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
    """기본 헬스체크"""
    return {"status": "healthy", "version": "2.0.0", "message": "Car-Sentix API"}

@app.get("/api/health/detailed")
async def health_detailed():
    """상세 헬스체크 - 모든 서비스 상태 확인"""
    import time
    start = time.time()
    
    services = {
        "prediction": {"status": "unknown", "message": ""},
        "timing": {"status": "unknown", "message": ""},
        "groq_ai": {"status": "unknown", "message": ""},
        "database": {"status": "unknown", "message": ""},
        "recommendation": {"status": "unknown", "message": ""},
    }
    
    # 예측 서비스 체크
    try:
        prediction_service.predict("현대", "그랜저", 2023, 50000)
        services["prediction"] = {"status": "healthy", "message": "OK"}
    except Exception as e:
        services["prediction"] = {"status": "unhealthy", "message": str(e)[:50]}
    
    # 타이밍 서비스 체크
    try:
        timing_service.analyze_timing("그랜저")
        services["timing"] = {"status": "healthy", "message": "OK"}
    except Exception as e:
        services["timing"] = {"status": "unhealthy", "message": str(e)[:50]}
    
    # Groq AI 체크
    services["groq_ai"] = {
        "status": "healthy" if groq_service.is_available() else "unavailable",
        "message": "Connected" if groq_service.is_available() else "API key missing"
    }
    
    # DB 체크
    try:
        db_service.get_dashboard_stats()
        services["database"] = {"status": "healthy", "message": "OK"}
    except Exception as e:
        services["database"] = {"status": "unhealthy", "message": str(e)[:50]}
    
    # 추천 서비스 체크
    try:
        recommendation_service.get_popular_models("domestic", 1)
        services["recommendation"] = {"status": "healthy", "message": "OK"}
    except Exception as e:
        services["recommendation"] = {"status": "unhealthy", "message": str(e)[:50]}
    
    # 전체 상태 결정
    all_healthy = all(s["status"] == "healthy" for s in services.values() if s["status"] != "unavailable")
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "version": "2.0.0",
        "response_time_ms": round((time.time() - start) * 1000, 2),
        "services": services
    }

# ========== 차량 이미지 API ==========

# 이미지 캐시 (압축된 이미지 저장)
_image_cache: Dict[str, bytes] = {}

def compress_image(file_path: str, max_size: int = 400, quality: int = 85) -> bytes:
    """이미지를 압축하여 반환 (5MB → ~50KB)"""
    cache_key = f"{file_path}:{max_size}:{quality}"
    
    # 캐시 확인
    if cache_key in _image_cache:
        return _image_cache[cache_key]
    
    if PIL_AVAILABLE:
        try:
            with Image.open(file_path) as img:
                # RGBA to RGB (PNG → JPEG 변환 시 필요)
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 크기 조절
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # JPEG로 압축
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=quality, optimize=True)
                compressed = buffer.getvalue()
                
                # 캐시 저장 (최대 100개)
                if len(_image_cache) < 100:
                    _image_cache[cache_key] = compressed
                
                logger.info(f"Image compressed: {file_path} -> {len(compressed)/1024:.1f}KB")
                return compressed
        except Exception as e:
            logger.error(f"Image compression failed: {e}")
    
    # PIL 없거나 실패시 원본 반환
    with open(file_path, "rb") as f:
        return f.read()

@app.get("/car-images/{filename:path}")
async def get_car_image(filename: str, size: int = 400, quality: int = 85):
    """
    차량 이미지 제공 (압축 지원) - 국산차 + 외제차
    - size: 최대 크기 (기본 400px)
    - quality: JPEG 품질 (기본 85)
    """
    # URL 디코딩 (한글 파일명 지원)
    decoded_filename = unquote(filename)
    
    # 확장자 제거 (나중에 여러 확장자 시도)
    base_name = decoded_filename
    if decoded_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        base_name = os.path.splitext(decoded_filename)[0]
    
    # 검색할 폴더와 확장자 조합
    search_dirs = [CAR_IMAGES_DIR, CAR_IMAGES_IMPORTED_DIR]
    extensions = ['.png', '.jpg', '.jpeg']
    
    file_path = None
    for search_dir in search_dirs:
        for ext in extensions:
            candidate = os.path.join(search_dir, base_name + ext)
            if os.path.exists(candidate):
                file_path = candidate
                break
        if file_path:
            break

    if file_path:
        # 이미지 압축 후 반환
        image_data = compress_image(file_path, max_size=size, quality=quality)
        
        # JPEG로 변환됨
        media_type = "image/jpeg" if PIL_AVAILABLE else "image/png"
        
        return Response(
            content=image_data,
            media_type=media_type,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Cache-Control": "public, max-age=604800",  # 7일 캐시
                "Content-Length": str(len(image_data)),
            }
        )

    # 파일이 없으면 404 (로그 추가)
    logger.warning(f"Image not found: {base_name} (searched in domestic & imported)")
    raise HTTPException(status_code=404, detail=f"이미지를 찾을 수 없습니다: {base_name}")

@app.get("/api/car-images/list")
async def list_car_images():
    """사용 가능한 차량 이미지 목록 (국산차 + 외제차)"""
    images = []
    
    # 국산차 이미지
    if os.path.exists(CAR_IMAGES_DIR):
        for f in os.listdir(CAR_IMAGES_DIR):
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                images.append({"name": os.path.splitext(f)[0], "category": "domestic"})
    
    # 외제차 이미지
    if os.path.exists(CAR_IMAGES_IMPORTED_DIR):
        for f in os.listdir(CAR_IMAGES_IMPORTED_DIR):
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                images.append({"name": os.path.splitext(f)[0], "category": "imported"})
    
    return {
        "success": True, 
        "images": sorted(images, key=lambda x: x["name"]), 
        "count": len(images),
        "domestic_count": len([i for i in images if i["category"] == "domestic"]),
        "imported_count": len([i for i in images if i["category"] == "imported"])
    }

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

@app.get("/api/market-timing")
async def get_market_timing():
    """
    오늘의 시장 타이밍 요약 (홈화면용)
    차별화 포인트: 경제지표 기반 구매 타이밍 분석
    """
    try:
        # 일반적인 시장 타이밍 분석 (특정 모델 없이)
        result = timing_service.analyze_timing("중고차")  # 일반 시장 분석
        
        # 홈화면 표시용 요약 데이터
        score = result.get('timing_score', 60)
        
        # 점수별 라벨 및 색상
        if score >= 70:
            label = "지금이 적기!"
            color = "green"
            emoji = "🟢"
            action = "적극 매수 추천"
        elif score >= 55:
            label = "괜찮은 시기"
            color = "blue"
            emoji = "🔵"
            action = "매수 고려"
        elif score >= 45:
            label = "보통"
            color = "yellow"
            emoji = "🟡"
            action = "시장 관망"
        else:
            label = "대기 권장"
            color = "red"
            emoji = "🔴"
            action = "구매 보류"
        
        # 경제지표 요약 (차별화 포인트 강조)
        breakdown = result.get('breakdown', {})
        indicators = []
        
        macro_score = breakdown.get('macro', 60)
        if macro_score >= 60:
            indicators.append({"name": "금리", "status": "positive", "desc": "낮은 금리"})
        else:
            indicators.append({"name": "금리", "status": "negative", "desc": "높은 금리"})
            
        trend_score = breakdown.get('trend', 60)
        if trend_score >= 60:
            indicators.append({"name": "유가", "status": "positive", "desc": "안정세"})
        else:
            indicators.append({"name": "유가", "status": "negative", "desc": "상승세"})
            
        schedule_score = breakdown.get('schedule', 60)
        if schedule_score >= 60:
            indicators.append({"name": "신차출시", "status": "neutral", "desc": "영향 적음"})
        else:
            indicators.append({"name": "신차출시", "status": "negative", "desc": "출시 임박"})
        
        return {
            "success": True,
            "score": score,
            "label": label,
            "color": color,
            "emoji": emoji,
            "action": action,
            "indicators": indicators,
            "reasons": result.get('reasons', [])[:3],  # 상위 3개 이유만
            "updated_at": datetime.now().isoformat(),
            "message": f"경제지표 분석 결과, {label.lower()}"
        }
    except Exception as e:
        logger.error(f"시장 타이밍 분석 오류: {e}")
        return {
            "success": True,
            "score": 60,
            "label": "분석 중",
            "color": "gray",
            "emoji": "⏳",
            "action": "데이터 수집 중",
            "indicators": [],
            "reasons": [],
            "updated_at": datetime.now().isoformat(),
            "message": "시장 데이터를 수집하고 있습니다"
        }

@app.post("/api/smart-analysis")
async def smart_analysis(request: SmartAnalysisRequest, user_id: str = "guest"):
    """통합 스마트 분석 (가격 + 타이밍 + AI)"""
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

    grade = request.inspection_grade or "normal"
    accident_free = request.is_accident_free if request.is_accident_free is not None else True
    logger.info(f"smart-analysis: model={request.model}, fuel={request.fuel}, grade={grade}, accident_free={accident_free}")

    pred = prediction_service.predict(
        brand=request.brand,
        model_name=request.model,
        year=request.year,
        mileage=request.mileage,
        options=options,
        accident_free=accident_free,
        grade=grade,  # 성능점검 등급 전달
        fuel=request.fuel
    )

    # 타이밍
    timing = timing_service.analyze_timing(request.model)

    # Groq AI (네고 대본 생성만 사용)
    groq = None
    if groq_service.is_available() and request.sale_price:
        vehicle = {'brand': request.brand, 'model': request.model, 'year': request.year, 'mileage': request.mileage, 'sale_price': request.sale_price}
        prediction = {'predicted_price': pred.predicted_price}

        groq = {}
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
async def analyze_deal(request: Request, user_id: str = "guest"):
    """
    개별 매물 상세 분석 (규칙 기반)
    - 가격 적정성
    - 허위매물 위험도 (규칙 기반)
    - 구매 타이밍 (규칙 기반)
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
    
    # user_id 정규화
    if not user_id or user_id in ['anonymous', 'null', 'undefined']:
        user_id = 'guest'

    # 예측가가 없으면 직접 예측
    if predicted_price == 0:
        try:
            result = prediction_service.predict(brand, model, year, mileage, fuel=fuel)
            predicted_price = int(result.predicted_price)
        except:
            predicted_price = actual_price  # 예측 실패 시 실제가 사용

    # 규칙 기반 분석 (recommendation_service)
    analysis = recommendation_service.analyze_deal(
        brand=brand,
        model=model,
        year=year,
        mileage=mileage,
        actual_price=actual_price,
        predicted_price=predicted_price,
        fuel=fuel
    )
    
    # 타이밍 분석 (규칙 기반 - timing_service)
    timing_result = timing_service.analyze_timing(model)
    
    # 규칙 기반 시그널 생성
    price_gap = actual_price - predicted_price
    price_gap_pct = round((price_gap / predicted_price * 100), 1) if predicted_price > 0 else 0
    
    if price_gap_pct <= -10:
        signal = 'strong_buy'
        signal_summary = f"시세 대비 {abs(price_gap_pct):.1f}% 저렴합니다. 적극 매수 추천!"
    elif price_gap_pct <= -5:
        signal = 'buy'
        signal_summary = f"시세 대비 {abs(price_gap_pct):.1f}% 저렴합니다. 매수 추천."
    elif price_gap_pct <= 5:
        signal = 'hold'
        signal_summary = "시세와 비슷한 적정 가격입니다."
    else:
        signal = 'avoid'
        signal_summary = f"시세 대비 {price_gap_pct:.1f}% 비쌉니다. 협상 필요."
    
    signal_result = {
        'signal': signal,
        'summary': signal_summary,
        'price_gap': price_gap,
        'price_gap_percent': price_gap_pct
    }
    
    # 분석 이력 저장 (대시보드 통계용)
    fraud_risk = analysis.get('fraud_risk', {})
    db_service.save_analysis({
        'user_id': user_id,
        'brand': brand,
        'model': model,
        'year': year,
        'mileage': mileage,
        'fuel_type': fuel,
        'predicted_price': float(predicted_price),
        'confidence': 85.0,
        'timing_score': timing_result.get('timing_score') if timing_result else None,
        'signal': signal,
        'request': {
            'brand': brand, 'model': model, 'year': year, 'mileage': mileage,
            'actual_price': actual_price, 'predicted_price': predicted_price
        },
        'response': {
            'timing': timing_result,
            'signal': signal_result,
            'fraud_risk': fraud_risk
        }
    })
    
    # AI 로그 저장 (규칙 기반)
    db_service.save_ai_log("signal", {
        "user_id": user_id,
        "car_info": f"{brand} {model} {year}년",
        "request": {
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": mileage,
            "predicted_price": predicted_price,
            "sale_price": actual_price,
        },
        "response": {"signal": signal_result, "success": True},
        "success": True,
        "ai_model": "Rule-based"
    })
    
    db_service.save_ai_log("fraud_detection", {
        "user_id": user_id,
        "car_info": f"{brand} {model} {year}년",
        "request": {
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": mileage,
            "predicted_price": predicted_price,
            "sale_price": actual_price,
        },
        "response": {
            "fraud_check": {
                "risk_level": fraud_risk.get('level', 'low'),
                "risk_score": fraud_risk.get('score', 0),
                "warnings": [f.get('msg', '') for f in fraud_risk.get('factors', []) if f.get('status') in ['warn', 'fail']],
                "summary": f"규칙 기반 분석: 위험도 {fraud_risk.get('score', 0)}점"
            },
            "success": True
        },
        "success": True,
        "ai_model": "Rule-based"
    })

    return {
        "brand": brand,
        "model": model,
        "year": year,
        "mileage": mileage,
        "fuel": fuel,
        "timing": timing_result,
        "signal_analysis": signal_result,
        **analysis  # price_fairness, fraud_risk, nego_points, summary
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

        # AI 로그 기록 (메모리 + DB 영구 저장) - 주행거리 포함
        mileage = request.mileage or 0
        log_data = {
            "user_id": "guest",
            "car_info": f"{brand} {model_part} {year or ''}년식",
            "request": {
                "brand": brand,
                "model": model_part,
                "year": year,
                "mileage": mileage,
                "predicted_price": predicted_price,
                "sale_price": sale_price,
            },
            "response": {
                "success": True,
                "negotiation": {
                    "script": response.get('message_script'),
                    "phone_scripts": response.get('phone_script', []),
                    "target_price": response.get('target_price'),
                    "key_arguments": response.get('key_arguments', []),
                    "tip": response.get('tip'),
                },
                "scripts": [
                    {"situation": "문자 발송", "script": response.get('message_script', '')},
                    *[{"situation": ps.split(': ')[0] if ': ' in ps else f"단계 {i+1}", "script": ps.split(': ')[1] if ': ' in ps else ps} 
                      for i, ps in enumerate(response.get('phone_script', []))]
                ]
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
        'model': GROQ_MODEL if groq_service.is_available() else None,
        'status': 'connected' if groq_service.is_available() else 'disconnected'
    }

# ========== 관리자 대시보드 API ==========

try:
    from config.server_config import SPRING_BOOT_URL, DEFAULT_USERS, ADMIN_ACCOUNTS
except ImportError:
    SPRING_BOOT_URL = "http://localhost:8080"
    DEFAULT_USERS = []
    ADMIN_ACCOUNTS = {}

@app.get("/api/admin/users", tags=["Admin"])
async def get_admin_users(page: int = 1, limit: int = 20):
    """사용자 목록 조회 (페이지네이션 지원)"""
    import httpx
    import math
    
    users = []
    spring_boot_available = False
    
    # 1. Spring Boot User Service에서 실제 가입 사용자 조회 시도
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{SPRING_BOOT_URL}/api/admin/users-public")
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('users'):
                    users = data['users']
                    spring_boot_available = True
                    logger.info(f"Spring Boot에서 {len(users)}명의 사용자 로드됨")
    except Exception as e:
        logger.warning(f"Spring Boot 사용자 조회 실패: {e}")
    
    # 2. Spring Boot 실패 시 기본 사용자 목록 (설정 파일에서 로드)
    if not spring_boot_available:
        users = DEFAULT_USERS if DEFAULT_USERS else [
            {"id": 1, "email": "admin@car-sentix.com", "username": "관리자", "role": "ADMIN", "isActive": True},
        ]
    
    # 3. 분석 이력 및 AI 로그에서 사용자 ID 수집하여 병합
    analysis_users = {}
    try:
        history = db_service.get_analysis_history(limit=1000)
        for h in history:
            uid = h.get('user_id', 'anonymous')
            if uid and uid not in ['anonymous', 'guest', '']:
                if uid not in analysis_users:
                    analysis_users[uid] = 0
                analysis_users[uid] += 1
        
        ai_logs = db_service.get_ai_logs(limit=1000)
        for log in ai_logs:
            uid = log.get('user_id', 'anonymous')
            if uid and uid not in ['anonymous', 'guest', '']:
                if uid not in analysis_users:
                    analysis_users[uid] = 0
                analysis_users[uid] += 1
                
        views = db_service.get_vehicle_views(limit=1000)
        for v in views:
            uid = v.get('user_id', 'anonymous')
            if uid and uid not in ['anonymous', 'guest', '']:
                if uid not in analysis_users:
                    analysis_users[uid] = 0
                analysis_users[uid] += 1
    except Exception as e:
        logger.warning(f"사용자 이력 수집 실패: {e}")
    
    # 4. 기존 사용자 목록에 없는 분석 이력 사용자 추가
    existing_emails = {u.get('email', '') for u in users}
    next_id = max([u.get('id', 0) for u in users] or [0]) + 1
    
    for uid, count in analysis_users.items():
        if uid not in existing_emails:
            users.append({
                "id": next_id,
                "email": uid,
                "username": uid.split('@')[0] if '@' in uid else uid,
                "phoneNumber": "-",
                "role": "USER",
                "provider": "LOCAL",
                "isActive": True,
                "analysisCount": count
            })
            next_id += 1
    
    # 5. 각 사용자의 분석 횟수 계산
    for user in users:
        email = user.get('email', '')
        user['analysisCount'] = analysis_users.get(email, 0)
    
    # 6. 페이지네이션 적용
    total_count = len(users)
    total_pages = math.ceil(total_count / limit) if total_count > 0 else 1
    offset = (page - 1) * limit
    paginated_users = users[offset:offset + limit]
    
    return {
        "success": True,
        "users": paginated_users,
        "total": total_count,
        "page": page,
        "totalPages": total_pages,
        "limit": limit,
        "source": "spring_boot" if spring_boot_available else "local"
    }

@app.put("/api/admin/users/{user_id}", tags=["Admin"])
async def update_admin_user(user_id: int, request: Request):
    """사용자 정보 수정 (관리자 전용)"""
    data = await request.json()
    return {"success": True, "message": f"사용자 {user_id} 수정 완료 (목업)"}

@app.delete("/api/admin/users/{user_id}", tags=["Admin"])
async def delete_admin_user(user_id: int):
    """사용자 삭제 (관리자 전용)"""
    return {"success": True, "message": f"사용자 {user_id} 삭제 완료 (목업)"}

@app.put("/api/admin/users/{user_id}/activate", tags=["Admin"])
async def activate_user(user_id: int):
    """사용자 활성화"""
    return {"success": True, "message": f"사용자 {user_id} 활성화 완료"}

@app.put("/api/admin/users/{user_id}/deactivate", tags=["Admin"])
async def deactivate_user(user_id: int):
    """사용자 비활성화"""
    return {"success": True, "message": f"사용자 {user_id} 비활성화 완료"}

@app.get("/api/admin/me", tags=["Admin"])
async def get_admin_me(request: Request):
    """현재 로그인한 관리자 정보 (토큰 검증용)"""
    # Authorization 헤더에서 토큰 추출 (실제 구현 시 JWT 검증 필요)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        # 토큰이 있으면 관리자 정보 반환 (목업)
        return {
            "id": 1,
            "email": "admin@car-sentix.com",
            "username": "관리자",
            "role": "ADMIN",
            "isActive": True
        }
    raise HTTPException(status_code=401, detail="인증이 필요합니다")

class AdminLoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/admin/login", tags=["Admin"])
async def admin_login(request: AdminLoginRequest):
    """관리자 로그인 (설정 파일 연동)"""
    email = request.email.lower().strip()
    password = request.password
    
    # 설정 파일에서 로드된 ADMIN_ACCOUNTS 사용
    if email in ADMIN_ACCOUNTS and ADMIN_ACCOUNTS[email].get("password") == password:
        account = ADMIN_ACCOUNTS[email]
        # 간단한 토큰 생성 (실제 구현 시 JWT 사용)
        import hashlib
        import time
        token = hashlib.sha256(f"{email}:{time.time()}".encode()).hexdigest()
        
        return {
            "success": True,
            "token": token,
            "user": {
                "id": account["id"],
                "email": email,
                "username": account["username"],
                "role": account["role"],
                "isActive": True
            },
            "message": "로그인 성공"
        }
    
    return {
        "success": False,
        "message": "이메일 또는 비밀번호가 올바르지 않습니다"
    }

@app.get("/api/admin/dashboard-stats", tags=["Admin"])
async def get_dashboard_stats():
    """대시보드 통계 (오늘 조회수, 전체 조회수, 인기 모델) - DB 기반"""
    db_stats = db_service.get_dashboard_stats()
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
    page: int = 1,
    limit: int = 20,
    price_min: int = None,
    price_max: int = None
):
    """차량 목록 조회 (페이지네이션, 가격 범위 검색 지원) - 캐시 적용"""
    # 캐시 키 생성
    cache_key = f"vehicles:{brand}:{model}:{category}:{page}:{limit}:{price_min}:{price_max}"
    
    # 캐시 확인
    cached = vehicle_cache.get(cache_key)
    if cached:
        return cached
    
    # 데이터 조회
    result = admin_service.get_vehicles(
        brand=brand, model=model, category=category,
        page=page, limit=limit, price_min=price_min, price_max=price_max
    )
    
    # 캐시 저장
    vehicle_cache.set(cache_key, result)
    return result


@app.get("/api/admin/history", tags=["Admin"])
async def get_admin_history(limit: int = 50):
    """분석 이력 목록"""
    return admin_service.get_history_list(limit)


@app.get("/api/admin/vehicle/{car_id}", tags=["Admin"])
async def get_vehicle_detail(car_id: int, category: str = "domestic"):
    """차량 상세정보 (옵션, 사고이력 포함)"""
    return admin_service.get_vehicle_detail(car_id, category)


@app.get("/api/admin/ai-logs", tags=["Admin"])
async def get_ai_logs(log_type: str = None, page: int = 1, limit: int = 20):
    """AI 분석 로그 조회 (페이지네이션 지원)"""
    import math
    
    # 페이지네이션 계산
    offset = (page - 1) * limit
    
    # 전체 건수 조회
    total_count = db_service.get_total_ai_logs_count(log_type)
    total_pages = math.ceil(total_count / limit) if total_count > 0 else 1
    
    # DB에서 조회
    db_logs = db_service.get_ai_logs(log_type, limit, offset)
    db_stats = db_service.get_ai_stats()

    # DB에 데이터가 없으면 메모리 fallback
    if not db_logs and page == 1:
        logs = history_service.get_ai_logs(log_type, limit)
        stats = history_service.get_ai_stats()
        return {
            "success": True,
            "logs": logs,
            "stats": stats,
            "total": len(logs),
            "page": 1,
            "totalPages": 1,
            "limit": limit
        }

    return {
        "success": True,
        "logs": db_logs,
        "stats": db_stats,
        "total": total_count,
        "page": page,
        "totalPages": total_pages,
        "limit": limit
    }


@app.get("/api/admin/analysis-history", tags=["Admin"])
async def get_analysis_history(user_id: str = None, page: int = 1, limit: int = 20):
    """분석 이력 조회 (페이지네이션 지원)"""
    import math
    
    # 페이지네이션 계산
    offset = (page - 1) * limit
    
    # 전체 건수 조회
    total_count = db_service.get_total_analysis_count(user_id)
    total_pages = math.ceil(total_count / limit) if total_count > 0 else 1
    
    # DB에서 조회
    history = db_service.get_analysis_history(user_id, limit, offset)
    
    return {
        "success": True,
        "history": history,
        "total": total_count,
        "page": page,
        "totalPages": total_pages,
        "limit": limit
    }


# 차량 이미지 API
@app.get("/api/car-image", tags=["Utils"])
async def get_car_image(brand: str, model: str):
    """차량 모델별 이미지 URL 반환"""
    return CarImageService.get_image_with_fallback(brand, model)


# ========== 알림 시스템 API ==========

@app.get("/api/notifications", tags=["Notifications"])
async def get_notifications(user_id: str = "guest", limit: int = 50, unread_only: bool = False):
    """알림 내역 조회"""
    notifications = db_service.get_notifications(user_id, limit, unread_only)
    unread_count = db_service.get_unread_notification_count(user_id)
    return {
        "success": True,
        "notifications": notifications,
        "unread_count": unread_count,
        "total": len(notifications)
    }

@app.post("/api/notifications", tags=["Notifications"])
async def add_notification(request: Request):
    """알림 추가 (허위매물 고위험 등)"""
    data = await request.json()
    notification_id = db_service.add_notification(data)
    return {"success": True, "id": notification_id}

@app.put("/api/notifications/{notification_id}/read", tags=["Notifications"])
async def mark_notification_read(notification_id: int):
    """알림 읽음 처리"""
    success = db_service.mark_notification_read(notification_id)
    return {"success": success}

@app.get("/api/notifications/unread-count", tags=["Notifications"])
async def get_unread_count(user_id: str = "guest"):
    """읽지 않은 알림 개수"""
    count = db_service.get_unread_notification_count(user_id)
    return {"count": count}


# ========== 매물 조회 기록 API (추천탭 등) ==========

@app.post("/api/vehicle-views", tags=["Analytics"])
async def add_vehicle_view(request: Request):
    """개별 매물 조회 기록 (추천탭에서 클릭 시)"""
    data = await request.json()
    view_id = db_service.add_vehicle_view(data)
    
    # 허위매물 고위험인 경우 자동 알림 생성
    risk_level = data.get('risk_level', '')
    risk_score = data.get('risk_score', 0)
    
    if risk_level == 'high' or risk_score >= 70:
        notification_data = {
            "user_id": data.get('user_id', 'guest'),
            "notification_type": "fraud_alert",
            "title": "⚠️ 허위매물 고위험 경고",
            "message": f"{data.get('brand', '')} {data.get('model', '')} 매물이 허위매물 위험도가 높습니다. 주의가 필요합니다.",
            "car_id": data.get('car_id', ''),
            "car_info": {
                "brand": data.get('brand'),
                "model": data.get('model'),
                "year": data.get('year'),
                "price": data.get('price'),
            },
            "risk_level": risk_level,
            "risk_score": risk_score
        }
        db_service.add_notification(notification_data)
    
    return {"success": True, "id": view_id}

@app.get("/api/vehicle-views", tags=["Analytics"])
async def get_vehicle_views(user_id: str = None, limit: int = 50):
    """매물 조회 이력"""
    views = db_service.get_vehicle_views(user_id, limit)
    return {"success": True, "views": views, "total": len(views)}

@app.get("/api/admin/total-views", tags=["Admin"])
async def get_total_views():
    """전체 조회 통계 (시세 예측 + 개별 매물 조회)"""
    stats = db_service.get_total_views_count()
    return {"success": True, **stats}


# ========== 대시보드 통계 확장 (매물 조회 포함) ==========

@app.get("/api/admin/dashboard-stats-extended", tags=["Admin"])
async def get_dashboard_stats_extended():
    """대시보드 통계 확장 (시세 예측 + 매물 조회 포함)"""
    db_stats = db_service.get_dashboard_stats()
    view_stats = db_service.get_total_views_count()
    ai_stats = db_service.get_ai_stats()
    
    return {
        "success": True,
        # 기본 통계 (시세 예측)
        "todayPredictions": db_stats.get('todayCount', 0),
        "totalPredictions": db_stats.get('totalCount', 0),
        # 매물 조회 통계
        "todayViews": view_stats.get('today_views', 0),
        "totalViews": view_stats.get('total_views', 0),
        # 합계
        "todayTotal": view_stats.get('today_total', db_stats.get('todayCount', 0)),
        "totalCount": view_stats.get('total', db_stats.get('totalCount', 0)),
        # 기존 통계
        "avgConfidence": db_stats.get('avgConfidence', 0),
        "popularModels": db_stats.get('popularModels', []),
        # AI 통계
        "aiStats": ai_stats
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("ML_SERVICE_PORT", 8000))
    print(f"\n[Car-Sentix API Server Starting...]")
    print(f"URL: http://localhost:{port}")
    print(f"Docs: http://localhost:{port}/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
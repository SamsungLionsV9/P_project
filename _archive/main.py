"""
FastAPI 백엔드 메인
중고차 가격 예측 및 타이밍 분석 API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os

from .schemas.schemas import (
    PredictRequest, PredictResponse,
    TimingRequest, TimingResponse,
    SmartAnalysisRequest, SmartAnalysisResponse,
    HealthResponse, BrandsResponse, ModelsResponse, FuelTypesResponse
)
from .services.prediction_v11 import PredictionServiceV11
from .services.timing import TimingService
from .services.groq_service import GroqService
from .services.admin_service import get_admin_service
from .services.history_service import get_history_service
from .utils.validators import (
    validate_vehicle_data,
    get_supported_brands,
    get_supported_fuel_types,
    get_models_by_brand
)

# FastAPI 앱 생성
app = FastAPI(
    title="중고차 가격 예측 API",
    description="ML 기반 중고차 가격 예측 및 구매 타이밍 분석 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 초기화
prediction_service = PredictionServiceV11()
timing_service = TimingService()
groq_service = GroqService()
admin_service = get_admin_service()
history_service = get_history_service()


# ========== 헬스체크 ==========

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    API 헬스체크
    
    Returns:
        HealthResponse: 상태 정보
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "중고차 가격 예측 API가 정상 작동 중입니다"
    }


# ========== 가격 예측 ==========

@app.post("/api/predict", response_model=PredictResponse, tags=["Prediction"])
async def predict_price(request: PredictRequest):
    """
    차량 가격 예측
    
    Args:
        request: 차량 정보 (브랜드, 모델, 연식, 주행거리, 연료)
        
    Returns:
        PredictResponse: 예측 가격 및 범위
        
    Example:
        ```
        POST /api/predict
        {
          "brand": "현대",
          "model": "그랜저",
          "year": 2022,
          "mileage": 35000,
          "fuel": "가솔린"
        }
        ```
    """
    # 입력 데이터 검증
    is_valid, messages = validate_vehicle_data(
        request.brand, request.model, request.year, 
        request.mileage, request.fuel
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail={
            "error": "입력 데이터 검증 실패",
            "messages": messages
        })
    
    try:
        # 옵션 정보 수집
        options = {
            'has_sunroof': 1 if request.has_sunroof else 0,
            'has_navigation': 1 if request.has_navigation else 0,
            'has_leather_seat': 1 if request.has_leather_seat else 0,
            'has_smart_key': 1 if request.has_smart_key else 0,
            'has_rear_camera': 1 if request.has_rear_camera else 0,
            'has_led_lamp': 1 if request.has_led_lamp else 0,
            'has_heated_seat': 1 if request.has_heated_seat else 0,
            'has_ventilated_seat': 1 if request.has_ventilated_seat else 0,
        }
        
        # 무사고 여부
        accident_free = request.is_accident_free if request.is_accident_free else True
        
        # 가격 예측 (V11 서비스)
        result = prediction_service.predict(
            brand=request.brand,
            model_name=request.model,
            year=request.year,
            mileage=request.mileage,
            options=options,
            accident_free=accident_free
        )

        # 관리자 통계 기록
        admin_service.record_request(request.model)

        # 분석 이력 기록 (admin-dashboard 연동용)
        history_service.add_history("system", {
            "brand": request.brand,
            "model": request.model,
            "year": request.year,
            "mileage": request.mileage,
            "fuel": request.fuel,
            "predicted_price": result.predicted_price
        })

        return PredictResponse(
            predicted_price=result.predicted_price,
            price_range=list(result.price_range),
            confidence=result.confidence / 100.0  # 0-100 -> 0-1
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": "가격 예측 실패",
            "message": str(e)
        })


# ========== 타이밍 분석 ==========

@app.post("/api/timing", response_model=TimingResponse, tags=["Timing"])
async def analyze_timing(request: TimingRequest):
    """
    구매 타이밍 분석
    
    Args:
        request: 모델명
        
    Returns:
        TimingResponse: 타이밍 점수 및 판단
        
    Example:
        ```
        POST /api/timing
        {
          "model": "그랜저"
        }
        ```
    """
    try:
        # 타이밍 분석
        result = timing_service.analyze_timing(request.model)
        
        return TimingResponse(
            timing_score=result['timing_score'],
            decision=result['decision'],
            color=result['color'],
            breakdown=result['breakdown'],
            reasons=result['reasons']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": "타이밍 분석 실패",
            "message": str(e)
        })


# ========== 통합 스마트 분석 ==========

@app.post("/api/smart-analysis", response_model=SmartAnalysisResponse, tags=["Smart Analysis"])
async def smart_analysis(request: SmartAnalysisRequest):
    """
    통합 스마트 분석 (가격 예측 + 타이밍 + Groq AI)
    
    Args:
        request: 차량 정보 + 판매가 + 딜러 설명글 (선택)
        
    Returns:
        SmartAnalysisResponse: 종합 분석 결과
        
    Example:
        ```
        POST /api/smart-analysis
        {
          "brand": "현대",
          "model": "그랜저",
          "year": 2022,
          "mileage": 35000,
          "fuel": "가솔린",
          "sale_price": 3200,
          "dealer_description": "완벽한 차량입니다."
        }
        ```
    """
    # 입력 데이터 검증
    is_valid, messages = validate_vehicle_data(
        request.brand, request.model, request.year,
        request.mileage, request.fuel
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail={
            "error": "입력 데이터 검증 실패",
            "messages": messages
        })
    
    try:
        # 1. 가격 예측 (V11 서비스)
        prediction_result = prediction_service.predict(
            brand=request.brand,
            model_name=request.model,
            year=request.year,
            mileage=request.mileage
        )
        
        # 2. 타이밍 분석
        timing_result = timing_service.analyze_timing(request.model)
        
        # 3. Groq AI 분석 (선택)
        groq_analysis = None
        if groq_service.is_available() and request.sale_price:
            vehicle_data = {
                'brand': request.brand,
                'model': request.model,
                'year': request.year,
                'mileage': request.mileage,
                'fuel': request.fuel,
                'sale_price': request.sale_price
            }
            
            prediction_data = {
                'predicted_price': prediction_result.predicted_price
            }
            
            timing_data = {
                'final_score': timing_result['timing_score'],
                'decision': timing_result['decision']
            }
            
            groq_analysis = {}
            
            # 신호등 리포트
            try:
                groq_analysis['signal'] = groq_service.generate_signal_report(
                    vehicle_data, prediction_data, timing_data
                )
            except Exception as e:
                print(f"⚠️ Groq 신호 분석 실패: {e}")
            
            # 허위매물 탐지 (설명글이 있는 경우)
            if request.dealer_description:
                try:
                    groq_analysis['fraud_check'] = groq_service.detect_fraud(
                        request.dealer_description,
                        request.performance_record
                    )
                except Exception as e:
                    print(f"⚠️ Groq 허위매물 탐지 실패: {e}")
            
            # 네고 대본 생성
            try:
                issues = []
                if groq_analysis.get('fraud_check', {}).get('is_suspicious'):
                    issues = groq_analysis['fraud_check'].get('warnings', [])
                
                groq_analysis['negotiation'] = groq_service.generate_negotiation_script(
                    vehicle_data, prediction_data, issues
                )
            except Exception as e:
                print(f"⚠️ Groq 네고 대본 생성 실패: {e}")
        
        # 응답 생성
        return SmartAnalysisResponse(
            prediction=PredictResponse(
                predicted_price=prediction_result.predicted_price,
                price_range=list(prediction_result.price_range),
                confidence=prediction_result.confidence / 100.0
            ),
            timing=TimingResponse(
                timing_score=timing_result['timing_score'],
                decision=timing_result['decision'],
                color=timing_result['color'],
                breakdown=timing_result['breakdown'],
                reasons=timing_result['reasons']
            ),
            groq_analysis=groq_analysis
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": "통합 분석 실패",
            "message": str(e)
        })


# ========== 메타데이터 API ==========

@app.get("/api/brands", response_model=BrandsResponse, tags=["Metadata"])
async def get_brands():
    """
    지원하는 브랜드 목록
    
    Returns:
        BrandsResponse: 브랜드 목록
    """
    return {
        "brands": get_supported_brands()
    }


@app.get("/api/models/{brand}", response_model=ModelsResponse, tags=["Metadata"])
async def get_models(brand: str):
    """
    브랜드별 모델 목록
    
    Args:
        brand: 브랜드명
        
    Returns:
        ModelsResponse: 모델 목록
    """
    models = get_models_by_brand(brand)
    
    if not models:
        return {
            "brand": brand,
            "models": []
        }
    
    return {
        "brand": brand,
        "models": models
    }


@app.get("/api/fuel-types", response_model=FuelTypesResponse, tags=["Metadata"])
async def get_fuel_types():
    """
    지원하는 연료 타입 목록
    
    Returns:
        FuelTypesResponse: 연료 타입 목록
    """
    return {
        "fuel_types": get_supported_fuel_types()
    }


# ========== 관리자 API ==========

@app.get("/api/admin/dashboard-stats", tags=["Admin"])
async def get_dashboard_stats():
    """
    대시보드 통계 (오늘 조회수, 전체 조회수, 인기 모델)
    """
    return admin_service.get_dashboard_stats()


@app.get("/api/admin/daily-requests", tags=["Admin"])
async def get_daily_requests(days: int = 7):
    """
    일별 요청 통계
    """
    return admin_service.get_daily_requests(days)


@app.get("/api/admin/vehicle-stats", tags=["Admin"])
async def get_vehicle_stats():
    """
    차량 데이터 통계 (국산/수입 대수)
    """
    return admin_service.get_vehicle_stats()


@app.get("/api/admin/vehicles", tags=["Admin"])
async def get_vehicles(
    brand: str = None,
    model: str = None,
    category: str = "all",
    limit: int = 50
):
    """
    차량 목록 조회
    """
    return admin_service.get_vehicles(brand, model, category, limit)


@app.get("/api/admin/history", tags=["Admin"])
async def get_admin_history(limit: int = 50):
    """
    분석 이력 목록
    """
    return admin_service.get_history_list(limit)


# ========== 루트 ==========

@app.get("/", tags=["Root"])
async def root():
    """
    API 루트

    Returns:
        환영 메시지
    """
    return {
        "message": "중고차 가격 예측 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


# ========== 앱 실행 ==========

if __name__ == "__main__":
    import uvicorn
    
    # 개발 모드 실행
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


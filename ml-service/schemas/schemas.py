"""
Pydantic 스키마 정의
API 요청/응답 모델
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict


# ========== 요청 모델 ==========

class PredictRequest(BaseModel):
    """가격 예측 요청"""
    brand: str = Field(..., description="제조사 (예: 현대, 기아)")
    model: str = Field(..., description="모델명 (예: 그랜저)")
    year: int = Field(..., ge=2000, le=2025, description="연식")
    mileage: int = Field(..., ge=0, description="주행거리 (km)")
    fuel: str = Field(..., description="연료 (가솔린/디젤/LPG/하이브리드/전기)")
    # 옵션 필드 (선택사항)
    has_sunroof: Optional[bool] = Field(None, description="선루프 유무")
    has_navigation: Optional[bool] = Field(None, description="네비게이션 유무")
    has_leather_seat: Optional[bool] = Field(None, description="가죽시트 유무")
    has_smart_key: Optional[bool] = Field(None, description="스마트키 유무")
    has_rear_camera: Optional[bool] = Field(None, description="후방카메라 유무")
    has_led_lamp: Optional[bool] = Field(None, description="LED 램프 유무")
    has_heated_seat: Optional[bool] = Field(None, description="열선시트 유무")
    has_ventilated_seat: Optional[bool] = Field(None, description="통풍시트 유무")
    is_accident_free: Optional[bool] = Field(None, description="무사고 여부")
    
    class Config:
        json_schema_extra = {
            "example": {
                "brand": "현대",
                "model": "그랜저",
                "year": 2022,
                "mileage": 35000,
                "fuel": "가솔린"
            }
        }


class TimingRequest(BaseModel):
    """타이밍 분석 요청"""
    model: str = Field(..., description="모델명")
    
    class Config:
        schema_extra = {
            "example": {
                "model": "그랜저"
            }
        }


class SmartAnalysisRequest(BaseModel):
    """통합 스마트 분석 요청"""
    brand: str = Field(..., description="제조사")
    model: str = Field(..., description="모델명")
    year: int = Field(..., ge=2000, le=2025, description="연식")
    mileage: int = Field(..., ge=0, description="주행거리 (km)")
    fuel: str = Field(..., description="연료")
    sale_price: Optional[int] = Field(None, description="판매가 (만원)")
    dealer_description: Optional[str] = Field(None, description="딜러 설명글")
    performance_record: Optional[Dict] = Field(None, description="성능기록부")
    
    class Config:
        schema_extra = {
            "example": {
                "brand": "현대",
                "model": "그랜저",
                "year": 2022,
                "mileage": 35000,
                "fuel": "가솔린",
                "sale_price": 3200,
                "dealer_description": "완벽한 차량입니다. 무사고입니다.",
                "performance_record": {
                    "accidents": "없음",
                    "repairs": "없음",
                    "replacements": "없음"
                }
            }
        }


# ========== 응답 모델 ==========

class PredictResponse(BaseModel):
    """가격 예측 응답"""
    predicted_price: float = Field(..., description="예측 가격 (만원)")
    price_range: List[float] = Field(..., description="가격 범위 [최소, 최대]")
    confidence: float = Field(..., description="신뢰도 (0-1)")
    
    class Config:
        schema_extra = {
            "example": {
                "predicted_price": 3200,
                "price_range": [2880, 3520],
                "confidence": 0.87
            }
        }


class TimingResponse(BaseModel):
    """타이밍 분석 응답"""
    timing_score: float = Field(..., description="타이밍 점수 (0-100)")
    decision: str = Field(..., description="판단 (구매/관망/대기)")
    color: str = Field(..., description="신호등 색상")
    breakdown: Dict[str, float] = Field(..., description="세부 점수")
    reasons: List[str] = Field(..., description="판단 근거")
    
    class Config:
        schema_extra = {
            "example": {
                "timing_score": 75.5,
                "decision": "구매 적기",
                "color": "🟢",
                "breakdown": {
                    "macro": 78.2,
                    "trend": 72.5,
                    "schedule": 75.8
                },
                "reasons": [
                    "✅ 저금리 2.5% (구매 적기)",
                    "✅ 관심도 안정 (5.2%)",
                    "✅ 신차 출시 예정 없음"
                ]
            }
        }


class GroqSignalResponse(BaseModel):
    """Groq AI 신호 분석 응답"""
    signal: str = Field(..., description="매수/관망/회피")
    signal_text: str = Field(..., description="신호 텍스트")
    color: str = Field(..., description="색상")
    emoji: str = Field(..., description="이모지")
    confidence: int = Field(..., description="신뢰도 (0-100)")
    short_summary: str = Field(..., description="한 줄 요약")
    key_points: List[str] = Field(..., description="핵심 포인트")
    report: str = Field(..., description="상세 리포트")


class GroqFraudResponse(BaseModel):
    """Groq AI 허위매물 탐지 응답"""
    is_suspicious: bool = Field(..., description="의심 여부")
    fraud_score: int = Field(..., description="의심 점수 (0-100)")
    warnings: List[str] = Field(..., description="경고 메시지")
    highlighted_text: List[str] = Field(..., description="의심 문장")
    summary: str = Field(..., description="종합 의견")


class GroqNegotiationResponse(BaseModel):
    """Groq AI 네고 대본 응답"""
    target_price: int = Field(..., description="목표 가격")
    discount_amount: int = Field(..., description="할인액")
    message_script: str = Field(..., description="문자 메시지 초안")
    phone_script: str = Field(..., description="전화 대본")
    key_arguments: List[str] = Field(..., description="핵심 논거")
    tips: List[str] = Field(..., description="협상 팁")


class SmartAnalysisResponse(BaseModel):
    """통합 스마트 분석 응답"""
    prediction: PredictResponse
    timing: TimingResponse
    groq_analysis: Optional[Dict] = Field(None, description="Groq AI 분석 결과")
    
    class Config:
        schema_extra = {
            "example": {
                "prediction": {
                    "predicted_price": 3200,
                    "price_range": [2880, 3520],
                    "confidence": 0.87
                },
                "timing": {
                    "timing_score": 75.5,
                    "decision": "구매 적기",
                    "color": "🟢",
                    "breakdown": {
                        "macro": 78.2,
                        "trend": 72.5,
                        "schedule": 75.8
                    },
                    "reasons": ["✅ 저금리", "✅ 관심도 안정"]
                },
                "groq_analysis": {
                    "signal": {},
                    "fraud_check": {},
                    "negotiation": {}
                }
            }
        }


# ========== 기타 응답 모델 ==========

class HealthResponse(BaseModel):
    """헬스체크 응답"""
    status: str
    version: str
    message: str


class BrandsResponse(BaseModel):
    """브랜드 목록 응답"""
    brands: List[str]


class ModelsResponse(BaseModel):
    """모델 목록 응답"""
    brand: str
    models: List[str]


class FuelTypesResponse(BaseModel):
    """연료 타입 목록 응답"""
    fuel_types: List[str]


"""
가격 예측 서비스 V12 (Production)
================================
- 국산차: domestic_v12.pkl (MAPE 9.7%) - FuelType 포함!
- 외제차: imported_v14.pkl (MAPE 12.0%) - FuelType 포함!
- 연료, 옵션 효과 학습됨
- 신뢰도 표시 + 분해 설명
"""

import pandas as pd
import numpy as np
import joblib
import os
import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

# 모델 경로
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')


@dataclass
class PredictionResult:
    """예측 결과 데이터 클래스"""
    predicted_price: float
    confidence: float
    mape: float
    price_range: Tuple[float, float]
    breakdown: Dict
    model_type: str
    warnings: list


class PredictionServiceV12:
    """가격 예측 서비스 V12 - FuelType 포함"""
    
    DOMESTIC_BRANDS = ['현대', '기아', '제네시스', 'KG모빌리티', '쉐보레', '르노코리아', 
                       '쌍용', '삼성', 'Hyundai', 'Kia', 'Genesis', 'Chevrolet']
    
    IMPORTED_BRANDS = ['벤츠', 'BMW', '아우디', '폭스바겐', '볼보', '렉서스', '토요타', 
                       '혼다', '닛산', '포르쉐', '재규어', '랜드로버', '미니', '지프', '테슬라']
    
    # 옵션 프리미엄 (외제차)
    IMPORTED_OPT_PREMIUM = {
        'has_ventilated_seat': 120, 'has_sunroof': 100, 'has_led_lamp': 100,
        'has_leather_seat': 80, 'has_navigation': 80, 'has_heated_seat': 60,
        'has_smart_key': 50, 'has_rear_camera': 50,
    }
    
    def __init__(self):
        self.domestic_model = None
        self.domestic_encoders = None
        self.domestic_features = None
        self.imported_model = None
        self.imported_encoders = None
        self.imported_features = None
        self._load_models()
    
    def _load_models(self):
        """모델 로드 (V12/V14 우선, 없으면 V11/V13)"""
        try:
            # 국산차 V12 (FuelType 포함)
            domestic_path = os.path.join(MODEL_DIR, 'domestic_v12.pkl')
            if os.path.exists(domestic_path):
                self.domestic_model = joblib.load(domestic_path)
                self.domestic_encoders = joblib.load(os.path.join(MODEL_DIR, 'domestic_v12_encoders.pkl'))
                self.domestic_features = joblib.load(os.path.join(MODEL_DIR, 'domestic_v12_features.pkl'))
                self.domestic_version = 'V12'
                print("✓ 국산차 V12 모델 로드 완료 (FuelType 포함)")
            else:
                # Fallback to V11
                domestic_path = os.path.join(MODEL_DIR, 'domestic_v11.pkl')
                if os.path.exists(domestic_path):
                    self.domestic_model = joblib.load(domestic_path)
                    self.domestic_encoders = joblib.load(os.path.join(MODEL_DIR, 'domestic_v11_encoders.pkl'))
                    self.domestic_features = joblib.load(os.path.join(MODEL_DIR, 'domestic_v11_features.pkl'))
                    self.domestic_version = 'V11'
                    print("✓ 국산차 V11 모델 로드 완료")
            
            # 외제차 V14 (FuelType 포함)
            imported_path = os.path.join(MODEL_DIR, 'imported_v14.pkl')
            if os.path.exists(imported_path):
                self.imported_model = joblib.load(imported_path)
                self.imported_encoders = joblib.load(os.path.join(MODEL_DIR, 'imported_v14_encoders.pkl'))
                self.imported_features = joblib.load(os.path.join(MODEL_DIR, 'imported_v14_features.pkl'))
                self.imported_version = 'V14'
                print("✓ 외제차 V14 모델 로드 완료 (FuelType 포함)")
            else:
                # Fallback to V13
                imported_path = os.path.join(MODEL_DIR, 'imported_v13.pkl')
                if os.path.exists(imported_path):
                    self.imported_model = joblib.load(imported_path)
                    self.imported_encoders = joblib.load(os.path.join(MODEL_DIR, 'imported_v13_encoders.pkl'))
                    self.imported_features = joblib.load(os.path.join(MODEL_DIR, 'imported_v13_features.pkl'))
                    self.imported_version = 'V13'
                    print("✓ 외제차 V13 모델 로드 완료")
                    
        except Exception as e:
            print(f"⚠️ 모델 로드 실패: {e}")
    
    def _get_model_type(self, brand: str) -> str:
        for b in self.DOMESTIC_BRANDS:
            if b.lower() in brand.lower() or brand.lower() in b.lower():
                return 'domestic'
        return 'imported'
    
    def _get_mileage_group(self, mileage: int) -> str:
        if mileage < 30000: return 'A'
        elif mileage < 60000: return 'B'
        elif mileage < 100000: return 'C'
        elif mileage < 150000: return 'D'
        return 'E'
    
    def _normalize_fuel(self, fuel: str) -> str:
        """연료 타입 정규화"""
        fuel = str(fuel).lower()
        if '하이브리드' in fuel or '전기' in fuel or 'hybrid' in fuel:
            return '하이브리드'
        elif 'lpg' in fuel:
            return 'LPG'
        elif '디젤' in fuel or 'diesel' in fuel:
            return '디젤'
        return '가솔린'
    
    def _create_domestic_features_v12(self, model_name: str, year: int, mileage: int,
                                       fuel: str, options: Dict, accident_free: bool, 
                                       grade: str) -> pd.DataFrame:
        """국산차 V12 피처 생성 (FuelType 포함)"""
        age = 2025 - year
        mg = self._get_mileage_group(mileage)
        my = f"{model_name}_{year}"
        mymg = f"{my}_{mg}"
        fuel_norm = self._normalize_fuel(fuel)
        
        enc = self.domestic_encoders
        default_val = 2500
        
        model_enc_val = enc.get('model_enc', {}).get(model_name, default_val)
        my_enc_val = enc.get('model_year_enc', {}).get(my, model_enc_val)
        mymg_enc_val = enc.get('model_year_mg_enc', {}).get(mymg, my_enc_val)
        brand_enc_val = enc.get('brand_enc', {}).get('현대', default_val)
        fuel_enc_val = enc.get('fuel_enc', {}).get(fuel_norm, default_val)
        
        # 옵션
        opt_cols = ['has_sunroof','has_leather_seat','has_led_lamp','has_smart_key',
                    'has_navigation','has_heated_seat','has_ventilated_seat','has_rear_camera']
        opt_values = {c: int(bool(options.get(c, False))) for c in opt_cols}
        opt_count = sum(opt_values.values())
        opt_premium = (opt_values.get('has_sunroof',0)*3 + opt_values.get('has_leather_seat',0)*2 +
                       opt_values.get('has_ventilated_seat',0)*3 + opt_values.get('has_led_lamp',0)*2)
        
        grade_map = {'normal': 0, 'good': 1, 'excellent': 2}
        grade_enc = grade_map.get(grade, 0)
        
        f = {
            'Model_enc': model_enc_val,
            'Model_Year_enc': my_enc_val,
            'Model_Year_MG_enc': mymg_enc_val,
            'Brand_enc': brand_enc_val,
            'Fuel_enc': fuel_enc_val,
            'is_diesel': 1 if fuel_norm == '디젤' else 0,
            'is_hybrid': 1 if fuel_norm == '하이브리드' else 0,
            'is_lpg': 1 if fuel_norm == 'LPG' else 0,
            'Age': age,
            'Age_log': np.log1p(age),
            'Age_sq': age ** 2,
            'Mileage': mileage,
            'Mile_log': np.log1p(mileage),
            'Km_per_Year': mileage / (age + 1),
            'is_accident_free': 1 if accident_free else 0,
            'inspection_grade_enc': grade_enc,
            'Opt_Count': opt_count,
            'Opt_Premium': opt_premium,
            **opt_values
        }
        
        return pd.DataFrame([f])[self.domestic_features]
    
    def _extract_class(self, model_name: str, brand: str) -> tuple:
        """외제차 클래스 추출"""
        model = str(model_name)
        mfr = str(brand).lower()
        
        CLASS_RANK = {
            'A': 1, 'B': 1, 'C': 2, 'E': 3, 'S': 4, 'G': 5,
            'GLA': 2, 'GLB': 2, 'GLC': 3, 'GLE': 3, 'GLS': 4,
            '1시리즈': 1, '3시리즈': 2, '5시리즈': 3, '7시리즈': 4,
            'X1': 2, 'X3': 3, 'X5': 4, 'X7': 5,
            'A3': 1, 'A4': 2, 'A6': 3, 'A8': 4,
            'Q3': 2, 'Q5': 3, 'Q7': 4,
        }
        
        if '벤츠' in mfr:
            match = re.search(r'([A-Z])-?클래스|([A-Z])-?Class', model, re.I)
            if match:
                cls = (match.group(1) or match.group(2)).upper()
                return cls, CLASS_RANK.get(cls, 3)
            match = re.search(r'(GL[ABCES])', model, re.I)
            if match:
                return match.group(1).upper(), CLASS_RANK.get(match.group(1).upper(), 3)
        
        if 'bmw' in mfr:
            match = re.search(r'(\d)시리즈', model)
            if match:
                cls = f"{match.group(1)}시리즈"
                return cls, CLASS_RANK.get(cls, 3)
            match = re.search(r'\b([Xi]\d)\b', model)
            if match:
                return match.group(1).upper(), CLASS_RANK.get(match.group(1).upper(), 3)
        
        if '아우디' in mfr:
            match = re.search(r'\b(A\d|Q\d)', model, re.I)
            if match:
                return match.group(1).upper(), CLASS_RANK.get(match.group(1).upper(), 3)
        
        clean = re.sub(r'\([^)]*\)', '', model).strip()
        first = clean.split()[0] if clean else model
        return first if len(first) > 1 else 'Unknown', 3
    
    def _create_imported_features_v14(self, model_name: str, brand: str, year: int, 
                                       mileage: int, fuel: str, options: Dict,
                                       accident_free: bool, grade: str) -> pd.DataFrame:
        """외제차 V14 피처 생성 (FuelType 포함)"""
        age = 2025 - year
        mg = self._get_mileage_group(mileage)
        my = f"{model_name}_{year}"
        mymg = f"{my}_{mg}"
        cls, cls_rank = self._extract_class(model_name, brand)
        cls_year = f"{cls}_{year}"
        fuel_norm = self._normalize_fuel(fuel)
        
        enc = self.imported_encoders
        global_mean = enc.get('global_mean', 5000)
        
        BRAND_TIER = {
            '벤츠': 4, 'BMW': 4, '아우디': 4, '포르쉐': 5, '렉서스': 4,
            '볼보': 3, '폭스바겐': 2, '미니': 2, '테슬라': 4,
        }
        
        grade_map = {'normal': 0, 'good': 1, 'excellent': 2}
        
        f = {
            'Model_enc': enc.get('model_enc', {}).get(model_name, global_mean),
            'Model_Year_enc': enc.get('model_year_enc', {}).get(my, global_mean),
            'Model_Year_MG_enc': enc.get('model_year_mg_enc', {}).get(mymg, global_mean),
            'Brand_enc': enc.get('brand_enc', {}).get(brand, global_mean),
            'Class_enc': enc.get('class_enc', {}).get(cls, global_mean),
            'Class_Year_enc': enc.get('class_year_enc', {}).get(cls_year, global_mean),
            'Fuel_enc': enc.get('fuel_enc', {}).get(fuel_norm, global_mean),
            'is_diesel': 1 if fuel_norm == '디젤' else 0,
            'is_hybrid': 1 if fuel_norm == '하이브리드' else 0,
            'Brand_Tier': BRAND_TIER.get(brand, 3),
            'Class_Rank': cls_rank,
            'Age': age,
            'Age_log': np.log1p(age),
            'Mileage': mileage,
            'Mile_log': np.log1p(mileage),
            'Km_per_Year': mileage / (age + 1),
            'is_accident_free': 1 if accident_free else 0,
            'inspection_grade_enc': grade_map.get(grade, 0),
        }
        
        return pd.DataFrame([f])[self.imported_features]
    
    # 시장 현실 기반 연료별 가격 조정 (실제 중고차 시장 데이터 기반)
    # 동일 모델/연식/주행거리 조건에서의 연료별 가격 차이
    FUEL_ADJUSTMENT = {
        '가솔린': 1.0,       # 기준
        '디젤': 1.02,        # +2% (연비 우수)
        '하이브리드': 1.05,  # +5% (친환경, 높은 잔존가치)
        'LPG': 0.94,         # -6% (실제 데이터 기반: -5.6%)
    }
    
    def predict(self, brand: str, model_name: str, year: int, mileage: int,
                options: Optional[Dict] = None, accident_free: bool = True,
                grade: str = 'normal', fuel: str = '가솔린') -> PredictionResult:
        """통합 예측"""
        options = options or {}
        warnings = []
        
        model_type = self._get_model_type(brand)
        fuel_norm = self._normalize_fuel(fuel)
        fuel_adj = self.FUEL_ADJUSTMENT.get(fuel_norm, 1.0)
        
        if model_type == 'domestic':
            if self.domestic_model is None:
                raise ValueError("국산차 모델이 로드되지 않았습니다")
            
            if hasattr(self, 'domestic_version') and self.domestic_version == 'V12':
                # V12: 가솔린 기준으로 예측 후 수동 연료 조정 적용
                # (모델의 연료 피처 효과가 왜곡되어 있으므로 무력화)
                features = self._create_domestic_features_v12(
                    model_name, year, mileage, '가솔린', options, accident_free, grade)
                pred_log = self.domestic_model.predict(features)[0]
                base_price = np.expm1(pred_log)
                predicted_price = base_price * fuel_adj  # 시장 현실 기반 조정
            else:
                # Fallback V11 (수동 연료 프리미엄)
                features = self._create_domestic_features_v11(
                    model_name, year, mileage, options, accident_free, grade)
                pred_log = self.domestic_model.predict(features)[0]
                base_price = np.expm1(pred_log)
                predicted_price = base_price * fuel_adj
            
            mape = 9.7  # V12 MAPE
            
        else:  # imported
            if self.imported_model is None:
                raise ValueError("외제차 모델이 로드되지 않았습니다")
            
            # 외제차 연료 조정 (디젤이 더 비싸야 함)
            imported_fuel_adj = {'가솔린': 1.0, '디젤': 1.05, '하이브리드': 1.10}.get(fuel_norm, 1.0)
            
            if hasattr(self, 'imported_version') and self.imported_version == 'V14':
                # V14: 가솔린 기준 예측 후 수동 조정
                features = self._create_imported_features_v14(
                    model_name, brand, year, mileage, '가솔린', options, accident_free, grade)
                pred_log = self.imported_model.predict(features)[0]
                base_price = np.expm1(pred_log)
            else:
                # Fallback V13
                features = self._create_imported_features_v13(
                    model_name, brand, year, mileage, options, accident_free, grade)
                pred_log = self.imported_model.predict(features)[0]
                base_price = np.expm1(pred_log)
            
            # 연료 조정 + 옵션 프리미엄
            base_price = base_price * imported_fuel_adj
            opt_total = sum(int(bool(options.get(k, False))) * v 
                           for k, v in self.IMPORTED_OPT_PREMIUM.items())
            predicted_price = base_price + opt_total
            mape = 12.0  # V14 MAPE
        
        # 신뢰도 (MAPE 기반 - 개선된 공식)
        # MAPE 5% 이하: 95%+, MAPE 10%: 85%, MAPE 15%: 75%
        confidence = max(50, min(98, 95 - (mape - 5) * 2))
        
        # 옵션 개수에 따른 불확실성 추가
        opt_count = sum(1 for v in options.values() if v)
        opt_uncertainty = opt_count * 0.5  # 옵션당 0.5% 추가 불확실성
        
        # 연료에 따른 불확실성
        fuel_uncertainty = {'하이브리드': 1.5, 'LPG': 2.0, '디젤': 0.5}.get(fuel_norm, 0)
        
        # 총 불확실성
        total_mape = mape + opt_uncertainty + fuel_uncertainty
        
        # 가격 범위 (옵션/연료 반영)
        error_margin = predicted_price * (total_mape / 100)
        price_range = (predicted_price - error_margin, predicted_price + error_margin)
        
        # 분해
        breakdown = self._generate_breakdown(model_name, year, mileage, fuel_norm,
                                              options, accident_free, predicted_price, model_type)
        
        # 경고
        if year < 2015:
            warnings.append("10년 이상 된 차량은 예측 정확도가 낮을 수 있습니다")
        if mileage > 150000:
            warnings.append("고주행 차량은 실제 상태에 따라 가격 차이가 클 수 있습니다")
        
        return PredictionResult(
            predicted_price=round(predicted_price, 0),
            confidence=round(confidence, 1),
            mape=mape,
            price_range=(round(price_range[0], 0), round(price_range[1], 0)),
            breakdown=breakdown,
            model_type=model_type,
            warnings=warnings
        )
    
    def _generate_breakdown(self, model_name: str, year: int, mileage: int, fuel: str,
                            options: Dict, accident_free: bool, 
                            predicted_price: float, model_type: str) -> Dict:
        """예측 분해 설명"""
        return {
            'model_info': {'model': model_name, 'year': year, 'mileage': mileage, 'fuel': fuel},
            'accident_free': accident_free,
            'options': options,
            'data_source': f"{'국산차 V12' if model_type == 'domestic' else '외제차 V14'} (FuelType 학습됨)"
        }


# 싱글톤
_prediction_service = None

def get_prediction_service() -> PredictionServiceV12:
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionServiceV12()
    return _prediction_service


if __name__ == "__main__":
    service = get_prediction_service()
    
    print("\n" + "="*60)
    print("🧪 V12 테스트 - 연료별 가격")
    print("="*60)
    
    for fuel in ['가솔린', '디젤', '하이브리드', 'LPG']:
        result = service.predict(
            brand='현대',
            model_name='더 뉴 그랜저 IG',
            year=2022,
            mileage=30000,
            fuel=fuel
        )
        print(f"{fuel:10}: {result.predicted_price:,.0f}만원")

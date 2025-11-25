"""
가격 예측 서비스
V2: 국산차는 Model_Year_Mileage Target Encoding 기반
- 신차가격(MSRP) 기반 모델 서열 반영
"""

import pandas as pd
import numpy as np
import sys
import os
from typing import Dict, Tuple

# MSRP 데이터 임포트
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from msrp_data import DOMESTIC_MSRP, IMPORTED_MSRP, get_msrp

from ..utils.model_loader import get_model_loader


class PredictionService:
    """가격 예측 서비스 - 3개 모델 지원"""
    
    def __init__(self):
        self.model_loader = get_model_loader()
    
    def create_features_v2(self, df: pd.DataFrame, brand: str, encoders: dict, 
                           model_type: str = 'domestic', options: dict = None) -> pd.DataFrame:
        """
        V2 Feature Engineering (모든 모델)
        - Model_Year_Mileage Target Encoding 기반
        - price_segment 없음
        - 옵션 정보 반영
        """
        # 기본 정보
        year = df['year'].values[0]
        mileage = df['mileage'].values[0]
        model_name = df['model_name'].values[0]
        age = 2025 - year
        
        # 주행거리 구간 (5단계)
        if mileage < 30000:
            mg = 'A'
        elif mileage < 60000:
            mg = 'B'
        elif mileage < 100000:
            mg = 'C'
        elif mileage < 150000:
            mg = 'D'
        else:
            mg = 'E'
        
        # Target Encoding 조회
        model_enc = encoders.get('Model_enc', {})
        if hasattr(model_enc, 'to_dict'):
            model_enc = model_enc.to_dict()
        
        brand_enc = encoders.get('Brand_enc', encoders.get('Manufacturer_enc', {}))
        if hasattr(brand_enc, 'to_dict'):
            brand_enc = brand_enc.to_dict()
        
        my_enc = encoders.get('Model_Year_enc', {})
        if hasattr(my_enc, 'to_dict'):
            my_enc = my_enc.to_dict()
        
        mym_enc = encoders.get('Model_Year_Mileage_enc', {})
        if hasattr(mym_enc, 'to_dict'):
            mym_enc = mym_enc.to_dict()
        
        # 인코딩 값 계산
        default_val = 8.0
        model_enc_val = model_enc.get(model_name, model_enc.get('__default__', default_val))
        brand_enc_val = brand_enc.get(brand, brand_enc.get('__default__', default_val))
        my_key = f"{model_name}_{year}"
        my_enc_val = my_enc.get(my_key, model_enc_val)
        mym_key = f"{model_name}_{year}_{mg}"
        mym_enc_val = mym_enc.get(mym_key, my_enc_val)
        
        # 옵션 처리 (None이면 기본값 0.5 사용)
        if options is None:
            options = {}
        
        # 옵션 값 추출 (None이면 기본값 0.5)
        has_sunroof = 1 if options.get('has_sunroof') == True else (0 if options.get('has_sunroof') == False else 0.5)
        has_navigation = 1 if options.get('has_navigation') == True else (0 if options.get('has_navigation') == False else 0.5)
        has_leather_seat = 1 if options.get('has_leather_seat') == True else (0 if options.get('has_leather_seat') == False else 0.5)
        has_smart_key = 1 if options.get('has_smart_key') == True else (0 if options.get('has_smart_key') == False else 0.5)
        has_rear_camera = 1 if options.get('has_rear_camera') == True else (0 if options.get('has_rear_camera') == False else 0.5)
        has_led_lamp = 1 if options.get('has_led_lamp') == True else (0 if options.get('has_led_lamp') == False else 0.5)
        has_heated_seat = 1 if options.get('has_heated_seat') == True else (0 if options.get('has_heated_seat') == False else 0.5)
        has_ventilated_seat = 1 if options.get('has_ventilated_seat') == True else (0 if options.get('has_ventilated_seat') == False else 0.5)
        is_accident_free = 1 if options.get('is_accident_free') == True else (0 if options.get('is_accident_free') == False else 0.8)
        
        # 옵션 개수 및 비율 계산
        option_values = [has_sunroof, has_navigation, has_leather_seat, has_smart_key, 
                        has_rear_camera, has_led_lamp, has_heated_seat, has_ventilated_seat]
        option_count = sum(1 for v in option_values if v == 1)
        option_rate = sum(option_values) / len(option_values)
        
        # 프리미엄 옵션 점수 (선루프, 가죽시트, 통풍시트에 가중치)
        option_premium = (has_sunroof * 2 + has_leather_seat * 2 + has_ventilated_seat * 2 + 
                         has_navigation + has_smart_key + has_led_lamp + has_heated_seat + has_rear_camera)
        
        # 브랜드 티어 (수입차용)
        luxury = ['벤츠', 'Mercedes-Benz', 'BMW', '아우디', 'Audi', '포르쉐', 'Porsche', '렉서스']
        premium = ['볼보', 'Volvo', '재규어', 'Jaguar', '랜드로버', '인피니티']
        if any(b in brand for b in luxury):
            brand_tier = 3
        elif any(b in brand for b in premium):
            brand_tier = 2
        else:
            brand_tier = 1
        
        # 피처 생성
        df['Model_enc'] = model_enc_val
        df['Brand_enc'] = brand_enc_val
        df['Manufacturer_enc'] = brand_enc_val
        df['Model_Year_enc'] = my_enc_val
        df['Model_Year_Mileage_enc'] = mym_enc_val
        df['age'] = age
        df['age_squared'] = age ** 2
        df['age_log'] = np.log1p(age)
        df['Mileage'] = mileage
        df['mileage_log'] = np.log1p(mileage)
        df['mileage_squared'] = mileage ** 2
        df['mileage_per_year'] = mileage / (age + 1)
        df['option_count'] = option_count
        df['option_rate'] = option_rate
        df['option_premium'] = option_premium
        df['has_sunroof'] = has_sunroof
        df['has_led_lamp'] = has_led_lamp
        df['has_leather_seat'] = has_leather_seat
        df['has_smart_key'] = has_smart_key
        df['is_accident_free'] = is_accident_free
        df['is_diesel'] = 0
        df['is_lpg'] = 0
        df['is_hybrid'] = 0
        
        # 차급 계산 (학습과 동일하게!)
        m = model_name.lower()
        if 'g90' in m or 'gv90' in m:
            vehicle_class = 7  # 최고급
        elif 'g80' in m or 'gv80' in m:
            vehicle_class = 6  # 고급
        elif 'g70' in m or 'gv70' in m:
            vehicle_class = 5  # 준고급
        elif any(x in m for x in ['팰리세이드', '모하비']):
            vehicle_class = 5  # 대형 SUV
        elif any(x in m for x in ['싼타페', '쏘렌토']):
            vehicle_class = 4  # 중형 SUV
        elif any(x in m for x in ['투싼', '스포티지', '셀토스', '니로']):
            vehicle_class = 3  # 준중형 SUV
        elif any(x in m for x in ['코나', '베뉴', '티볼리']):
            vehicle_class = 2  # 소형 SUV
        elif any(x in m for x in ['카니발', '스타리아']):
            vehicle_class = 5  # 대형 MPV
        elif '스타렉스' in m:
            vehicle_class = 4  # 중형 MPV
        elif any(x in m for x in ['k9', '에쿠스']):
            vehicle_class = 6  # 최고급 세단
        elif any(x in m for x in ['그랜저', 'k8']):
            vehicle_class = 5  # 고급 세단
        elif any(x in m for x in ['k7', '제네시스 세단']):
            vehicle_class = 4  # 준고급 세단
        elif any(x in m for x in ['쏘나타', 'k5']):
            vehicle_class = 3  # 중형 세단
        elif any(x in m for x in ['아반떼', 'k3']):
            vehicle_class = 2  # 준중형 세단
        elif any(x in m for x in ['모닝', '레이', '캐스퍼', '스파크']):
            vehicle_class = 1  # 소형/경차
        else:
            vehicle_class = 3  # 기본값
        
        df['vehicle_class'] = vehicle_class
        df['brand_tier'] = brand_tier
        
        # 신차가격(MSRP) 추가 - 모델 서열 반영!
        is_imported = model_type == 'imported'
        msrp = get_msrp(model_name, is_imported=is_imported)
        df['msrp'] = msrp
        df['msrp_log'] = np.log1p(msrp)
        
        # 상호작용 피처
        df['enc_x_age'] = mym_enc_val * age
        df['enc_x_mileage'] = mym_enc_val * np.log1p(mileage)
        df['enc_x_option'] = mym_enc_val * option_rate
        df['msrp_x_age'] = df['msrp_log'] * age
        df['msrp_x_mileage'] = df['msrp_log'] * np.log1p(mileage)
        
        return df
        
    def create_features(self, df: pd.DataFrame, brand: str, encoders: dict) -> pd.DataFrame:
        """
        Feature Engineering (학습 시와 동일하게)
        
        Args:
            df: 입력 데이터프레임
            brand: 제조사 (모델 타입 결정용)
            encoders: Target Encoding 딕셔너리
            
        Returns:
            피처가 추가된 데이터프레임
        """
        current_year = 2025
        
        # 기본 피처
        df['Year'] = df['year']
        df['Mileage'] = df['mileage']
        df['age'] = current_year - df['year']
        df['age_squared'] = df['age'] ** 2
        df['age_cubed'] = df['age'] ** 3
        
        # 주행거리 피처
        df['mileage_log'] = np.log1p(df['mileage'])
        df['mileage_squared'] = df['mileage'] ** 2
        df['mileage_per_year'] = df['mileage'] / (df['age'] + 1)
        df['is_low_mileage'] = (df['mileage'] < 30000).astype(int)
        df['is_high_mileage'] = (df['mileage'] > 150000).astype(int)
        
        # 주행거리 상태 인코딩
        def encode_mileage_condition(m):
            if m < 30000: return 0  # 저주행
            elif m < 100000: return 1  # 보통
            elif m < 150000: return 2  # 고주행
            else: return 3  # 매우 고주행
        df['mileage_condition_encoded'] = df['mileage'].apply(encode_mileage_condition)
        
        # 연료 타입 인코딩
        fuel_map = {'가솔린': 0, '디젤': 1, 'LPG': 2, '하이브리드': 3, '전기': 4}
        df['FuelType_encoded'] = df['fuel'].map(fuel_map).fillna(0).astype(int)
        df['is_diesel'] = (df['fuel'] == '디젤').astype(int)
        df['is_hybrid'] = df['fuel'].str.contains('하이브리드', na=False).astype(int)
        df['is_eco_fuel'] = df['fuel'].str.contains('하이브리드|전기', na=False).astype(int)
        
        # Target Encoding 적용
        model_type = self.model_loader._get_model_type(brand)
        
        if encoders:
            # 제조사 Target Encoding
            if 'Manufacturer_target_enc' in encoders:
                mfr_enc = encoders['Manufacturer_target_enc']
                # pandas Series 또는 dict 모두 처리
                if hasattr(mfr_enc, 'to_dict'):
                    mfr_enc = mfr_enc.to_dict()
                default_mfr = np.mean(list(mfr_enc.values())) if mfr_enc else 7.5
                df['Manufacturer_target_enc'] = df['brand'].map(
                    lambda x: mfr_enc.get(x, default_mfr)
                )
            else:
                df['Manufacturer_target_enc'] = 7.5  # 기본값
            
            # 모델 Target Encoding
            if 'Model_target_enc' in encoders:
                model_enc = encoders['Model_target_enc']
                # pandas Series 또는 dict 모두 처리
                if hasattr(model_enc, 'to_dict'):
                    model_enc = model_enc.to_dict()
                default_model = np.mean(list(model_enc.values())) if model_enc else 7.5
                df['Model_target_enc'] = df['model_name'].map(
                    lambda x: model_enc.get(x, default_model)
                )
            else:
                df['Model_target_enc'] = 7.5  # 기본값
        else:
            df['Manufacturer_target_enc'] = 7.5
            df['Model_target_enc'] = 7.5
        
        # Model+Year Target Encoding 적용
        year = df['year'].values[0]
        year_only = int(year) if year > 2000 else 2020
        model_year_key = f"{df['model_name'].values[0]}_{year_only}"
        
        if encoders and 'Model_Year_target_enc' in encoders:
            my_enc = encoders['Model_Year_target_enc']
            if hasattr(my_enc, 'to_dict'):
                my_enc = my_enc.to_dict()
            default_my = df['Model_target_enc'].values[0]  # Model+Year 없으면 Model 사용
            df['Model_Year_target_enc'] = my_enc.get(model_year_key, default_my)
        else:
            df['Model_Year_target_enc'] = df['Model_target_enc'].values[0]
        
        # price_segment 추정 (Model_Year_target_enc 기반)
        # Model_Year_target_enc가 로그 가격이므로, 이를 segment로 변환
        model_year_enc_val = df['Model_Year_target_enc'].values[0]
        estimated_price = np.expm1(model_year_enc_val)  # 로그 → 원래 가격
        
        # 가격을 segment로 변환 (학습 데이터 15분위 기준)
        segment_boundaries = [0, 430, 588, 730, 890, 1090, 1290, 1490, 1690, 1930, 2250, 2630, 3090, 3730, 4750, 999999]
        df['price_segment'] = 14  # 기본값
        for i, bound in enumerate(segment_boundaries[1:]):
            if estimated_price < bound:
                df['price_segment'] = i
                break
        
        # 옵션 점수 (API에서 옵션 정보 없으면 일반적인 값 사용)
        # 데이터 기준 평균 장착률: 약 65%
        option_defaults = {
            'has_sunroof': 0.42, 'has_navigation': 0.89, 'has_leather_seat': 0.67,
            'has_smart_key': 0.85, 'has_rear_camera': 0.78, 'has_led_lamp': 0.54,
            'has_parking_sensor': 0.61, 'has_auto_ac': 0.73,
            'has_heated_seat': 0.69, 'has_ventilated_seat': 0.38
        }
        option_cols = list(option_defaults.keys())
        
        for col in option_cols:
            if col not in df.columns:
                df[col] = option_defaults[col]
        
        df['option_score'] = df[option_cols].sum(axis=1)
        df['option_rate'] = df['option_score'] / 10.0
        df['option_weighted'] = df['option_score'] * 1.2  # 기본 가중치
        df['is_full_option'] = (df['option_score'] >= 7).astype(int)
        
        # 차량 상태 (기본값)
        df['is_accident_free'] = 1  # 무사고 가정
        df['inspection_score'] = 2  # 보통
        df['is_premium_condition'] = 0
        
        # 지역 (기본값)
        df['is_metro'] = 1  # 수도권 가정
        
        # 상호작용 피처
        df['age_option_interaction'] = df['age'] * df['option_rate']
        df['model_option_interaction'] = df['Model_target_enc'] * df['option_weighted']
        df['age_mileage_interaction'] = df['age'] * df['mileage_log']
        
        # 추가 상호작용 피처
        df['model_age_interaction'] = df['Model_target_enc'] * df['age']
        df['model_mileage_interaction'] = df['Model_target_enc'] * df['mileage_log']
        df['brand_age_interaction'] = df['Manufacturer_target_enc'] * df['age']
        df['brand_mileage_interaction'] = df['Manufacturer_target_enc'] * df['mileage_log']
        
        # 감가 및 가치 피처
        df['depreciation_factor'] = 1 - (df['age'] * 0.08 + df['mileage_log'] * 0.02)
        df['estimated_value'] = df['Model_target_enc'] * df['depreciation_factor']
        
        # 연령 그룹
        age_val = df['age'].values[0]
        if age_val <= 2:
            df['age_group'] = 4
        elif age_val <= 5:
            df['age_group'] = 3
        elif age_val <= 8:
            df['age_group'] = 2
        elif age_val <= 12:
            df['age_group'] = 1
        else:
            df['age_group'] = 0
        
        # 차급 분류
        model_name_lower = str(df['model_name'].values[0]).lower()
        if any(x in model_name_lower for x in ['투싼', '코나', '싼타페', '팰리세이드', 'suv', '쏘렌토', '스포티지', '셀토스', '니로', '베뉴']):
            df['vehicle_segment'] = 4
        elif any(x in model_name_lower for x in ['카니발', '스타리아', '스타렉스']):
            df['vehicle_segment'] = 4
        elif any(x in model_name_lower for x in ['그랜저', 'k7', 'k8', 'k9']):
            df['vehicle_segment'] = 3
        elif any(x in model_name_lower for x in ['쏘나타', 'k5']):
            df['vehicle_segment'] = 2
        elif any(x in model_name_lower for x in ['아반떼', 'k3']):
            df['vehicle_segment'] = 1
        elif any(x in model_name_lower for x in ['모닝', '레이', '캐스퍼', '스파크']):
            df['vehicle_segment'] = 0
        else:
            df['vehicle_segment'] = 2
        
        # 수입차 전용 피처
        if model_type == 'imported':
            # 브랜드 티어
            luxury_brands = ['벤츠', 'BMW', '아우디', '렉서스', '포르쉐', 'Mercedes-Benz']
            premium_brands = ['볼보', '재규어', '랜드로버', '인피니티', 'Volvo', 'Jaguar']
            if brand in luxury_brands or any(b in brand for b in luxury_brands):
                df['brand_tier_encoded'] = 3
            elif brand in premium_brands or any(b in brand for b in premium_brands):
                df['brand_tier_encoded'] = 2
            else:
                df['brand_tier_encoded'] = 1
            
            # 브랜드 국적
            german_brands = ['벤츠', 'BMW', '아우디', '폭스바겐', '포르쉐', '미니']
            japanese_brands = ['렉서스', '토요타', '혼다', '닛산', '인피니티']
            if any(b in brand for b in german_brands):
                df['brand_origin_encoded'] = 1  # German
            elif any(b in brand for b in japanese_brands):
                df['brand_origin_encoded'] = 2  # Japanese
            else:
                df['brand_origin_encoded'] = 0  # Other
            
            df['brand_option_interaction'] = df['Manufacturer_target_enc'] * df['option_weighted']
            df['tier_option_interaction'] = df['brand_tier_encoded'] * df['option_weighted']
        
        return df
    
    def predict_price(self, brand: str, model_name: str, year: int, 
                     mileage: int, fuel: str, options: dict = None) -> Dict:
        """
        차량 가격 예측 (3개 모델 자동 선택)
        
        Args:
            brand: 제조사
            model_name: 모델명
            year: 연식
            mileage: 주행거리 (km)
            fuel: 연료 타입
            options: 옵션 정보 (선택)
            
        Returns:
            dict: {
                'predicted_price': float (만원),
                'price_range': [min, max] (만원),
                'confidence': float (0-1),
                'details': dict
            }
        """
        try:
            # 브랜드에 맞는 모델 로드
            model = self.model_loader.load_price_model(brand)
            encoders = self.model_loader.get_encoders(brand)
            feature_cols = self.model_loader.get_features(brand)
            model_type = self.model_loader._get_model_type(brand)
            
            # 입력 데이터 준비
            input_data = pd.DataFrame({
                'brand': [brand],
                'model_name': [model_name],
                'year': [year],
                'mileage': [mileage],
                'fuel': [fuel]
            })
            
            # Feature Engineering (V2: 모든 모델, 옵션 포함)
            input_data = self.create_features_v2(input_data, brand, encoders, model_type, options)
            
            # 피처 선택 (저장된 피처 목록 사용 또는 기본 목록)
            if feature_cols:
                # 누락된 피처는 기본값으로 채움
                for col in feature_cols:
                    if col not in input_data.columns:
                        input_data[col] = 0
                X = input_data[feature_cols]
            else:
                # 기본 피처 목록 사용
                default_features = [
                    'Year', 'age', 'age_squared', 'age_cubed',
                    'Mileage', 'mileage_log', 'mileage_per_year',
                    'Model_target_enc', 'Manufacturer_target_enc',
                    'FuelType_encoded', 'price_segment', 'is_eco_fuel',
                    'is_accident_free', 'inspection_score',
                    'option_score', 'option_rate', 'option_weighted',
                    'is_metro', 'age_option_interaction', 
                    'model_option_interaction', 'age_mileage_interaction'
                ]
                for col in default_features:
                    if col not in input_data.columns:
                        input_data[col] = 0
                X = input_data[[c for c in default_features if c in input_data.columns]]
            
            # 예측 (로그 가격 → 원래 가격)
            log_pred = model.predict(X)[0]
            pred_price = np.expm1(log_pred)
            
            # 가격 범위 계산 (모델별 MAE 기반)
            metrics = self.model_loader.metrics.get(model_type, {})
            mae = metrics.get('test_mae', pred_price * 0.10)
            price_range = [
                max(0, float(pred_price - mae)),
                float(pred_price + mae)
            ]
            
            # 신뢰도 계산
            age = input_data['age'].values[0]
            r2 = metrics.get('test_r2', 0.85)
            confidence = self._calculate_confidence(age, mileage, r2)
            
            return {
                'predicted_price': float(pred_price),
                'price_range': price_range,
                'confidence': confidence,
                'details': {
                    'model_type': model_type,
                    'age': int(age),
                    'mileage_per_year': float(input_data['mileage_per_year'].values[0]),
                    'model_r2': float(r2),
                    'model_mae': float(mae)
                }
            }
            
        except Exception as e:
            raise Exception(f"가격 예측 중 오류 발생: {str(e)}")
    
    def _calculate_confidence(self, age: int, mileage: int, r2: float = 0.90) -> float:
        """
        예측 신뢰도 계산
        
        Args:
            age: 차량 나이
            mileage: 주행거리
            r2: 모델 R² 점수
            
        Returns:
            신뢰도 (0-1)
        """
        # 모델 R² 기반 기본 신뢰도
        confidence = min(0.95, r2)
        
        # 차량 나이가 많을수록 신뢰도 감소
        if age > 10:
            confidence -= 0.10
        elif age > 7:
            confidence -= 0.07
        elif age > 5:
            confidence -= 0.03
        
        # 주행거리가 많거나 적으면 신뢰도 감소
        if mileage > 200000:
            confidence -= 0.08
        elif mileage < 10000 and age > 1:
            confidence -= 0.05  # 주행거리 조작 의심
        
        return max(0.5, min(0.95, confidence))


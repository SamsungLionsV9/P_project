"""
가격 예측 서비스
ML 모델을 사용한 중고차 가격 예측
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple

from ..utils.model_loader import get_model_loader


class PredictionService:
    """가격 예측 서비스"""
    
    def __init__(self):
        self.model_loader = get_model_loader()
        
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Feature Engineering (학습 시와 동일)
        
        Args:
            df: 입력 데이터프레임
            
        Returns:
            피처가 추가된 데이터프레임
        """
        current_year = 2025
        df['age'] = current_year - df['year']
        
        # Mileage features
        df['mileage_per_year'] = df['mileage'] / (df['age'] + 1)
        df['is_low_mileage'] = (df['mileage'] < 30000).astype(int)
        df['is_high_mileage'] = (df['mileage'] > 150000).astype(int)
        
        # Age groups
        df['age_group'] = pd.cut(
            df['age'], 
            bins=[-1, 1, 3, 5, 10, 100], 
            labels=['new', 'semi_new', 'used', 'old', 'very_old']
        )
        
        # Brand-fuel interaction
        df['brand_fuel'] = df['brand'] + '_' + df['fuel']
        
        # Model popularity (단일 예측 시 기본값 사용)
        df['model_popularity_log'] = 5.0
        
        # Premium brand
        premium_brands = ['제네시스', '벤츠', 'BMW', '아우디', '렉서스', '포르쉐']
        df['is_premium'] = df['brand'].isin(premium_brands).astype(int)
        
        # Premium interactions
        df['premium_age'] = df['is_premium'] * df['age']
        df['premium_mileage'] = df['is_premium'] * df['mileage']
        
        # Brand mileage (단일 예측 시 기본값)
        df['mileage_vs_brand_avg'] = 1.0
        
        # Eco-friendly
        df['is_eco'] = df['fuel'].str.contains('전기|하이브리드', na=False).astype(int)
        
        return df
    
    def predict_price(self, brand: str, model_name: str, year: int, 
                     mileage: int, fuel: str) -> Dict:
        """
        차량 가격 예측
        
        Args:
            brand: 제조사
            model_name: 모델명
            year: 연식
            mileage: 주행거리 (km)
            fuel: 연료 타입
            
        Returns:
            dict: {
                'predicted_price': float (만원),
                'price_range': [min, max] (만원),
                'confidence': float (0-1),
                'details': dict
            }
        """
        try:
            # 모델 로드
            model = self.model_loader.load_price_model()
            
            # 입력 데이터 준비
            input_data = pd.DataFrame({
                'brand': [brand],
                'model_name': [model_name],
                'year': [year],
                'mileage': [mileage],
                'fuel': [fuel]
            })
            
            # Feature Engineering
            input_data = self.create_features(input_data)
            
            # 피처 선택 (학습 시와 동일)
            feature_cols = [
                'brand', 'model_name', 'fuel', 'age', 'mileage',
                'mileage_per_year', 'is_low_mileage', 'is_high_mileage',
                'age_group', 'brand_fuel', 'model_popularity_log',
                'is_premium', 'premium_age', 'premium_mileage',
                'mileage_vs_brand_avg', 'is_eco'
            ]
            
            X = input_data[feature_cols]
            
            # 예측
            log_pred = model.predict(X)[0]
            pred_price = np.expm1(log_pred)
            
            # 가격 범위 계산 (±10%)
            margin = pred_price * 0.10
            price_range = [
                float(pred_price - margin),
                float(pred_price + margin)
            ]
            
            # 신뢰도 계산 (차량 나이와 주행거리 기반)
            age = input_data['age'].values[0]
            confidence = self._calculate_confidence(age, mileage)
            
            return {
                'predicted_price': float(pred_price),
                'price_range': price_range,
                'confidence': confidence,
                'details': {
                    'age': int(age),
                    'mileage_per_year': float(input_data['mileage_per_year'].values[0]),
                    'is_premium': bool(input_data['is_premium'].values[0]),
                    'is_eco': bool(input_data['is_eco'].values[0])
                }
            }
            
        except Exception as e:
            raise Exception(f"가격 예측 중 오류 발생: {str(e)}")
    
    def _calculate_confidence(self, age: int, mileage: int) -> float:
        """
        예측 신뢰도 계산
        
        Args:
            age: 차량 나이
            mileage: 주행거리
            
        Returns:
            신뢰도 (0-1)
        """
        confidence = 0.90  # 기본 신뢰도
        
        # 차량 나이가 많을수록 신뢰도 감소
        if age > 10:
            confidence -= 0.15
        elif age > 7:
            confidence -= 0.10
        elif age > 5:
            confidence -= 0.05
        
        # 주행거리가 많거나 적으면 신뢰도 감소
        if mileage > 200000:
            confidence -= 0.10
        elif mileage < 10000 and age > 1:
            confidence -= 0.05  # 주행거리 조작 의심
        
        return max(0.5, min(1.0, confidence))


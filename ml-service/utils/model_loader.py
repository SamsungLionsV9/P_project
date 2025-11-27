"""
ML 모델 로더
학습된 가격 예측 모델을 로드하고 관리
"""

import os
import joblib
from pathlib import Path


class ModelLoader:
    """ML 모델 로더 클래스"""
    
    def __init__(self):
        self.model = None
        self.model_path = None
        
    def load_price_model(self):
        """
        가격 예측 모델 로드
        
        Returns:
            모델 객체 또는 None
        """
        if self.model is not None:
            return self.model
        
        # 모델 경로 찾기
        possible_paths = [
            'improved_car_price_model.pkl',
            'car_price_model.pkl',
            'models/improved_car_price_model.pkl',
            'models/car_price_model.pkl',
            '../improved_car_price_model.pkl',
            '../car_price_model.pkl',
            '../models/improved_car_price_model.pkl',
            '../models/car_price_model.pkl',
        ]
        
        # 프로젝트 루트 기준으로도 검색
        project_root = Path(__file__).parent.parent.parent
        for path in possible_paths:
            full_path = project_root / path
            if full_path.exists():
                print(f"✓ 모델 로드: {full_path}")
                try:
                    self.model = joblib.load(full_path)
                    self.model_path = str(full_path)
                    return self.model
                except Exception as e:
                    print(f"⚠️ 모델 로드 실패 ({full_path}): {e}")
                    continue
        
        raise FileNotFoundError(
            "❌ 가격 예측 모델을 찾을 수 없습니다. "
            "train_model_improved.py를 실행하여 모델을 먼저 학습시켜주세요."
        )
    
    def get_model_info(self):
        """
        모델 정보 반환
        
        Returns:
            dict: 모델 정보
        """
        if self.model is None:
            return None
        
        return {
            "model_path": self.model_path,
            "model_type": type(self.model).__name__,
            "loaded": True
        }


# 싱글톤 인스턴스
_model_loader = ModelLoader()


def get_model_loader():
    """
    모델 로더 싱글톤 인스턴스 반환
    
    Returns:
        ModelLoader: 모델 로더 인스턴스
    """
    return _model_loader


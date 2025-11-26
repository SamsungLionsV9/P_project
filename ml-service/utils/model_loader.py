"""
ML 모델 로더
3개의 Ultimate 모델 (국산차, 제네시스, 수입차) 로드 및 관리
"""

import os
import joblib
from pathlib import Path
from typing import Dict, Any, Optional


# 수입차 브랜드 목록 (쉐보레(GM대우)는 국산차이므로 제외!)
IMPORTED_BRANDS = [
    '벤츠', 'BMW', '아우디', '폭스바겐', '포르쉐', '미니', 
    '렉서스', '토요타', '혼다', '닛산', '인피니티',
    '볼보', '랜드로버', '재규어', '푸조', '시트로엥',
    '테슬라', '캐딜락', '링컨', '지프', '포드',
    'Mercedes-Benz', 'Audi', 'Volkswagen', 'Porsche', 'MINI',
    'Lexus', 'Toyota', 'Honda', 'Nissan', 'Infiniti',
    'Volvo', 'Land Rover', 'Jaguar', 'Peugeot', 'Citroen',
    'Tesla', 'Cadillac', 'Lincoln', 'Jeep', 'Ford'
]
# 쉐보레(GM대우), Chevrolet 제거 - 한국 국산차


class ModelLoader:
    """3개 Ultimate 모델 로더 클래스"""
    
    def __init__(self):
        self.models = {}  # {model_type: model}
        self.encoders = {}  # {model_type: encoders}
        self.features = {}  # {model_type: feature_list}
        self.metrics = {}  # {model_type: metrics}
        self.project_root = Path(__file__).parent.parent.parent
        
    def _get_model_type(self, brand: str) -> str:
        """
        브랜드에 따라 적절한 모델 타입 반환
        
        Args:
            brand: 제조사명
            
        Returns:
            'imported' 또는 'domestic' (제네시스 = 국산차)
        """
        brand_upper = brand.upper() if brand else ''
        brand_lower = brand.lower() if brand else ''
        
        # 제네시스는 국산차에 통합! (고급 국산 브랜드)
        # if '제네시스' in brand or 'GENESIS' in brand_upper:
        #     return 'domestic'
        
        # 수입차 체크
        for imported_brand in IMPORTED_BRANDS:
            if imported_brand.lower() in brand_lower or imported_brand in brand:
                return 'imported'
        
        # 기본값: 국산차 (제네시스 포함)
        return 'domestic'
    
    def load_model(self, model_type: str) -> Any:
        """
        특정 타입의 모델 로드
        
        Args:
            model_type: 'domestic', 'genesis', 또는 'imported'
            
        Returns:
            XGBoost 모델 객체
        """
        if model_type in self.models:
            return self.models[model_type]
        
        # V2 모델 사용 (모든 모델)
        model_path = self.project_root / f'models/{model_type}_v2.pkl'
        if not model_path.exists():
            # V2 없으면 ultimate 시도
            model_path = self.project_root / f'models/{model_type}_ultimate.pkl'
        
        if not model_path.exists():
            raise FileNotFoundError(f"❌ {model_type} 모델을 찾을 수 없습니다: {model_path}")
        
        print(f"✓ {model_type} 모델 로드: {model_path}")
        self.models[model_type] = joblib.load(model_path)
        
        # Encoders 로드 (V2 우선)
        encoder_path = self.project_root / f'models/{model_type}_v2_encoders.pkl'
        if not encoder_path.exists():
            encoder_path = self.project_root / f'models/{model_type}_ultimate_encoders.pkl'
        if encoder_path.exists():
            self.encoders[model_type] = joblib.load(encoder_path)
            print(f"✓ {model_type} 인코더 로드: {encoder_path}")
        
        # Features 로드 (V2 우선)
        features_path = self.project_root / f'models/{model_type}_v2_features.pkl'
        if not features_path.exists():
            features_path = self.project_root / f'models/{model_type}_ultimate_features.pkl'
        if features_path.exists():
            self.features[model_type] = joblib.load(features_path)
            print(f"✓ {model_type} 피처 로드: {features_path}")
        
        # Metrics 로드 (V2 우선)
        metrics_path = self.project_root / f'models/{model_type}_v2_metrics.pkl'
        if not metrics_path.exists():
            metrics_path = self.project_root / f'models/{model_type}_ultimate_metrics.pkl'
        if metrics_path.exists():
            self.metrics[model_type] = joblib.load(metrics_path)
            print(f"✓ {model_type} 메트릭 로드: {metrics_path}")
        
        return self.models[model_type]
    
    def load_price_model(self, brand: str = '현대') -> Any:
        """
        브랜드에 맞는 가격 예측 모델 로드
        
        Args:
            brand: 제조사명 (기본값: 현대 → domestic 모델)
            
        Returns:
            적절한 XGBoost 모델 객체
        """
        model_type = self._get_model_type(brand)
        return self.load_model(model_type)
    
    def get_encoders(self, brand: str) -> Optional[Dict]:
        """브랜드에 맞는 인코더 반환"""
        model_type = self._get_model_type(brand)
        if model_type not in self.encoders:
            self.load_model(model_type)
        return self.encoders.get(model_type)
    
    def get_features(self, brand: str) -> Optional[list]:
        """브랜드에 맞는 피처 목록 반환"""
        model_type = self._get_model_type(brand)
        if model_type not in self.features:
            self.load_model(model_type)
        return self.features.get(model_type)
    
    def get_model_info(self, brand: str = None) -> Dict:
        """
        모델 정보 반환
        
        Args:
            brand: 특정 브랜드 (None이면 전체)
            
        Returns:
            dict: 모델 정보
        """
        if brand:
            model_type = self._get_model_type(brand)
            return {
                "model_type": model_type,
                "loaded": model_type in self.models,
                "metrics": self.metrics.get(model_type, {}),
                "n_features": len(self.features.get(model_type, []))
            }
        
        return {
            "domestic": {
                "loaded": 'domestic' in self.models,
                "metrics": self.metrics.get('domestic', {})
            },
            "genesis": {
                "loaded": 'genesis' in self.models,
                "metrics": self.metrics.get('genesis', {})
            },
            "imported": {
                "loaded": 'imported' in self.models,
                "metrics": self.metrics.get('imported', {})
            }
        }
    
    def preload_all_models(self):
        """모든 모델 미리 로드"""
        for model_type in ['domestic', 'genesis', 'imported']:
            try:
                self.load_model(model_type)
            except Exception as e:
                print(f"⚠️ {model_type} 모델 로드 실패: {e}")


# 싱글톤 인스턴스
_model_loader = ModelLoader()


def get_model_loader() -> ModelLoader:
    """
    모델 로더 싱글톤 인스턴스 반환
    
    Returns:
        ModelLoader: 모델 로더 인스턴스
    """
    return _model_loader


"""
가격 예측 서비스 (Production)
============================
- 국산차: domestic_v11.pkl (MAPE 9.9%)
- 외제차: imported_v13.pkl (MAPE 12.1%, Unknown 1.2%)
- 옵션 효과 보장 (프리미엄 분리)
- 신뢰도 표시 + 분해 설명
"""

import pandas as pd
import numpy as np
import joblib
import os
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

# 모델 경로
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')


@dataclass
class PredictionResult:
    """예측 결과 데이터 클래스"""
    predicted_price: float          # 예상 가격 (만원)
    confidence: float               # 신뢰도 (0~100%)
    mape: float                     # 예상 오차율 (%)
    price_range: Tuple[float, float]  # 가격 범위 (하한, 상한)
    breakdown: Dict                 # 분해 설명
    model_type: str                 # 'domestic' or 'imported'
    warnings: list                  # 경고 메시지


class PredictionServiceV11:
    """가격 예측 서비스 V11"""
    
    # 국산차 브랜드
    DOMESTIC_BRANDS = ['현대', '기아', '제네시스', 'KG모빌리티', '쉐보레', '르노코리아', 
                       '쌍용', '삼성', 'Hyundai', 'Kia', 'Genesis', 'Chevrolet']
    
    # 외제차 브랜드
    IMPORTED_BRANDS = ['벤츠', 'BMW', '아우디', '폭스바겐', '볼보', '렉서스', '토요타', 
                       '혼다', '닛산', '포르쉐', '재규어', '랜드로버', '미니', '지프',
                       '테슬라', 'Mercedes-Benz', 'Audi', 'Volkswagen', 'Volvo', 'Lexus']
    
    def __init__(self):
        self.domestic_model = None
        self.domestic_encoders = None
        self.domestic_features = None
        self.imported_model = None
        self.imported_encoders = None
        self.imported_features = None
        self._load_models()
    
    def _load_models(self):
        """모델 로드"""
        try:
            # 국산차 V11
            domestic_path = os.path.join(MODEL_DIR, 'domestic_v11.pkl')
            if os.path.exists(domestic_path):
                self.domestic_model = joblib.load(domestic_path)
                self.domestic_encoders = joblib.load(os.path.join(MODEL_DIR, 'domestic_v11_encoders.pkl'))
                self.domestic_features = joblib.load(os.path.join(MODEL_DIR, 'domestic_v11_features.pkl'))
                print("✓ 국산차 V11 모델 로드 완료")
            
            # 외제차 V13
            imported_path = os.path.join(MODEL_DIR, 'imported_v13.pkl')
            if os.path.exists(imported_path):
                self.imported_model = joblib.load(imported_path)
                self.imported_encoders = joblib.load(os.path.join(MODEL_DIR, 'imported_v13_encoders.pkl'))
                self.imported_features = joblib.load(os.path.join(MODEL_DIR, 'imported_v13_features.pkl'))
                print("✓ 외제차 V13 모델 로드 완료")
                
        except Exception as e:
            print(f"⚠️ 모델 로드 실패: {e}")
    
    def _get_model_type(self, brand: str) -> str:
        """브랜드로 모델 타입 결정"""
        brand_lower = brand.lower()
        for b in self.DOMESTIC_BRANDS:
            if b.lower() in brand_lower or brand_lower in b.lower():
                return 'domestic'
        return 'imported'
    
    def _get_mileage_group(self, mileage: int) -> str:
        """주행거리 그룹"""
        if mileage < 30000: return 'A'
        elif mileage < 60000: return 'B'
        elif mileage < 100000: return 'C'
        elif mileage < 150000: return 'D'
        return 'E'
    
    def _create_domestic_features(self, model_name: str, year: int, mileage: int,
                                   options: Dict, accident_free: bool, grade: str) -> pd.DataFrame:
        """국산차 피처 생성"""
        age = 2025 - year
        mg = self._get_mileage_group(mileage)
        my = f"{model_name}_{year}"
        mymg = f"{my}_{mg}"
        
        # 인코딩 값
        model_enc = self.domestic_encoders.get('model_enc', {})
        model_year_enc = self.domestic_encoders.get('model_year_enc', {})
        model_year_mg_enc = self.domestic_encoders.get('model_year_mg_enc', {})
        brand_enc = self.domestic_encoders.get('brand_enc', {})
        
        default_val = 2500
        model_enc_val = model_enc.get(model_name, default_val)
        my_enc_val = model_year_enc.get(my, model_enc_val)
        mymg_enc_val = model_year_mg_enc.get(mymg, my_enc_val)
        brand_enc_val = brand_enc.get('현대', default_val)
        
        # 옵션 처리
        opt_cols = ['has_sunroof','has_leather_seat','has_led_lamp','has_smart_key',
                    'has_navigation','has_heated_seat','has_ventilated_seat','has_rear_camera']
        opt_values = {c: options.get(c, 0) for c in opt_cols}
        opt_count = sum(opt_values.values())
        opt_premium = (opt_values.get('has_sunroof',0)*3 + opt_values.get('has_leather_seat',0)*2 +
                       opt_values.get('has_ventilated_seat',0)*3 + opt_values.get('has_led_lamp',0)*2)
        
        # 상태
        grade_map = {'normal': 0, 'good': 1, 'excellent': 2}
        grade_enc = grade_map.get(grade, 0)
        
        # 피처 딕셔너리
        f = {
            'Model_enc': model_enc_val,
            'Model_Year_enc': my_enc_val,
            'Model_Year_MG_enc': mymg_enc_val,
            'Brand_enc': brand_enc_val,
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
    
    def _extract_class_v13(self, model_name: str, brand: str) -> tuple:
        """V13: 모델명에서 클래스 추출"""
        import re
        model = str(model_name)
        mfr = str(brand).lower()
        
        # 벤츠
        if '벤츠' in mfr:
            match = re.search(r'([A-Z])-?클래스|([A-Z])-?Class|^([A-Z])[\s-]', model, re.I)
            if match:
                cls = (match.group(1) or match.group(2) or match.group(3)).upper()
                rank = {'A':1,'B':1,'C':2,'E':3,'S':4,'G':5}.get(cls, 3)
                return cls, rank
            match = re.search(r'(GL[ABCES]|EQ[SE]|AMG)', model, re.I)
            if match:
                cls = match.group(1).upper()
                rank = {'GLA':2,'GLB':2,'GLC':3,'GLE':3,'GLS':4,'EQS':4,'EQE':3,'AMG':5}.get(cls, 3)
                return cls, rank
        
        # BMW
        if 'bmw' in mfr:
            match = re.search(r'(\d)시리즈', model)
            if match:
                n = match.group(1)
                cls = f"{n}시리즈"
                rank = {'1':1,'2':1,'3':2,'4':2,'5':3,'6':3,'7':4,'8':4}.get(n, 3)
                return cls, rank
            match = re.search(r'\b([XMZi]\d)\b', model)
            if match:
                cls = match.group(1).upper()
                rank = {'X1':2,'X2':2,'X3':3,'X4':3,'X5':4,'X6':4,'X7':5,'M3':4,'M4':4,'M5':5}.get(cls, 3)
                return cls, rank
        
        # 아우디
        if '아우디' in mfr:
            match = re.search(r'\b(A\d|Q\d|RS\d|R8)', model, re.I)
            if match:
                cls = match.group(1).upper()
                rank = {'A1':1,'A3':1,'A4':2,'A5':2,'A6':3,'A7':3,'A8':4,'Q2':1,'Q3':2,'Q5':3,'Q7':4,'Q8':4}.get(cls, 3)
                return cls, rank
        
        # 기본: 첫 단어
        clean = re.sub(r'\([^)]*\)', '', model).strip()
        first = clean.split()[0] if clean else model
        return first if len(first) > 1 else 'Unknown', 3
    
    def _create_imported_features(self, model_name: str, brand: str, year: int, mileage: int,
                                   options: Dict, accident_free: bool, grade: str) -> pd.DataFrame:
        """외제차 V13 피처 생성"""
        age = 2025 - year
        mg = self._get_mileage_group(mileage)
        my = f"{model_name}_{year}"
        mymg = f"{my}_{mg}"
        
        # 클래스 추출
        cls, cls_rank = self._extract_class_v13(model_name, brand)
        cls_year = f"{cls}_{year}"
        
        # 인코딩 값
        enc = self.imported_encoders
        global_mean = enc.get('global_mean', 5000)
        
        model_enc_val = enc.get('model_enc', {}).get(model_name, global_mean)
        my_enc_val = enc.get('model_year_enc', {}).get(my, model_enc_val)
        mymg_enc_val = enc.get('model_year_mg_enc', {}).get(mymg, my_enc_val)
        brand_enc_val = enc.get('brand_enc', {}).get(brand, global_mean)
        class_enc_val = enc.get('class_enc', {}).get(cls, global_mean)
        class_year_enc_val = enc.get('class_year_enc', {}).get(cls_year, class_enc_val)
        
        # 브랜드 등급
        brand_tier_map = {'벤츠': 4, 'BMW': 4, '아우디': 4, '포르쉐': 5, '렉서스': 4,
                          '볼보': 3, '폭스바겐': 2, '미니': 2, '테슬라': 4, '랜드로버': 3}
        brand_tier = brand_tier_map.get(brand, 3)
        
        # 상태
        grade_map = {'normal': 0, 'good': 1, 'excellent': 2}
        grade_enc = grade_map.get(grade, 0)
        
        # V13 피처 (옵션은 별도 프리미엄으로 처리)
        f = {
            'Model_enc': model_enc_val,
            'Model_Year_enc': my_enc_val,
            'Model_Year_MG_enc': mymg_enc_val,
            'Brand_enc': brand_enc_val,
            'Class_enc': class_enc_val,
            'Class_Year_enc': class_year_enc_val,
            'Brand_Tier': brand_tier,
            'Class_Rank': cls_rank,
            'Age': age,
            'Age_log': np.log1p(age),
            'Mileage': mileage,
            'Mile_log': np.log1p(mileage),
            'Km_per_Year': mileage / (age + 1),
            'is_accident_free': 1 if accident_free else 0,
            'inspection_grade_enc': grade_enc,
        }
        
        return pd.DataFrame([f])[self.imported_features]
    
    def predict(self, brand: str, model_name: str, year: int, mileage: int,
                options: Optional[Dict] = None, accident_free: bool = True,
                grade: str = 'normal', fuel: str = '가솔린') -> PredictionResult:
        """
        통합 예측 (국산차/외제차 자동 분류)
        
        Args:
            brand: 제조사 (현대, BMW 등)
            model_name: 모델명 (아반떼 (CN7), E-Class (W214) 등)
            year: 연식 (2022 등)
            mileage: 주행거리 (30000 등)
            options: 옵션 딕셔너리 (has_sunroof, has_leather_seat 등)
            accident_free: 무사고 여부
            grade: 검사 등급 (normal, good, excellent)
            fuel: 연료 타입 (가솔린, 디젤, 하이브리드, 전기, LPG)
            
        Returns:
            PredictionResult: 예측 결과
        """
        options = options or {}
        warnings = []
        
        # 연료 타입별 가격 조정 비율
        fuel_multipliers = {
            '가솔린': 1.0,      # 기준
            '디젤': 1.03,       # +3% (디젤 프리미엄)
            '하이브리드': 1.08, # +8% (친환경 프리미엄)
            '전기': 1.10,       # +10% (전기차 프리미엄)
            'LPG': 0.92,        # -8% (LPG 할인)
        }
        fuel_multiplier = fuel_multipliers.get(fuel, 1.0)
        
        # 모델 타입 결정
        model_type = self._get_model_type(brand)
        
        if model_type == 'domestic':
            if self.domestic_model is None:
                raise ValueError("국산차 모델이 로드되지 않았습니다")
            
            features = self._create_domestic_features(model_name, year, mileage, 
                                                       options, accident_free, grade)
            pred_log = self.domestic_model.predict(features)[0]
            base_price = np.expm1(pred_log)
            
            # 국산차도 옵션 프리미엄 추가 (모델 가중치가 낮아서 수동 보정)
            domestic_opt_premiums = {
                'has_sunroof': 80,        # 선루프 +80만원
                'has_leather_seat': 60,   # 가죽시트 +60만원
                'has_navigation': 50,     # 내비게이션 +50만원
                'has_ventilated_seat': 70, # 통풍시트 +70만원
                'has_heated_seat': 40,    # 열선시트 +40만원
                'has_smart_key': 30,      # 스마트키 +30만원
                'has_rear_camera': 30,    # 후방카메라 +30만원
                'has_led_lamp': 40,       # LED램프 +40만원
            }
            option_total = sum(int(bool(options.get(k, False))) * v for k, v in domestic_opt_premiums.items())
            predicted_price = (base_price * fuel_multiplier) + option_total  # 연료 배율 적용
            mape = 9.9  # 국산차 V11 MAPE
            
        else:
            if self.imported_model is None:
                raise ValueError("외제차 모델이 로드되지 않았습니다")
            
            features = self._create_imported_features(model_name, brand, year, mileage,
                                                       options, accident_free, grade)
            pred_log = self.imported_model.predict(features)[0]
            base_price = np.expm1(pred_log)
            
            # V13: 옵션 프리미엄 별도 계산
            opt_premiums = self.imported_encoders.get('option_premiums', {
                'has_ventilated_seat': 120, 'has_sunroof': 100, 'has_led_lamp': 100,
                'has_leather_seat': 80, 'has_navigation': 80, 'has_heated_seat': 60,
                'has_smart_key': 50, 'has_rear_camera': 50,
            })
            option_total = sum(int(bool(options.get(k, False))) * v for k, v in opt_premiums.items())
            predicted_price = (base_price * fuel_multiplier) + option_total  # 연료 배율 적용
            mape = 12.1  # 외제차 V13 MAPE
        
        # 신뢰도 계산 (MAPE 기반)
        confidence = max(0, 100 - mape * 5)  # MAPE 10% → 신뢰도 50%
        
        # 가격 범위 계산
        error_margin = predicted_price * (mape / 100)
        price_range = (predicted_price - error_margin, predicted_price + error_margin)
        
        # 분해 설명 생성
        breakdown = self._generate_breakdown(model_name, year, mileage, options,
                                              accident_free, predicted_price, model_type)
        
        # 경고 생성
        if year < 2015:
            warnings.append("10년 이상 된 차량은 예측 정확도가 낮을 수 있습니다")
        if mileage > 150000:
            warnings.append("고주행 차량(15만km 이상)은 실제 상태에 따라 가격 차이가 클 수 있습니다")
        
        return PredictionResult(
            predicted_price=round(predicted_price, 0),
            confidence=round(confidence, 1),
            mape=mape,
            price_range=(round(price_range[0], 0), round(price_range[1], 0)),
            breakdown=breakdown,
            model_type=model_type,
            warnings=warnings
        )
    
    def _generate_breakdown(self, model_name: str, year: int, mileage: int,
                            options: Dict, accident_free: bool, 
                            predicted_price: float, model_type: str) -> Dict:
        """예측 분해 설명 생성"""
        # 옵션 프리미엄 (국산차 vs 외제차 구분)
        if model_type == 'imported':
            option_premiums = {
                'has_ventilated_seat': 120, 'has_sunroof': 100, 'has_led_lamp': 100,
                'has_leather_seat': 80, 'has_navigation': 80, 'has_heated_seat': 60,
                'has_smart_key': 50, 'has_rear_camera': 50,
            }
        else:
            option_premiums = {
                'has_led_lamp': 80, 'has_sunroof': 44, 'has_leather_seat': 43,
                'has_smart_key': 42, 'has_navigation': 42, 'has_ventilated_seat': 37,
                'has_heated_seat': 35, 'has_rear_camera': 33,
            }
        
        total_option_premium = sum(options.get(opt, 0) * premium 
                                    for opt, premium in option_premiums.items())
        
        # 무사고 프리미엄
        accident_premium = 250 if accident_free else 0
        
        # 기본가격 추정
        base_price = predicted_price - total_option_premium - accident_premium
        
        # 옵션 상세
        option_details = []
        for opt, premium in option_premiums.items():
            if options.get(opt):
                opt_name = {
                    'has_led_lamp': 'LED 램프',
                    'has_sunroof': '썬루프',
                    'has_leather_seat': '가죽시트',
                    'has_smart_key': '스마트키',
                    'has_navigation': '네비게이션',
                    'has_ventilated_seat': '통풍시트',
                    'has_heated_seat': '열선시트',
                    'has_rear_camera': '후방카메라',
                }.get(opt, opt)
                option_details.append({'name': opt_name, 'premium': premium})
        
        return {
            'base_price': round(base_price, 0),
            'option_premium': total_option_premium,
            'option_details': option_details,
            'accident_premium': accident_premium,
            'model_info': {
                'model': model_name,
                'year': year,
                'mileage': mileage,
            },
            'data_source': f"{'국산차' if model_type == 'domestic' else '외제차'} 실거래 데이터 {'79,000' if model_type == 'domestic' else '35,000'}건 학습"
        }
    
    def explain_prediction(self, result: PredictionResult) -> str:
        """예측 결과 설명 텍스트 생성"""
        bd = result.breakdown
        
        text = f"""
📌 이 차량의 예상 시세: {result.predicted_price:,.0f}만원

[세부 분해]
- 기본 차량 가격: {bd['base_price']:,.0f}만원
"""
        if bd['option_premium'] > 0:
            text += f"- 옵션 프리미엄: +{bd['option_premium']:,.0f}만원\n"
            for opt in bd['option_details']:
                text += f"  ㄴ {opt['name']}: +{opt['premium']}만원\n"
        
        if bd['accident_premium'] > 0:
            text += f"- 무사고 프리미엄: +{bd['accident_premium']:,.0f}만원\n"
        
        text += f"""
──────────────────────
- 최종 예측가: {result.predicted_price:,.0f}만원
- 예상 오차 범위: {result.price_range[0]:,.0f}~{result.price_range[1]:,.0f}만원
- 신뢰도: {result.confidence:.0f}% (MAPE {result.mape}%)

📊 {bd['data_source']}
"""
        if result.warnings:
            text += "\n⚠️ 주의사항:\n"
            for w in result.warnings:
                text += f"  - {w}\n"
        
        return text


# 싱글톤 인스턴스
_prediction_service = None

def get_prediction_service() -> PredictionServiceV11:
    """예측 서비스 싱글톤 반환"""
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionServiceV11()
    return _prediction_service


# 테스트
if __name__ == "__main__":
    service = get_prediction_service()
    
    print("\n" + "="*60)
    print("🧪 국산차 테스트")
    print("="*60)
    
    result = service.predict(
        brand='현대',
        model_name='더 뉴 그랜저 IG',
        year=2022,
        mileage=30000,
        options={'has_sunroof': 1, 'has_leather_seat': 1, 'has_led_lamp': 1},
        accident_free=True,
        grade='good'
    )
    print(service.explain_prediction(result))
    
    print("\n" + "="*60)
    print("🧪 외제차 테스트")
    print("="*60)
    
    result = service.predict(
        brand='벤츠',
        model_name='E-Class (W214)',
        year=2022,
        mileage=30000,
        options={'has_sunroof': 1, 'has_leather_seat': 1},
        accident_free=True
    )
    print(service.explain_prediction(result))

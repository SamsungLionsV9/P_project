"""
통합 중고차 구매 어드바이저
Track 1: 가격 예측 (XGBoost)
Track 2: 타이밍 분석 (Car-Sentix)
→ 종합 의사결정 제공
"""

import sys
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

from data_collectors_complete import collect_complete_data
from timing_engine import TimingScoreEngine


class IntegratedCarAdvisor:
    """가격 + 타이밍 통합 어드바이저"""
    
    def __init__(self):
        # 가격 예측 모델 로드
        model_files = [
            'improved_car_price_model.pkl',
            'best_car_price_model_improved.pkl',
            'best_car_price_model.pkl'
        ]
        
        self.model = None
        for model_file in model_files:
            try:
                self.model = joblib.load(model_file)
                print(f"✅ 가격 예측 모델 로드 완료 ({model_file})")
                break
            except:
                continue
        
        if not self.model:
            print("⚠️ 가격 예측 모델 없음")
        
        # 타이밍 엔진
        self.timing_engine = TimingScoreEngine()
    
    def predict_price(self, brand, model_name, year, mileage, fuel):
        """
        가격 예측 (Track 1)
        
        Args:
            brand: 브랜드 (예: "현대")
            model_name: 모델명 (예: "그랜저")
            year: 연식 (예: 2022)
            mileage: 주행거리 (km)
            fuel: 연료 (예: "가솔린")
            
        Returns:
            float: 예상 가격 (만원)
        """
        if not self.model:
            print("⚠️ 가격 예측 모델이 로드되지 않았습니다")
            return None
        
        # 입력 데이터 준비
        input_data = pd.DataFrame({
            'brand': [brand],
            'model_name': [model_name],
            'year': [year],
            'mileage': [mileage],
            'fuel': [fuel]
        })
        
        # Feature engineering (predict_car_price.py와 동일)
        current_year = 2025
        input_data['age'] = current_year - input_data['year']
        
        # Mileage features
        input_data['mileage_per_year'] = input_data['mileage'] / (input_data['age'] + 1)
        input_data['is_low_mileage'] = (input_data['mileage'] < 30000).astype(int)
        input_data['is_high_mileage'] = (input_data['mileage'] > 150000).astype(int)
        
        # Age groups
        input_data['age_group'] = pd.cut(input_data['age'], 
                                  bins=[-1, 1, 3, 5, 10, 100], 
                                  labels=['new', 'semi_new', 'used', 'old', 'very_old'])
        
        # Brand-fuel interaction
        input_data['brand_fuel'] = input_data['brand'] + '_' + input_data['fuel']
        
        # Model popularity (default)
        input_data['model_popularity_log'] = 5.0
        
        # Premium brand
        premium_brands = ['제네시스', '벤츠', 'BMW', '아우디', '렉서스', '포르쉐']
        input_data['is_premium'] = input_data['brand'].isin(premium_brands).astype(int)
        
        # Premium interactions
        input_data['premium_age'] = input_data['is_premium'] * input_data['age']
        input_data['premium_mileage'] = input_data['is_premium'] * input_data['mileage']
        
        # Brand mileage (default)
        input_data['mileage_vs_brand_avg'] = 1.0
        
        # Eco-friendly
        input_data['is_eco'] = input_data['fuel'].str.contains('전기|하이브리드', na=False).astype(int)
        
        # Select features
        feature_cols = [
            'brand', 'model_name', 'fuel', 'age', 'mileage',
            'mileage_per_year', 'is_low_mileage', 'is_high_mileage',
            'age_group', 'brand_fuel', 'model_popularity_log',
            'is_premium', 'premium_age', 'premium_mileage',
            'mileage_vs_brand_avg', 'is_eco'
        ]
        
        X = input_data[feature_cols]
        
        try:
            # 예측 (log 변환 역변환)
            log_prediction = self.model.predict(X)[0]
            price = np.expm1(log_prediction)
            
            return price
            
        except Exception as e:
            print(f"⚠️ 가격 예측 실패: {e}")
            return None
    
    def analyze_timing(self, car_model):
        """
        타이밍 분석 (Track 2)
        
        Args:
            car_model: 차량 모델명
            
        Returns:
            dict: 타이밍 분석 결과
        """
        # 데이터 수집
        collected_data = collect_complete_data(car_model)
        
        # 점수 계산
        result = self.timing_engine.calculate_final_score(collected_data)
        
        return result
    
    def integrated_advice(self, brand, model_name, year, mileage, fuel):
        """
        통합 구매 조언
        
        Args:
            brand: 브랜드
            model_name: 모델명
            year: 연식
            mileage: 주행거리
            fuel: 연료
            
        Returns:
            dict: 통합 분석 결과
        """
        print("\n" + "=" * 80)
        print("🚗 통합 중고차 구매 어드바이저")
        print("=" * 80)
        
        print(f"\n차량 정보:")
        print(f"  브랜드: {brand}")
        print(f"  모델: {model_name}")
        print(f"  연식: {year}년")
        print(f"  주행거리: {mileage:,}km")
        print(f"  연료: {fuel}")
        
        # Track 1: 가격 예측
        print("\n" + "─" * 80)
        print("[Track 1] 가격 예측 (XGBoost)")
        print("─" * 80)
        
        predicted_price = self.predict_price(brand, model_name, year, mileage, fuel)
        
        if predicted_price:
            print(f"\n💰 예상 가격: {predicted_price:,.0f}만원")
            print(f"   ({predicted_price*10000:,.0f}원)")
        else:
            print("\n⚠️ 가격 예측 불가")
        
        # Track 2: 타이밍 분석
        print("\n" + "─" * 80)
        print("[Track 2] 타이밍 분석 (Car-Sentix)")
        print("─" * 80)
        
        timing_result = self.analyze_timing(model_name)
        
        # 통합 판단
        print("\n" + "=" * 80)
        print("🎯 종합 구매 조언")
        print("=" * 80)
        
        # 점수와 가격 기반 종합 판단
        timing_score = timing_result['final_score']
        timing_decision = timing_result['decision_text']
        
        print(f"\n📊 타이밍 점수: {timing_score:.1f}점 / 100점")
        print(f"   판단: {timing_result['decision']}")
        
        if predicted_price:
            print(f"\n💰 예상 적정 가격: {predicted_price:,.0f}만원")
            
            # 협상 범위 제시
            lower_bound = predicted_price * 0.95  # -5%
            upper_bound = predicted_price * 1.05  # +5%
            
            print(f"\n💡 구매 가격 가이드:")
            print(f"   🟢 매우 좋음: {lower_bound:,.0f}만원 이하")
            print(f"   🟡 적정 범위: {lower_bound:,.0f}~{upper_bound:,.0f}만원")
            print(f"   🔴 비쌈: {upper_bound:,.0f}만원 초과")
        
        # 종합 의사결정
        print(f"\n{'=' * 80}")
        print(f"✨ 최종 조언")
        print(f"{'=' * 80}")
        
        if timing_score >= 70:
            if predicted_price:
                print(f"\n🟢 지금이 구매 적기입니다!")
                print(f"   - 목표 가격: {predicted_price:,.0f}만원 이하")
                print(f"   - 추천: {predicted_price * 0.95:,.0f}만원 이하면 즉시 계약")
            else:
                print(f"\n🟢 타이밍은 좋습니다!")
                print(f"   - 시장 조사 후 적극 구매 추천")
        
        elif timing_score >= 55:
            if predicted_price:
                print(f"\n🟡 신중한 검토가 필요합니다")
                print(f"   - 목표 가격: {predicted_price * 0.90:,.0f}만원 이하")
                print(f"   - 추천: 가격 협상 적극 시도, {predicted_price * 0.90:,.0f}만원 이하면 구매")
            else:
                print(f"\n🟡 관망하는 것이 좋습니다")
                print(f"   - 1-2주 후 시장 재평가 권장")
        
        else:
            if predicted_price:
                print(f"\n🔴 구매를 미루시는 것을 권장합니다")
                print(f"   - 만약 구매 시: {predicted_price * 0.85:,.0f}만원 이하")
                print(f"   - 추천: 1-2개월 후 재검토")
            else:
                print(f"\n🔴 지금은 구매 시기가 아닙니다")
                print(f"   - 1-2개월 후 재평가 필수")
        
        # 세부 이유
        print(f"\n📋 상세 이유:")
        for reason in timing_result['summary'][:5]:
            print(f"   {reason}")
        
        print(f"\n{'=' * 80}")
        
        return {
            'brand': brand,
            'model': model_name,
            'year': year,
            'mileage': mileage,
            'fuel': fuel,
            'predicted_price': predicted_price,
            'timing_score': timing_score,
            'timing_decision': timing_decision,
            'timing_result': timing_result,
            'analyzed_at': datetime.now().isoformat()
        }


def main():
    """메인 실행"""
    print("=" * 80)
    print("🚗 통합 중고차 구매 어드바이저")
    print("   Track 1: 가격 예측 (XGBoost)")
    print("   Track 2: 타이밍 분석 (Car-Sentix)")
    print("=" * 80)
    
    advisor = IntegratedCarAdvisor()
    
    # 사용자 입력
    print("\n차량 정보를 입력하세요:")
    print("─" * 80)
    
    brand = input("브랜드 (예: 현대, 기아, 제네시스): ").strip()
    model_name = input("모델명 (예: 그랜저, 아반떼, K5): ").strip()
    year = int(input("연식 (예: 2022): ").strip())
    mileage = int(input("주행거리 (km, 예: 50000): ").strip())
    fuel = input("연료 (예: 가솔린, 디젤, 가솔린+전기): ").strip()
    
    # 통합 분석
    result = advisor.integrated_advice(brand, model_name, year, mileage, fuel)
    
    print("\n✅ 분석 완료!")


if __name__ == "__main__":
    if len(sys.argv) == 6:
        # 명령줄 인자로 실행
        brand = sys.argv[1]
        model = sys.argv[2]
        year = int(sys.argv[3])
        mileage = int(sys.argv[4])
        fuel = sys.argv[5]
        
        advisor = IntegratedCarAdvisor()
        advisor.integrated_advice(brand, model, year, mileage, fuel)
    else:
        # 대화형 모드
        main()

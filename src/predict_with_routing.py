"""
3-Model 자동 라우팅 예측 시스템
- 브랜드에 따라 최적 모델 자동 선택
- 일반 국산차 / 제네시스 / 수입차
"""
import joblib
import pandas as pd
import numpy as np
import os

class CarPricePredictor:
    """3-Model 통합 예측기"""
    
    def __init__(self, models_dir='../models'):
        """모델 로드"""
        print("🚀 3-Model 시스템 초기화...")
        
        self.regular_model = joblib.load(os.path.join(models_dir, 'regular_domestic_model.pkl'))
        print("  ✓ 일반 국산차 모델 로드")
        
        self.genesis_model = joblib.load(os.path.join(models_dir, 'genesis_car_price_model.pkl'))
        print("  ✓ 제네시스 모델 로드")
        
        self.imported_model = joblib.load(os.path.join(models_dir, 'imported_car_price_model.pkl'))
        print("  ✓ 수입차 모델 로드")
        
        # 브랜드 분류
        self.domestic_brands = ['현대', '기아', '쉐보레(GM대우)', 'KG모빌리티(쌍용)', '르노코리아(삼성)', '기타 제조사']
        
        print("✅ 초기화 완료!\n")
    
    def select_model(self, brand):
        """브랜드에 따라 모델 선택"""
        if brand == '제네시스':
            return self.genesis_model, 'genesis'
        elif brand in self.domestic_brands:
            return self.regular_model, 'regular_domestic'
        else:
            return self.imported_model, 'imported'
    
    def prepare_features(self, data, model_type):
        """모델 타입에 맞는 피처 준비"""
        df = data.copy()
        current_year = 2025
        
        df['age'] = current_year - df['year']
        df['mileage_per_year'] = df['mileage'] / (df['age'] + 1)
        df['is_low_mileage'] = (df['mileage'] < 30000).astype(int)
        df['age_group'] = pd.cut(df['age'], 
                                  bins=[-1, 1, 3, 5, 10, 100], 
                                  labels=['new', 'semi_new', 'used', 'old', 'very_old'])
        
        model_counts = df['model_name'].value_counts()
        df['model_popularity'] = df['model_name'].map(model_counts).fillna(1)
        df['model_popularity_log'] = np.log1p(df['model_popularity'])
        
        df['is_eco'] = df['fuel'].str.contains('전기|하이브리드', na=False).astype(int)
        
        if model_type == 'regular_domestic':
            df['is_high_mileage'] = (df['mileage'] > 150000).astype(int)
            df['age_mileage_interaction'] = df['age'] * np.log1p(df['mileage'])
            df['brand_fuel'] = df['brand'] + '_' + df['fuel']
            
            brand_price_mean = df.groupby('brand')['price'].transform('mean').fillna(2000)
            df['brand_price_tier'] = pd.cut(brand_price_mean, bins=3, labels=['budget', 'mid', 'premium'])
            
            feature_cols = ['brand', 'model_name', 'fuel', 'age_group', 'brand_fuel', 'brand_price_tier',
                           'age', 'mileage', 'mileage_per_year', 'is_low_mileage', 'is_high_mileage',
                           'model_popularity_log', 'age_mileage_interaction', 'is_eco']
        
        elif model_type == 'genesis':
            df['is_high_mileage'] = (df['mileage'] > 100000).astype(int)
            df['model_tier'] = 'mid'
            df.loc[df['model_name'].str.contains('G70|GV70', na=False), 'model_tier'] = 'entry'
            df.loc[df['model_name'].str.contains('G90|GV90', na=False), 'model_tier'] = 'luxury'
            df['is_suv'] = df['model_name'].str.contains('GV', na=False).astype(int)
            
            model_price_map = {'G70': 4500, 'G80': 5500, 'G90': 9000,
                              'GV70': 5000, 'GV80': 6500, 'GV90': 10000}
            def get_base_price(model_name):
                for key, price in model_price_map.items():
                    if key in str(model_name):
                        return price
                return 5000
            df['model_base_price'] = df['model_name'].apply(get_base_price)
            
            df['depreciation_rate'] = (1 - (df['age'] * 0.12)).clip(0.3, 1.0)
            df['rarity_score'] = 1 / (df['model_popularity'] + 1)
            
            model_price_mean = df.groupby('model_name')['price'].transform('mean').fillna(5000)
            df['is_high_trim'] = (df['price'] > model_price_mean * 1.1).astype(int)
            
            df['condition_score'] = (df['mileage_per_year'] / 15000).clip(0, 3)
            
            feature_cols = ['model_name', 'fuel', 'age_group', 'model_tier',
                           'age', 'mileage', 'mileage_per_year', 'is_low_mileage', 'is_high_mileage',
                           'model_popularity_log', 'is_suv', 'model_base_price',
                           'depreciation_rate', 'rarity_score', 'is_high_trim', 'is_eco', 'condition_score']
        
        else:  # imported
            df['is_high_mileage'] = (df['mileage'] > 150000).astype(int)
            df['brand_fuel'] = df['brand'] + '_' + df['fuel']
            
            luxury_brands = ['벤츠', 'BMW', '아우디', '렉서스', '포르쉐', 
                            '페라리', '람보르기니', '벤틀리', '롤스로이스', '맥라렌',
                            '마세라티', '애스턴마틴']
            df['is_luxury'] = df['brand'].isin(luxury_brands).astype(int)
            df['is_ultra_premium'] = (df['price'] > 5000).astype(int)
            
            brand_price_mean = df.groupby('brand')['price'].transform('mean').fillna(5000)
            df['brand_value'] = brand_price_mean
            df['price_vs_brand_avg'] = df['price'] / (brand_price_mean + 1)
            df['model_rarity'] = 1 / (df['model_popularity'] + 1)
            
            feature_cols = ['brand', 'model_name', 'fuel', 'age_group', 'brand_fuel',
                           'age', 'mileage', 'mileage_per_year', 'is_low_mileage',
                           'model_popularity_log', 'is_eco', 'is_luxury', 'is_ultra_premium',
                           'brand_value', 'price_vs_brand_avg', 'model_rarity']
        
        # 존재하는 컬럼만 선택
        feature_cols = [f for f in feature_cols if f in df.columns]
        
        return df[feature_cols]
    
    def predict(self, brand, model_name, year, mileage, fuel, price=None):
        """단일 차량 가격 예측"""
        
        # 모델 선택
        model, model_type = self.select_model(brand)
        model_name_kr = {
            'regular_domestic': '일반 국산차',
            'genesis': '제네시스',
            'imported': '수입차'
        }[model_type]
        
        print(f"🔍 선택된 모델: {model_name_kr} ({brand})")
        
        # 데이터 준비
        data = pd.DataFrame([{
            'brand': brand,
            'model_name': model_name,
            'year': year,
            'mileage': mileage,
            'fuel': fuel,
            'price': price if price else 3000  # 임시값
        }])
        
        # 피처 생성
        features = self.prepare_features(data, model_type)
        
        # 예측
        log_pred = model.predict(features)[0]
        predicted_price = np.expm1(log_pred)
        
        print(f"📊 예측 가격: {predicted_price:.0f}만원")
        
        if price:
            error = abs(predicted_price - price)
            error_pct = error / price * 100
            print(f"   실제 가격: {price:.0f}만원")
            print(f"   오차: {error:.0f}만원 ({error_pct:.1f}%)")
        
        return predicted_price
    
    def predict_batch(self, data_df):
        """배치 예측"""
        print(f"\n📋 배치 예측: {len(data_df)}건")
        
        results = []
        
        for idx, row in data_df.iterrows():
            pred = self.predict(
                brand=row['brand'],
                model_name=row['model_name'],
                year=row['year'],
                mileage=row['mileage'],
                fuel=row['fuel'],
                price=row.get('price', None)
            )
            results.append(pred)
            print()
        
        return results

def test_predictions():
    """테스트 예측"""
    predictor = CarPricePredictor()
    
    print("="*70)
    print("🧪 테스트 예측")
    print("="*70)
    
    test_cases = [
        {'brand': '현대', 'model_name': '그랜저 IG', 'year': 2020, 'mileage': 50000, 'fuel': '가솔린', 'price': 2000},
        {'brand': '제네시스', 'model_name': 'G80 (RG3)', 'year': 2022, 'mileage': 30000, 'fuel': '가솔린', 'price': 4500},
        {'brand': 'BMW', 'model_name': '5시리즈 (G30)', 'year': 2021, 'mileage': 40000, 'fuel': '디젤', 'price': 4000},
        {'brand': '기아', 'model_name': '카니발 4세대', 'year': 2023, 'mileage': 15000, 'fuel': '디젤', 'price': 4200},
        {'brand': '제네시스', 'model_name': 'GV80', 'year': 2021, 'mileage': 55000, 'fuel': '디젤', 'price': 5000},
        {'brand': '벤츠', 'model_name': 'E-클래스 W213', 'year': 2020, 'mileage': 60000, 'fuel': '디젤', 'price': 3500},
    ]
    
    test_df = pd.DataFrame(test_cases)
    predictor.predict_batch(test_df)
    
    print("="*70)
    print("✅ 테스트 완료!")
    print("="*70)

if __name__ == "__main__":
    test_predictions()

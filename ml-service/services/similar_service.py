"""
비슷한 차량 가격 분포 서비스
- 전처리된 데이터 사용
- 이상치 필터링 (가격 100~15000만원)
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional

class SimilarVehicleService:
    """비슷한 차량 가격 분포 분석"""
    
    # 가격 필터 (이상치 제거)
    PRICE_MIN = 100   # 100만원 이상
    PRICE_MAX = 15000 # 1.5억 이하
    
    def __init__(self):
        self.data_path = Path(__file__).parent.parent.parent / "data"
        self._combined_df = None
        self._load_data()
    
    def _load_data(self):
        """전처리된 통합 데이터 로드"""
        try:
            # 전처리된 통합 데이터 사용
            combined_path = self.data_path / "processed_encar_combined.csv"
            if combined_path.exists():
                df = pd.read_csv(combined_path)
                # 이상치 필터링
                df = df[(df['price'] >= self.PRICE_MIN) & (df['price'] <= self.PRICE_MAX)]
                self._combined_df = df
                print(f"✓ 전처리 데이터 로드: {len(df):,}건 (이상치 제거됨)")
            else:
                print(f"⚠️ 전처리 데이터 없음, 원본 데이터 사용")
                self._load_raw_data()
        except Exception as e:
            print(f"⚠️ 데이터 로드 실패: {e}")
            self._load_raw_data()
    
    def _load_raw_data(self):
        """원본 데이터 로드 (fallback)"""
        try:
            domestic_path = self.data_path / "encar_raw_domestic.csv"
            if domestic_path.exists():
                df = pd.read_csv(domestic_path)
                df = df[(df['Price'] >= self.PRICE_MIN) & (df['Price'] <= self.PRICE_MAX)]
                # 컬럼명 통일
                df = df.rename(columns={'Manufacturer': 'brand', 'Model': 'model_name', 
                                        'Year': 'year', 'Mileage': 'mileage', 'Price': 'price'})
                self._combined_df = df
                print(f"✓ 원본 데이터 로드: {len(df):,}건")
        except Exception as e:
            print(f"⚠️ 원본 데이터 로드 실패: {e}")
    
    def get_similar_distribution(self, brand: str, model: str, year: int, 
                                  mileage: int, predicted_price: float) -> Dict:
        """
        비슷한 차량 가격 분포 조회 (전처리된 데이터 기준)
        """
        df = self._combined_df
        
        if df is None or len(df) == 0:
            return self._empty_result()
        
        # 모델명 첫 단어 추출 (예: "그랜저 (GN7)" → "그랜저")
        model_keyword = model.split()[0] if model else ""
        
        # 비슷한 차량 필터링 (전처리된 데이터 컬럼명 사용)
        year_range = 2
        mileage_range = 30000
        
        try:
            # year 컬럼이 문자열일 수 있음
            df_year = df['year'].astype(str).str[:4].astype(int)
            
            similar = df[
                (df['brand'].str.contains(brand, case=False, na=False)) &
                (df['model_name'].str.contains(model_keyword, case=False, na=False)) &
                (df_year.between(year - year_range, year + year_range)) &
                (df['mileage'].between(mileage - mileage_range, mileage + mileage_range))
            ].copy()
            
            if len(similar) < 5:
                # 조건 완화: 모델명만으로 검색
                similar = df[
                    (df['model_name'].str.contains(model_keyword, case=False, na=False)) &
                    (df_year.between(year - 3, year + 3))
                ].copy()
        except Exception as e:
            print(f"⚠️ 필터링 오류: {e}")
            return self._empty_result()
        
        if len(similar) == 0:
            return self._empty_result()
        
        # 가격 배열에서 이상치 제거 (IQR 방법)
        prices_raw = similar['price'].values
        q1, q3 = np.percentile(prices_raw, [25, 75])
        iqr = q3 - q1
        lower_bound = max(q1 - 1.5 * iqr, 100)  # 최소 100만원
        upper_bound = min(q3 + 1.5 * iqr, 10000)  # 최대 1억
        
        prices = prices_raw[(prices_raw >= lower_bound) & (prices_raw <= upper_bound)]
        
        if len(prices) < 3:
            prices = prices_raw[(prices_raw >= 100) & (prices_raw <= 10000)]
        
        if len(prices) == 0:
            return self._empty_result()
        
        # 가격 분포 계산 (이상치 제거된 데이터)
        distribution = {
            "min": float(np.min(prices)),
            "q1": float(np.percentile(prices, 25)),
            "median": float(np.median(prices)),
            "q3": float(np.percentile(prices, 75)),
            "max": float(np.max(prices)),
            "mean": float(np.mean(prices)),
            "std": float(np.std(prices))
        }
        
        # 히스토그램 생성 (적절한 bin 크기)
        price_range = np.max(prices) - np.min(prices)
        if price_range > 3000:
            bin_width = 500
        elif price_range > 1000:
            bin_width = 200
        else:
            bin_width = 100
            
        bins = np.arange(
            int(np.min(prices) // bin_width) * bin_width,
            int(np.max(prices) // bin_width + 2) * bin_width,
            bin_width
        )
        
        # bin 개수 제한 (최대 12개)
        if len(bins) > 13:
            bins = np.linspace(np.min(prices), np.max(prices), 11)
            
        hist, edges = np.histogram(prices, bins=bins)
        
        histogram = []
        for i in range(len(hist)):
            histogram.append({
                "range": f"{int(edges[i])}-{int(edges[i+1])}",
                "range_min": int(edges[i]),
                "range_max": int(edges[i+1]),
                "count": int(hist[i])
            })
        
        # 예측가 위치 계산
        percentile = (prices < predicted_price).sum() / len(prices) * 100
        if percentile <= 25:
            position = "하위 25% (저렴)"
            position_color = "green"
        elif percentile <= 50:
            position = "하위 50% (적정)"
            position_color = "blue"
        elif percentile <= 75:
            position = "상위 50% (다소 높음)"
            position_color = "orange"
        else:
            position = "상위 25% (높음)"
            position_color = "red"
        
        # 비슷한 차량 샘플 (5개) - 전처리 데이터 컬럼명 사용
        sample_vehicles = []
        for _, row in similar.head(5).iterrows():
            sample_vehicles.append({
                "brand": row.get('brand', brand),
                "model": row.get('model_name', model),
                "year": str(row.get('year', year))[:4],
                "mileage": int(row.get('mileage', mileage)),
                "price": int(row.get('price', 0))
            })
        
        return {
            "similar_count": len(prices),  # 이상치 제거 후 개수
            "price_distribution": distribution,
            "histogram": histogram,
            "your_price": predicted_price,
            "your_percentile": round(percentile, 1),
            "your_position": position,
            "position_color": position_color,
            "similar_vehicles": sample_vehicles
        }
    
    def _empty_result(self) -> Dict:
        """빈 결과"""
        return {
            "similar_count": 0,
            "price_distribution": None,
            "histogram": [],
            "your_position": "데이터 부족",
            "position_color": "gray",
            "similar_vehicles": []
        }


# 싱글톤
_similar_service = None

def get_similar_service() -> SimilarVehicleService:
    global _similar_service
    if _similar_service is None:
        _similar_service = SimilarVehicleService()
    return _similar_service

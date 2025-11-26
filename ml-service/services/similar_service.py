"""
비슷한 차량 가격 분포 서비스
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional

class SimilarVehicleService:
    """비슷한 차량 가격 분포 분석"""
    
    def __init__(self):
        self.data_path = Path(__file__).parent.parent.parent / "data"
        self._domestic_df = None
        self._imported_df = None
        self._load_data()
    
    def _load_data(self):
        """데이터 로드"""
        try:
            domestic_path = self.data_path / "encar_raw_domestic.csv"
            if domestic_path.exists():
                self._domestic_df = pd.read_csv(domestic_path)
                print(f"✓ 국산차 데이터 로드: {len(self._domestic_df):,}건")
        except Exception as e:
            print(f"⚠️ 국산차 데이터 로드 실패: {e}")
        
        try:
            imported_path = self.data_path / "encar_imported_data.csv"
            if imported_path.exists():
                self._imported_df = pd.read_csv(imported_path)
                print(f"✓ 외제차 데이터 로드: {len(self._imported_df):,}건")
        except Exception as e:
            print(f"⚠️ 외제차 데이터 로드 실패: {e}")
    
    def get_similar_distribution(self, brand: str, model: str, year: int, 
                                  mileage: int, predicted_price: float) -> Dict:
        """
        비슷한 차량 가격 분포 조회
        
        Returns:
            {
                "similar_count": int,
                "price_distribution": {
                    "min": float,
                    "q1": float,
                    "median": float,
                    "q3": float,
                    "max": float,
                    "mean": float
                },
                "histogram": [
                    {"range": "1000-1500", "count": 10},
                    ...
                ],
                "your_position": "하위 30%",
                "similar_vehicles": [...]
            }
        """
        # 국산/외제 구분
        domestic_brands = ['현대', '기아', '제네시스', '쉐보레', 'KG모빌리티', '르노코리아']
        is_domestic = brand in domestic_brands
        
        df = self._domestic_df if is_domestic else self._imported_df
        
        if df is None or len(df) == 0:
            return self._empty_result()
        
        # 비슷한 차량 필터링
        year_range = 2
        mileage_range = 30000
        
        similar = df[
            (df['Manufacturer'].str.contains(brand, case=False, na=False)) &
            (df['Model'].str.contains(model.split()[0], case=False, na=False)) &
            (df['Year'].astype(str).str[:4].astype(int).between(year - year_range, year + year_range)) &
            (df['Mileage'].between(mileage - mileage_range, mileage + mileage_range)) &
            (df['Price'] > 100) & (df['Price'] < 30000)
        ].copy()
        
        if len(similar) < 5:
            # 조건 완화
            similar = df[
                (df['Model'].str.contains(model.split()[0], case=False, na=False)) &
                (df['Year'].astype(str).str[:4].astype(int).between(year - 3, year + 3)) &
                (df['Price'] > 100) & (df['Price'] < 30000)
            ].copy()
        
        if len(similar) == 0:
            return self._empty_result()
        
        prices = similar['Price'].values
        
        # 가격 분포 계산
        distribution = {
            "min": float(np.min(prices)),
            "q1": float(np.percentile(prices, 25)),
            "median": float(np.median(prices)),
            "q3": float(np.percentile(prices, 75)),
            "max": float(np.max(prices)),
            "mean": float(np.mean(prices)),
            "std": float(np.std(prices))
        }
        
        # 히스토그램 생성
        bin_width = 500 if np.max(prices) > 5000 else 200
        bins = np.arange(
            int(np.min(prices) // bin_width) * bin_width,
            int(np.max(prices) // bin_width + 2) * bin_width,
            bin_width
        )
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
        
        # 비슷한 차량 샘플 (5개)
        sample_vehicles = []
        for _, row in similar.head(5).iterrows():
            sample_vehicles.append({
                "brand": row.get('Manufacturer', brand),
                "model": row.get('Model', model),
                "year": str(row.get('Year', year))[:4],
                "mileage": int(row.get('Mileage', mileage)),
                "price": int(row.get('Price', 0))
            })
        
        return {
            "similar_count": len(similar),
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

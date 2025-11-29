"""
관리자 대시보드용 서비스
admin-dashboard 백엔드 API 지원

v2.0 - CSV 컬럼명 자동 매핑 지원
"""
import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

class AdminService:
    """관리자 대시보드 서비스"""

    # 컬럼 매핑 (다양한 CSV 형식 지원)
    COLUMN_MAPPING = {
        'brand': ['brand', '브랜드', 'Brand', 'manufacturer'],
        'model': ['model_name', 'model', '모델', 'Model', 'model_full'],
        'year': ['year', '연식', 'Year', 'model_year'],
        'mileage': ['mileage', '주행거리', 'Mileage', 'km'],
        'fuel': ['fuel', '연료', 'Fuel', 'fuel_type'],
        'price': ['price', '가격', 'Price', 'sale_price'],
        'region': ['region', '지역', 'Region', 'location'],
        'car_type': ['car_type', '차종', 'category'],
    }

    def __init__(self):
        # 조회 통계 저장 (메모리 기반 - 추후 DB로 교체)
        self._request_stats = defaultdict(int)  # 모델별 조회수
        self._daily_requests = defaultdict(int)  # 일별 요청수
        self._total_requests = 0

        # 차량 데이터 로드
        self._domestic_data = None
        self._imported_data = None
        self._domestic_details = None  # 상세정보 (옵션, 사고이력)
        self._imported_details = None
        self._load_vehicle_data()
        self._load_detail_data()  # 상세정보 로드

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """CSV 컬럼명을 표준 형식으로 변환"""
        rename_map = {}
        for std_name, variants in self.COLUMN_MAPPING.items():
            for variant in variants:
                if variant in df.columns and std_name not in df.columns:
                    rename_map[variant] = std_name
                    break
        if rename_map:
            df = df.rename(columns=rename_map)
        return df

    def _load_vehicle_data(self):
        """CSV 데이터 로드"""
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # 메인 데이터 (브랜드, 모델, 가격 등 포함)
        combined_path = os.path.join(base_path, "data", "processed_encar_combined.csv")
        if os.path.exists(combined_path):
            try:
                df = pd.read_csv(combined_path, encoding='utf-8-sig')
                df = self._normalize_columns(df)

                # 국산차/수입차 분류 (대소문자 무시)
                if 'car_type' in df.columns:
                    df['car_type_lower'] = df['car_type'].str.lower()
                    self._domestic_data = df[df['car_type_lower'] == 'domestic'].copy()
                    self._imported_data = df[df['car_type_lower'] == 'imported'].copy()
                    # 임시 컬럼 제거
                    if 'car_type_lower' in self._domestic_data.columns:
                        self._domestic_data = self._domestic_data.drop(columns=['car_type_lower'])
                    if 'car_type_lower' in self._imported_data.columns:
                        self._imported_data = self._imported_data.drop(columns=['car_type_lower'])
                else:
                    # car_type 없으면 전부 국산차로 처리
                    self._domestic_data = df.copy()
                    self._imported_data = pd.DataFrame()

                print(f"✓ 차량 데이터 로드: 국산 {len(self._domestic_data)}대, 수입 {len(self._imported_data)}대")
            except Exception as e:
                print(f"⚠️ 차량 데이터 로드 실패: {e}")
                self._domestic_data = pd.DataFrame()
                self._imported_data = pd.DataFrame()
        else:
            print(f"⚠️ 데이터 파일 없음: {combined_path}")
            self._domestic_data = pd.DataFrame()
            self._imported_data = pd.DataFrame()

    def _load_detail_data(self):
        """상세정보 CSV 로드 (옵션, 사고이력 등)"""
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # 국산차 상세정보
        domestic_detail_path = os.path.join(base_path, "data", "complete_domestic_details.csv")
        if os.path.exists(domestic_detail_path):
            try:
                self._domestic_details = pd.read_csv(domestic_detail_path, encoding='utf-8-sig')
                print(f"✓ 국산차 상세정보 로드: {len(self._domestic_details)}건")
            except Exception as e:
                print(f"⚠️ 국산차 상세정보 로드 실패: {e}")
                self._domestic_details = pd.DataFrame()
        else:
            self._domestic_details = pd.DataFrame()

        # 외제차 상세정보
        imported_detail_path = os.path.join(base_path, "data", "complete_imported_details.csv")
        if os.path.exists(imported_detail_path):
            try:
                self._imported_details = pd.read_csv(imported_detail_path, encoding='utf-8-sig')
                print(f"✓ 외제차 상세정보 로드: {len(self._imported_details)}건")
            except Exception as e:
                print(f"⚠️ 외제차 상세정보 로드 실패: {e}")
                self._imported_details = pd.DataFrame()
        else:
            self._imported_details = pd.DataFrame()

    def get_vehicle_detail(self, car_id: int, category: str = "domestic") -> Dict:
        """차량 상세정보 조회 (옵션, 사고이력 포함)"""
        detail_df = self._domestic_details if category == "domestic" else self._imported_details

        if detail_df is None or len(detail_df) == 0:
            return {"success": False, "error": "상세정보 데이터 없음"}

        # car_id로 검색
        match = detail_df[detail_df['car_id'] == car_id]
        if len(match) == 0:
            return {"success": False, "error": f"차량 ID {car_id} 상세정보 없음"}

        row = match.iloc[0]

        def safe_bool(val):
            if pd.isna(val):
                return False
            return bool(val)

        return {
            "success": True,
            "car_id": car_id,
            "is_accident_free": safe_bool(row.get('is_accident_free')),
            "inspection_grade": row.get('inspection_grade', 'normal'),
            "region": row.get('region', ''),
            "options": {
                "sunroof": safe_bool(row.get('has_sunroof')),
                "navigation": safe_bool(row.get('has_navigation')),
                "leather_seat": safe_bool(row.get('has_leather_seat')),
                "smart_key": safe_bool(row.get('has_smart_key')),
                "rear_camera": safe_bool(row.get('has_rear_camera')),
                "led_lamp": safe_bool(row.get('has_led_lamp')),
                "heated_seat": safe_bool(row.get('has_heated_seat')),
                "ventilated_seat": safe_bool(row.get('has_ventilated_seat')),
                "parking_sensor": safe_bool(row.get('has_parking_sensor')),
                "auto_ac": safe_bool(row.get('has_auto_ac')),
            }
        }

    def record_request(self, model: str):
        """시세 조회 요청 기록"""
        self._request_stats[model] += 1
        today = datetime.now().strftime("%Y-%m-%d")
        self._daily_requests[today] += 1
        self._total_requests += 1
    
    def get_dashboard_stats(self) -> Dict:
        """대시보드 통계 (더미데이터 제거 - 실제 데이터만 반환)"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_count = self._daily_requests.get(today, 0)

        # 인기 모델 Top 5
        sorted_models = sorted(
            self._request_stats.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        popular_models = [
            {"name": model, "value": count}
            for model, count in sorted_models
        ]

        return {
            "success": True,
            "todayCount": today_count,
            "totalCount": self._total_requests,
            "avgConfidence": 0,  # DB에서 실제 계산
            "popularModels": popular_models
        }

    def get_daily_requests(self, days: int = 7) -> Dict:
        """일별 요청 통계 (더미데이터 제거)"""
        result = []
        for i in range(days - 1, -1, -1):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            day_label = date.strftime("%m/%d")
            count = self._daily_requests.get(date_str, 0)

            result.append({
                "date": date_str,
                "day": day_label,
                "count": count
            })

        return {
            "success": True,
            "data": result
        }
    
    def get_vehicle_stats(self) -> Dict:
        """차량 데이터 통계"""
        domestic_count = len(self._domestic_data) if self._domestic_data is not None else 0
        imported_count = len(self._imported_data) if self._imported_data is not None else 0
        
        return {
            "success": True,
            "domesticCount": domestic_count,
            "importedCount": imported_count,
            "totalCount": domestic_count + imported_count
        }
    
    def get_vehicles(self, brand: str = None, model: str = None,
                     category: str = "all", limit: int = 50) -> Dict:
        """차량 목록 조회"""
        vehicles = []

        # 국산차
        if category in ["all", "domestic"] and self._domestic_data is not None and len(self._domestic_data) > 0:
            df = self._domestic_data.copy()
            if brand and 'brand' in df.columns:
                df = df[df['brand'].str.contains(brand, na=False, case=False)]
            if model and 'model' in df.columns:
                df = df[df['model'].str.contains(model, na=False, case=False)]

            for _, row in df.head(limit // 2 if category == "all" else limit).iterrows():
                vehicles.append(self._row_to_vehicle(row, "domestic"))

        # 수입차
        if category in ["all", "imported"] and self._imported_data is not None and len(self._imported_data) > 0:
            df = self._imported_data.copy()
            if brand and 'brand' in df.columns:
                df = df[df['brand'].str.contains(brand, na=False, case=False)]
            if model and 'model' in df.columns:
                df = df[df['model'].str.contains(model, na=False, case=False)]

            for _, row in df.head(limit // 2 if category == "all" else limit).iterrows():
                vehicles.append(self._row_to_vehicle(row, "imported"))

        return {
            "success": True,
            "vehicles": vehicles[:limit],
            "total": len(vehicles)
        }

    def _row_to_vehicle(self, row, category: str) -> Dict:
        """DataFrame 행을 차량 dict로 변환 (표준화된 컬럼명 사용)"""
        def safe_get(key, default=None):
            try:
                val = row.get(key, default)
                if pd.isna(val):
                    return default
                return val
            except:
                return default

        return {
            "id": safe_get('car_id', hash(str(row.values)) % 100000),
            "category": category,
            "brand": safe_get('brand', ''),
            "model": safe_get('model', ''),
            "year": int(safe_get('year', 2020)),
            "mileage": int(safe_get('mileage', 0)),
            "fuel": safe_get('fuel', ''),
            "price": int(safe_get('price', 0)),
            "region": safe_get('region', ''),
            "options": {
                "sunroof": bool(safe_get('has_sunroof', False)),
                "navigation": bool(safe_get('has_navigation', False)),
                "leather_seat": bool(safe_get('has_leather_seat', False)),
                "smart_key": bool(safe_get('has_smart_key', False)),
                "rear_camera": bool(safe_get('has_rear_camera', False)),
                "heated_seat": bool(safe_get('has_heated_seat', False)),
            }
        }

    def get_history_list(self, limit: int = 50) -> Dict:
        """분석 이력 목록 (전체)"""
        # 히스토리 서비스에서 가져옴 (추후 DB 연동)
        from .history_service import get_history_service
        history_service = get_history_service()

        # 모든 사용자의 히스토리 합치기
        all_history = []
        for user_id, histories in history_service._history.items():
            for h in histories:
                all_history.append({**h, "user_id": user_id})

        # 최신순 정렬
        all_history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return {
            "success": True,
            "history": all_history[:limit],
            "total": len(all_history)
        }


# 싱글톤 인스턴스
_admin_service = None

def get_admin_service() -> AdminService:
    global _admin_service
    if _admin_service is None:
        _admin_service = AdminService()
    return _admin_service


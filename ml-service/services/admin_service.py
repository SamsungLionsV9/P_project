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

    # 가격 필터 (이상치 제거)
    PRICE_MIN = 100      # 100만원 이상 (가격 미정/상담 제외)
    PRICE_MAX = 100000   # 10억 이하 (외제차 고가 모델 포함)

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
        """CSV 데이터 로드 (Raw 데이터 사용 - car_id, region 포함)"""
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # Raw 데이터 사용 (car_id, region 포함)
        domestic_raw_path = os.path.join(base_path, "data", "encar_raw_domestic.csv")
        imported_raw_path = os.path.join(base_path, "data", "encar_imported_data.csv")
        
        # 국산차 로드
        if os.path.exists(domestic_raw_path):
            try:
                df = pd.read_csv(domestic_raw_path, encoding='utf-8-sig')
                # 컬럼명 표준화
                df = df.rename(columns={
                    'Id': 'car_id',
                    'Manufacturer': 'brand',
                    'Model': 'model',
                    'Year': 'year_raw',
                    'FormYear': 'year',
                    'Mileage': 'mileage',
                    'FuelType': 'fuel',
                    'Price': 'price',
                    'OfficeCityState': 'region'
                })
                # 가격 단위 스마트 변환 (혼재된 데이터 처리)
                # - 500 미만: 백만원 단위 → *100 해서 만원으로 변환
                # - 500 이상: 이미 만원 단위 → 변환 없음
                df['price'] = df['price'].apply(
                    lambda x: x * 100 if x < 500 else x
                )
                # 가격 필터링 (100만원 ~ 10억원)
                df = df[(df['price'] >= self.PRICE_MIN) & (df['price'] <= self.PRICE_MAX)]
                # 가격 0인 데이터 제외
                df = df[df['price'] > 0]
                self._domestic_data = df
                print(f"[OK] Domestic raw data loaded: {len(df)} vehicles")
            except Exception as e:
                print(f"[WARN] Domestic raw data load failed: {e}")
                self._domestic_data = pd.DataFrame()
        else:
            self._domestic_data = pd.DataFrame()
            
        # 수입차 로드
        if os.path.exists(imported_raw_path):
            try:
                df = pd.read_csv(imported_raw_path, encoding='utf-8-sig')
                df = df.rename(columns={
                    'Id': 'car_id',
                    'Manufacturer': 'brand',
                    'Model': 'model',
                    'Year': 'year_raw',
                    'FormYear': 'year',
                    'Mileage': 'mileage',
                    'FuelType': 'fuel',
                    'Price': 'price',
                    'OfficeCityState': 'region'
                })
                # 가격 단위 스마트 변환
                df['price'] = df['price'].apply(
                    lambda x: x * 100 if x < 500 else x
                )
                df = df[(df['price'] >= self.PRICE_MIN) & (df['price'] <= self.PRICE_MAX)]
                df = df[df['price'] > 0]
                self._imported_data = df
                print(f"[OK] Imported raw data loaded: {len(df)} vehicles")
            except Exception as e:
                print(f"[WARN] Imported raw data load failed: {e}")
                self._imported_data = pd.DataFrame()
        else:
            self._imported_data = pd.DataFrame()
        
        # Fallback: processed_encar_combined.csv 사용
        if len(self._domestic_data) == 0 and len(self._imported_data) == 0:
            combined_path = os.path.join(base_path, "data", "processed_encar_combined.csv")
            if os.path.exists(combined_path):
                try:
                    df = pd.read_csv(combined_path, encoding='utf-8-sig')
                    df = df.rename(columns={'model_name': 'model'})
                    if 'car_id' not in df.columns:
                        df['car_id'] = range(1, len(df) + 1)
                    df = df[(df['price'] >= self.PRICE_MIN) & (df['price'] <= self.PRICE_MAX)]
                    
                    imported_brands = ['BMW', 'Mercedes-Benz', 'Audi', 'Volkswagen', 'Volvo',
                                       'Porsche', 'Land Rover', 'Jaguar', 'Mini', 'Lexus',
                                       'Toyota', 'Honda', 'Nissan', 'Ford', 'Chevrolet']
                    self._domestic_data = df[~df['brand'].isin(imported_brands)].copy()
                    self._imported_data = df[df['brand'].isin(imported_brands)].copy()
                    print(f"[OK] Fallback combined data: {len(self._domestic_data)} domestic, {len(self._imported_data)} imported")
                except Exception as e:
                    print(f"[WARN] Fallback combined data failed: {e}")

    def _load_detail_data(self):
        """상세정보 CSV 로드 (옵션, 사고이력 등)"""
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # 국산차 상세정보
        domestic_detail_path = os.path.join(base_path, "data", "complete_domestic_details.csv")
        if os.path.exists(domestic_detail_path):
            try:
                self._domestic_details = pd.read_csv(domestic_detail_path, encoding='utf-8-sig')
                print(f"[OK] Domestic details loaded: {len(self._domestic_details)} records")
            except Exception as e:
                print(f"[WARN] Domestic details load failed: {e}")
                self._domestic_details = pd.DataFrame()
        else:
            self._domestic_details = pd.DataFrame()

        # 외제차 상세정보
        imported_detail_path = os.path.join(base_path, "data", "complete_imported_details.csv")
        if os.path.exists(imported_detail_path):
            try:
                self._imported_details = pd.read_csv(imported_detail_path, encoding='utf-8-sig')
                print(f"[OK] Imported details loaded: {len(self._imported_details)} records")
            except Exception as e:
                print(f"[WARN] Imported details load failed: {e}")
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
        """대시보드 통계 (DB 기반)"""
        from .database_service import get_database_service
        db = get_database_service()
        
        # DB에서 통계 가져오기
        db_stats = db.get_dashboard_stats()
        
        # 메모리 통계와 병합 (서버 시작 후 데이터)
        today = datetime.now().strftime("%Y-%m-%d")
        memory_today = self._daily_requests.get(today, 0)
        
        # 인기 모델: DB + 메모리 병합
        popular_models = db_stats.get('popularModels', [])
        
        # 메모리에만 있는 모델 추가
        db_model_names = {m['name'] for m in popular_models}
        for model, count in sorted(self._request_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            if model not in db_model_names:
                popular_models.append({"name": model, "value": count})
        
        # 조회수로 재정렬
        popular_models.sort(key=lambda x: x.get('value', 0), reverse=True)
        
        return {
            "success": True,
            "todayCount": db_stats.get('todayCount', 0) + memory_today,
            "totalCount": db_stats.get('totalCount', 0) + self._total_requests,
            "avgConfidence": db_stats.get('avgConfidence', 0),
            "popularModels": popular_models[:5]
        }

    def get_daily_requests(self, days: int = 7) -> Dict:
        """일별 요청 통계 (DB 기반)"""
        from .database_service import get_database_service
        db = get_database_service()
        
        # DB에서 일별 통계 가져오기
        db_result = db.get_daily_requests(days)
        
        # 메모리 데이터와 병합
        result = []
        for item in db_result.get('data', []):
            date_str = item.get('day', '')
            # 메모리에 있는 오늘 데이터 추가
            memory_count = self._daily_requests.get(date_str, 0)
            result.append({
                "day": item.get('day', ''),
                "count": item.get('count', 0) + memory_count
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
                     category: str = "all", page: int = 1, limit: int = 20,
                     price_min: int = None, price_max: int = None) -> Dict:
        """차량 목록 조회 (페이지네이션, 가격 범위 검색 지원)"""

        # 가격 범위 설정 (기본값 또는 사용자 지정)
        min_price = price_min if price_min is not None else self.PRICE_MIN
        max_price = price_max if price_max is not None else self.PRICE_MAX

        # 필터링된 데이터프레임 수집
        filtered_dfs = []

        # 국산차
        if category in ["all", "domestic"] and self._domestic_data is not None and len(self._domestic_data) > 0:
            df = self._domestic_data.copy()
            # 가격 범위 필터링
            df = df[(df['price'] >= min_price) & (df['price'] <= max_price)]
            if brand and 'brand' in df.columns:
                df = df[df['brand'].str.contains(brand, na=False, case=False)]
            if model and 'model' in df.columns:
                df = df[df['model'].str.contains(model, na=False, case=False)]
            df['_category'] = 'domestic'
            filtered_dfs.append(df)

        # 수입차
        if category in ["all", "imported"] and self._imported_data is not None and len(self._imported_data) > 0:
            df = self._imported_data.copy()
            # 가격 범위 필터링
            df = df[(df['price'] >= min_price) & (df['price'] <= max_price)]
            if brand and 'brand' in df.columns:
                df = df[df['brand'].str.contains(brand, na=False, case=False)]
            if model and 'model' in df.columns:
                df = df[df['model'].str.contains(model, na=False, case=False)]
            df['_category'] = 'imported'
            filtered_dfs.append(df)

        # 데이터 병합
        if not filtered_dfs:
            return {
                "success": True,
                "vehicles": [],
                "total": 0,
                "page": page,
                "limit": limit,
                "totalPages": 0
            }

        import pandas as pd
        combined = pd.concat(filtered_dfs, ignore_index=True)
        total_count = len(combined)
        total_pages = (total_count + limit - 1) // limit  # 올림 나눗셈

        # 페이지네이션 적용 (서버 부하 최적화)
        offset = (page - 1) * limit
        page_data = combined.iloc[offset:offset + limit]

        # 차량 데이터 변환
        vehicles = []
        for _, row in page_data.iterrows():
            cat = row.get('_category', 'domestic')
            vehicles.append(self._row_to_vehicle(row, cat))

        return {
            "success": True,
            "vehicles": vehicles,
            "total": total_count,
            "page": page,
            "limit": limit,
            "totalPages": total_pages
        }

    def _row_to_vehicle(self, row, category: str) -> Dict:
        """DataFrame 행을 차량 dict로 변환 (상세정보 병합)"""
        def safe_get(key, default=None):
            try:
                val = row.get(key, default)
                if pd.isna(val):
                    return default
                return val
            except:
                return default

        # 연식 (전처리 데이터는 YYYY 형식)
        raw_year = safe_get('year', 2020)
        year = int(raw_year) if raw_year else 2020
        
        # 가격 (전처리 데이터는 만원 단위로 통일됨)
        raw_price = safe_get('price', 0)
        price = int(float(raw_price)) if raw_price else 0
        
        # car_id
        car_id = safe_get('car_id', hash(str(row.values)) % 100000)
        
        # 상세정보 병합 (car_id로 조회)
        detail_df = self._domestic_details if category == "domestic" else self._imported_details
        options = {}
        is_accident_free = None
        inspection_grade = 'normal'
        
        if detail_df is not None and len(detail_df) > 0:
            match = detail_df[detail_df['car_id'] == car_id]
            if len(match) > 0:
                detail_row = match.iloc[0]
                options = {
                    "sunroof": bool(detail_row.get('has_sunroof', 0)),
                    "navigation": bool(detail_row.get('has_navigation', 0)),
                    "leather_seat": bool(detail_row.get('has_leather_seat', 0)),
                    "smart_key": bool(detail_row.get('has_smart_key', 0)),
                    "rear_camera": bool(detail_row.get('has_rear_camera', 0)),
                    "heated_seat": bool(detail_row.get('has_heated_seat', 0)),
                    "ventilated_seat": bool(detail_row.get('has_ventilated_seat', 0)),
                    "led_lamp": bool(detail_row.get('has_led_lamp', 0)),
                    "parking_sensor": bool(detail_row.get('has_parking_sensor', 0)),
                    "auto_ac": bool(detail_row.get('has_auto_ac', 0)),
                }
                is_accident_free = bool(detail_row.get('is_accident_free', 0))
                inspection_grade = detail_row.get('inspection_grade', 'normal')

        return {
            "id": car_id,
            "category": category,
            "brand": safe_get('brand', ''),
            "model": safe_get('model', ''),
            "year": year,
            "mileage": int(safe_get('mileage', 0)),
            "fuel": safe_get('fuel', ''),
            "price": price,
            "region": safe_get('region', ''),
            "is_accident_free": is_accident_free,
            "inspection_grade": inspection_grade,
            "options": options
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


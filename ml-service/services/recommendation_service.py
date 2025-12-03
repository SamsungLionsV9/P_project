"""
차량 추천 및 인기 모델 서비스 (엔카 데이터 기반)
==============================================
- 실제 엔카 데이터 기반 인기 모델 분석
- 예측 가격 기반 추천 차량
- 사용자 조회 이력 기반 추천
"""
import pandas as pd
import numpy as np
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter
import sys
import os
import re

# 상위 경로 추가 (prediction_v12 사용 위함)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def extract_model_core(model_name: str) -> str:
    """
    모델명에서 핵심 식별자 추출
    - 벤츠 E-클래스 W213 → E-클래스
    - 벤츠 GLE-클래스 W167 → GLE-클래스
    - 테슬라 모델 3 → 모델 3
    - 테슬라 모델 Y → 모델 Y
    - 그랜저 IG → 그랜저
    """
    model = model_name.strip()
    
    # 벤츠 클래스 패턴 (E-클래스, GLE-클래스, S-클래스 등)
    benz_match = re.match(r'((?:GL)?[A-Z])-?클래스', model, re.IGNORECASE)
    if benz_match:
        return benz_match.group(0).replace('-', '-')
    
    # BMW 시리즈 패턴 (3시리즈, 5시리즈, X3 등)
    bmw_series = re.match(r'(\d시리즈|[XZiM]\d)', model, re.IGNORECASE)
    if bmw_series:
        return bmw_series.group(1)
    
    # 테슬라 모델 패턴 (모델 3, 모델 Y, 모델 S 등)
    tesla_match = re.match(r'(모델\s*[3YSX]|Model\s*[3YSX])', model, re.IGNORECASE)
    if tesla_match:
        return tesla_match.group(1).replace(' ', ' ')
    
    # 아우디 패턴 (A6, Q5 등)
    audi_match = re.match(r'([AQeSR][0-9]+)', model, re.IGNORECASE)
    if audi_match:
        return audi_match.group(1).upper()
    
    # 일반 모델명: 첫 번째 핵심 단어 (공백/괄호 이전)
    # 그랜저 IG, 쏘나타 DN8 → 그랜저, 쏘나타
    core_match = re.match(r'^([가-힣A-Za-z0-9]+)', model)
    if core_match:
        return core_match.group(1)
    
    return model


def is_model_match(target_model: str, candidate_model: str) -> bool:
    """
    두 모델이 같은 계열인지 정확히 판단
    - target: 사용자가 선택한 모델 (E-클래스, 모델 3 등)
    - candidate: 데이터셋의 모델명
    """
    target_core = extract_model_core(target_model)
    candidate_core = extract_model_core(candidate_model)
    
    # 정확한 핵심 식별자 매칭
    # E-클래스 ↔ E-클래스 OK, E-클래스 ↔ GLE-클래스 NO
    return target_core.lower() == candidate_core.lower()


class RecommendationService:
    """엔카 데이터 기반 추천 시스템"""
    
    # 이상치 필터 (similar_service와 통일)
    PRICE_MIN = 100    # 100만원 이상
    PRICE_MAX = 50000  # 5억 이하 (학습 데이터와 동일)
    
    # 특수 가격 이상치 (가격 미정 표시 등)
    SPECIAL_PRICES = {9999, 8888, 7777, 6666, 5555, 1111, 10000}
    
    # 엔카 데스크톱 상세페이지 URL 템플릿 (모바일은 502 에러 발생)
    ENCAR_DETAIL_URL = "https://www.encar.com/dc/dc_cardetailview.do?carid={car_id}"
    
    def __init__(self):
        self.data_path = Path(__file__).parent.parent.parent / "data"
        self.db_path = Path(__file__).parent.parent.parent / "data" / "user_data.db"
        
        self._domestic_df = None
        self._imported_df = None
        self._prediction_service = None
        self._car_details = {}  # car_id별 상세 옵션 정보
        
        self._init_db()
        self._load_data()
        self._load_car_details()  # 옵션 상세 정보 로드
        self._analyze_popular()
    
    def _init_db(self):
        """SQLite DB 초기화 (영구 저장)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 조회 이력 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                brand TEXT,
                model TEXT,
                year INTEGER,
                mileage INTEGER,
                fuel TEXT,
                predicted_price REAL,
                searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 즐겨찾기 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                brand TEXT,
                model TEXT,
                year INTEGER,
                mileage INTEGER,
                fuel TEXT,
                predicted_price REAL,
                actual_price INTEGER,
                car_id TEXT,
                detail_url TEXT,
                memo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 기존 테이블에 컬럼 추가 (마이그레이션)
        try:
            cursor.execute('ALTER TABLE favorites ADD COLUMN actual_price INTEGER')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE favorites ADD COLUMN car_id TEXT')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE favorites ADD COLUMN detail_url TEXT')
        except:
            pass
        
        # 전역 검색 통계 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT,
                model TEXT,
                search_count INTEGER DEFAULT 1,
                last_searched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(brand, model)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"[OK] DB 초기화 완료: {self.db_path}")
    
    def _load_data(self):
        """엔카 데이터 로드 (가격 이상치 필터링 적용)"""
        try:
            domestic_path = self.data_path / "encar_raw_domestic.csv"
            if domestic_path.exists():
                self._domestic_df = pd.read_csv(domestic_path)
                self._domestic_df['YearOnly'] = (self._domestic_df['Year'] // 100).astype(int)
                self._domestic_df['Type'] = 'domestic'
                # 가격 이상치 필터링 (가격 미정/상담 차량 제외)
                original_count = len(self._domestic_df)
                self._domestic_df = self._domestic_df[
                    (self._domestic_df['Price'] >= self.PRICE_MIN) &
                    (self._domestic_df['Price'] <= self.PRICE_MAX)
                ]
                print(f"[OK] 국산차 데이터: {len(self._domestic_df):,}건 (필터링: {original_count - len(self._domestic_df):,}건 제외)")
        except Exception as e:
            print(f"[WARN] 국산차 로드 실패: {e}")

        try:
            imported_path = self.data_path / "encar_imported_data.csv"
            if imported_path.exists():
                self._imported_df = pd.read_csv(imported_path)
                self._imported_df['YearOnly'] = (self._imported_df['Year'] // 100).astype(int)
                self._imported_df['Type'] = 'imported'
                # 가격 이상치 필터링 (가격 미정/상담 차량 제외)
                original_count = len(self._imported_df)
                self._imported_df = self._imported_df[
                    (self._imported_df['Price'] >= self.PRICE_MIN) &
                    (self._imported_df['Price'] <= self.PRICE_MAX)
                ]
                print(f"[OK] 외제차 데이터: {len(self._imported_df):,}건 (필터링: {original_count - len(self._imported_df):,}건 제외)")
        except Exception as e:
            print(f"[WARN] 외제차 로드 실패: {e}")
    
    def _load_car_details(self):
        """차량 상세 옵션 정보 로드 (car_id별 조회용)"""
        try:
            # 국산차 상세 정보
            domestic_details_path = self.data_path / "complete_domestic_details.csv"
            if domestic_details_path.exists():
                df = pd.read_csv(domestic_details_path)
                for _, row in df.iterrows():
                    car_id = str(row.get('car_id', ''))
                    if car_id:
                        self._car_details[car_id] = {
                            'is_accident_free': bool(row.get('is_accident_free', 0)),
                            'inspection_grade': str(row.get('inspection_grade', '')),
                            'has_sunroof': bool(row.get('has_sunroof', 0)),
                            'has_navigation': bool(row.get('has_navigation', 0)),
                            'has_leather_seat': bool(row.get('has_leather_seat', 0)),
                            'has_smart_key': bool(row.get('has_smart_key', 0)),
                            'has_rear_camera': bool(row.get('has_rear_camera', 0)),
                            'has_heated_seat': bool(row.get('has_heated_seat', 0)),
                            'has_ventilated_seat': bool(row.get('has_ventilated_seat', 0)),
                        }
                print(f"[OK] 국산차 상세정보: {len(self._car_details):,}건")
            
            # 외제차 상세 정보
            imported_details_path = self.data_path / "complete_imported_details.csv"
            if imported_details_path.exists():
                df = pd.read_csv(imported_details_path)
                for _, row in df.iterrows():
                    car_id = str(row.get('car_id', ''))
                    if car_id and car_id not in self._car_details:
                        self._car_details[car_id] = {
                            'is_accident_free': bool(row.get('is_accident_free', 0)),
                            'inspection_grade': str(row.get('inspection_grade', '')),
                            'has_sunroof': bool(row.get('has_sunroof', 0)),
                            'has_navigation': bool(row.get('has_navigation', 0)),
                            'has_leather_seat': bool(row.get('has_leather_seat', 0)),
                            'has_smart_key': bool(row.get('has_smart_key', 0)),
                            'has_rear_camera': bool(row.get('has_rear_camera', 0)),
                            'has_heated_seat': bool(row.get('has_heated_seat', 0)),
                            'has_ventilated_seat': bool(row.get('has_ventilated_seat', 0)),
                        }
                print(f"[OK] 전체 차량 상세정보: {len(self._car_details):,}건")
        except Exception as e:
            print(f"[WARN] 상세정보 로드 실패: {e}")
    
    def get_car_options(self, car_id: str) -> Optional[Dict]:
        """car_id로 차량 옵션 정보 조회"""
        return self._car_details.get(str(car_id))
    
    def _analyze_popular(self):
        """엔카 데이터 기반 인기 모델 분석"""
        self._popular_domestic = []
        self._popular_imported = []
        
        if self._domestic_df is not None:
            # 국산차: 등록 수 기반 인기 모델
            model_stats = self._domestic_df.groupby(['Manufacturer', 'Model']).agg({
                'Price': ['mean', 'median', 'count'],
                'YearOnly': 'max'
            }).reset_index()
            model_stats.columns = ['brand', 'model', 'avg_price', 'median_price', 'listings', 'latest_year']
            
            # 최근 3년 내 모델만, 등록 수 100건 이상
            recent_models = model_stats[
                (model_stats['latest_year'] >= 2022) & 
                (model_stats['listings'] >= 100)
            ].sort_values('listings', ascending=False)
            
            for _, row in recent_models.head(10).iterrows():
                self._popular_domestic.append({
                    'brand': row['brand'],
                    'model': row['model'],
                    'listings': int(row['listings']),
                    'avg_price': int(row['avg_price']),
                    'median_price': int(row['median_price'])
                })
            
            print(f"[OK] 국산 인기 모델 분석: {len(self._popular_domestic)}개")
        
        if self._imported_df is not None:
            # 외제차
            model_stats = self._imported_df.groupby(['Manufacturer', 'Model']).agg({
                'Price': ['mean', 'median', 'count'],
                'YearOnly': 'max'
            }).reset_index()
            model_stats.columns = ['brand', 'model', 'avg_price', 'median_price', 'listings', 'latest_year']
            
            recent_models = model_stats[
                (model_stats['latest_year'] >= 2022) & 
                (model_stats['listings'] >= 50)
            ].sort_values('listings', ascending=False)
            
            for _, row in recent_models.head(10).iterrows():
                self._popular_imported.append({
                    'brand': row['brand'],
                    'model': row['model'],
                    'listings': int(row['listings']),
                    'avg_price': int(row['avg_price']),
                    'median_price': int(row['median_price'])
                })
            
            print(f"[OK] 외제 인기 모델 분석: {len(self._popular_imported)}개")
    
    # ========== 검색 이력 ==========
    
    def add_search_history(self, user_id: str, search_data: Dict) -> Dict:
        """검색 이력 저장 (DB)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO search_history (user_id, brand, model, year, mileage, fuel, predicted_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            search_data.get('brand'),
            search_data.get('model'),
            search_data.get('year'),
            search_data.get('mileage'),
            search_data.get('fuel', '가솔린'),
            search_data.get('predicted_price')
        ))
        
        # 전역 검색 통계 업데이트
        cursor.execute('''
            INSERT INTO search_stats (brand, model, search_count, last_searched)
            VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(brand, model) DO UPDATE SET 
                search_count = search_count + 1,
                last_searched = CURRENT_TIMESTAMP
        ''', (search_data.get('brand'), search_data.get('model')))
        
        conn.commit()
        history_id = cursor.lastrowid
        conn.close()
        
        return {'id': history_id, **search_data}
    
    def get_search_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """사용자 검색 이력 조회 (id 포함 - 개별 삭제용)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 가장 최근 검색 기록만 가져오면서 id도 반환 (개별 삭제 지원)
        cursor.execute('''
            SELECT id, brand, model, year, mileage, fuel, predicted_price, searched_at
            FROM search_history 
            WHERE user_id = ? AND id IN (
                SELECT MAX(id) 
                FROM search_history 
                WHERE user_id = ?
                GROUP BY brand, model, year
            )
            ORDER BY searched_at DESC
            LIMIT ?
        ''', (user_id, user_id, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'brand': row[1],
                'model': row[2],
                'year': row[3],
                'mileage': row[4],
                'fuel': row[5],
                'predicted_price': row[6],
                'last_searched': row[7]
            })
        
        conn.close()
        return results
    
    def remove_search_history(self, user_id: str, history_id: int) -> bool:
        """검색 이력 삭제"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM search_history WHERE id = ? AND user_id = ?
        ''', (history_id, user_id))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def clear_search_history(self, user_id: str) -> int:
        """검색 이력 전체 삭제"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM search_history WHERE user_id = ?
        ''', (user_id,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def get_trending_models(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """최근 N일간 인기 검색 모델 (전체 사용자 기준)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT brand, model, COUNT(*) as search_count
            FROM search_history
            WHERE searched_at >= ?
            GROUP BY brand, model
            ORDER BY search_count DESC
            LIMIT ?
        ''', (since, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'brand': row[0],
                'model': row[1],
                'search_count': row[2]
            })
        
        conn.close()
        return results
    
    # ========== 인기 모델 ==========
    
    def get_popular_models(self, category: str = 'all', limit: int = 5) -> List[Dict]:
        """엔카 데이터 기반 인기 모델"""
        if category == 'domestic':
            return self._popular_domestic[:limit]
        elif category == 'imported':
            return self._popular_imported[:limit]
        else:
            # 교차 배치
            result = []
            for i in range(limit):
                if i < len(self._popular_domestic):
                    result.append({**self._popular_domestic[i], 'type': 'domestic'})
                if i < len(self._popular_imported):
                    result.append({**self._popular_imported[i], 'type': 'imported'})
            return result[:limit * 2]
    
    # ========== 차량 추천 ==========
    
    def get_recommended_vehicles(self, user_id: str = None, 
                                  budget_min: int = None, budget_max: int = None,
                                  category: str = 'all', limit: int = 10) -> List[Dict]:
        """
        추천 차량 목록 (예측 가격 기반)
        
        추천 로직:
        1. 사용자 검색 이력 기반 선호 브랜드/모델
        2. 예산 범위 내 차량
        3. 가성비 좋은 차량 (실제가 < 예측가)
        """
        recommendations = []
        
        # 사용자 선호도 분석
        preferred_brands = []
        if user_id:
            history = self.get_search_history(user_id, limit=20)
            brand_counter = Counter(h['brand'] for h in history if h['brand'])
            preferred_brands = [b for b, _ in brand_counter.most_common(3)]
        
        # 데이터 선택
        if category == 'domestic' and self._domestic_df is not None:
            df = self._domestic_df.copy()
        elif category == 'imported' and self._imported_df is not None:
            df = self._imported_df.copy()
        else:
            # 합치기
            dfs = []
            if self._domestic_df is not None:
                dfs.append(self._domestic_df)
            if self._imported_df is not None:
                dfs.append(self._imported_df)
            df = pd.concat(dfs, ignore_index=True) if dfs else None
        
        if df is None or len(df) == 0:
            return []
        
        # 필터링 (이상치 제거 - 학습 데이터와 통일)
        df = df[(df['Price'] >= self.PRICE_MIN) & (df['Price'] <= self.PRICE_MAX)]
        df = df[~df['Price'].isin(self.SPECIAL_PRICES)]  # 특수 가격 제거 (9999 등)
        df = df[df['YearOnly'] >= 2018]  # 최근 7년 이내
        
        # car_id가 있는 차량만 선택 (상세페이지 연결 가능)
        df = df[df['Id'].notna() & (df['Id'] != '')]
        
        if budget_min:
            df = df[df['Price'] >= budget_min]
        if budget_max:
            df = df[df['Price'] <= budget_max]
        
        if len(df) == 0:
            return []
        
        # 예측 서비스 초기화 (lazy load)
        if self._prediction_service is None:
            try:
                from services.prediction_v12 import PredictionServiceV12
                self._prediction_service = PredictionServiceV12()
            except Exception as e:
                print(f"[WARN] 예측 서비스 로드 실패: {e}")
        
        # 샘플링 및 추천 점수 계산
        sample_size = min(100, len(df))
        sample = df.sample(sample_size, random_state=42)
        
        for _, row in sample.iterrows():
            try:
                car_id = row.get('Id', '')  # 엔카 차량 ID
                brand = row.get('Manufacturer', '')
                model = row.get('Model', '')
                year = int(row.get('YearOnly', 2020))
                mileage = int(row.get('Mileage', 50000))
                actual_price = int(row.get('Price', 0))
                fuel = str(row.get('FuelType', '가솔린'))
                
                # 연료 정규화
                fuel_norm = '가솔린'
                if '하이브리드' in fuel.lower(): fuel_norm = '하이브리드'
                elif '디젤' in fuel.lower(): fuel_norm = '디젤'
                elif 'lpg' in fuel.lower(): fuel_norm = 'LPG'
                
                # 예측 가격
                predicted_price = actual_price  # 기본값
                if self._prediction_service:
                    try:
                        result = self._prediction_service.predict(
                            brand, model, year, mileage, fuel=fuel_norm
                        )
                        predicted_price = result.predicted_price
                    except:
                        pass
                
                # 추천 점수 계산
                score = 0
                
                # 1. 가성비 (실제가 < 예측가면 +점수)
                price_diff = predicted_price - actual_price
                if price_diff > 0:
                    score += min(price_diff / 100, 10)  # 최대 10점
                
                # 2. 선호 브랜드 가산점
                if brand in preferred_brands:
                    score += 5
                
                # 3. 주행거리 적을수록 가산점
                if mileage < 30000:
                    score += 3
                elif mileage < 50000:
                    score += 2
                elif mileage < 80000:
                    score += 1
                
                # 4. 최신 연식 가산점
                if year >= 2023:
                    score += 3
                elif year >= 2021:
                    score += 2
                elif year >= 2019:
                    score += 1
                
                # 엔카 상세페이지 URL 생성
                detail_url = None
                if car_id:
                    detail_url = self.ENCAR_DETAIL_URL.format(car_id=car_id)

                # 옵션 정보 조회
                options = self.get_car_options(car_id) if car_id else None

                recommendations.append({
                    'brand': str(brand),
                    'model': str(model),
                    'year': int(year),
                    'mileage': int(mileage),
                    'fuel': str(fuel_norm),
                    'actual_price': int(actual_price),
                    'predicted_price': int(predicted_price),
                    'price_diff': int(price_diff),
                    'is_good_deal': bool(price_diff > 100),  # 명시적 bool 변환
                    'score': float(round(score, 1)),
                    'type': str(row.get('Type', 'domestic')),
                    'car_id': str(car_id) if car_id else None,
                    'detail_url': detail_url,
                    'options': options
                })
                
            except Exception as e:
                continue
        
        # 점수순 정렬
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:limit]
    
    def get_good_deals(self, category: str = 'all', limit: int = 10) -> List[Dict]:
        """
        가성비 좋은 차량 추천 (예측가 > 실제가)
        """
        return self.get_recommended_vehicles(
            category=category, 
            limit=limit * 2  # 필터링 후 줄어들 수 있으므로
        )[:limit]
    
    def get_model_deals(self, brand: str, model: str, limit: int = 10) -> List[Dict]:
        """
        특정 모델의 가성비 좋은 매물 추천
        
        가치 점수 계산:
        1. 가격 괴리율: (예측가 - 실제가) / 예측가 * 100 (최대 40점)
        2. 주행거리 점수: 낮을수록 좋음 (최대 30점)
        3. 연식 점수: 최신일수록 좋음 (최대 30점)
        """
        # 데이터 필터링
        dfs = []
        if self._domestic_df is not None:
            dfs.append(self._domestic_df)
        if self._imported_df is not None:
            dfs.append(self._imported_df)
        
        if not dfs:
            return []
        
        df = pd.concat(dfs, ignore_index=True)
        
        # 모델 필터링 (브랜드 + 정확한 모델 계열 매칭)
        brand_mask = df['Manufacturer'].str.contains(brand, case=False, na=False)
        # 정확한 모델 매칭 (E-클래스 ↔ E-클래스만, GLE-클래스 제외)
        model_mask = df['Model'].apply(lambda x: is_model_match(model, str(x)))
        df = df[brand_mask & model_mask]
        
        # 이상치 제거 + car_id 필수 (상세페이지 연결 가능한 차량만)
        df = df[(df['Price'] >= self.PRICE_MIN) & (df['Price'] <= self.PRICE_MAX)]
        df = df[~df['Price'].isin(self.SPECIAL_PRICES)]
        df = df[df['YearOnly'] >= 2018]
        df = df[df['Id'].notna() & (df['Id'] != '')]
        
        if len(df) == 0:
            return []
        
        # 예측 서비스 초기화
        if self._prediction_service is None:
            try:
                from services.prediction_v12 import PredictionServiceV12
                self._prediction_service = PredictionServiceV12()
            except:
                pass
        
        deals = []
        sample_size = min(50, len(df))
        sample = df.sample(sample_size, random_state=42) if len(df) > sample_size else df
        
        for _, row in sample.iterrows():
            try:
                # car_id 처리: NaN, 빈 문자열, None 모두 None으로 통일
                raw_car_id = row.get('Id', '')
                car_id = str(raw_car_id).strip() if raw_car_id and str(raw_car_id).strip() and str(raw_car_id) != 'nan' else None
                year = int(row.get('YearOnly', 2020))
                mileage = int(row.get('Mileage', 50000))
                actual_price = int(row.get('Price', 0))
                fuel = str(row.get('FuelType', '가솔린'))
                
                # 연료 정규화
                fuel_norm = '가솔린'
                if '하이브리드' in fuel.lower(): fuel_norm = '하이브리드'
                elif '디젤' in fuel.lower(): fuel_norm = '디젤'
                elif 'lpg' in fuel.lower(): fuel_norm = 'LPG'
                
                # 예측 가격 계산 (실제 데이터의 모델명 사용)
                actual_model_name = str(row.get('Model', model))
                predicted_price = actual_price
                if self._prediction_service:
                    try:
                        result = self._prediction_service.predict(
                            brand, actual_model_name, year, mileage, fuel=fuel_norm
                        )
                        predicted_price = result.predicted_price
                    except:
                        pass
                
                # 가치 점수 계산 (모든 값을 Python 기본 타입으로 변환)
                # 1. 가격 괴리율 (40점 만점)
                price_gap_pct = float((predicted_price - actual_price) / max(predicted_price, 1) * 100)
                price_score = float(min(max(price_gap_pct * 4, 0), 40))
                
                # 2. 주행거리 점수 (30점 만점)
                mileage_score = float(max(30 - (mileage / 3500), 0))
                
                # 3. 연식 점수 (30점 만점)
                year_score = float(min(max((year - 2018) * 5, 0), 30))
                
                total_score = float(price_score + mileage_score + year_score)
                
                # 엔카 URL 생성 (차량 ID 기반 상세 페이지)
                detail_url = None
                if car_id:
                    detail_url = self.ENCAR_DETAIL_URL.format(car_id=car_id)
                
                # 옵션 정보 조회
                options = self.get_car_options(car_id) if car_id else None
                
                deals.append({
                    'brand': str(brand),
                    'model': str(row.get('Model', model)),
                    'year': int(year),
                    'mileage': int(mileage),
                    'fuel': str(fuel_norm),
                    'actual_price': int(actual_price),
                    'predicted_price': int(predicted_price),
                    'price_diff': int(predicted_price - actual_price),
                    'value_score': round(total_score, 1),
                    'is_good_deal': price_gap_pct > 5,
                    'car_id': str(car_id) if car_id else None,
                    'detail_url': str(detail_url) if detail_url else None,
                    # 옵션 정보 (수집된 데이터 기반)
                    'options': options
                })
            except:
                continue
        
        # 정렬: 연식(최신순) → 가격(저렴순) → 주행거리(적은순)
        deals.sort(key=lambda x: (-x['year'], x['actual_price'], x['mileage']))
        return deals[:limit]
    
    # ========== 개별 매물 분석 ==========
    
    def analyze_deal(self, brand: str, model: str, year: int, mileage: int,
                     actual_price: int, predicted_price: int, fuel: str = '가솔린') -> Dict:
        """
        개별 매물 상세 분석
        - 가격 적정성
        - 허위매물 위험도
        - 네고 포인트
        """
        result = {
            'price_fairness': self._calculate_price_fairness(actual_price, predicted_price),
            'fraud_risk': self._calculate_fraud_risk(actual_price, predicted_price, year, mileage),
            'nego_points': self._generate_nego_points(actual_price, predicted_price, year, mileage),
            'summary': {}
        }
        
        # 요약 정보
        price_diff = predicted_price - actual_price
        price_diff_pct = (price_diff / predicted_price * 100) if predicted_price > 0 else 0
        
        result['summary'] = {
            'actual_price': int(actual_price),
            'predicted_price': int(predicted_price),
            'price_diff': int(price_diff),
            'price_diff_pct': round(price_diff_pct, 1),
            'is_good_deal': price_diff > 0,
            'verdict': self._get_verdict(price_diff_pct, result['fraud_risk']['score'])
        }
        
        return result
    
    def _calculate_price_fairness(self, actual_price: int, predicted_price: int) -> Dict:
        """가격 적정성 계산"""
        if predicted_price <= 0:
            return {'score': 50, 'label': '판단불가', 'percentile': 50, 'description': '예측가 정보 부족'}
        
        price_ratio = actual_price / predicted_price
        
        # 점수 계산 (저렴할수록 높은 점수)
        if price_ratio <= 0.85:
            score = 95
            label = '매우 저렴'
            percentile = 5
        elif price_ratio <= 0.95:
            score = 80
            label = '저렴'
            percentile = 15
        elif price_ratio <= 1.05:
            score = 60
            label = '적정'
            percentile = 50
        elif price_ratio <= 1.15:
            score = 40
            label = '다소 비쌈'
            percentile = 75
        else:
            score = 20
            label = '비쌈'
            percentile = 90
        
        descriptions = {
            '매우 저렴': '동일 조건 차량 중 매우 저렴합니다. 차량 상태를 꼼꼼히 확인하세요.',
            '저렴': '동일 조건 차량 중 저렴한 편입니다.',
            '적정': '시세에 맞는 적정 가격입니다.',
            '다소 비쌈': '시세보다 다소 높은 가격입니다. 네고 여지가 있습니다.',
            '비쌈': '시세보다 높은 가격입니다. 충분한 네고가 필요합니다.'
        }
        
        return {
            'score': score,
            'label': label,
            'percentile': percentile,
            'description': descriptions.get(label, '')
        }
    
    def _calculate_fraud_risk(self, actual_price: int, predicted_price: int, 
                               year: int, mileage: int) -> Dict:
        """허위매물 위험도 산출"""
        risk_score = 0
        factors = []
        
        # 1. 가격 범위 체크 (예측가의 70~130% 범위)
        if predicted_price > 0:
            price_ratio = actual_price / predicted_price
            
            if price_ratio < 0.7:
                risk_score += 40
                factors.append({
                    'check': 'price_too_cheap',
                    'status': 'fail',
                    'msg': '시세 대비 30% 이상 저렴 - 주의 필요'
                })
            elif price_ratio < 0.85:
                risk_score += 15
                factors.append({
                    'check': 'price_cheap',
                    'status': 'warn',
                    'msg': '시세 대비 다소 저렴 - 상태 확인 권장'
                })
            elif price_ratio > 1.3:
                risk_score += 10
                factors.append({
                    'check': 'price_expensive',
                    'status': 'warn',
                    'msg': '시세 대비 높은 가격'
                })
            else:
                factors.append({
                    'check': 'price_range',
                    'status': 'pass',
                    'msg': '가격이 시세 범위 내'
                })
        
        # 2. 주행거리 체크 (연간 1.5만km 기준)
        current_year = 2025
        age = max(current_year - year, 1)
        expected_mileage = age * 15000
        mileage_ratio = mileage / max(expected_mileage, 1)
        
        if mileage_ratio < 0.3:  # 너무 적음 (연식 대비)
            risk_score += 20
            factors.append({
                'check': 'mileage_low',
                'status': 'warn',
                'msg': f'주행거리가 연식 대비 매우 적음 ({mileage:,}km)'
            })
        elif mileage_ratio > 2.0:  # 너무 많음
            risk_score += 10
            factors.append({
                'check': 'mileage_high',
                'status': 'warn',
                'msg': f'주행거리가 평균보다 많음 ({mileage:,}km)'
            })
        else:
            avg_per_year = mileage / age
            factors.append({
                'check': 'mileage_normal',
                'status': 'pass',
                'msg': f'주행거리 정상 (연평균 {avg_per_year/10000:.1f}만km)'
            })
        
        # 3. 연식 체크
        if year >= 2020:
            factors.append({
                'check': 'year_recent',
                'status': 'pass',
                'msg': f'최근 연식 ({year}년)'
            })
        elif year >= 2015:
            risk_score += 5
            factors.append({
                'check': 'year_mid',
                'status': 'info',
                'msg': f'중간 연식 ({year}년) - 관리 상태 확인 권장'
            })
        else:
            risk_score += 15
            factors.append({
                'check': 'year_old',
                'status': 'warn',
                'msg': f'오래된 연식 ({year}년) - 정비 이력 확인 필수'
            })
        
        # 위험도 레벨 결정
        if risk_score >= 60:
            level = 'high'
        elif risk_score >= 30:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'score': min(risk_score, 100),
            'level': level,
            'factors': factors
        }
    
    def _generate_nego_points(self, actual_price: int, predicted_price: int,
                               year: int, mileage: int) -> List[str]:
        """네고 포인트 생성"""
        points = []
        
        price_diff = predicted_price - actual_price
        price_diff_pct = (price_diff / predicted_price * 100) if predicted_price > 0 else 0
        
        # 가격 기반 네고 포인트
        if price_diff_pct > 10:
            points.append('예측가 대비 이미 저렴하여 추가 네고 어려울 수 있음')
        elif price_diff_pct > 0:
            points.append(f'예측가 대비 {abs(price_diff):,}만원 저렴 - 소폭 네고 시도 가능')
        elif price_diff_pct > -5:
            points.append(f'예측가 수준 - {abs(price_diff):,}만원 정도 네고 시도')
        elif price_diff_pct > -15:
            points.append(f'예측가 대비 {abs(price_diff):,}만원 비쌈 - 적극 네고 필요')
        else:
            points.append(f'예측가 대비 많이 비쌈 - {abs(price_diff):,}만원 이상 네고 필수')
        
        # 일반적인 네고 포인트
        points.append('등록비용/이전비용 포함 협상 시도')
        points.append('소모품(타이어, 브레이크패드) 교체 여부 확인')
        
        # 주행거리 기반
        if mileage > 80000:
            points.append('주행거리 많음 - 타이밍벨트/체인 교체 여부 확인')
        
        # 연식 기반
        current_year = 2025
        age = current_year - year
        if age >= 5:
            points.append(f'{age}년 된 차량 - 주요 소모품 교체 이력 확인')
        
        return points
    
    def _get_verdict(self, price_diff_pct: float, fraud_risk_score: int) -> str:
        """종합 판정"""
        if fraud_risk_score >= 60:
            return '주의 필요'
        elif fraud_risk_score >= 30:
            if price_diff_pct > 5:
                return '확인 후 구매 권장'
            else:
                return '신중한 검토 필요'
        else:
            if price_diff_pct > 10:
                return '추천 매물'
            elif price_diff_pct > 0:
                return '괜찮은 매물'
            elif price_diff_pct > -10:
                return '적정 매물'
            else:
                return '네고 필요'
    
    # ========== 즐겨찾기 ==========
    
    def add_favorite(self, user_id: str, data: Dict) -> Dict:
        """즐겨찾기 추가"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        car_id = data.get('car_id')
        detail_url = data.get('detail_url')
        actual_price = data.get('actual_price')
        
        # 중복 체크 (car_id > detail_url > actual_price 순)
        if car_id:
            cursor.execute('SELECT id FROM favorites WHERE user_id = ? AND car_id = ?', (user_id, car_id))
        elif detail_url:
            cursor.execute('SELECT id FROM favorites WHERE user_id = ? AND detail_url = ?', (user_id, detail_url))
        else:
            cursor.execute('''
                SELECT id FROM favorites 
                WHERE user_id = ? AND brand = ? AND model = ? AND year = ? AND actual_price = ?
            ''', (user_id, data.get('brand'), data.get('model'), data.get('year'), actual_price))
        
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return {'success': False, 'message': '이미 즐겨찾기에 있습니다', 'id': existing[0]}
        
        cursor.execute('''
            INSERT INTO favorites (user_id, brand, model, year, mileage, fuel, predicted_price, actual_price, car_id, detail_url, memo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data.get('brand'),
            data.get('model'),
            data.get('year'),
            data.get('mileage'),
            data.get('fuel', '가솔린'),
            data.get('predicted_price'),
            actual_price,
            car_id,
            detail_url,
            data.get('memo', '')
        ))
        
        conn.commit()
        fav_id = cursor.lastrowid
        conn.close()
        
        return {'success': True, 'id': fav_id, **data}
    
    def get_favorites(self, user_id: str) -> List[Dict]:
        """즐겨찾기 목록 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, brand, model, year, mileage, fuel, predicted_price, actual_price, car_id, detail_url, memo, created_at
            FROM favorites
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'brand': row[1],
                'model': row[2],
                'year': row[3],
                'mileage': row[4],
                'fuel': row[5],
                'predicted_price': row[6],
                'actual_price': row[7],
                'car_id': row[8],
                'detail_url': row[9],
                'memo': row[10],
                'created_at': row[11]
            })
        
        conn.close()
        return results
    
    def remove_favorite(self, user_id: str, favorite_id: int) -> bool:
        """즐겨찾기 삭제"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM favorites WHERE id = ? AND user_id = ?
        ''', (favorite_id, user_id))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    # ========== 가격 알림 ==========
    
    def _init_alerts_table(self):
        """알림 테이블 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                brand TEXT,
                model TEXT,
                year INTEGER,
                target_price REAL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_price_alert(self, user_id: str, data: Dict) -> Dict:
        """가격 알림 설정"""
        self._init_alerts_table()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO price_alerts (user_id, brand, model, year, target_price, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (
            user_id,
            data.get('brand'),
            data.get('model'),
            data.get('year'),
            data.get('target_price')
        ))
        
        conn.commit()
        alert_id = cursor.lastrowid
        conn.close()
        
        return {'success': True, 'id': alert_id, **data}
    
    def get_alerts(self, user_id: str) -> List[Dict]:
        """알림 목록 조회"""
        self._init_alerts_table()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, brand, model, year, target_price, is_active, created_at
            FROM price_alerts
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'brand': row[1],
                'model': row[2],
                'year': row[3],
                'target_price': row[4],
                'is_active': bool(row[5]),
                'created_at': row[6]
            })
        
        conn.close()
        return results
    
    def toggle_alert(self, user_id: str, alert_id: int) -> Dict:
        """알림 활성화/비활성화 토글"""
        self._init_alerts_table()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE price_alerts 
            SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END
            WHERE id = ? AND user_id = ?
        ''', (alert_id, user_id))
        
        cursor.execute('SELECT is_active FROM price_alerts WHERE id = ?', (alert_id,))
        result = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'id': alert_id, 'is_active': bool(result[0]) if result else False}
    
    def remove_alert(self, user_id: str, alert_id: int) -> bool:
        """알림 삭제"""
        self._init_alerts_table()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM price_alerts WHERE id = ? AND user_id = ?
        ''', (alert_id, user_id))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted


# 싱글톤
_recommendation_service = None

def get_recommendation_service() -> RecommendationService:
    global _recommendation_service
    if _recommendation_service is None:
        _recommendation_service = RecommendationService()
    return _recommendation_service


if __name__ == "__main__":
    # 테스트
    service = get_recommendation_service()
    
    print("\n" + "="*60)
    print("📊 인기 모델 (국산)")
    print("="*60)
    for m in service.get_popular_models('domestic', 5):
        print(f"  {m['brand']} {m['model']}: {m['listings']}건, 평균 {m['avg_price']:,}만원")
    
    print("\n" + "="*60)
    print("📊 인기 모델 (외제)")
    print("="*60)
    for m in service.get_popular_models('imported', 5):
        print(f"  {m['brand']} {m['model']}: {m['listings']}건, 평균 {m['avg_price']:,}만원")
    
    print("\n" + "="*60)
    print("💡 추천 차량 (2000-3000만원)")
    print("="*60)
    for v in service.get_recommended_vehicles(budget_min=2000, budget_max=3000, limit=5):
        deal = "🔥 가성비" if v['is_good_deal'] else ""
        print(f"  {v['brand']} {v['model']} {v['year']}년 {v['mileage']/10000:.1f}만km")
        print(f"    실제: {v['actual_price']:,}만원, 예측: {v['predicted_price']:,}만원 ({v['price_diff']:+,}) {deal}")

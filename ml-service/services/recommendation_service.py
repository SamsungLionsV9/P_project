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

# 상위 경로 추가 (prediction_v12 사용 위함)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class RecommendationService:
    """엔카 데이터 기반 추천 시스템"""
    
    def __init__(self):
        self.data_path = Path(__file__).parent.parent.parent / "data"
        self.db_path = Path(__file__).parent.parent.parent / "data" / "user_data.db"
        
        self._domestic_df = None
        self._imported_df = None
        self._domestic_details_df = None  # 상세 옵션 데이터
        self._imported_details_df = None
        self._prediction_service = None
        
        self._init_db()
        self._load_data()
        self._load_details()  # 상세 옵션 데이터 로드
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
                source_url TEXT,
                memo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
        print(f"✓ DB 초기화 완료: {self.db_path}")
    
    def _load_data(self):
        """엔카 데이터 로드"""
        try:
            domestic_path = self.data_path / "encar_raw_domestic.csv"
            if domestic_path.exists():
                self._domestic_df = pd.read_csv(domestic_path)
                self._domestic_df['YearOnly'] = (self._domestic_df['Year'] // 100).astype(int)
                self._domestic_df['Type'] = 'domestic'
                print(f"✓ 국산차 데이터: {len(self._domestic_df):,}건")
        except Exception as e:
            print(f"⚠️ 국산차 로드 실패: {e}")
        
        try:
            imported_path = self.data_path / "encar_imported_data.csv"
            if imported_path.exists():
                self._imported_df = pd.read_csv(imported_path)
                self._imported_df['YearOnly'] = (self._imported_df['Year'] // 100).astype(int)
                self._imported_df['Type'] = 'imported'
                print(f"✓ 외제차 데이터: {len(self._imported_df):,}건")
        except Exception as e:
            print(f"⚠️ 외제차 로드 실패: {e}")
    
    def _load_details(self):
        """상세 옵션 데이터 로드 (complete_domestic_details.csv 등)"""
        try:
            domestic_detail_path = self.data_path / "complete_domestic_details.csv"
            if domestic_detail_path.exists():
                self._domestic_details_df = pd.read_csv(domestic_detail_path)
                print(f"✓ 국산차 상세 데이터: {len(self._domestic_details_df):,}건")
        except Exception as e:
            print(f"⚠️ 국산차 상세 로드 실패: {e}")
        
        try:
            imported_detail_path = self.data_path / "complete_imported_details.csv"
            if imported_detail_path.exists():
                self._imported_details_df = pd.read_csv(imported_detail_path)
                print(f"✓ 외제차 상세 데이터: {len(self._imported_details_df):,}건")
        except Exception as e:
            print(f"⚠️ 외제차 상세 로드 실패: {e}")
    
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
            
            print(f"✓ 국산 인기 모델 분석: {len(self._popular_domestic)}개")
        
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
            
            print(f"✓ 외제 인기 모델 분석: {len(self._popular_imported)}개")
    
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
        """사용자 검색 이력 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT brand, model, year, mileage, fuel, predicted_price, 
                   MAX(searched_at) as last_searched
            FROM search_history 
            WHERE user_id = ?
            GROUP BY brand, model, year
            ORDER BY last_searched DESC
            LIMIT ?
        ''', (user_id, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'brand': row[0],
                'model': row[1],
                'year': row[2],
                'mileage': row[3],
                'fuel': row[4],
                'predicted_price': row[5],
                'last_searched': row[6]
            })
        
        conn.close()
        return results
    
    def get_all_history(self, limit: int = 100) -> List[Dict]:
        """관리자용 - 모든 사용자의 검색 이력 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, brand, model, year, mileage, fuel, 
                   predicted_price, searched_at
            FROM search_history 
            ORDER BY searched_at DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'user_id': row[1],
                'brand': row[2],
                'model': row[3],
                'year': row[4],
                'mileage': row[5],
                'fuel': row[6],
                'predicted_price': row[7],
                'searched_at': row[8]
            })
        
        conn.close()
        return results
    
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
    
    def get_dashboard_stats(self) -> Dict:
        """대시보드 통계 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 오늘 날짜
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 오늘 조회 수
        cursor.execute('''
            SELECT COUNT(*) FROM search_history 
            WHERE DATE(searched_at) = ?
        ''', (today,))
        today_count = cursor.fetchone()[0]
        
        # 전체 누적 조회 수
        cursor.execute('SELECT COUNT(*) FROM search_history')
        total_count = cursor.fetchone()[0]
        
        # 평균 예측가 (오늘)
        cursor.execute('''
            SELECT AVG(predicted_price) FROM search_history 
            WHERE DATE(searched_at) = ? AND predicted_price IS NOT NULL
        ''', (today,))
        avg_price = cursor.fetchone()[0] or 0
        
        # 모델별 조회 수 (인기 모델)
        cursor.execute('''
            SELECT model, COUNT(*) as cnt FROM search_history
            GROUP BY model
            ORDER BY cnt DESC
            LIMIT 7
        ''')
        popular_models = [{'name': row[0] or '기타', 'value': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'todayCount': today_count,
            'totalCount': total_count,
            'avgPrice': round(avg_price, 0),
            'avgConfidence': 85,  # 고정값 (실제 신뢰도 평균)
            'popularModels': popular_models
        }
    
    def get_daily_request_stats(self, days: int = 7) -> List[Dict]:
        """일별 요청 통계"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        results = []
        for i in range(days - 1, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            day_name = ['월', '화', '수', '목', '금', '토', '일'][(datetime.now() - timedelta(days=i)).weekday()]
            
            cursor.execute('''
                SELECT COUNT(*) FROM search_history 
                WHERE DATE(searched_at) = ?
            ''', (date,))
            count = cursor.fetchone()[0]
            
            results.append({
                'date': date,
                'day': day_name,
                'count': count
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
        
        # 필터링
        df = df[(df['Price'] >= 100) & (df['Price'] <= 50000)]
        df = df[df['YearOnly'] >= 2018]  # 최근 7년 이내
        
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
                print(f"⚠️ 예측 서비스 로드 실패: {e}")
        
        # 샘플링 및 추천 점수 계산
        sample_size = min(100, len(df))
        sample = df.sample(sample_size, random_state=42)
        
        for _, row in sample.iterrows():
            try:
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
                
                # 옵션 정보 가져오기
                car_id = row.get('Id', None)
                is_imported = row.get('Type', 'domestic') == 'imported'
                options = self._get_vehicle_options(car_id, is_imported) if car_id else {}
                
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
                    'options': options,
                    'accident_free': options.get('accident_free', False),
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
    
    # ========== 즐겨찾기 ==========
    
    def add_favorite(self, user_id: str, data: Dict) -> Dict:
        """즐겨찾기 추가"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 중복 체크
        cursor.execute('''
            SELECT id FROM favorites 
            WHERE user_id = ? AND brand = ? AND model = ? AND year = ?
        ''', (user_id, data.get('brand'), data.get('model'), data.get('year')))
        
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return {'success': False, 'message': '이미 즐겨찾기에 있습니다', 'id': existing[0]}
        
        cursor.execute('''
            INSERT INTO favorites (user_id, brand, model, year, mileage, fuel, predicted_price, memo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data.get('brand'),
            data.get('model'),
            data.get('year'),
            data.get('mileage'),
            data.get('fuel', '가솔린'),
            data.get('predicted_price'),
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
            SELECT id, brand, model, year, mileage, fuel, predicted_price, memo, created_at
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
                'memo': row[7],
                'created_at': row[8]
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


    # ========== 차량 데이터 관리 (관리자용) ==========
    
    def _get_vehicle_options(self, car_id, is_imported: bool = False) -> Dict:
        """차량 ID로 옵션 정보 조회"""
        details_df = self._imported_details_df if is_imported else self._domestic_details_df
        if details_df is None:
            return {}
        
        try:
            row = details_df[details_df['car_id'] == car_id]
            if row.empty:
                return {}
            row = row.iloc[0]
            return {
                'sunroof': bool(row.get('has_sunroof', False)),
                'navigation': bool(row.get('has_navigation', False)),
                'leather_seat': bool(row.get('has_leather_seat', False)),
                'smart_key': bool(row.get('has_smart_key', False)),
                'rear_camera': bool(row.get('has_rear_camera', False)),
                'led_lamp': bool(row.get('has_led_lamp', False)),
                'heated_seat': bool(row.get('has_heated_seat', False)),
                'ventilated_seat': bool(row.get('has_ventilated_seat', False)),
                'accident_free': bool(row.get('is_accident_free', False)),
            }
        except Exception:
            return {}
    
    def get_vehicles_for_admin(self, brand: str = None, model: str = None,
                                year_min: int = None, year_max: int = None,
                                price_min: int = None, price_max: int = None,
                                category: str = "all", page: int = 1, limit: int = 20) -> Dict:
        """관리자용 차량 데이터 조회 (옵션 정보 포함)"""
        vehicles = []
        
        # 국산차 데이터 (컬럼: Manufacturer, Model, Year, Mileage, FuelType, Price, OfficeCityState)
        # Price 단위: 만원 (예: 2500 = 2500만원)
        if category in ['all', 'domestic'] and self._domestic_df is not None:
            df = self._domestic_df.copy()
            # 기본 필터: 합리적인 가격 범위만 (500만원 ~ 1억5천만원)
            # 99999 등 가격 미정 데이터 제외
            df = df[(df['Price'] >= 500) & (df['Price'] <= 15000)]
            # 연식 최신순 정렬
            df = df.sort_values('YearOnly', ascending=False)
            
            if brand:
                df = df[df['Manufacturer'].str.contains(brand, na=False, case=False)]
            if model:
                df = df[df['Model'].str.contains(model, na=False, case=False)]
            if year_min:
                df = df[df['YearOnly'] >= year_min]
            if year_max:
                df = df[df['YearOnly'] <= year_max]
            if price_min:
                df = df[df['Price'] >= price_min]
            if price_max:
                df = df[df['Price'] <= price_max]
            
            for idx, row in df.head(limit if category == 'domestic' else limit // 2).iterrows():
                price = int(row.get('Price', 0)) if pd.notna(row.get('Price')) else 0
                car_id = row.get('Id', idx)
                options = self._get_vehicle_options(car_id, is_imported=False)
                vehicles.append({
                    'id': int(idx) if isinstance(idx, (int, float)) else hash(str(idx)) % 1000000,
                    'car_id': car_id,
                    'category': 'domestic',
                    'brand': str(row.get('Manufacturer', '')),
                    'model': str(row.get('Model', '')),
                    'year': int(row.get('YearOnly', 0)),
                    'mileage': int(row.get('Mileage', 0)) if pd.notna(row.get('Mileage')) else 0,
                    'price': price,  # 만원 단위
                    'fuel': str(row.get('FuelType', '가솔린')),
                    'region': str(row.get('OfficeCityState', '')),
                    'options': options,
                    'accident_free': options.get('accident_free', False),
                })
        
        # 외제차 데이터
        if category in ['all', 'imported'] and self._imported_df is not None:
            df = self._imported_df.copy()
            # 기본 필터: 합리적인 가격 범위만 (500만원 ~ 5억원, 외제차는 범위가 넓음)
            df = df[(df['Price'] >= 500) & (df['Price'] <= 50000)]
            # 연식 최신순 정렬
            df = df.sort_values('YearOnly', ascending=False)
            
            if brand:
                df = df[df['Manufacturer'].str.contains(brand, na=False, case=False)]
            if model:
                df = df[df['Model'].str.contains(model, na=False, case=False)]
            if year_min:
                df = df[df['YearOnly'] >= year_min]
            if year_max:
                df = df[df['YearOnly'] <= year_max]
            if price_min:
                df = df[df['Price'] >= price_min]
            if price_max:
                df = df[df['Price'] <= price_max]
            
            for idx, row in df.head(limit if category == 'imported' else limit // 2).iterrows():
                price = int(row.get('Price', 0)) if pd.notna(row.get('Price')) else 0
                car_id = row.get('Id', idx)
                options = self._get_vehicle_options(car_id, is_imported=True)
                vehicles.append({
                    'id': (int(idx) if isinstance(idx, (int, float)) else hash(str(idx)) % 1000000) + 1000000,
                    'car_id': car_id,
                    'category': 'imported',
                    'brand': str(row.get('Manufacturer', '')),
                    'model': str(row.get('Model', '')),
                    'year': int(row.get('YearOnly', 0)),
                    'mileage': int(row.get('Mileage', 0)) if pd.notna(row.get('Mileage')) else 0,
                    'price': price,  # 만원 단위
                    'fuel': str(row.get('FuelType', '가솔린')),
                    'region': str(row.get('OfficeCityState', '')),
                    'options': options,
                    'accident_free': options.get('accident_free', False),
                })
        
        # 페이지네이션
        total = len(vehicles)
        start = (page - 1) * limit
        end = start + limit
        
        return {
            'vehicles': vehicles[start:end] if start < total else vehicles[:limit],
            'total': total,
            'page': page,
            'limit': limit
        }
    
    def get_vehicle_detail(self, vehicle_id: int, category: str = "domestic") -> Dict:
        """차량 상세 정보"""
        df = self._imported_df if category == 'imported' or vehicle_id >= 1000000 else self._domestic_df
        actual_id = vehicle_id - 1000000 if vehicle_id >= 1000000 else vehicle_id
        
        if df is None or actual_id not in df.index:
            return None
        
        row = df.loc[actual_id]
        return {
            'id': vehicle_id,
            'category': 'imported' if vehicle_id >= 1000000 else 'domestic',
            'brand': str(row.get('Manufacturer', '')),
            'model': str(row.get('Model', '')),
            'year': int(row.get('YearOnly', 0)),
            'mileage': int(row.get('Mileage', 0)) if pd.notna(row.get('Mileage')) else 0,
            'price': int(row.get('Price', 0)) if pd.notna(row.get('Price')) else 0,
            'fuel': str(row.get('FuelType', '')),
            'region': str(row.get('OfficeCityState', ''))
        }
    
    def get_vehicle_stats(self) -> Dict:
        """차량 데이터 통계"""
        domestic_count = len(self._domestic_df) if self._domestic_df is not None else 0
        imported_count = len(self._imported_df) if self._imported_df is not None else 0
        
        domestic_brands = {}
        imported_brands = {}
        
        if self._domestic_df is not None and 'Manufacturer' in self._domestic_df.columns:
            domestic_brands = self._domestic_df['Manufacturer'].value_counts().head(10).to_dict()
        
        if self._imported_df is not None and 'Manufacturer' in self._imported_df.columns:
            imported_brands = self._imported_df['Manufacturer'].value_counts().head(10).to_dict()
        
        return {
            'domesticCount': domestic_count,
            'importedCount': imported_count,
            'totalCount': domestic_count + imported_count,
            'domesticBrands': [{'brand': k, 'count': v} for k, v in domestic_brands.items()],
            'importedBrands': [{'brand': k, 'count': v} for k, v in imported_brands.items()]
        }


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

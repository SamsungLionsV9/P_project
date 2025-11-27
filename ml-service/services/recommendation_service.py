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
        self._prediction_service = None
        
        self._init_db()
        self._load_data()
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
                    'type': str(row.get('Type', 'domestic'))
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

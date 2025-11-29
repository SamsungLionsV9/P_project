"""
Database Service - SQLite 기반 영구 저장소
==========================================
기존 메모리 기반 저장소를 SQLite로 교체
- 분석 이력 (검색, 예측 결과)
- AI 로그 (네고대본, 시그널, 허위매물)
- 사용자 즐겨찾기/알림
- 통계 데이터 (신뢰도, 일별 요청수)
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import threading

class DatabaseService:
    """SQLite 기반 영구 저장소 서비스"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: str = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = None):
        if self._initialized:
            return
            
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, 'data', 'car_sentix.db')
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._create_tables()
        self._initialized = True
        print(f"✓ DB 초기화 완료: {db_path}")
    
    def _get_conn(self) -> sqlite3.Connection:
        """스레드별 DB 연결"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_tables(self):
        """테이블 생성"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # 분석 이력 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'anonymous',
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER,
                mileage INTEGER,
                fuel_type TEXT,
                predicted_price REAL,
                confidence REAL,
                timing_score INTEGER,
                signal TEXT,
                detail_url TEXT,
                request_data TEXT,
                response_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # AI 로그 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'anonymous',
                log_type TEXT NOT NULL,
                car_info TEXT,
                request_data TEXT,
                response_data TEXT,
                success INTEGER DEFAULT 1,
                ai_model TEXT DEFAULT 'llama-3.3-70b',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 일별 통계 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                request_count INTEGER DEFAULT 0,
                avg_confidence REAL DEFAULT 0,
                total_confidence REAL DEFAULT 0,
                confidence_count INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 모델별 조회 통계
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT UNIQUE NOT NULL,
                view_count INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 즐겨찾기 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                car_id INTEGER,
                car_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, car_id)
            )
        ''')
        
        # 가격 알림 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                target_price REAL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    # ========== 분석 이력 ==========

    def save_analysis(self, data: Dict) -> int:
        """분석 결과 저장"""
        conn = self._get_conn()
        cursor = conn.cursor()

        today = datetime.now().strftime("%Y-%m-%d")
        confidence = data.get('confidence', 85)

        cursor.execute('''
            INSERT INTO analysis_history
            (user_id, brand, model, year, mileage, fuel_type, predicted_price,
             confidence, timing_score, signal, detail_url, request_data, response_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('user_id', 'anonymous'),
            data.get('brand', ''),
            data.get('model', ''),
            data.get('year'),
            data.get('mileage'),
            data.get('fuel_type', ''),
            data.get('predicted_price'),
            confidence,
            data.get('timing_score'),
            data.get('signal'),
            data.get('detail_url'),
            json.dumps(data.get('request', {}), ensure_ascii=False),
            json.dumps(data.get('response', {}), ensure_ascii=False)
        ))

        # 일별 통계 업데이트
        cursor.execute('''
            INSERT INTO daily_stats (date, request_count, avg_confidence, total_confidence, confidence_count)
            VALUES (?, 1, ?, ?, 1)
            ON CONFLICT(date) DO UPDATE SET
                request_count = request_count + 1,
                total_confidence = total_confidence + ?,
                confidence_count = confidence_count + 1,
                avg_confidence = (total_confidence + ?) / (confidence_count + 1),
                updated_at = CURRENT_TIMESTAMP
        ''', (today, confidence, confidence, confidence, confidence))

        # 모델별 통계 업데이트
        model_name = data.get('model', '')
        if model_name:
            cursor.execute('''
                INSERT INTO model_stats (model_name, view_count)
                VALUES (?, 1)
                ON CONFLICT(model_name) DO UPDATE SET
                    view_count = view_count + 1,
                    updated_at = CURRENT_TIMESTAMP
            ''', (model_name,))

        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    def get_analysis_history(self, user_id: str = None, limit: int = 50) -> List[Dict]:
        """분석 이력 조회"""
        conn = self._get_conn()
        cursor = conn.cursor()

        if user_id and user_id != 'anonymous':
            cursor.execute('''
                SELECT * FROM analysis_history
                WHERE user_id = ?
                ORDER BY created_at DESC LIMIT ?
            ''', (user_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM analysis_history
                ORDER BY created_at DESC LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # ========== AI 로그 ==========

    def save_ai_log(self, log_type: str, data: Dict) -> int:
        """AI 로그 저장 (네고대본, 시그널, 허위매물)"""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO ai_logs
            (user_id, log_type, car_info, request_data, response_data, success, ai_model)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('user_id', 'anonymous'),
            log_type,
            data.get('car_info', ''),
            json.dumps(data.get('request', {}), ensure_ascii=False),
            json.dumps(data.get('response', {}), ensure_ascii=False),
            1 if data.get('success', True) else 0,
            data.get('ai_model', 'llama-3.3-70b')
        ))

        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    def get_ai_logs(self, log_type: str = None, limit: int = 100) -> List[Dict]:
        """AI 로그 조회"""
        conn = self._get_conn()
        cursor = conn.cursor()

        if log_type:
            cursor.execute('''
                SELECT * FROM ai_logs
                WHERE log_type = ?
                ORDER BY created_at DESC LIMIT ?
            ''', (log_type, limit))
        else:
            cursor.execute('''
                SELECT * FROM ai_logs
                ORDER BY created_at DESC LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            item = dict(row)
            try:
                item['request_data'] = json.loads(item['request_data']) if item['request_data'] else {}
                item['response_data'] = json.loads(item['response_data']) if item['response_data'] else {}
            except:
                pass
            result.append(item)

        return result

    def get_ai_stats(self) -> Dict:
        """AI 사용 통계"""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as total FROM ai_logs')
        total = cursor.fetchone()['total']

        cursor.execute('''
            SELECT log_type, COUNT(*) as count
            FROM ai_logs
            GROUP BY log_type
        ''')
        by_type = {row['log_type']: row['count'] for row in cursor.fetchall()}

        conn.close()

        return {
            "total_calls": total,
            "negotiation_scripts": by_type.get("negotiation", 0),
            "signal_reports": by_type.get("signal", 0),
            "fraud_detections": by_type.get("fraud_detection", 0)
        }

    # ========== 대시보드 통계 ==========

    def get_dashboard_stats(self) -> Dict:
        """대시보드 통계 (실제 데이터)"""
        conn = self._get_conn()
        cursor = conn.cursor()

        today = datetime.now().strftime("%Y-%m-%d")

        # 오늘 조회수
        cursor.execute('SELECT request_count FROM daily_stats WHERE date = ?', (today,))
        row = cursor.fetchone()
        today_count = row['request_count'] if row else 0

        # 전체 조회수
        cursor.execute('SELECT SUM(request_count) as total FROM daily_stats')
        row = cursor.fetchone()
        total_count = row['total'] if row and row['total'] else 0

        # 평균 신뢰도 (전체)
        cursor.execute('''
            SELECT AVG(confidence) as avg_conf FROM analysis_history
            WHERE confidence IS NOT NULL AND confidence > 0
        ''')
        row = cursor.fetchone()
        avg_confidence = round(row['avg_conf'], 1) if row and row['avg_conf'] else 0

        # 인기 모델 Top 5
        cursor.execute('''
            SELECT model_name as name, view_count as value
            FROM model_stats
            ORDER BY view_count DESC LIMIT 5
        ''')
        popular_models = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return {
            "success": True,
            "todayCount": today_count,
            "totalCount": total_count,
            "avgConfidence": avg_confidence if avg_confidence > 0 else 0,
            "popularModels": popular_models
        }

    def get_daily_requests(self, days: int = 7) -> Dict:
        """일별 요청 통계"""
        conn = self._get_conn()
        cursor = conn.cursor()

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)

        cursor.execute('''
            SELECT date as day, request_count as count
            FROM daily_stats
            WHERE date >= ? AND date <= ?
            ORDER BY date ASC
        ''', (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))

        data = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # 빈 날짜 채우기
        date_map = {d['day']: d['count'] for d in data}
        result = []
        for i in range(days):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            day_label = (start_date + timedelta(days=i)).strftime("%m/%d")
            result.append({
                "day": day_label,
                "count": date_map.get(date, 0)
            })

        return {"success": True, "data": result}

    # ========== 즐겨찾기 ==========

    def add_favorite(self, user_id: str, car_id: int, car_info: Dict) -> bool:
        """즐겨찾기 추가"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO favorites (user_id, car_id, car_info)
                VALUES (?, ?, ?)
            ''', (user_id, car_id, json.dumps(car_info, ensure_ascii=False)))
            conn.commit()
            return True
        except Exception as e:
            print(f"즐겨찾기 추가 실패: {e}")
            return False
        finally:
            conn.close()

    def get_favorites(self, user_id: str) -> List[Dict]:
        """즐겨찾기 조회"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM favorites WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            item = dict(row)
            try:
                item['car_info'] = json.loads(item['car_info']) if item['car_info'] else {}
            except:
                pass
            result.append(item)
        return result

    def remove_favorite(self, user_id: str, car_id: int) -> bool:
        """즐겨찾기 삭제"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM favorites WHERE user_id = ? AND car_id = ?', (user_id, car_id))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted


# 싱글톤 인스턴스 제공
_db_service = None

def get_database_service() -> DatabaseService:
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service


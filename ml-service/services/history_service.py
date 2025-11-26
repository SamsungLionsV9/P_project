"""
검색 히스토리 & 즐겨찾기 서비스
(메모리 기반 - 추후 DB 연동)
"""
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
import json

class HistoryService:
    """검색 히스토리 관리"""
    
    def __init__(self):
        # 메모리 저장소 (추후 Redis/DB로 교체)
        self._history: Dict[str, List[Dict]] = defaultdict(list)
        self._favorites: Dict[str, List[Dict]] = defaultdict(list)
        self._alerts: Dict[str, List[Dict]] = defaultdict(list)
    
    def add_history(self, user_id: str, search_data: Dict) -> Dict:
        """검색 이력 추가"""
        entry = {
            "id": f"h_{len(self._history[user_id]) + 1}",
            "timestamp": datetime.now().isoformat(),
            "brand": search_data.get("brand"),
            "model": search_data.get("model"),
            "year": search_data.get("year"),
            "mileage": search_data.get("mileage"),
            "predicted_price": search_data.get("predicted_price"),
            "timing_score": search_data.get("timing_score")
        }
        
        # 중복 제거 (같은 차량 재검색 시 업데이트)
        self._history[user_id] = [
            h for h in self._history[user_id]
            if not (h["brand"] == entry["brand"] and 
                   h["model"] == entry["model"] and
                   h["year"] == entry["year"])
        ]
        
        self._history[user_id].insert(0, entry)
        
        # 최대 50개 유지
        self._history[user_id] = self._history[user_id][:50]
        
        return entry
    
    def get_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """검색 이력 조회"""
        return self._history[user_id][:limit]
    
    def clear_history(self, user_id: str) -> bool:
        """검색 이력 삭제"""
        self._history[user_id] = []
        return True
    
    # ========== 즐겨찾기 ==========
    
    def add_favorite(self, user_id: str, vehicle_data: Dict) -> Dict:
        """즐겨찾기 추가"""
        entry = {
            "id": f"f_{len(self._favorites[user_id]) + 1}",
            "timestamp": datetime.now().isoformat(),
            "brand": vehicle_data.get("brand"),
            "model": vehicle_data.get("model"),
            "year": vehicle_data.get("year"),
            "mileage": vehicle_data.get("mileage"),
            "predicted_price": vehicle_data.get("predicted_price"),
            "sale_price": vehicle_data.get("sale_price"),
            "source_url": vehicle_data.get("source_url"),
            "memo": vehicle_data.get("memo", "")
        }
        
        # 중복 체크
        for fav in self._favorites[user_id]:
            if (fav["brand"] == entry["brand"] and 
                fav["model"] == entry["model"] and
                fav["year"] == entry["year"] and
                fav["mileage"] == entry["mileage"]):
                return {"error": "이미 즐겨찾기에 있습니다", "existing": fav}
        
        self._favorites[user_id].insert(0, entry)
        return entry
    
    def get_favorites(self, user_id: str) -> List[Dict]:
        """즐겨찾기 목록"""
        return self._favorites[user_id]
    
    def remove_favorite(self, user_id: str, favorite_id: str) -> bool:
        """즐겨찾기 삭제"""
        before = len(self._favorites[user_id])
        self._favorites[user_id] = [
            f for f in self._favorites[user_id] if f["id"] != favorite_id
        ]
        return len(self._favorites[user_id]) < before
    
    # ========== 가격 알림 ==========
    
    def add_alert(self, user_id: str, alert_data: Dict) -> Dict:
        """가격 알림 설정"""
        entry = {
            "id": f"a_{len(self._alerts[user_id]) + 1}",
            "created_at": datetime.now().isoformat(),
            "brand": alert_data.get("brand"),
            "model": alert_data.get("model"),
            "year_min": alert_data.get("year_min"),
            "year_max": alert_data.get("year_max"),
            "target_price": alert_data.get("target_price"),
            "alert_type": alert_data.get("alert_type", "below"),  # below, above, any
            "is_active": True
        }
        
        self._alerts[user_id].append(entry)
        return entry
    
    def get_alerts(self, user_id: str) -> List[Dict]:
        """가격 알림 목록"""
        return self._alerts[user_id]
    
    def toggle_alert(self, user_id: str, alert_id: str) -> Optional[Dict]:
        """알림 활성화/비활성화"""
        for alert in self._alerts[user_id]:
            if alert["id"] == alert_id:
                alert["is_active"] = not alert["is_active"]
                return alert
        return None
    
    def remove_alert(self, user_id: str, alert_id: str) -> bool:
        """알림 삭제"""
        before = len(self._alerts[user_id])
        self._alerts[user_id] = [
            a for a in self._alerts[user_id] if a["id"] != alert_id
        ]
        return len(self._alerts[user_id]) < before


class PopularService:
    """인기 차량 서비스"""
    
    # 인기 차량 (정적 데이터 - 추후 실시간 분석으로 교체)
    POPULAR_MODELS = {
        "domestic": [
            {"brand": "현대", "model": "그랜저", "searches": 15420, "avg_price": 3200},
            {"brand": "기아", "model": "K5", "searches": 12350, "avg_price": 2400},
            {"brand": "현대", "model": "아반떼", "searches": 11200, "avg_price": 1800},
            {"brand": "기아", "model": "쏘렌토", "searches": 10800, "avg_price": 3500},
            {"brand": "현대", "model": "투싼", "searches": 9500, "avg_price": 2800},
        ],
        "imported": [
            {"brand": "벤츠", "model": "E-클래스", "searches": 8900, "avg_price": 5500},
            {"brand": "BMW", "model": "5시리즈", "searches": 8200, "avg_price": 5200},
            {"brand": "벤츠", "model": "C-클래스", "searches": 7500, "avg_price": 4200},
            {"brand": "BMW", "model": "3시리즈", "searches": 7100, "avg_price": 4000},
            {"brand": "아우디", "model": "A6", "searches": 5800, "avg_price": 4800},
        ]
    }
    
    def get_popular(self, category: str = "all", limit: int = 5) -> List[Dict]:
        """인기 차량 목록"""
        if category == "domestic":
            return self.POPULAR_MODELS["domestic"][:limit]
        elif category == "imported":
            return self.POPULAR_MODELS["imported"][:limit]
        else:
            # 전체 (국산 + 외제 섞어서)
            combined = []
            for i in range(limit):
                if i < len(self.POPULAR_MODELS["domestic"]):
                    combined.append({**self.POPULAR_MODELS["domestic"][i], "type": "domestic"})
                if i < len(self.POPULAR_MODELS["imported"]):
                    combined.append({**self.POPULAR_MODELS["imported"][i], "type": "imported"})
            return combined[:limit]


# 싱글톤 인스턴스
_history_service = None
_popular_service = None

def get_history_service() -> HistoryService:
    global _history_service
    if _history_service is None:
        _history_service = HistoryService()
    return _history_service

def get_popular_service() -> PopularService:
    global _popular_service
    if _popular_service is None:
        _popular_service = PopularService()
    return _popular_service

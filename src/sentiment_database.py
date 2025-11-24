"""
차량 감성 데이터베이스 로더
- 실시간 크롤링 실패 시 대체 사용
- 전문가 평가 기반 감성 점수
"""

import json
import os


class VehicleSentimentDB:
    """차량 감성 데이터베이스"""
    
    def __init__(self, db_path=None):
        """
        Args:
            db_path: 데이터베이스 파일 경로 (None이면 자동 탐색)
        """
        if db_path is None:
            # 자동으로 경로 찾기
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'data', 'vehicle_sentiment.json')
        
        self.db_path = db_path
        self.data = self._load_db()
    
    def _load_db(self):
        """데이터베이스 로드"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ 감성 DB 파일을 찾을 수 없습니다: {self.db_path}")
            return {"vehicles": {}}
        except Exception as e:
            print(f"⚠️ 감성 DB 로드 실패: {e}")
            return {"vehicles": {}}
    
    def get_sentiment(self, car_model):
        """
        차량 모델의 감성 데이터 조회
        
        Args:
            car_model: 차량 모델명 (예: "그랜저", "아반떼")
            
        Returns:
            dict: 감성 분석 결과
                {
                    'score': -10 ~ +10,
                    'positive_ratio': 0.0 ~ 1.0,
                    'negative_ratio': 0.0 ~ 1.0,
                    'neutral_ratio': 0.0 ~ 1.0,
                    'trend': 'positive' | 'neutral' | 'negative',
                    'total_posts': int,
                    'summary': str
                }
        """
        vehicles = self.data.get('vehicles', {})
        
        # 정확한 매칭 시도
        if car_model in vehicles:
            return self._format_result(vehicles[car_model], car_model)
        
        # 부분 매칭 시도
        for key, value in vehicles.items():
            if car_model in key or key in car_model:
                print(f"  ℹ️ '{car_model}' → '{key}'로 매칭됨")
                return self._format_result(value, key)
        
        # 매칭 실패 시 중립 반환
        print(f"  ⚠️ '{car_model}' 감성 데이터 없음 → 중립값 사용")
        return self._get_neutral_result()
    
    def _format_result(self, data, model_name):
        """결과 포맷팅"""
        return {
            'score': data.get('score', 0),
            'positive_ratio': data.get('positive_ratio', 0.5),
            'negative_ratio': data.get('negative_ratio', 0.5),
            'neutral_ratio': data.get('neutral_ratio', 0.0),
            'trend': data.get('trend', 'neutral'),
            'total_posts': data.get('total_reviews', 0),
            'summary': data.get('summary', ''),
            'top_positive': data.get('top_positive', []),
            'top_negative': data.get('top_negative', []),
            'source': 'static_db',
            'model_name': model_name
        }
    
    def _get_neutral_result(self):
        """중립 결과 반환"""
        return {
            'score': 0,
            'positive_ratio': 0.5,
            'negative_ratio': 0.5,
            'neutral_ratio': 0.0,
            'trend': 'neutral',
            'total_posts': 0,
            'summary': '감성 데이터 없음',
            'top_positive': [],
            'top_negative': [],
            'source': 'default',
            'model_name': None
        }
    
    def list_available_models(self):
        """사용 가능한 차량 모델 목록"""
        vehicles = self.data.get('vehicles', {})
        return list(vehicles.keys())
    
    def get_all_sentiments(self):
        """모든 차량 감성 데이터"""
        return self.data.get('vehicles', {})


if __name__ == "__main__":
    # 테스트
    print("=" * 80)
    print("차량 감성 데이터베이스 테스트")
    print("=" * 80)
    
    db = VehicleSentimentDB()
    
    print(f"\n사용 가능한 차량: {len(db.list_available_models())}개")
    print(", ".join(db.list_available_models()[:10]))
    
    # 테스트 케이스
    test_models = ["그랜저", "아반떼", "K5", "테슬라"]
    
    for model in test_models:
        print(f"\n{'='*80}")
        print(f"🚗 {model}")
        print(f"{'='*80}")
        
        result = db.get_sentiment(model)
        
        print(f"점수: {result['score']:.1f}/10")
        print(f"긍정: {result['positive_ratio']:.0%} | 부정: {result['negative_ratio']:.0%}")
        print(f"추세: {result['trend']}")
        print(f"출처: {result['source']}")
        if result['summary']:
            print(f"요약: {result['summary']}")

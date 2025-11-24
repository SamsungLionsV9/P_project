"""
네이버 블로그 검색 API를 사용한 커뮤니티 감성 분석
- 크롤링 없이 공식 API 사용
- 안정적인 데이터 수집
"""

import os
import requests
from datetime import datetime, timedelta
import time


POSITIVE_KEYWORDS = [
    "빠르다", "조용", "부드럽", "안정적", "탄탄", "견고",
    "가성비", "저렴", "합리적", "혜자",
    "추천", "만족", "좋음", "훌륭", "최고", "굿", "괜찮",
    "계약", "구입", "샀어", "질렀",
    "예쁘", "멋지", "고급", "세련",
    "편하", "쾌적", "넓", "실용",
]

NEGATIVE_KEYWORDS = [
    "고장", "결함", "하자", "문제", "이슈", "불량",
    "실망", "후회", "최악", "별로", "아쉽",
    "리콜", "회수", "급발진",
    "흉기차", "폭탄", "쓰레기",
    "비싸", "비쌈", "부담",
    "시끄럽", "떨림", "소음", "진동",
]


class NaverBlogSentimentAnalyzer:
    """네이버 블로그 API 기반 감성 분석"""
    
    def __init__(self, client_id=None, client_secret=None):
        """
        Args:
            client_id: 네이버 API Client ID
            client_secret: 네이버 API Client Secret
        """
        from dotenv import load_dotenv
        load_dotenv()
        
        self.client_id = client_id or os.getenv('NAVER_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('NAVER_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            print("⚠️ 네이버 API 키가 설정되지 않았습니다")
    
    def search_blogs(self, query, display=100):
        """
        네이버 블로그 검색
        
        Args:
            query: 검색어
            display: 결과 개수 (최대 100)
            
        Returns:
            list: 블로그 포스트 리스트
        """
        if not self.client_id:
            return []
        
        url = "https://openapi.naver.com/v1/search/blog.json"
        
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        
        params = {
            "query": query,
            "display": display,
            "sort": "sim"  # 정확도순
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('items', [])
            
            print(f"  ✓ 네이버 블로그 {len(items)}개 검색 완료")
            
            return items
            
        except Exception as e:
            print(f"  ⚠️ 네이버 블로그 검색 실패: {e}")
            return []
    
    def analyze_sentiment(self, posts):
        """
        감성 분석
        
        Args:
            posts: 블로그 포스트 리스트
            
        Returns:
            dict: 감성 분석 결과
        """
        if not posts:
            return {
                'score': 0,
                'positive_ratio': 0.5,
                'negative_ratio': 0.5,
                'neutral_ratio': 0.0,
                'trend': 'neutral',
                'total_posts': 0,
                'source': 'naver_blog_api'
            }
        
        pos_count = 0
        neg_count = 0
        total_score = 0
        
        for post in posts:
            # title과 description 합치기
            text = (post.get('title', '') + ' ' + post.get('description', '')).lower()
            
            # HTML 태그 제거
            import re
            text = re.sub(r'<[^>]+>', '', text)
            
            # 긍정/부정 키워드 카운트
            pos_score = sum(1 for w in POSITIVE_KEYWORDS if w in text)
            neg_score = sum(1 for w in NEGATIVE_KEYWORDS if w in text)
            
            post_score = pos_score - neg_score
            total_score += post_score
            
            if post_score > 0:
                pos_count += 1
            elif post_score < 0:
                neg_count += 1
        
        total = len(posts)
        pos_ratio = pos_count / total if total > 0 else 0
        neg_ratio = neg_count / total if total > 0 else 0
        neu_ratio = 1 - pos_ratio - neg_ratio
        
        # 점수 정규화 (-10 ~ +10)
        avg_score = total_score / total if total > 0 else 0
        normalized_score = max(-10, min(10, avg_score))
        
        # 추세 판단
        if normalized_score > 2:
            trend = 'positive'
        elif normalized_score < -2:
            trend = 'negative'
        else:
            trend = 'neutral'
        
        result = {
            'score': round(normalized_score, 1),
            'positive_ratio': round(pos_ratio, 2),
            'negative_ratio': round(neg_ratio, 2),
            'neutral_ratio': round(neu_ratio, 2),
            'trend': trend,
            'total_posts': total,
            'source': 'naver_blog_api'
        }
        
        print(f"\n📊 감성 분석 (네이버 블로그 API):")
        print(f"  분석 대상: {total}개")
        print(f"  긍정: {result['positive_ratio']:.0%} | 부정: {result['negative_ratio']:.0%}")
        print(f"  점수: {result['score']:.1f}/10 ({result['trend']})")
        
        return result
    
    def collect_and_analyze(self, car_model, keywords_variations=None):
        """
        블로그 검색 + 감성 분석 통합
        
        Args:
            car_model: 차량 모델명
            keywords_variations: 추가 검색어 변형 (선택)
            
        Returns:
            dict: 감성 분석 결과
        """
        if keywords_variations is None:
            keywords_variations = [
                f"{car_model}",
                f"{car_model} 중고차",
                f"{car_model} 리뷰",
                f"{car_model} 후기"
            ]
        
        print(f"🔍 네이버 블로그 검색: {car_model}")
        
        all_posts = []
        
        for keyword in keywords_variations:
            posts = self.search_blogs(keyword, display=50)
            all_posts.extend(posts)
            time.sleep(0.1)  # API 호출 간격
        
        # 중복 제거 (링크 기준)
        unique_posts = []
        seen_links = set()
        for post in all_posts:
            link = post.get('link', '')
            if link not in seen_links:
                seen_links.add(link)
                unique_posts.append(post)
        
        print(f"  ✓ 총 {len(unique_posts)}개 고유 포스트")
        
        # 감성 분석
        result = self.analyze_sentiment(unique_posts)
        
        return result


if __name__ == "__main__":
    print("=" * 80)
    print("네이버 블로그 API 감성 분석 테스트")
    print("=" * 80)
    
    analyzer = NaverBlogSentimentAnalyzer()
    
    test_models = ["그랜저", "아반떼"]
    
    for model in test_models:
        print(f"\n{'='*80}")
        print(f"🚗 {model}")
        print(f"{'='*80}")
        
        result = analyzer.collect_and_analyze(model)
        
        print(f"\n최종 점수: {result['score']:.1f}/10")
        print(f"추세: {result['trend']}")

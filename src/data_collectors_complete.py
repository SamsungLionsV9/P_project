"""
Car-Sentix 타이밍 어드바이저 - 완전한 실제 데이터 수집기
- 한국은행 API (금리)
- 네이버 데이터랩 API (검색 트렌드)
- 실제 커뮤니티 크롤링
- 확장된 키워드 감성 분석
"""

import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import time
from bs4 import BeautifulSoup
import re
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# 기존 data_collectors_real.py의 모든 코드 import
from data_collectors_real import (
    POSITIVE_KEYWORDS, NEGATIVE_KEYWORDS, STRONG_POSITIVE, STRONG_NEGATIVE,
    RealCommunityCollector, RealMacroEconomicCollector
)
from data_collectors import NewCarScheduleManager


class NaverTrendAPI:
    """네이버 데이터랩 API로 실제 검색 트렌드 조회"""
    
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id or os.getenv('NAVER_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('NAVER_CLIENT_SECRET')
    
    def get_search_trend(self, keyword, days=30):
        """
        네이버 데이터랩 API로 실제 검색량 트렌드 조회
        
        Args:
            keyword: 검색 키워드
            days: 조회 기간 (일)
            
        Returns:
            dict: {'ratio': 1.2, 'trend': 'up', 'data': [...]}
        """
        print(f"🔍 네이버 데이터랩 '{keyword}' 검색 트렌드 조회 중...")
        
        if not self.client_id or not self.client_secret:
            print(f"  ⚠️ 네이버 API 키 없음. 대안 방법으로 전환")
            return self._get_trend_alternative(keyword)
        
        try:
            url = "https://openapi.naver.com/v1/datalab/search"
            
            headers = {
                "X-Naver-Client-Id": self.client_id,
                "X-Naver-Client-Secret": self.client_secret,
                "Content-Type": "application/json"
            }
            
            # 기간 설정: 최근 60일 (비교를 위해)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=60)
            
            body = {
                "startDate": start_date.strftime("%Y-%m-%d"),
                "endDate": end_date.strftime("%Y-%m-%d"),
                "timeUnit": "week",
                "keywordGroups": [
                    {
                        "groupName": keyword,
                        "keywords": [keyword]
                    }
                ],
                "device": "pc",  # pc, mo, or ""
                "ages": [],
                "gender": ""
            }
            
            response = requests.post(url, headers=headers, json=body, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'results' in data and len(data['results']) > 0:
                    results = data['results'][0]['data']
                    
                    # 최근 4주 vs 이전 4주 비교
                    if len(results) >= 8:
                        recent = results[-4:]
                        previous = results[-8:-4]
                        
                        recent_avg = sum(d['ratio'] for d in recent) / len(recent)
                        previous_avg = sum(d['ratio'] for d in previous) / len(previous)
                        
                        if previous_avg > 0:
                            ratio = recent_avg / previous_avg
                        else:
                            ratio = 1.0
                        
                        change_pct = (ratio - 1) * 100
                        
                        # 추세 판단
                        if ratio > 1.15:
                            trend = 'up'
                        elif ratio < 0.85:
                            trend = 'down'
                        else:
                            trend = 'stable'
                        
                        result = {
                            'keyword': keyword,
                            'ratio': round(ratio, 2),
                            'trend': trend,
                            'change_pct': round(change_pct, 1),
                            'recent_avg': round(recent_avg, 1),
                            'previous_avg': round(previous_avg, 1),
                            'data': results,
                            'source': '네이버 데이터랩 API'
                        }
                        
                        print(f"  ✓ 검색량 변화: {change_pct:+.1f}%")
                        print(f"  ✓ 추세: {trend}")
                        
                        return result
                    else:
                        print(f"  ⚠️ 데이터 부족 (최소 8주 필요)")
                        return self._get_trend_alternative(keyword)
                else:
                    print(f"  ⚠️ 검색 결과 없음")
                    return self._get_trend_alternative(keyword)
            
            elif response.status_code == 401:
                print(f"  ✗ 인증 실패 (API 키 확인 필요)")
                return self._get_trend_alternative(keyword)
            
            elif response.status_code == 403:
                print(f"  ✗ 권한 없음 (데이터랩 API 승인 대기 중일 수 있음)")
                return self._get_trend_alternative(keyword)
            
            else:
                print(f"  ✗ API 오류: {response.status_code}")
                return self._get_trend_alternative(keyword)
                
        except Exception as e:
            print(f"  ✗ API 호출 실패: {e}")
            return self._get_trend_alternative(keyword)
    
    def _get_trend_alternative(self, keyword):
        """
        네이버 API 없이 대안 방법으로 트렌드 추정
        (구글 트렌드 또는 네이버 블로그 검색량)
        """
        print(f"  → 대안: 네이버 블로그 검색량으로 추정")
        
        try:
            # 현재 검색량
            collector = RealCommunityCollector()
            current_count = collector.get_naver_blog_count(keyword)
            
            # 1개월 전 데이터는 없으므로, 상대적 지표만 제공
            # 검색량이 많으면 관심도가 높다고 가정
            
            if current_count > 10000:
                trend = 'up'
                ratio = 1.3
            elif current_count > 5000:
                trend = 'stable'
                ratio = 1.0
            else:
                trend = 'down'
                ratio = 0.8
            
            result = {
                'keyword': keyword,
                'ratio': ratio,
                'trend': trend,
                'blog_count': current_count,
                'source': '네이버 블로그 검색량 (추정)'
            }
            
            return result
            
        except Exception as e:
            print(f"  ✗ 대안 방법 실패: {e}")
            return {
                'keyword': keyword,
                'ratio': 1.0,
                'trend': 'stable',
                'source': 'default'
            }


def collect_complete_data(car_model):
    """
    모든 데이터 소스에서 실제 데이터 수집
    
    Args:
        car_model: 차량 모델명
        
    Returns:
        dict: 완전한 타이밍 분석 데이터
    """
    print("=" * 80)
    print(f"📡 '{car_model}' 완전한 데이터 수집 시작")
    print("=" * 80)
    
    # API 키 확인
    bok_key = os.getenv('BOK_API_KEY')
    naver_id = os.getenv('NAVER_CLIENT_ID')
    naver_secret = os.getenv('NAVER_CLIENT_SECRET')
    
    print(f"\n🔑 API 키 상태:")
    print(f"  한국은행: {'✓' if bok_key else '✗'}")
    print(f"  네이버 ID: {'✓' if naver_id else '✗'}")
    print(f"  네이버 Secret: {'✓' if naver_secret else '✗'}")
    print()
    
    # 1. 거시경제 지표
    print("📊 거시경제 지표 수집 중...")
    macro = RealMacroEconomicCollector(bok_key)
    macro_data = macro.get_all_indicators()
    
    print()
    
    # 2. 검색 트렌드 (네이버 데이터랩)
    print("🔍 검색 트렌드 수집 중...")
    trend_api = NaverTrendAPI(naver_id, naver_secret)
    trend_data = trend_api.get_search_trend(car_model)
    
    print()
    
    # 3. 커뮤니티 데이터
    print("💬 커뮤니티 데이터 수집 중...")
    
    sentiment_data = None
    posts = []
    
    # 방법 1: 보배드림 Selenium 크롤러 (실시간)
    try:
        from bobaedream_scraper import BobaedreamScraper
        
        scraper = BobaedreamScraper(headless=True)
        try:
            result = scraper.collect_all(car_model, limit=50)
            posts = result['posts']
            sentiment_data = result['sentiment']
            
            # 데이터가 너무 적으면 실패로 간주
            if sentiment_data['total_posts'] < 5:
                print(f"  ⚠️ 수집된 게시글이 너무 적음 ({sentiment_data['total_posts']}개)")
                sentiment_data = None
        finally:
            scraper.close()
            
    except Exception as e:
        print(f"  ⚠️ 보배드림 Selenium 실패: {e}")
    
    # 방법 2: 기본 크롤러 (실시간)
    if sentiment_data is None:
        print(f"  → 기본 크롤러 시도")
        try:
            community = RealCommunityCollector()
            posts = community.scrape_bobaedream(car_model, limit=50)
            
            if not posts:
                print(f"  → 네이버 블로그 시도")
                posts = community.search_naver_blog(f"{car_model} 중고차", limit=50)
            
            if posts and len(posts) >= 5:
                sentiment_data = community.analyze_sentiment_enhanced(posts)
        except Exception as e:
            print(f"  ⚠️ 기본 크롤러 실패: {e}")
    
    # 방법 3: 네이버 블로그 검색 API (실제 데이터) ⭐
    if sentiment_data is None or sentiment_data.get('total_posts', 0) < 5:
        print(f"  → 네이버 블로그 API 사용 (실제 데이터)")
        try:
            from naver_blog_api import NaverBlogSentimentAnalyzer
            
            analyzer = NaverBlogSentimentAnalyzer()
            sentiment_data = analyzer.collect_and_analyze(car_model)
            
            if sentiment_data['total_posts'] >= 10:
                print(f"  ✅ 네이버 블로그 {sentiment_data['total_posts']}개 분석 완료")
                print(f"    점수: {sentiment_data['score']:.1f}/10 ({sentiment_data['trend']})")
            else:
                print(f"  ⚠️ 데이터 부족 ({sentiment_data['total_posts']}개)")
                sentiment_data = None
                
        except Exception as e:
            print(f"  ⚠️ 네이버 블로그 API 실패: {e}")
            sentiment_data = None
    
    # 방법 4: 정적 데이터베이스 (최후의 대안)
    if sentiment_data is None or sentiment_data.get('total_posts', 0) < 5:
        print(f"  → 모든 실시간 수집 실패, 정적 DB 사용 (참고용)")
        try:
            from sentiment_database import VehicleSentimentDB
            
            db = VehicleSentimentDB()
            sentiment_data = db.get_sentiment(car_model)
            
            if sentiment_data['source'] == 'static_db':
                print(f"  ⚠️ '{sentiment_data['model_name']}' 정적 데이터 (참고용)")
                print(f"    점수: {sentiment_data['score']:.1f}/10 ({sentiment_data['trend']})")
            else:
                print(f"  ⚠️ DB에 없음, 중립값 사용")
                
        except Exception as e:
            print(f"  ⚠️ 정적 DB 로드 실패: {e}")
            # 최후의 대안: 중립값
            sentiment_data = {
                'score': 0,
                'positive_ratio': 0.5,
                'negative_ratio': 0.5,
                'neutral_ratio': 0.0,
                'trend': 'neutral',
                'total_posts': 0,
                'source': 'default'
            }
    
    print()
    
    # 4. 신차 일정
    print("🚗 신차 출시 일정 확인 중...")
    schedule = NewCarScheduleManager()
    schedule_data = schedule.check_upcoming_release(car_model)
    
    print()
    print("=" * 80)
    print("✅ 완전한 데이터 수집 완료!")
    print("=" * 80)
    
    return {
        'car_model': car_model,
        'macro': macro_data,
        'trend': trend_data,
        'community': {
            'posts': posts,
            'sentiment': sentiment_data,
            'post_count': len(posts)
        },
        'schedule': schedule_data,
        'collected_at': datetime.now().isoformat(),
        'api_status': {
            'bok': bool(bok_key),
            'naver_datalab': bool(naver_id and naver_secret)
        }
    }


if __name__ == "__main__":
    print("=" * 80)
    print("Car-Sentix 완전한 데이터 수집기 테스트")
    print("=" * 80)
    
    # 테스트 차량
    test_models = ["그랜저", "아반떼", "K5"]
    
    for model in test_models[:1]:  # 일단 하나만 테스트
        print(f"\n{'=' * 80}")
        print(f"테스트 차량: {model}")
        print(f"{'=' * 80}\n")
        
        data = collect_complete_data(model)
        
        # 결과 요약
        print("\n" + "=" * 80)
        print("📊 수집 데이터 요약")
        print("=" * 80)
        
        print(f"\n🚗 차량: {data['car_model']}")
        
        print(f"\n📊 거시경제:")
        print(f"  - 금리: {data['macro']['interest_rate']['rate']}% ({data['macro']['interest_rate']['trend']})")
        print(f"  - 유가: ${data['macro']['oil_price']['price']:.2f} ({data['macro']['oil_price']['trend']})")
        print(f"  - 환율: {data['macro']['exchange_rate']['rate']:.2f}원 ({data['macro']['exchange_rate']['trend']})")
        
        print(f"\n🔍 검색 트렌드:")
        print(f"  - 출처: {data['trend']['source']}")
        if 'change_pct' in data['trend']:
            print(f"  - 변화율: {data['trend']['change_pct']:+.1f}%")
        print(f"  - 추세: {data['trend']['trend']}")
        
        print(f"\n💬 커뮤니티:")
        print(f"  - 수집 게시글: {data['community']['post_count']}개")
        print(f"  - 긍정 비율: {data['community']['sentiment']['positive_ratio']:.0%}")
        print(f"  - 부정 비율: {data['community']['sentiment']['negative_ratio']:.0%}")
        print(f"  - 감성 점수: {data['community']['sentiment']['score']:.1f}/10")
        print(f"  - 추세: {data['community']['sentiment']['trend']}")
        
        print(f"\n🚗 신차 출시:")
        if data['schedule']['has_upcoming']:
            print(f"  - 예정 모델: {data['schedule']['new_model']}")
            print(f"  - 출시일: {data['schedule']['release_date']}")
            print(f"  - 영향도: {data['schedule']['impact']}")
        else:
            print(f"  - 예정 없음")
        
        print(f"\n🔑 API 상태:")
        print(f"  - 한국은행: {'✓ 작동' if data['api_status']['bok'] else '✗ 미설정'}")
        print(f"  - 네이버 데이터랩: {'✓ 작동' if data['api_status']['naver_datalab'] else '✗ 미설정'}")
        
        # JSON 저장
        output_file = f'complete_timing_data_{model}_{datetime.now().strftime("%Y%m%d_%H%M")}.json'
        
        # posts는 크기가 커서 요약만 저장
        save_data = data.copy()
        if data['community']['posts']:
            save_data['community']['posts_sample'] = [
                {
                    'title': p.get('title', ''),
                    'source': p.get('source', '')
                }
                for p in data['community']['posts'][:10]
            ]
        del save_data['community']['posts']
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 데이터 저장: {output_file}")
    
    print("\n" + "=" * 80)
    print("🎉 테스트 완료!")
    print("=" * 80)
    print("\n✅ 실제 데이터 수집 시스템 가동 중")
    print("✅ 한국은행 API: 실시간 금리")
    print("✅ 네이버 데이터랩 API: 검색 트렌드")
    print("✅ 커뮤니티 크롤링: 감성 분석")
    print("✅ 신차 일정: 타이밍 분석")
    print("\n🚀 다음 단계: 타이밍 점수 엔진 구현")

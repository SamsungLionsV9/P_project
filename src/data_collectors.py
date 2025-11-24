"""
Car-Sentix 타이밍 어드바이저 - 데이터 수집기
1. 거시경제 지표 (금리, 유가, 환율)
2. 네이버 검색 트렌드
3. 신차 출시 일정
"""

import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import time
from bs4 import BeautifulSoup

class MacroEconomicCollector:
    """거시경제 지표 수집기"""
    
    def __init__(self):
        self.cache = {}
        
    def get_interest_rate(self):
        """
        한국 기준금리 조회
        
        Returns:
            dict: {'rate': 3.5, 'date': '2025-01-01', 'trend': 'up'}
        """
        print("📊 금리 정보 수집 중...")
        
        try:
            # 방법 1: 한국은행 Open API (API 키 필요)
            # 여기서는 시뮬레이션
            
            # 실제 구현 시:
            # BOK_API_KEY = "YOUR_API_KEY"
            # url = f"https://ecos.bok.or.kr/api/StatisticSearch/{BOK_API_KEY}/json/kr/1/1/722Y001/M/202401/202412/0101000"
            
            # 임시 데이터 (실제로는 API에서 가져옴)
            current_rate = 3.25  # 2024년 기준
            
            # 추세 계산 (6개월 전과 비교)
            # 실제로는 과거 데이터를 가져와서 계산
            previous_rate = 3.50
            trend = 'down' if current_rate < previous_rate else 'up' if current_rate > previous_rate else 'stable'
            
            result = {
                'rate': current_rate,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'trend': trend,
                'previous_rate': previous_rate,
                'change': current_rate - previous_rate,
                'source': '한국은행 (시뮬레이션)'
            }
            
            print(f"  ✓ 현재 금리: {current_rate}%")
            print(f"  ✓ 추세: {trend}")
            
            return result
            
        except Exception as e:
            print(f"  ✗ 금리 조회 실패: {e}")
            # 기본값 반환
            return {
                'rate': 3.5,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'trend': 'stable',
                'source': 'default'
            }
    
    def get_oil_price(self):
        """
        국제 유가 조회 (WTI 원유)
        
        Returns:
            dict: {'price': 75.5, 'date': '2025-01-01', 'trend': 'up'}
        """
        print("🛢️ 유가 정보 수집 중...")
        
        try:
            # yfinance로 WTI 원유 가격 조회
            oil = yf.Ticker("CL=F")
            history = oil.history(period="5d")
            
            if not history.empty:
                current_price = history['Close'].iloc[-1]
                previous_price = history['Close'].iloc[0]
                
                trend = 'up' if current_price > previous_price * 1.02 else \
                        'down' if current_price < previous_price * 0.98 else 'stable'
                
                result = {
                    'price': round(current_price, 2),
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'trend': trend,
                    'previous_price': round(previous_price, 2),
                    'change': round(current_price - previous_price, 2),
                    'change_pct': round((current_price - previous_price) / previous_price * 100, 2),
                    'source': 'Yahoo Finance (WTI)'
                }
                
                print(f"  ✓ 현재 유가: ${current_price:.2f}")
                print(f"  ✓ 추세: {trend}")
                
                return result
            else:
                raise ValueError("유가 데이터 없음")
                
        except Exception as e:
            print(f"  ✗ 유가 조회 실패: {e}")
            # 기본값 반환
            return {
                'price': 75.0,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'trend': 'stable',
                'source': 'default'
            }
    
    def get_exchange_rate(self):
        """
        USD/KRW 환율 조회
        
        Returns:
            dict: {'rate': 1300, 'date': '2025-01-01', 'trend': 'up'}
        """
        print("💱 환율 정보 수집 중...")
        
        try:
            # yfinance로 USD/KRW 환율 조회
            krw = yf.Ticker("KRW=X")
            history = krw.history(period="5d")
            
            if not history.empty:
                current_rate = history['Close'].iloc[-1]
                previous_rate = history['Close'].iloc[0]
                
                trend = 'up' if current_rate > previous_rate * 1.01 else \
                        'down' if current_rate < previous_rate * 0.99 else 'stable'
                
                result = {
                    'rate': round(current_rate, 2),
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'trend': trend,
                    'previous_rate': round(previous_rate, 2),
                    'change': round(current_rate - previous_rate, 2),
                    'source': 'Yahoo Finance'
                }
                
                print(f"  ✓ 현재 환율: {current_rate:.2f}원")
                print(f"  ✓ 추세: {trend}")
                
                return result
            else:
                raise ValueError("환율 데이터 없음")
                
        except Exception as e:
            print(f"  ✗ 환율 조회 실패: {e}")
            # 기본값 반환
            return {
                'rate': 1300.0,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'trend': 'stable',
                'source': 'default'
            }
    
    def get_all_indicators(self):
        """모든 거시경제 지표 수집"""
        return {
            'interest_rate': self.get_interest_rate(),
            'oil_price': self.get_oil_price(),
            'exchange_rate': self.get_exchange_rate(),
            'collected_at': datetime.now().isoformat()
        }


class NaverTrendCollector:
    """네이버 검색 트렌드 수집기"""
    
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id
        self.client_secret = client_secret
        
    def get_search_trend(self, keyword, days=30):
        """
        네이버 검색량 트렌드 조회
        
        Args:
            keyword: 검색 키워드 (예: "그랜저")
            days: 조회 기간 (일)
            
        Returns:
            dict: {'ratio': 1.2, 'trend': 'up', 'raw_data': [...]}
        """
        print(f"🔍 '{keyword}' 검색 트렌드 수집 중...")
        
        try:
            # 실제 구현 시 네이버 데이터랩 API 사용
            # if not self.client_id or not self.client_secret:
            #     raise ValueError("네이버 API 키 필요")
            
            # url = "https://openapi.naver.com/v1/datalab/search"
            # headers = {
            #     "X-Naver-Client-Id": self.client_id,
            #     "X-Naver-Client-Secret": self.client_secret,
            #     "Content-Type": "application/json"
            # }
            # body = {
            #     "startDate": (datetime.now() - timedelta(days=days*2)).strftime("%Y-%m-%d"),
            #     "endDate": datetime.now().strftime("%Y-%m-%d"),
            #     "timeUnit": "week",
            #     "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}]
            # }
            # response = requests.post(url, headers=headers, data=json.dumps(body))
            
            # 임시 시뮬레이션 데이터
            import random
            
            # 최근 기간과 이전 기간의 평균 검색량
            recent_avg = random.uniform(80, 150)
            previous_avg = random.uniform(70, 120)
            
            ratio = recent_avg / previous_avg
            trend = 'up' if ratio > 1.15 else 'down' if ratio < 0.85 else 'stable'
            
            result = {
                'keyword': keyword,
                'ratio': round(ratio, 2),
                'trend': trend,
                'recent_avg': round(recent_avg, 1),
                'previous_avg': round(previous_avg, 1),
                'change_pct': round((ratio - 1) * 100, 1),
                'period_days': days,
                'source': '시뮬레이션',
                'collected_at': datetime.now().isoformat()
            }
            
            print(f"  ✓ 검색량 변화: {result['change_pct']:+.1f}%")
            print(f"  ✓ 추세: {trend}")
            
            return result
            
        except Exception as e:
            print(f"  ✗ 검색 트렌드 조회 실패: {e}")
            return {
                'keyword': keyword,
                'ratio': 1.0,
                'trend': 'stable',
                'source': 'default'
            }
    
    def get_related_keywords(self, keyword):
        """연관 검색어 조회 (보너스 기능)"""
        print(f"🔗 '{keyword}' 연관 검색어 수집 중...")
        
        # 시뮬레이션
        related = [
            f"{keyword} 가격",
            f"{keyword} 중고",
            f"{keyword} 리뷰",
            f"{keyword} 결함"
        ]
        
        print(f"  ✓ {len(related)}개 연관 검색어 발견")
        
        return related


class CommunityCollector:
    """커뮤니티 데이터 수집기"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_bobaedream_simple(self, car_model, limit=50):
        """
        보배드림 간단 크롤링 (키워드만)
        
        Args:
            car_model: 차량 모델명
            limit: 수집할 게시글 수
            
        Returns:
            list: [{'title': '...', 'date': '...', 'sentiment': 'positive'}, ...]
        """
        print(f"💬 '{car_model}' 커뮤니티 데이터 수집 중...")
        
        try:
            # 실제 크롤링 대신 시뮬레이션
            # 실제 구현 시:
            # url = f"https://www.bobaedream.co.kr/search?q={car_model}"
            # response = requests.get(url, headers=self.headers)
            # soup = BeautifulSoup(response.text, 'html.parser')
            
            # 시뮬레이션 데이터
            import random
            
            positive_words = ['추천', '만족', '좋음', '가성비', '계약', '성공']
            negative_words = ['고장', '결함', '후회', '리콜', '하자', '불만']
            neutral_words = ['문의', '질문', '비교', '고민']
            
            posts = []
            for i in range(limit):
                # 랜덤하게 긍정/부정/중립 키워드 선택
                sentiment_type = random.choices(
                    ['positive', 'negative', 'neutral'],
                    weights=[0.5, 0.3, 0.2]
                )[0]
                
                if sentiment_type == 'positive':
                    word = random.choice(positive_words)
                    sentiment = 'positive'
                elif sentiment_type == 'negative':
                    word = random.choice(negative_words)
                    sentiment = 'negative'
                else:
                    word = random.choice(neutral_words)
                    sentiment = 'neutral'
                
                posts.append({
                    'title': f"{car_model} {word} 관련 글",
                    'date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
                    'sentiment': sentiment
                })
            
            # 감성 통계
            pos_count = sum(1 for p in posts if p['sentiment'] == 'positive')
            neg_count = sum(1 for p in posts if p['sentiment'] == 'negative')
            neu_count = sum(1 for p in posts if p['sentiment'] == 'neutral')
            
            print(f"  ✓ {len(posts)}개 게시글 수집")
            print(f"  ✓ 긍정: {pos_count}, 부정: {neg_count}, 중립: {neu_count}")
            
            return posts
            
        except Exception as e:
            print(f"  ✗ 커뮤니티 크롤링 실패: {e}")
            return []
    
    def analyze_sentiment_simple(self, posts):
        """
        간단한 감성 분석 (키워드 기반)
        
        Args:
            posts: 게시글 리스트
            
        Returns:
            dict: {'positive_ratio': 0.6, 'score': 20, 'trend': 'positive'}
        """
        if not posts:
            return {
                'positive_ratio': 0.5,
                'negative_ratio': 0.5,
                'score': 0,
                'trend': 'neutral'
            }
        
        pos_count = sum(1 for p in posts if p['sentiment'] == 'positive')
        neg_count = sum(1 for p in posts if p['sentiment'] == 'negative')
        total = len(posts)
        
        pos_ratio = pos_count / total
        neg_ratio = neg_count / total
        
        # 점수 계산 (-10 ~ +10)
        score = round((pos_ratio - neg_ratio) * 10, 1)
        
        # 추세 판단
        if score > 3:
            trend = 'positive'
        elif score < -3:
            trend = 'negative'
        else:
            trend = 'neutral'
        
        return {
            'positive_ratio': round(pos_ratio, 2),
            'negative_ratio': round(neg_ratio, 2),
            'neutral_ratio': round(1 - pos_ratio - neg_ratio, 2),
            'score': score,
            'trend': trend,
            'total_posts': total
        }


class NewCarScheduleManager:
    """신차 출시 일정 관리"""
    
    def __init__(self, db_file='new_car_schedule.csv'):
        self.db_file = db_file
        self._initialize_db()
    
    def _initialize_db(self):
        """초기 데이터베이스 생성"""
        try:
            self.schedule = pd.read_csv(self.db_file)
            print(f"✓ 신차 일정 DB 로드: {len(self.schedule)}개")
        except FileNotFoundError:
            # 샘플 데이터 생성
            print("⚠️ 신차 일정 DB 없음. 샘플 생성 중...")
            
            sample_data = [
                {'brand': '현대', 'model': '그랜저 (8세대)', 'release_date': '2025-03-01', 'type': '풀체인지'},
                {'brand': '기아', 'model': 'K9 (4세대)', 'release_date': '2025-06-01', 'type': '풀체인지'},
                {'brand': '제네시스', 'model': 'GV80 쿠페', 'release_date': '2025-09-01', 'type': '신모델'},
                {'brand': '현대', 'model': '아반떼 (CN7) 페이스리프트', 'release_date': '2025-04-01', 'type': '페이스리프트'},
                {'brand': '기아', 'model': 'K5 페이스리프트', 'release_date': '2025-07-01', 'type': '페이스리프트'},
            ]
            
            self.schedule = pd.DataFrame(sample_data)
            self.schedule.to_csv(self.db_file, index=False, encoding='utf-8-sig')
            print(f"✓ 샘플 DB 생성: {len(self.schedule)}개")
    
    def check_upcoming_release(self, car_model):
        """
        특정 모델의 신차 출시 예정 확인 (미래 일정만)
        
        Args:
            car_model: 차량 모델명
            
        Returns:
            dict: {'has_upcoming': True, 'months_until': 3, 'new_model': '...', 'type': '풀체인지'}
        """
        print(f"🚗 '{car_model}' 신차 출시 일정 확인 중...")
        
        # 모델명에서 핵심 키워드 추출 (간단 버전)
        base_model = car_model.split()[0] if car_model else ""
        
        # 오늘 날짜
        today = datetime.now()
        
        # 날짜 컬럼을 datetime으로 변환
        self.schedule['release_date_dt'] = pd.to_datetime(self.schedule['release_date'])
        
        # 미래 일정만 필터링 + 모델 검색
        upcoming = self.schedule[
            (self.schedule['model'].str.contains(base_model, case=False, na=False)) &
            (self.schedule['release_date_dt'] > today)
        ].sort_values('release_date_dt')
        
        if not upcoming.empty:
            # 가장 가까운 출시일 선택
            release_date = upcoming.iloc[0]['release_date_dt']
            days_until = (release_date - today).days
            months_until = round(days_until / 30, 1)
            
            # 영향도 계산 (출시가 가까울수록 영향 큼)
            if months_until <= 3:
                impact = 'high'
                impact_score = -20  # 곧 신차 나옴 → 중고차 가격 하락 예상
            elif months_until <= 6:
                impact = 'medium'
                impact_score = -10
            else:
                impact = 'low'
                impact_score = -5
            
            result = {
                'has_upcoming': True,
                'new_model': upcoming.iloc[0]['model'],
                'release_date': release_date.strftime('%Y-%m-%d'),
                'days_until': days_until,
                'months_until': months_until,
                'type': upcoming.iloc[0]['type'],
                'impact': impact,
                'impact_score': impact_score  # 타이밍 점수에 반영
            }
            
            print(f"  ✓ 출시 예정: {result['new_model']}")
            print(f"  ✓ 출시일: {result['release_date']} ({months_until:.1f}개월 후)")
            print(f"  ✓ 영향도: {impact}")
            
        else:
            result = {
                'has_upcoming': False,
                'months_until': 999,
                'impact': 'none',
                'impact_score': 0
            }
            
            print(f"  ✓ 예정된 신차 없음")
        
        return result
    
    def add_schedule(self, brand, model, release_date, type='풀체인지'):
        """신차 일정 추가"""
        new_row = {
            'brand': brand,
            'model': model,
            'release_date': release_date,
            'type': type
        }
        
        self.schedule = pd.concat([self.schedule, pd.DataFrame([new_row])], ignore_index=True)
        self.schedule.to_csv(self.db_file, index=False, encoding='utf-8-sig')
        
        print(f"✓ 신차 일정 추가: {model} ({release_date})")


# 통합 데이터 수집 함수
def collect_all_data(car_model):
    """
    모든 데이터를 한 번에 수집
    
    Args:
        car_model: 차량 모델명
        
    Returns:
        dict: 모든 수집 데이터
    """
    print("=" * 80)
    print(f"📡 '{car_model}' 타이밍 분석 데이터 수집 시작")
    print("=" * 80)
    
    # 1. 거시경제 지표
    macro = MacroEconomicCollector()
    macro_data = macro.get_all_indicators()
    
    print()
    
    # 2. 검색 트렌드
    trend = NaverTrendCollector()
    trend_data = trend.get_search_trend(car_model)
    
    print()
    
    # 3. 커뮤니티 감성
    community = CommunityCollector()
    posts = community.scrape_bobaedream_simple(car_model, limit=50)
    sentiment_data = community.analyze_sentiment_simple(posts)
    
    print()
    
    # 4. 신차 출시 일정
    schedule = NewCarScheduleManager()
    schedule_data = schedule.check_upcoming_release(car_model)
    
    print()
    print("=" * 80)
    print("✅ 데이터 수집 완료!")
    print("=" * 80)
    
    return {
        'car_model': car_model,
        'macro': macro_data,
        'trend': trend_data,
        'sentiment': sentiment_data,
        'schedule': schedule_data,
        'collected_at': datetime.now().isoformat()
    }


if __name__ == "__main__":
    # 테스트
    print("=" * 80)
    print("Car-Sentix 데이터 수집기 테스트")
    print("=" * 80)
    
    # 샘플 차량으로 테스트
    test_model = "그랜저"
    
    data = collect_all_data(test_model)
    
    # 결과 요약 출력
    print("\n" + "=" * 80)
    print("📊 수집 데이터 요약")
    print("=" * 80)
    
    print(f"\n🚗 차량: {data['car_model']}")
    
    print(f"\n📊 거시경제:")
    print(f"  - 금리: {data['macro']['interest_rate']['rate']}% ({data['macro']['interest_rate']['trend']})")
    print(f"  - 유가: ${data['macro']['oil_price']['price']:.2f} ({data['macro']['oil_price']['trend']})")
    print(f"  - 환율: {data['macro']['exchange_rate']['rate']:.2f}원 ({data['macro']['exchange_rate']['trend']})")
    
    print(f"\n🔍 검색 트렌드:")
    print(f"  - 변화율: {data['trend']['change_pct']:+.1f}%")
    print(f"  - 추세: {data['trend']['trend']}")
    
    print(f"\n💬 커뮤니티 감성:")
    print(f"  - 긍정 비율: {data['sentiment']['positive_ratio']:.0%}")
    print(f"  - 부정 비율: {data['sentiment']['negative_ratio']:.0%}")
    print(f"  - 감성 점수: {data['sentiment']['score']:.1f}/10")
    print(f"  - 추세: {data['sentiment']['trend']}")
    
    print(f"\n🚗 신차 출시:")
    if data['schedule']['has_upcoming']:
        print(f"  - 예정 모델: {data['schedule']['new_model']}")
        print(f"  - 출시일: {data['schedule']['release_date']} ({data['schedule']['months_until']:.1f}개월 후)")
        print(f"  - 영향도: {data['schedule']['impact']}")
    else:
        print(f"  - 예정 없음")
    
    # JSON 저장
    output_file = f'timing_data_{test_model}_{datetime.now().strftime("%Y%m%d")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 데이터 저장: {output_file}")

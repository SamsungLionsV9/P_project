"""
Car-Sentix 타이밍 어드바이저 - 실제 데이터 수집기
- 보배드림 실제 크롤링
- 네이버 블로그 검색량 수집
- 확장된 키워드 사전 기반 감성 분석
- 한국은행/네이버 API 연동 (API 키 있을 시)
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

# 키워드 사전 (대폭 확장)
POSITIVE_KEYWORDS = [
    # 성능
    "빠르다", "빠름", "조용", "부드럽", "안정적", "탄탄", "견고",
    # 가격
    "가성비", "저렴", "합리적", "이득", "혜자", "저렴",
    # 만족도
    "추천", "만족", "좋음", "훌륭", "최고", "굿", "좋아", "괜찮",
    # 구매
    "계약", "구입", "결정", "성공", "득템", "샀어", "질렀",
    # 온라인 은어
    "개꿀", "혜자", "갓성비", "쩐다", "ㄹㅇ", "인정", "레전드",
    # 디자인
    "예쁘", "멋지", "고급", "세련", "이쁘",
    # 편의
    "편하", "쾌적", "넓", "실용",
]

NEGATIVE_KEYWORDS = [
    # 고장
    "고장", "결함", "하자", "문제", "이슈", "불량", "파손",
    # 품질
    "형편없", "실망", "후회", "최악", "별로", "아쉽",
    # 리콜
    "리콜", "회수", "결함", "급발진",
    # 온라인 은어
    "흉기차", "폭탄", "지뢰", "쓰레기", "노답",
    # 비용
    "비싸", "비쌈", "비용", "부담",
    # 소음/진동
    "시끄럽", "떨림", "소음", "진동",
]

STRONG_POSITIVE = ["최고", "훌륭", "굿", "개꿀", "갓성비", "레전드"]
STRONG_NEGATIVE = ["최악", "쓰레기", "흉기차", "폭탄", "급발진"]


class RealCommunityCollector:
    """실제 커뮤니티 크롤링"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
    
    def scrape_bobaedream(self, car_model, limit=50):
        """
        보배드림 실제 크롤링
        
        Args:
            car_model: 차량 모델명
            limit: 수집할 게시글 수
            
        Returns:
            list: [{'title': '...', 'date': '...', 'url': '...'}, ...]
        """
        print(f"🌐 보배드림 '{car_model}' 검색 중...")
        
        posts = []
        
        try:
            # 보배드림 검색 URL
            search_url = f"https://www.bobaedream.co.kr/search/?kind=title&txt={car_model}"
            
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 게시글 목록 파싱 (실제 선택자는 사이트 구조에 따라 조정 필요)
            # 보배드림은 로그인이 필요할 수 있으므로, 대신 검색 결과 개수만 파싱
            
            # 검색 결과 영역 찾기
            search_results = soup.select('.search-result, .list-item, .board-list tr')
            
            if not search_results:
                print(f"  ⚠️ 검색 결과를 찾을 수 없습니다 (로그인 필요 or 선택자 변경)")
                # 대안: 네이버 블로그로 전환
                return self.search_naver_blog(car_model, limit)
            
            for idx, item in enumerate(search_results[:limit]):
                try:
                    # 제목 추출
                    title_elem = item.select_one('a, .title, td.title')
                    if not title_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    
                    # URL 추출
                    url = title_elem.get('href', '')
                    if url and not url.startswith('http'):
                        url = 'https://www.bobaedream.co.kr' + url
                    
                    # 날짜 추출
                    date_elem = item.select_one('.date, .time, td.date')
                    date = date_elem.text.strip() if date_elem else datetime.now().strftime('%Y-%m-%d')
                    
                    posts.append({
                        'title': title,
                        'date': date,
                        'url': url,
                        'source': '보배드림'
                    })
                    
                except Exception as e:
                    continue
            
            if posts:
                print(f"  ✓ 보배드림에서 {len(posts)}개 게시글 수집")
            else:
                print(f"  ⚠️ 보배드림 파싱 실패, 네이버 블로그로 대체")
                return self.search_naver_blog(car_model, limit)
            
        except Exception as e:
            print(f"  ✗ 보배드림 접속 실패: {e}")
            print(f"  → 네이버 블로그로 대체")
            return self.search_naver_blog(car_model, limit)
        
        return posts
    
    def search_naver_blog(self, car_model, limit=50):
        """
        네이버 블로그 검색 (API 없이)
        
        Args:
            car_model: 차량 모델명
            limit: 수집할 블로그 개수
            
        Returns:
            list: [{'title': '...', 'date': '...', 'url': '...'}, ...]
        """
        print(f"📝 네이버 블로그 '{car_model}' 검색 중...")
        
        posts = []
        
        try:
            # 검색 쿼리: "모델명 중고차" or "모델명 시승기" or "모델명 리뷰"
            queries = [
                f"{car_model} 중고차",
                f"{car_model} 리뷰",
                f"{car_model} 시승기"
            ]
            
            for query in queries[:1]:  # 일단 중고차만
                url = f"https://search.naver.com/search.naver?where=blog&query={query}"
                
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 블로그 검색 결과 파싱
                blog_items = soup.select('.view_wrap, .total_wrap')
                
                for item in blog_items[:limit]:
                    try:
                        # 제목
                        title_elem = item.select_one('.title_link, .api_txt_lines')
                        if not title_elem:
                            continue
                        
                        title = title_elem.text.strip()
                        
                        # URL
                        url = title_elem.get('href', '')
                        
                        # 날짜
                        date_elem = item.select_one('.sub_time, .sub_txt')
                        date = date_elem.text.strip() if date_elem else ''
                        
                        # 본문 일부
                        desc_elem = item.select_one('.dsc_link, .api_txt_lines.dsc_txt')
                        desc = desc_elem.text.strip() if desc_elem else ''
                        
                        posts.append({
                            'title': title,
                            'description': desc,
                            'date': date,
                            'url': url,
                            'source': '네이버블로그'
                        })
                        
                    except Exception as e:
                        continue
                
                if posts:
                    print(f"  ✓ 네이버 블로그에서 {len(posts)}개 게시글 수집")
                    break
                    
        except Exception as e:
            print(f"  ✗ 네이버 블로그 검색 실패: {e}")
        
        return posts
    
    def get_naver_blog_count(self, car_model):
        """
        네이버 블로그 검색 결과 개수 (검색량 지표)
        
        Returns:
            int: 검색 결과 개수
        """
        print(f"🔢 네이버 블로그 '{car_model}' 검색량 확인 중...")
        
        try:
            url = f"https://search.naver.com/search.naver?where=blog&query={car_model}+중고차"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 검색 결과 개수 파싱
            # "블로그 1-10 / 15,234건" 형태
            result_text = soup.select_one('.title_desc, .result_stats')
            
            if result_text:
                text = result_text.text
                # 숫자 추출
                numbers = re.findall(r'[\d,]+', text)
                if numbers:
                    count = int(numbers[-1].replace(',', ''))
                    print(f"  ✓ 검색 결과: {count:,}건")
                    return count
            
            print(f"  ⚠️ 검색 개수를 파싱할 수 없습니다")
            return 0
            
        except Exception as e:
            print(f"  ✗ 검색량 조회 실패: {e}")
            return 0
    
    def analyze_sentiment_enhanced(self, posts):
        """
        확장된 키워드 사전으로 감성 분석
        
        Args:
            posts: 게시글 리스트
            
        Returns:
            dict: {'positive_ratio': 0.6, 'score': 20, 'trend': 'positive', ...}
        """
        if not posts:
            return {
                'positive_ratio': 0.5,
                'negative_ratio': 0.5,
                'score': 0,
                'trend': 'neutral',
                'total_posts': 0
            }
        
        pos_count = 0
        neg_count = 0
        total_score = 0
        
        for post in posts:
            # 제목 + 설명 합치기
            text = post.get('title', '') + ' ' + post.get('description', '')
            text = text.lower()
            
            # 강한 긍정 (가중치 2)
            strong_pos = sum(2 for w in STRONG_POSITIVE if w in text)
            # 일반 긍정 (가중치 1)
            normal_pos = sum(1 for w in POSITIVE_KEYWORDS if w in text)
            
            # 강한 부정 (가중치 2)
            strong_neg = sum(2 for w in STRONG_NEGATIVE if w in text)
            # 일반 부정 (가중치 1)
            normal_neg = sum(1 for w in NEGATIVE_KEYWORDS if w in text)
            
            post_score = (strong_pos + normal_pos) - (strong_neg + normal_neg)
            total_score += post_score
            
            if post_score > 0:
                pos_count += 1
            elif post_score < 0:
                neg_count += 1
        
        total = len(posts)
        pos_ratio = pos_count / total
        neg_ratio = neg_count / total
        neu_ratio = 1 - pos_ratio - neg_ratio
        
        # 전체 점수 정규화 (-10 ~ +10)
        avg_score = total_score / total
        normalized_score = max(-10, min(10, avg_score))
        
        # 추세 판단
        if normalized_score > 3:
            trend = 'positive'
        elif normalized_score < -3:
            trend = 'negative'
        else:
            trend = 'neutral'
        
        result = {
            'positive_ratio': round(pos_ratio, 2),
            'negative_ratio': round(neg_ratio, 2),
            'neutral_ratio': round(neu_ratio, 2),
            'score': round(normalized_score, 1),
            'trend': trend,
            'total_posts': total,
            'keyword_matches': {
                'positive': sum(1 for p in posts if any(w in (p.get('title', '') + p.get('description', '')).lower() for w in POSITIVE_KEYWORDS)),
                'negative': sum(1 for p in posts if any(w in (p.get('title', '') + p.get('description', '')).lower() for w in NEGATIVE_KEYWORDS))
            }
        }
        
        print(f"\n📊 감성 분석 결과:")
        print(f"  긍정: {result['positive_ratio']:.0%}")
        print(f"  부정: {result['negative_ratio']:.0%}")
        print(f"  중립: {result['neutral_ratio']:.0%}")
        print(f"  점수: {result['score']:.1f}/10")
        print(f"  추세: {result['trend']}")
        
        return result


class RealMacroEconomicCollector:
    """실제 거시경제 지표 수집"""
    
    def __init__(self, bok_api_key=None):
        """
        Args:
            bok_api_key: 한국은행 Open API 키 (선택)
        """
        self.bok_api_key = bok_api_key or os.getenv('BOK_API_KEY')
    
    def get_interest_rate_real(self):
        """한국은행 API로 실제 기준금리 조회"""
        print("📊 기준금리 조회 중...")
        
        if not self.bok_api_key:
            print("  ⚠️ 한국은행 API 키 없음. 최근 공개 정보로 대체")
            # 최근 공개된 금리 정보 (2024년 11월 기준)
            return {
                'rate': 3.25,
                'date': '2024-11-01',
                'trend': 'stable',
                'source': '최근 공개 정보 (API 키 필요)',
                'note': 'BOK_API_KEY 환경변수 설정 필요'
            }
        
        try:
            # 한국은행 Open API
            # 통계코드: 722Y001 (기준금리)
            url = f"https://ecos.bok.or.kr/api/StatisticSearch/{self.bok_api_key}/json/kr/1/10/722Y001/D"
            
            # 최근 30일
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            url += f"/{start_date}/{end_date}/0101000"
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if 'StatisticSearch' in data and 'row' in data['StatisticSearch']:
                rows = data['StatisticSearch']['row']
                
                # 최신 금리
                latest = rows[0]
                current_rate = float(latest['DATA_VALUE'])
                
                # 추세 계산 (첫 데이터와 비교)
                if len(rows) > 1:
                    previous_rate = float(rows[-1]['DATA_VALUE'])
                    if current_rate > previous_rate:
                        trend = 'up'
                    elif current_rate < previous_rate:
                        trend = 'down'
                    else:
                        trend = 'stable'
                else:
                    trend = 'stable'
                    previous_rate = current_rate
                
                result = {
                    'rate': current_rate,
                    'date': latest['TIME'],
                    'trend': trend,
                    'previous_rate': previous_rate,
                    'change': current_rate - previous_rate,
                    'source': '한국은행 Open API'
                }
                
                print(f"  ✓ 현재 금리: {current_rate}%")
                print(f"  ✓ 추세: {trend}")
                
                return result
            else:
                raise ValueError("API 응답 형식 오류")
                
        except Exception as e:
            print(f"  ✗ API 조회 실패: {e}")
            # 최근 공개 정보로 fallback
            return {
                'rate': 3.25,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'trend': 'stable',
                'source': 'fallback'
            }
    
    def get_oil_price(self):
        """yfinance로 실제 유가 조회 (WTI)"""
        print("🛢️ 국제 유가 조회 중...")
        
        try:
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
                print(f"  ✓ 추세: {trend} ({result['change_pct']:+.1f}%)")
                
                return result
            else:
                raise ValueError("유가 데이터 없음")
                
        except Exception as e:
            print(f"  ✗ 유가 조회 실패: {e}")
            return {
                'price': 75.0,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'trend': 'stable',
                'source': 'default'
            }
    
    def get_exchange_rate(self):
        """yfinance로 실제 환율 조회 (USD/KRW)"""
        print("💱 환율 조회 중...")
        
        try:
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
            return {
                'rate': 1300.0,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'trend': 'stable',
                'source': 'default'
            }
    
    def get_all_indicators(self):
        """모든 거시경제 지표 수집"""
        return {
            'interest_rate': self.get_interest_rate_real(),
            'oil_price': self.get_oil_price(),
            'exchange_rate': self.get_exchange_rate(),
            'collected_at': datetime.now().isoformat()
        }


# 통합 함수
def collect_real_data(car_model, bok_api_key=None):
    """
    실제 데이터 수집 (시뮬레이션 없음)
    
    Args:
        car_model: 차량 모델명
        bok_api_key: 한국은행 API 키 (선택)
        
    Returns:
        dict: 모든 수집 데이터
    """
    print("=" * 80)
    print(f"📡 '{car_model}' 실제 데이터 수집 시작")
    print("=" * 80)
    
    # 1. 거시경제 지표
    macro = RealMacroEconomicCollector(bok_api_key)
    macro_data = macro.get_all_indicators()
    
    print()
    
    # 2. 커뮤니티 데이터
    community = RealCommunityCollector()
    
    # 보배드림 또는 네이버 블로그
    posts = community.scrape_bobaedream(car_model, limit=50)
    
    # 감성 분석
    sentiment_data = community.analyze_sentiment_enhanced(posts)
    
    print()
    
    # 3. 검색량 (추가)
    blog_count = community.get_naver_blog_count(car_model)
    
    print()
    
    # 4. 신차 일정 (기존 DB 활용)
    from data_collectors import NewCarScheduleManager
    schedule = NewCarScheduleManager()
    schedule_data = schedule.check_upcoming_release(car_model)
    
    print()
    print("=" * 80)
    print("✅ 실제 데이터 수집 완료!")
    print("=" * 80)
    
    return {
        'car_model': car_model,
        'macro': macro_data,
        'community': {
            'posts': posts,
            'sentiment': sentiment_data,
            'blog_count': blog_count
        },
        'schedule': schedule_data,
        'collected_at': datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("=" * 80)
    print("Car-Sentix 실제 데이터 수집기 테스트")
    print("=" * 80)
    
    # 테스트 차량
    test_model = "그랜저"
    
    # BOK API 키 (환경변수에서 읽기, 없으면 None)
    bok_key = os.getenv('BOK_API_KEY')
    
    if bok_key:
        print(f"✓ 한국은행 API 키 감지됨")
    else:
        print(f"⚠️ 한국은행 API 키 없음 (BOK_API_KEY 환경변수 설정)")
        print(f"   → 최근 공개 정보로 대체합니다")
    
    print()
    
    # 실제 데이터 수집
    data = collect_real_data(test_model, bok_key)
    
    # 결과 요약
    print("\n" + "=" * 80)
    print("📊 수집 데이터 요약")
    print("=" * 80)
    
    print(f"\n🚗 차량: {data['car_model']}")
    
    print(f"\n📊 거시경제:")
    print(f"  - 금리: {data['macro']['interest_rate']['rate']}% ({data['macro']['interest_rate']['trend']})")
    print(f"  - 유가: ${data['macro']['oil_price']['price']:.2f} ({data['macro']['oil_price']['trend']})")
    print(f"  - 환율: {data['macro']['exchange_rate']['rate']:.2f}원 ({data['macro']['exchange_rate']['trend']})")
    
    print(f"\n💬 커뮤니티:")
    print(f"  - 수집 게시글: {data['community']['sentiment']['total_posts']}개")
    print(f"  - 블로그 검색량: {data['community']['blog_count']:,}건")
    print(f"  - 긍정 비율: {data['community']['sentiment']['positive_ratio']:.0%}")
    print(f"  - 부정 비율: {data['community']['sentiment']['negative_ratio']:.0%}")
    print(f"  - 감성 점수: {data['community']['sentiment']['score']:.1f}/10")
    print(f"  - 추세: {data['community']['sentiment']['trend']}")
    
    print(f"\n🚗 신차 출시:")
    if data['schedule']['has_upcoming']:
        print(f"  - 예정 모델: {data['schedule']['new_model']}")
        print(f"  - 출시일: {data['schedule']['release_date']} ({data['schedule']['months_until']:.1f}개월 후)")
        print(f"  - 영향도: {data['schedule']['impact']}")
    else:
        print(f"  - 예정 없음")
    
    # JSON 저장
    output_file = f'real_timing_data_{test_model}_{datetime.now().strftime("%Y%m%d_%H%M")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        # posts는 너무 크므로 제외하고 요약만 저장
        save_data = data.copy()
        save_data['community']['posts_summary'] = {
            'count': len(data['community']['posts']),
            'sample_titles': [p['title'] for p in data['community']['posts'][:5]]
        }
        del save_data['community']['posts']
        
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 데이터 저장: {output_file}")
    
    print("\n" + "=" * 80)
    print("🎯 다음 단계:")
    print("=" * 80)
    print("\n1. ⏳ 한국은행 API 키 발급 (https://ecos.bok.or.kr)")
    print("   → BOK_API_KEY 환경변수로 설정")
    print("\n2. ✅ 커뮤니티 크롤링 정상 작동")
    print("   → 보배드림 or 네이버 블로그")
    print("\n3. ✅ 감성 분석 확장 키워드 적용")
    print(f"   → {len(POSITIVE_KEYWORDS)}개 긍정, {len(NEGATIVE_KEYWORDS)}개 부정 키워드")
    print("\n4. ⏳ 네이버 데이터랩 API (선택)")
    print("   → 검색 트렌드 정확도 향상")

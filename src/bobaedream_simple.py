"""
보배드림 간단 크롤러 - requests만 사용
Selenium 없이 공개 게시판만 크롤링
"""

import requests
from bs4 import BeautifulSoup
import time
import re


POSITIVE_KEYWORDS = [
    "빠르다", "조용", "부드럽", "안정적", "탄탄",
    "가성비", "저렴", "합리적", "혜자",
    "추천", "만족", "좋음", "훌륭", "최고", "굿", "괜찮",
    "계약", "구입", "샀어",
    "예쁘", "멋지", "고급",
    "편하", "쾌적", "넓", "실용",
]

NEGATIVE_KEYWORDS = [
    "고장", "결함", "하자", "문제", "이슈", "불량",
    "실망", "후회", "최악", "별로", "아쉽",
    "리콜", "급발진",
    "흉기차", "폭탄", "쓰레기",
    "비싸", "부담",
    "시끄럽", "떨림", "소음",
]


class SimpleBobaedreamCrawler:
    """requests 기반 간단 크롤러"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_free_board(self, car_model, pages=10):
        """
        자유게시판에서 차량 관련 글 수집
        
        Args:
            car_model: 차량 모델명
            pages: 페이지 수
            
        Returns:
            list: 게시글 리스트
        """
        print(f"🚗 보배드림 자유게시판 '{car_model}' 수집 중...")
        
        posts = []
        
        for page in range(1, pages + 1):
            try:
                # 자유게시판 URL
                url = f"https://www.bobaedream.co.kr/list?code=free&page={page}"
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 게시글 링크 찾기
                links = soup.find_all('a', href=re.compile(r'/view/'))
                
                page_posts = 0
                for link in links:
                    title = link.get_text(strip=True)
                    
                    # 차량명 필터링
                    if car_model.lower() not in title.lower():
                        continue
                    
                    if len(title) < 5:
                        continue
                    
                    url = link.get('href', '')
                    if url and not url.startswith('http'):
                        url = 'https://www.bobaedream.co.kr' + url
                    
                    posts.append({
                        'title': title,
                        'url': url,
                        'source': '보배드림-자유게시판'
                    })
                    page_posts += 1
                
                if page_posts > 0:
                    print(f"  ✓ 페이지 {page}: {page_posts}개")
                
                time.sleep(0.5)  # 요청 간격
                
            except Exception as e:
                print(f"  ⚠️ 페이지 {page} 실패: {e}")
                continue
        
        print(f"  ✓ 총 {len(posts)}개 수집")
        return posts
    
    def scrape_humor_board(self, car_model, pages=10):
        """
        유머게시판 (인기글)
        
        Args:
            car_model: 차량 모델명
            pages: 페이지 수
            
        Returns:
            list: 게시글 리스트
        """
        print(f"🚗 보배드림 유머게시판 '{car_model}' 수집 중...")
        
        posts = []
        
        for page in range(1, pages + 1):
            try:
                url = f"https://www.bobaedream.co.kr/list?code=humor&page={page}"
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=re.compile(r'/view/'))
                
                page_posts = 0
                for link in links:
                    title = link.get_text(strip=True)
                    
                    if car_model.lower() not in title.lower():
                        continue
                    
                    if len(title) < 5:
                        continue
                    
                    url = link.get('href', '')
                    if url and not url.startswith('http'):
                        url = 'https://www.bobaedream.co.kr' + url
                    
                    posts.append({
                        'title': title,
                        'url': url,
                        'source': '보배드림-유머게시판'
                    })
                    page_posts += 1
                
                if page_posts > 0:
                    print(f"  ✓ 페이지 {page}: {page_posts}개")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ⚠️ 페이지 {page} 실패: {e}")
                continue
        
        print(f"  ✓ 총 {len(posts)}개 수집")
        return posts
    
    def analyze_sentiment(self, posts):
        """감성 분석"""
        if not posts:
            return {
                'score': 0,
                'positive_ratio': 0.5,
                'negative_ratio': 0.5,
                'neutral_ratio': 0.0,
                'trend': 'neutral',
                'total_posts': 0,
                'source': 'bobaedream_simple'
            }
        
        pos_count = 0
        neg_count = 0
        total_score = 0
        
        for post in posts:
            text = post.get('title', '').lower()
            
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
        
        avg_score = total_score / total if total > 0 else 0
        normalized_score = max(-10, min(10, avg_score))
        
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
            'source': 'bobaedream_simple'
        }
        
        print(f"\n📊 감성 분석:")
        print(f"  긍정: {result['positive_ratio']:.0%} | 부정: {result['negative_ratio']:.0%}")
        print(f"  점수: {result['score']:.1f}/10 ({result['trend']})")
        
        return result
    
    def collect_all(self, car_model, free_pages=10, humor_pages=5):
        """
        통합 수집 + 감성 분석
        
        Args:
            car_model: 차량 모델명
            free_pages: 자유게시판 페이지 수
            humor_pages: 유머게시판 페이지 수
            
        Returns:
            dict: {'posts': [...], 'sentiment': {...}, 'post_count': int}
        """
        print("=" * 80)
        print(f"🚗 보배드림 '{car_model}' 간단 크롤링")
        print("=" * 80)
        
        all_posts = []
        
        # 자유게시판
        posts1 = self.scrape_free_board(car_model, pages=free_pages)
        all_posts.extend(posts1)
        
        # 유머게시판
        posts2 = self.scrape_humor_board(car_model, pages=humor_pages)
        all_posts.extend(posts2)
        
        # 중복 제거
        seen_titles = set()
        unique_posts = []
        for post in all_posts:
            if post['title'] not in seen_titles:
                seen_titles.add(post['title'])
                unique_posts.append(post)
        
        print(f"\n✅ 총 {len(unique_posts)}개 고유 게시글")
        
        # 감성 분석
        sentiment = self.analyze_sentiment(unique_posts)
        
        print("=" * 80)
        
        return {
            'posts': unique_posts,
            'sentiment': sentiment,
            'post_count': len(unique_posts)
        }


if __name__ == "__main__":
    print("=" * 80)
    print("보배드림 간단 크롤러 테스트")
    print("=" * 80)
    
    crawler = SimpleBobaedreamCrawler()
    
    # 테스트
    result = crawler.collect_all("그랜저", free_pages=10, humor_pages=5)
    
    print(f"\n📊 최종 결과:")
    print(f"  수집: {result['post_count']}개")
    print(f"  점수: {result['sentiment']['score']:.1f}/10")
    print(f"  추세: {result['sentiment']['trend']}")
    
    if result['posts']:
        print(f"\n📝 샘플 (상위 5개):")
        for i, post in enumerate(result['posts'][:5], 1):
            print(f"\n  {i}. {post['title']}")
            print(f"     출처: {post['source']}")

"""
보배드림 실제 크롤러 (Selenium 사용)
- 실제 브라우저로 접근하여 봇 차단 우회
- 검색 결과에서 제목과 내용 추출
- 감성 분석 적용
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

# 키워드 사전
POSITIVE_KEYWORDS = [
    "빠르다", "빠름", "조용", "부드럽", "안정적", "탄탄", "견고",
    "가성비", "저렴", "합리적", "이득", "혜자",
    "추천", "만족", "좋음", "훌륭", "최고", "굿", "좋아", "괜찮",
    "계약", "구입", "결정", "성공", "득템", "샀어", "질렀",
    "개꿀", "갓성비", "쩐다", "인정", "레전드",
    "예쁘", "멋지", "고급", "세련", "이쁘",
    "편하", "쾌적", "넓", "실용",
]

NEGATIVE_KEYWORDS = [
    "고장", "결함", "하자", "문제", "이슈", "불량", "파손",
    "형편없", "실망", "후회", "최악", "별로", "아쉽",
    "리콜", "회수", "급발진",
    "흉기차", "폭탄", "지뢰", "쓰레기", "노답",
    "비싸", "비쌈", "비용", "부담",
    "시끄럽", "떨림", "소음", "진동",
]

STRONG_POSITIVE = ["최고", "훌륭", "굿", "개꿀", "갓성비", "레전드"]
STRONG_NEGATIVE = ["최악", "쓰레기", "흉기차", "폭탄", "급발진"]


class BobaedreamScraper:
    """보배드림 Selenium 크롤러"""
    
    def __init__(self, headless=True):
        """
        Args:
            headless: 브라우저 창을 숨길지 여부 (True=백그라운드 실행)
        """
        self.headless = headless
        self.driver = None
    
    def _init_driver(self):
        """Selenium 드라이버 초기화"""
        if self.driver:
            return
        
        print("🌐 Chrome 드라이버 초기화 중...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # 봇 감지 우회 옵션
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # ChromeDriver 자동 설치 및 실행
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("  ✓ 드라이버 준비 완료")
    
    def scrape_bobaedream(self, car_model, limit=50):
        """
        보배드림에서 실제 게시글 크롤링
        
        Args:
            car_model: 차량 모델명
            limit: 수집할 게시글 수
            
        Returns:
            list: [{'title': '...', 'content': '...', 'date': '...', 'url': '...'}, ...]
        """
        print(f"🚗 보배드림 '{car_model}' 검색 중 (Selenium)...")
        
        try:
            self._init_driver()
            
            posts = []
            
            # 보배드림 통합 검색 (중고차 게시판 위주)
            search_url = f"https://www.bobaedream.co.kr/cyber/CyberCont.php?gubun=I&page=1&search_flag=Y&search_sel=I&search_txt={car_model}"
            
            print(f"  → URL 접속 중...")
            self.driver.get(search_url)
            
            # 페이지 로딩 대기
            time.sleep(3)
            
            # 페이지 소스 가져오기
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 게시글 목록 찾기 (보배드림 구조에 맞게)
            # 다양한 선택자 시도
            selectors = [
                'div.list',
                'table.bbsList',
                'tr.pl',
                'div.bulletin-list',
                'li.list-item'
            ]
            
            items = []
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    print(f"    ✓ '{selector}' 선택자로 {len(items)}개 발견")
                    break
            
            if not items:
                # 직접 링크로 시도
                items = soup.find_all('a', href=re.compile(r'view\.php|idx='))
                print(f"    ✓ 링크 기반으로 {len(items)}개 발견")
            
            for item in items[:limit]:
                try:
                    # 제목 추출
                    title_elem = item.find('a') if hasattr(item, 'find') else item
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # 제목이 너무 짧으면 스킵
                    if len(title) < 5:
                        continue
                    
                    # URL 추출
                    url = title_elem.get('href', '')
                    if url and not url.startswith('http'):
                        url = 'https://www.bobaedream.co.kr' + url
                    
                    # 날짜 추출 (가능하면)
                    date_elem = item.find(class_=re.compile(r'date|time'))
                    date = date_elem.get_text(strip=True) if date_elem else ''
                    
                    posts.append({
                        'title': title,
                        'content': '',  # 목록에서는 내용 없음
                        'date': date,
                        'url': url,
                        'source': '보배드림'
                    })
                    
                except Exception as e:
                    continue
            
            print(f"  ✓ 보배드림에서 {len(posts)}개 게시글 수집 완료")
            
            return posts
            
        except Exception as e:
            print(f"  ✗ 보배드림 크롤링 실패: {e}")
            return []
        
        finally:
            # 드라이버는 재사용을 위해 닫지 않음 (close()에서 처리)
            pass
    
    def scrape_bobaedream_usedcar_board(self, car_model, limit=30):
        """
        보배드림 중고차 게시판 직접 크롤링
        
        Args:
            car_model: 차량 모델명
            limit: 수집할 게시글 수
            
        Returns:
            list: 게시글 리스트
        """
        print(f"🚗 보배드림 중고차 게시판 '{car_model}' 검색 중...")
        
        try:
            self._init_driver()
            
            posts = []
            
            # 중고차 매물 게시판
            board_url = "https://www.bobaedream.co.kr/cyber/CyberCont.php?gubun=K"
            
            self.driver.get(board_url)
            time.sleep(2)
            
            # 검색창에 차량명 입력
            try:
                search_input = self.driver.find_element(By.NAME, "search_txt")
                search_input.clear()
                search_input.send_keys(car_model)
                
                # 검색 버튼 클릭
                search_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                search_btn.click()
                
                time.sleep(3)
                
            except:
                print("  ⚠️ 검색창 사용 불가, 직접 검색 URL 사용")
            
            # 결과 파싱
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 제목에서 차량명 포함된 것만 추출
            links = soup.find_all('a', href=True)
            
            for link in links[:limit]:
                try:
                    title = link.get_text(strip=True)
                    
                    # 차량명이 제목에 포함되어 있는지 확인
                    if car_model.lower() not in title.lower():
                        continue
                    
                    if len(title) < 5:
                        continue
                    
                    url = link.get('href', '')
                    if url and not url.startswith('http'):
                        url = 'https://www.bobaedream.co.kr' + url
                    
                    posts.append({
                        'title': title,
                        'content': '',
                        'url': url,
                        'source': '보배드림-중고차게시판'
                    })
                    
                except:
                    continue
            
            print(f"  ✓ {len(posts)}개 게시글 수집")
            
            return posts
            
        except Exception as e:
            print(f"  ✗ 중고차 게시판 크롤링 실패: {e}")
            return []
    
    def analyze_sentiment(self, posts):
        """
        수집된 게시글 감성 분석
        
        Args:
            posts: 게시글 리스트
            
        Returns:
            dict: 감성 분석 결과
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
            text = (post.get('title', '') + ' ' + post.get('content', '')).lower()
            
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
        pos_ratio = pos_count / total if total > 0 else 0
        neg_ratio = neg_count / total if total > 0 else 0
        neu_ratio = 1 - pos_ratio - neg_ratio
        
        # 점수 정규화 (-10 ~ +10)
        avg_score = total_score / total if total > 0 else 0
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
            'total_posts': total
        }
        
        print(f"\n📊 감성 분석 결과:")
        print(f"  긍정: {result['positive_ratio']:.0%} | 부정: {result['negative_ratio']:.0%} | 중립: {result['neutral_ratio']:.0%}")
        print(f"  점수: {result['score']:.1f}/10 ({result['trend']})")
        
        return result
    
    def collect_all(self, car_model, limit=50):
        """
        모든 방법으로 데이터 수집 + 감성 분석
        
        Args:
            car_model: 차량 모델명
            limit: 수집할 게시글 수
            
        Returns:
            dict: {'posts': [...], 'sentiment': {...}}
        """
        print("=" * 80)
        print(f"🚗 보배드림 '{car_model}' 데이터 수집 (Selenium)")
        print("=" * 80)
        
        all_posts = []
        
        # 방법 1: 통합 검색
        posts1 = self.scrape_bobaedream(car_model, limit=limit//2)
        all_posts.extend(posts1)
        
        # 방법 2: 중고차 게시판
        if len(all_posts) < limit:
            posts2 = self.scrape_bobaedream_usedcar_board(car_model, limit=limit//2)
            all_posts.extend(posts2)
        
        # 중복 제거
        seen_titles = set()
        unique_posts = []
        for post in all_posts:
            if post['title'] not in seen_titles:
                seen_titles.add(post['title'])
                unique_posts.append(post)
        
        print(f"\n✅ 총 {len(unique_posts)}개 고유 게시글 수집")
        
        # 감성 분석
        sentiment = self.analyze_sentiment(unique_posts)
        
        print("=" * 80)
        
        return {
            'posts': unique_posts,
            'sentiment': sentiment,
            'post_count': len(unique_posts)
        }
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("✓ 브라우저 종료")


if __name__ == "__main__":
    print("=" * 80)
    print("보배드림 Selenium 크롤러 테스트")
    print("=" * 80)
    
    scraper = BobaedreamScraper(headless=True)
    
    try:
        # 테스트
        result = scraper.collect_all("그랜저", limit=50)
        
        print(f"\n📊 결과 요약:")
        print(f"  수집 게시글: {result['post_count']}개")
        print(f"  감성 점수: {result['sentiment']['score']:.1f}/10")
        print(f"  추세: {result['sentiment']['trend']}")
        
        if result['posts']:
            print(f"\n📝 샘플 게시글 (상위 5개):")
            for i, post in enumerate(result['posts'][:5], 1):
                print(f"\n  {i}. {post['title']}")
                print(f"     출처: {post['source']}")
        
    finally:
        scraper.close()

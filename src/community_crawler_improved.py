"""
개선된 커뮤니티 크롤러
- 네이버 블로그 크롤링 강화
- 다양한 HTML 구조 대응
- 에러 처리 개선
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import quote


# 확장된 키워드 사전
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


class ImprovedCommunityCollector:
    """개선된 커뮤니티 크롤러"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.naver.com/'
        }
    
    def search_naver_blog_improved(self, car_model, limit=50):
        """
        개선된 네이버 블로그 검색
        - 더 많은 HTML 구조 지원
        - 재시도 로직
        - 더 많은 정보 추출
        
        Args:
            car_model: 차량 모델명
            limit: 수집할 게시글 수
            
        Returns:
            list: [{'title': '...', 'description': '...', 'date': '...', 'url': '...'}, ...]
        """
        print(f"📝 네이버 블로그 '{car_model}' 검색 중 (개선 버전)...")
        
        posts = []
        queries = [
            f"{car_model} 중고차",
            f"{car_model} 리뷰",
            f"{car_model} 시승기",
            f"{car_model} 구매",
        ]
        
        for query in queries:
            if len(posts) >= limit:
                break
            
            try:
                # URL 인코딩
                encoded_query = quote(query)
                url = f"https://search.naver.com/search.naver?where=blog&sm=tab_jum&query={encoded_query}"
                
                print(f"  → 검색: '{query}'")
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 다양한 선택자 시도
                selectors = [
                    'div.detail_box',  # 새로운 구조
                    'li.bx',           # 이전 구조
                    'div.total_wrap',  # 통합 검색
                    'div.api_subject_bx',  # API 형식
                ]
                
                items = []
                for selector in selectors:
                    items = soup.select(selector)
                    if items:
                        print(f"    ✓ 선택자 '{selector}'로 {len(items)}개 발견")
                        break
                
                if not items:
                    print(f"    ⚠️ '{query}' 검색 결과 없음")
                    continue
                
                for item in items:
                    if len(posts) >= limit:
                        break
                    
                    try:
                        # 제목 추출 (여러 선택자 시도)
                        title_elem = (
                            item.select_one('a.title_link') or
                            item.select_one('a.api_txt_lines.total_tit') or
                            item.select_one('.title') or
                            item.select_one('a')
                        )
                        
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        
                        # URL 추출
                        url = title_elem.get('href', '')
                        
                        # 설명 추출
                        desc_elem = (
                            item.select_one('a.dsc_link') or
                            item.select_one('.dsc_txt') or
                            item.select_one('.api_txt_lines.dsc_txt') or
                            item.select_one('.sh_blog_passage')
                        )
                        description = desc_elem.get_text(strip=True) if desc_elem else ''
                        
                        # 날짜 추출
                        date_elem = (
                            item.select_one('.sub_time') or
                            item.select_one('.date') or
                            item.select_one('.sub_txt')
                        )
                        date = date_elem.get_text(strip=True) if date_elem else ''
                        
                        # 블로거 이름
                        author_elem = (
                            item.select_one('.name') or
                            item.select_one('.sub_txt.sub_name')
                        )
                        author = author_elem.get_text(strip=True) if author_elem else ''
                        
                        posts.append({
                            'title': title,
                            'description': description,
                            'date': date,
                            'author': author,
                            'url': url,
                            'source': '네이버블로그',
                            'query': query
                        })
                        
                    except Exception as e:
                        continue
                
                # 요청 간 딜레이 (차단 방지)
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    ✗ '{query}' 검색 실패: {e}")
                continue
        
        # 중복 제거 (제목 기준)
        seen_titles = set()
        unique_posts = []
        for post in posts:
            if post['title'] not in seen_titles:
                seen_titles.add(post['title'])
                unique_posts.append(post)
        
        print(f"\n  ✓ 총 {len(unique_posts)}개 고유 게시글 수집 완료")
        
        return unique_posts
    
    def search_daum_cafe(self, car_model, limit=30):
        """
        다음 카페 검색 (추가 데이터 소스)
        
        Args:
            car_model: 차량 모델명
            limit: 수집할 게시글 수
            
        Returns:
            list: [{'title': '...', 'description': '...', ...}, ...]
        """
        print(f"☕ 다음 카페 '{car_model}' 검색 중...")
        
        posts = []
        
        try:
            query = f"{car_model} 중고차"
            encoded_query = quote(query)
            url = f"https://search.daum.net/search?w=cafe&q={encoded_query}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            items = soup.select('.item_cont')
            
            for item in items[:limit]:
                try:
                    title_elem = item.select_one('.tit_link')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    
                    desc_elem = item.select_one('.desc_link')
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    posts.append({
                        'title': title,
                        'description': description,
                        'url': url,
                        'source': '다음카페'
                    })
                    
                except Exception:
                    continue
            
            print(f"  ✓ 다음 카페에서 {len(posts)}개 수집")
            
        except Exception as e:
            print(f"  ✗ 다음 카페 검색 실패: {e}")
        
        return posts
    
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
                'total_posts': 0,
                'analysis_detail': '데이터 부족'
            }
        
        pos_count = 0
        neg_count = 0
        total_score = 0
        
        keyword_hits = {
            'positive': {},
            'negative': {}
        }
        
        for post in posts:
            # 제목 + 설명 합치기
            text = (post.get('title', '') + ' ' + post.get('description', '')).lower()
            
            # 강한 긍정 (가중치 2)
            for keyword in STRONG_POSITIVE:
                if keyword in text:
                    total_score += 2
                    keyword_hits['positive'][keyword] = keyword_hits['positive'].get(keyword, 0) + 1
            
            # 일반 긍정 (가중치 1)
            for keyword in POSITIVE_KEYWORDS:
                if keyword in text:
                    total_score += 1
                    keyword_hits['positive'][keyword] = keyword_hits['positive'].get(keyword, 0) + 1
            
            # 강한 부정 (가중치 2)
            for keyword in STRONG_NEGATIVE:
                if keyword in text:
                    total_score -= 2
                    keyword_hits['negative'][keyword] = keyword_hits['negative'].get(keyword, 0) + 1
            
            # 일반 부정 (가중치 1)
            for keyword in NEGATIVE_KEYWORDS:
                if keyword in text:
                    total_score -= 1
                    keyword_hits['negative'][keyword] = keyword_hits['negative'].get(keyword, 0) + 1
            
            # 게시글별 판단
            post_has_positive = any(k in text for k in POSITIVE_KEYWORDS + STRONG_POSITIVE)
            post_has_negative = any(k in text for k in NEGATIVE_KEYWORDS + STRONG_NEGATIVE)
            
            if post_has_positive and not post_has_negative:
                pos_count += 1
            elif post_has_negative and not post_has_positive:
                neg_count += 1
        
        total = len(posts)
        pos_ratio = pos_count / total if total > 0 else 0
        neg_ratio = neg_count / total if total > 0 else 0
        neu_ratio = 1 - pos_ratio - neg_ratio
        
        # 전체 점수 정규화 (-10 ~ +10)
        avg_score = total_score / total if total > 0 else 0
        normalized_score = max(-10, min(10, avg_score))
        
        # 추세 판단
        if normalized_score > 3:
            trend = 'positive'
        elif normalized_score < -3:
            trend = 'negative'
        else:
            trend = 'neutral'
        
        # 상위 키워드 추출
        top_positive = sorted(keyword_hits['positive'].items(), key=lambda x: x[1], reverse=True)[:5]
        top_negative = sorted(keyword_hits['negative'].items(), key=lambda x: x[1], reverse=True)[:5]
        
        result = {
            'positive_ratio': round(pos_ratio, 2),
            'negative_ratio': round(neg_ratio, 2),
            'neutral_ratio': round(neu_ratio, 2),
            'score': round(normalized_score, 1),
            'trend': trend,
            'total_posts': total,
            'top_positive_keywords': [f"{k} ({v}건)" for k, v in top_positive],
            'top_negative_keywords': [f"{k} ({v}건)" for k, v in top_negative],
            'keyword_matches': {
                'positive': sum(keyword_hits['positive'].values()),
                'negative': sum(keyword_hits['negative'].values())
            }
        }
        
        print(f"\n📊 감성 분석 결과:")
        print(f"  긍정: {result['positive_ratio']:.0%} | 부정: {result['negative_ratio']:.0%} | 중립: {result['neutral_ratio']:.0%}")
        print(f"  점수: {result['score']:.1f}/10 ({result['trend']})")
        
        if top_positive:
            print(f"  주요 긍정 키워드: {', '.join([k for k, _ in top_positive[:3]])}")
        if top_negative:
            print(f"  주요 부정 키워드: {', '.join([k for k, _ in top_negative[:3]])}")
        
        return result
    
    def collect_all_community_data(self, car_model, limit=50):
        """
        모든 커뮤니티 소스에서 데이터 수집
        
        Args:
            car_model: 차량 모델명
            limit: 수집할 게시글 수
            
        Returns:
            dict: {'posts': [...], 'sentiment': {...}}
        """
        print("=" * 80)
        print(f"💬 '{car_model}' 커뮤니티 데이터 수집 (멀티 소스)")
        print("=" * 80)
        
        all_posts = []
        
        # 1. 네이버 블로그
        naver_posts = self.search_naver_blog_improved(car_model, limit=limit)
        all_posts.extend(naver_posts)
        
        print()
        
        # 2. 다음 카페 (추가)
        if len(all_posts) < limit:
            daum_posts = self.search_daum_cafe(car_model, limit=min(30, limit - len(all_posts)))
            all_posts.extend(daum_posts)
        
        print()
        
        # 3. 감성 분석
        sentiment = self.analyze_sentiment_enhanced(all_posts)
        
        print(f"\n✅ 총 {len(all_posts)}개 게시글 수집 완료")
        print("=" * 80)
        
        return {
            'posts': all_posts,
            'sentiment': sentiment,
            'post_count': len(all_posts),
            'sources': list(set(p.get('source', 'unknown') for p in all_posts))
        }


if __name__ == "__main__":
    print("=" * 80)
    print("개선된 커뮤니티 크롤러 테스트")
    print("=" * 80)
    
    # 테스트
    collector = ImprovedCommunityCollector()
    
    test_models = ["그랜저", "아반떼", "K5"]
    
    for model in test_models[:1]:  # 일단 하나만
        print(f"\n{'='*80}")
        print(f"테스트: {model}")
        print(f"{'='*80}\n")
        
        result = collector.collect_all_community_data(model, limit=50)
        
        print(f"\n📊 결과 요약:")
        print(f"  수집 게시글: {result['post_count']}개")
        print(f"  데이터 소스: {', '.join(result['sources'])}")
        print(f"  감성 점수: {result['sentiment']['score']:.1f}/10")
        print(f"  추세: {result['sentiment']['trend']}")
        
        # 샘플 게시글 출력
        if result['posts']:
            print(f"\n📝 샘플 게시글 (상위 5개):")
            for i, post in enumerate(result['posts'][:5], 1):
                print(f"\n  {i}. {post['title']}")
                if post.get('description'):
                    desc = post['description'][:80] + '...' if len(post['description']) > 80 else post['description']
                    print(f"     {desc}")
                print(f"     출처: {post.get('source', 'unknown')}")

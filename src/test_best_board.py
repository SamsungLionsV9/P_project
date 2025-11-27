"""
보배드림 베스트 게시판 크롤러 테스트
"""

from bobaedream_scraper import BobaedreamScraper

print("=" * 80)
print("보배드림 베스트 게시판 크롤러 테스트")
print("=" * 80)

scraper = BobaedreamScraper(headless=False)  # 브라우저 창 표시

try:
    # 테스트: 그랜저
    result = scraper.collect_all("그랜저", limit=20)
    
    print(f"\n{'='*80}")
    print(f"📊 수집 결과")
    print(f"{'='*80}")
    print(f"총 게시글: {result['post_count']}개")
    print(f"감성 점수: {result['sentiment']['score']:.1f}/10")
    print(f"추세: {result['sentiment']['trend']}")
    
    if result['posts']:
        print(f"\n📝 샘플 게시글 (상위 5개):")
        for i, post in enumerate(result['posts'][:5], 1):
            print(f"\n{i}. {post['title']}")
            print(f"   출처: {post['source']}")
            if post['url']:
                print(f"   URL: {post['url'][:60]}...")
    
finally:
    scraper.close()

print(f"\n{'='*80}")
print("✅ 테스트 완료!")
print(f"{'='*80}")

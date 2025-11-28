"""
동기화된 파일 통합 테스트
"""
import sys
sys.path.insert(0, 'ml-service')

print("=" * 60)
print("🔄 동기화된 파일 테스트 시작")
print("=" * 60)

# 1. ML 서비스 테스트
print("\n[1] ML 서비스 모듈 테스트")
try:
    from services.prediction import PredictionService
    ps = PredictionService()
    print("   ✅ PredictionService 로드 성공")
except Exception as e:
    print(f"   ❌ PredictionService 오류: {e}")

try:
    from services.timing import TimingService
    ts = TimingService()
    print("   ✅ TimingService 로드 성공")
except Exception as e:
    print(f"   ❌ TimingService 오류: {e}")

try:
    from services.groq_service import GroqService
    gs = GroqService()
    print(f"   ✅ GroqService 로드 성공 (활성: {gs.is_available()})")
except Exception as e:
    print(f"   ❌ GroqService 오류: {e}")

# 2. 새로 추가된 서비스 테스트
print("\n[2] 새로 추가된 서비스 테스트")
try:
    from services.history_service import get_history_service, get_popular_service
    hs = get_history_service()
    ps_pop = get_popular_service()
    print("   ✅ HistoryService 로드 성공")
    print("   ✅ PopularService 로드 성공")
    
    # 인기 차량 테스트
    popular = ps_pop.get_popular("domestic", 3)
    print(f"   📊 인기 국산차 Top 3: {[m['model'] for m in popular]}")
except Exception as e:
    print(f"   ❌ History/Popular 서비스 오류: {e}")

try:
    from services.similar_service import get_similar_service
    ss = get_similar_service()
    print("   ✅ SimilarService 로드 성공")
except Exception as e:
    print(f"   ❌ SimilarService 오류: {e}")

# 3. 가격 예측 테스트
print("\n[3] 가격 예측 API 테스트")
try:
    from services.prediction_v11 import PredictionServiceV11
    ps_v11 = PredictionServiceV11()
    
    # 국산차 테스트
    result_d = ps_v11.predict(
        brand="현대",
        model_name="그랜저",
        year=2022,
        mileage=35000,
        options={'has_sunroof': True, 'has_navigation': True}
    )
    print(f"   ✅ 국산차 예측: {result_d.predicted_price:,.0f}만원")
    print(f"      범위: {result_d.price_range[0]:,.0f} ~ {result_d.price_range[1]:,.0f}만원")
    print(f"      신뢰도: {result_d.confidence:.1f}%")
    
    # 외제차 테스트
    result_i = ps_v11.predict(
        brand="벤츠",
        model_name="E-클래스",
        year=2021,
        mileage=40000,
        options={'has_sunroof': True}
    )
    print(f"   ✅ 외제차 예측: {result_i.predicted_price:,.0f}만원")
    print(f"      범위: {result_i.price_range[0]:,.0f} ~ {result_i.price_range[1]:,.0f}만원")
    print(f"      신뢰도: {result_i.confidence:.1f}%")
except Exception as e:
    print(f"   ❌ 예측 서비스 오류: {e}")

# 4. 타이밍 분석 테스트
print("\n[4] 타이밍 분석 테스트")
try:
    result_t = ts.analyze_timing("그랜저")
    print(f"   ✅ 타이밍 점수: {result_t['timing_score']:.1f}/100")
    print(f"      판단: {result_t['decision']}")
    print(f"      색상: {result_t['color']}")
except Exception as e:
    print(f"   ❌ 타이밍 분석 오류: {e}")

# 5. 비슷한 차량 분포 테스트
print("\n[5] 비슷한 차량 분포 테스트")
try:
    similar = ss.get_similar_distribution(
        brand="현대",
        model="그랜저",
        year=2022,
        mileage=35000,
        predicted_price=3200
    )
    print(f"   ✅ 비슷한 차량: {similar['similar_count']}대")
    if similar['price_distribution']:
        dist = similar['price_distribution']
        print(f"      중간가: {dist['median']:,.0f}만원")
        print(f"      내 위치: {similar['your_position']}")
except Exception as e:
    print(f"   ❌ 비슷한 차량 오류: {e}")

# 6. Spring Boot 파일 확인
print("\n[6] Spring Boot 파일 존재 확인")
import os
spring_files = [
    "user-service/src/main/java/com/example/carproject/controller/CarDataController.java",
    "user-service/src/main/java/com/example/carproject/service/CarDataService.java",
    "user-service/src/main/java/com/example/carproject/entity/DomesticCarDetails.java",
]
for f in spring_files:
    if os.path.exists(f):
        print(f"   ✅ {f.split('/')[-1]}")
    else:
        print(f"   ❌ {f.split('/')[-1]} 없음")

# 7. 설정 파일 확인
print("\n[7] Setup 파일 확인")
setup_files = [
    "setup/CSV_IMPORT_GUIDE.md",
    "setup/MYSQL_REMOTE_ACCESS.md",
    "setup/import_csv_to_mysql.py",
]
for f in setup_files:
    if os.path.exists(f):
        print(f"   ✅ {f.split('/')[-1]}")
    else:
        print(f"   ❌ {f.split('/')[-1]} 없음")

print("\n" + "=" * 60)
print("🎉 테스트 완료!")
print("=" * 60)

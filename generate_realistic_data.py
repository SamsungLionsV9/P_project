"""
통합 데이터 생성 스크립트
=========================
프론트엔드 조회 흐름에 맞게 모든 테이블에 일관된 데이터 생성

데이터 흐름:
1. 사용자가 매물 조회 → analysis_history + daily_stats + model_stats
2. 상세 분석 (시그널) → ai_logs (signal)
3. 네고 대본 생성 → ai_logs (negotiation)
4. 허위매물 분석 → ai_logs (fraud_detection)
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
import os

DB_PATH = "data/car_sentix.db"

# 실제 차량 데이터 (엔카 기반 현실적인 가격)
VEHICLES = [
    # 국산 세단
    {"brand": "현대", "model": "그랜저", "year_range": (2020, 2024), "price_range": (2800, 4500), "fuel": ["가솔린", "하이브리드"]},
    {"brand": "현대", "model": "쏘나타", "year_range": (2020, 2024), "price_range": (2000, 3200), "fuel": ["가솔린", "하이브리드"]},
    {"brand": "현대", "model": "아반떼", "year_range": (2021, 2024), "price_range": (1600, 2500), "fuel": ["가솔린", "하이브리드"]},
    {"brand": "기아", "model": "K8", "year_range": (2021, 2024), "price_range": (3200, 4800), "fuel": ["가솔린", "하이브리드"]},
    {"brand": "기아", "model": "K5", "year_range": (2020, 2024), "price_range": (2000, 3200), "fuel": ["가솔린", "하이브리드"]},
    {"brand": "제네시스", "model": "G80", "year_range": (2020, 2024), "price_range": (4500, 7500), "fuel": ["가솔린", "디젤"]},
    {"brand": "제네시스", "model": "G70", "year_range": (2020, 2024), "price_range": (3500, 5500), "fuel": ["가솔린"]},
    
    # 국산 SUV
    {"brand": "현대", "model": "팰리세이드", "year_range": (2020, 2024), "price_range": (3800, 5500), "fuel": ["디젤"]},
    {"brand": "현대", "model": "싼타페", "year_range": (2021, 2024), "price_range": (3000, 4500), "fuel": ["가솔린", "하이브리드", "디젤"]},
    {"brand": "현대", "model": "투싼", "year_range": (2021, 2024), "price_range": (2500, 3800), "fuel": ["가솔린", "하이브리드", "디젤"]},
    {"brand": "기아", "model": "쏘렌토", "year_range": (2020, 2024), "price_range": (3200, 4800), "fuel": ["가솔린", "하이브리드", "디젤"]},
    {"brand": "기아", "model": "스포티지", "year_range": (2022, 2024), "price_range": (2600, 3800), "fuel": ["가솔린", "하이브리드", "디젤"]},
    {"brand": "기아", "model": "카니발", "year_range": (2021, 2024), "price_range": (3500, 5200), "fuel": ["가솔린", "디젤"]},
    {"brand": "제네시스", "model": "GV80", "year_range": (2020, 2024), "price_range": (6500, 9500), "fuel": ["가솔린", "디젤"]},
    {"brand": "제네시스", "model": "GV70", "year_range": (2021, 2024), "price_range": (5000, 7000), "fuel": ["가솔린", "디젤"]},
    
    # 수입 세단
    {"brand": "벤츠", "model": "E-클래스", "year_range": (2020, 2024), "price_range": (5500, 8500), "fuel": ["가솔린", "디젤"]},
    {"brand": "벤츠", "model": "S-클래스", "year_range": (2021, 2024), "price_range": (12000, 18000), "fuel": ["가솔린"]},
    {"brand": "벤츠", "model": "C-클래스", "year_range": (2022, 2024), "price_range": (4500, 6500), "fuel": ["가솔린", "디젤"]},
    {"brand": "BMW", "model": "5시리즈", "year_range": (2020, 2024), "price_range": (5000, 8000), "fuel": ["가솔린", "디젤"]},
    {"brand": "BMW", "model": "3시리즈", "year_range": (2020, 2024), "price_range": (3800, 5500), "fuel": ["가솔린", "디젤"]},
    {"brand": "아우디", "model": "A6", "year_range": (2020, 2024), "price_range": (4800, 7500), "fuel": ["가솔린", "디젤"]},
    
    # 수입 SUV
    {"brand": "벤츠", "model": "GLC", "year_range": (2020, 2024), "price_range": (5500, 8000), "fuel": ["가솔린", "디젤"]},
    {"brand": "벤츠", "model": "GLE", "year_range": (2020, 2024), "price_range": (8000, 12000), "fuel": ["가솔린", "디젤"]},
    {"brand": "BMW", "model": "X5", "year_range": (2020, 2024), "price_range": (7500, 11000), "fuel": ["가솔린", "디젤"]},
    {"brand": "BMW", "model": "X3", "year_range": (2020, 2024), "price_range": (5000, 7500), "fuel": ["가솔린", "디젤"]},
    {"brand": "아우디", "model": "Q5", "year_range": (2020, 2024), "price_range": (5000, 7500), "fuel": ["가솔린", "디젤"]},
    {"brand": "볼보", "model": "XC60", "year_range": (2020, 2024), "price_range": (4500, 7000), "fuel": ["가솔린", "디젤", "하이브리드"]},
    {"brand": "렉서스", "model": "RX", "year_range": (2020, 2024), "price_range": (6000, 9000), "fuel": ["가솔린", "하이브리드"]},
    {"brand": "포르쉐", "model": "카이엔", "year_range": (2020, 2024), "price_range": (9000, 15000), "fuel": ["가솔린"]},
    
    # 전기차
    {"brand": "테슬라", "model": "모델Y", "year_range": (2022, 2024), "price_range": (5000, 7000), "fuel": ["전기"]},
    {"brand": "테슬라", "model": "모델3", "year_range": (2021, 2024), "price_range": (4000, 6000), "fuel": ["전기"]},
    {"brand": "현대", "model": "아이오닉6", "year_range": (2022, 2024), "price_range": (4500, 6000), "fuel": ["전기"]},
    {"brand": "기아", "model": "EV6", "year_range": (2022, 2024), "price_range": (5000, 7000), "fuel": ["전기"]},
]

USERS = [
    "wlsgh1602@gmail.com",
    "test@example.com", 
    "user123@naver.com",
    "carbuyer@gmail.com",
    "guest"
]

def generate_vehicle():
    """랜덤 차량 생성"""
    v = random.choice(VEHICLES)
    year = random.randint(v['year_range'][0], v['year_range'][1])
    fuel = random.choice(v['fuel'])
    
    # 연식에 따른 가격 조정 (최신일수록 비쌈)
    base_min, base_max = v['price_range']
    year_factor = (year - 2020) / 4  # 0~1
    price_min = int(base_min * (0.7 + 0.3 * year_factor))
    price_max = int(base_max * (0.7 + 0.3 * year_factor))
    sale_price = random.randint(price_min, price_max)
    
    # 주행거리 (연식이 오래될수록 많음)
    years_old = 2024 - year
    mileage = random.randint(5000 + years_old * 8000, 15000 + years_old * 15000)
    
    # 예측가 (판매가 대비 -15% ~ +20% 범위, 대부분 ±10%)
    error_rate = random.gauss(0, 0.06)  # 평균 0, 표준편차 6%
    error_rate = max(-0.15, min(0.20, error_rate))
    predicted_price = int(sale_price * (1 + error_rate))
    
    # 신뢰도 (오차가 작을수록 높음)
    confidence = max(75, min(95, 92 - abs(error_rate) * 150))
    
    # 타이밍 점수 (랜덤)
    timing_score = random.randint(40, 90)
    
    # 시그널
    diff_pct = error_rate * 100
    if diff_pct > 8:
        signal = "적극 매수"
    elif diff_pct > 3:
        signal = "매수 고려"
    elif diff_pct < -8:
        signal = "매도 권장"
    elif diff_pct < -3:
        signal = "관망"
    else:
        signal = "적정가"
    
    return {
        "brand": v['brand'],
        "model": v['model'],
        "year": year,
        "mileage": mileage,
        "fuel_type": fuel,
        "sale_price": sale_price,
        "predicted_price": predicted_price,
        "confidence": round(confidence, 1),
        "timing_score": timing_score,
        "signal": signal,
        "diff_pct": diff_pct
    }

def clear_existing_data(conn):
    """기존 데이터 삭제"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analysis_history")
    cursor.execute("DELETE FROM ai_logs")
    cursor.execute("DELETE FROM daily_stats")
    cursor.execute("DELETE FROM model_stats")
    conn.commit()
    print("[OK] 기존 데이터 삭제 완료")

def generate_data(days=60, analyses_per_day_range=(5, 20)):
    """데이터 생성"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 기존 데이터 삭제
    clear_existing_data(conn)
    
    total_analyses = 0
    total_signals = 0
    total_negotiations = 0
    total_frauds = 0
    
    print(f"[START] {days}일간 데이터 생성 시작...")
    
    for day_offset in range(days, -1, -1):  # 과거부터 현재까지
        date = datetime.now() - timedelta(days=day_offset)
        date_str = date.strftime('%Y-%m-%d')
        
        # 하루 분석 건수 (주말은 적게)
        if date.weekday() >= 5:  # 주말
            analyses_count = random.randint(analyses_per_day_range[0] // 2, analyses_per_day_range[1] // 2)
        else:
            analyses_count = random.randint(analyses_per_day_range[0], analyses_per_day_range[1])
        
        daily_confidence_sum = 0
        daily_confidence_count = 0
        
        for _ in range(analyses_count):
            user = random.choice(USERS)
            vehicle = generate_vehicle()
            
            # 시간 랜덤 (9시~23시)
            hour = random.randint(9, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            timestamp = date.replace(hour=hour, minute=minute, second=second)
            ts_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            
            # 1. analysis_history 저장
            cursor.execute("""
                INSERT INTO analysis_history 
                (user_id, brand, model, year, mileage, fuel_type, predicted_price, 
                 confidence, timing_score, signal, detail_url, request_data, response_data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user,
                vehicle['brand'],
                vehicle['model'],
                vehicle['year'],
                vehicle['mileage'],
                vehicle['fuel_type'],
                vehicle['predicted_price'],
                vehicle['confidence'],
                vehicle['timing_score'],
                vehicle['signal'],
                f"https://encar.com/detail/{random.randint(100000, 999999)}",
                json.dumps({"source": "encar", "analysis_type": "full"}, ensure_ascii=False),
                json.dumps({"status": "success"}, ensure_ascii=False),
                ts_str
            ))
            total_analyses += 1
            daily_confidence_sum += vehicle['confidence']
            daily_confidence_count += 1
            
            # 2. ai_logs - signal (모든 분석에서 시그널 생성)
            cursor.execute("""
                INSERT INTO ai_logs 
                (user_id, log_type, car_info, request_data, response_data, success, ai_model, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user,
                'signal',
                f"{vehicle['brand']} {vehicle['model']} {vehicle['year']}",
                json.dumps({
                    "brand": vehicle['brand'],
                    "model": vehicle['model'],
                    "year": vehicle['year'],
                    "mileage": vehicle['mileage'],
                    "fuel_type": vehicle['fuel_type'],
                    "predicted_price": vehicle['predicted_price'],
                    "sale_price": vehicle['sale_price'],
                    "confidence": vehicle['confidence'],
                    "signal": vehicle['signal']
                }, ensure_ascii=False),
                json.dumps({"status": "success", "processing_time_ms": random.randint(100, 300)}, ensure_ascii=False),
                1,
                'llama-3.3-70b',
                ts_str
            ))
            total_signals += 1
            
            # 3. ai_logs - negotiation (30% 확률로 네고대본 생성)
            if random.random() < 0.3:
                nego_time = timestamp + timedelta(minutes=random.randint(1, 5))
                cursor.execute("""
                    INSERT INTO ai_logs 
                    (user_id, log_type, car_info, request_data, response_data, success, ai_model, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user,
                    'negotiation',
                    f"{vehicle['brand']} {vehicle['model']} {vehicle['year']}",
                    json.dumps({
                        "brand": vehicle['brand'],
                        "model": vehicle['model'],
                        "year": vehicle['year'],
                        "asking_price": vehicle['sale_price'],
                        "target_price": int(vehicle['sale_price'] * 0.95)
                    }, ensure_ascii=False),
                    json.dumps({
                        "script": f"{vehicle['brand']} {vehicle['model']} 네고 대본 생성됨",
                        "tips": ["시세 언급", "결함 체크", "즉시 결제 제안"]
                    }, ensure_ascii=False),
                    1,
                    'llama-3.3-70b',
                    nego_time.strftime('%Y-%m-%d %H:%M:%S')
                ))
                total_negotiations += 1
            
            # 4. ai_logs - fraud_detection (20% 확률로 허위매물 분석)
            if random.random() < 0.2:
                fraud_time = timestamp + timedelta(minutes=random.randint(2, 8))
                risk_score = random.randint(10, 95)
                cursor.execute("""
                    INSERT INTO ai_logs 
                    (user_id, log_type, car_info, request_data, response_data, success, ai_model, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user,
                    'fraud_detection',
                    f"{vehicle['brand']} {vehicle['model']} {vehicle['year']}",
                    json.dumps({
                        "brand": vehicle['brand'],
                        "model": vehicle['model'],
                        "year": vehicle['year'],
                        "price": vehicle['sale_price']
                    }, ensure_ascii=False),
                    json.dumps({
                        "risk_score": risk_score,
                        "risk_level": "high" if risk_score > 70 else "medium" if risk_score > 40 else "low",
                        "flags": random.sample(["가격 이상", "사진 불일치", "판매자 이력", "설명 모호"], k=random.randint(0, 2))
                    }, ensure_ascii=False),
                    1,
                    'llama-3.3-70b',
                    fraud_time.strftime('%Y-%m-%d %H:%M:%S')
                ))
                total_frauds += 1
            
            # 5. model_stats 업데이트
            cursor.execute("""
                INSERT INTO model_stats (model_name, view_count, updated_at)
                VALUES (?, 1, ?)
                ON CONFLICT(model_name) DO UPDATE SET
                    view_count = view_count + 1,
                    updated_at = ?
            """, (vehicle['model'], ts_str, ts_str))
        
        # 6. daily_stats 저장
        if daily_confidence_count > 0:
            avg_conf = daily_confidence_sum / daily_confidence_count
            cursor.execute("""
                INSERT OR REPLACE INTO daily_stats 
                (date, request_count, avg_confidence, total_confidence, confidence_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                date_str,
                analyses_count,
                avg_conf,
                daily_confidence_sum,
                daily_confidence_count,
                date.strftime('%Y-%m-%d %H:%M:%S')
            ))
        
        # 진행상황 출력 (10일마다)
        if day_offset % 10 == 0:
            print(f"  ... {days - day_offset}/{days}일 완료")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 50)
    print("데이터 생성 완료!")
    print("=" * 50)
    print(f"분석 이력 (analysis_history): {total_analyses}건")
    print(f"시그널 분석 (ai_logs/signal): {total_signals}건")
    print(f"네고 대본 (ai_logs/negotiation): {total_negotiations}건")
    print(f"허위매물 분석 (ai_logs/fraud): {total_frauds}건")
    print(f"총 AI 로그: {total_signals + total_negotiations + total_frauds}건")
    
    return {
        "analyses": total_analyses,
        "signals": total_signals,
        "negotiations": total_negotiations,
        "frauds": total_frauds
    }

def verify_data():
    """데이터 검증"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "=" * 50)
    print("데이터 검증")
    print("=" * 50)
    
    # 테이블별 건수
    tables = ['analysis_history', 'ai_logs', 'daily_stats', 'model_stats']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count}건")
    
    # AI 로그 유형별
    print("\nAI 로그 유형별:")
    cursor.execute("SELECT log_type, COUNT(*) FROM ai_logs GROUP BY log_type")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}건")
    
    # 인기 모델 TOP 5
    print("\n인기 모델 TOP 5:")
    cursor.execute("SELECT model_name, view_count FROM model_stats ORDER BY view_count DESC LIMIT 5")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}회")
    
    # 날짜 범위
    print("\n날짜 범위:")
    cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM analysis_history")
    row = cursor.fetchone()
    print(f"  분석 이력: {row[0]} ~ {row[1]}")
    
    conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Car-Sentix 통합 데이터 생성기")
    print("=" * 50)
    
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] DB 파일 없음: {DB_PATH}")
        exit(1)
    
    # 60일간, 하루 평균 10~20건 = 약 900건
    generate_data(days=60, analyses_per_day_range=(8, 18))
    verify_data()

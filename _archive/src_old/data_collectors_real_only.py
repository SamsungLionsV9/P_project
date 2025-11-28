"""
실제 데이터만 수집 (커뮤니티 감성 제외)
- 한국은행 API (금리) ✅
- Yahoo Finance (환율, 유가) ✅
- 네이버 데이터랩 API (검색 트렌드) ✅
- 신차 출시 일정 ✅
"""

import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

from data_collectors_real import RealMacroEconomicCollector
from data_collectors import NewCarScheduleManager
from data_collectors_complete import NaverTrendAPI


def collect_real_data_only(car_model):
    """
    실제 데이터만 수집 (100% 객관적)
    
    Args:
        car_model: 차량 모델명
        
    Returns:
        dict: {
            'macro': {...},      # 거시경제
            'trend': {...},      # 검색 트렌드
            'schedule': {...}    # 신차 일정
        }
    """
    print("=" * 80)
    print(f"🎯 실제 데이터 수집 중: {car_model}")
    print("=" * 80)
    print()
    
    # API 키
    bok_key = os.getenv('BOK_API_KEY')
    naver_id = os.getenv('NAVER_CLIENT_ID')
    naver_secret = os.getenv('NAVER_CLIENT_SECRET')
    
    # 1. 거시경제 데이터 (금리, 환율, 유가)
    print("📊 거시경제 데이터 수집 중...")
    macro = RealMacroEconomicCollector(bok_key)
    indicators = macro.get_all_indicators()
    
    # 타이밍 엔진용 포맷으로 변환
    macro_data = {
        'interest_rate': indicators['interest_rate']['rate'],
        'exchange_rate': indicators['exchange_rate']['rate'],
        'oil_price': indicators['oil_price']['price'],
        'oil_trend': indicators['oil_price']['trend']
    }
    
    print()
    
    # 2. 검색 트렌드 (네이버 데이터랩)
    print("🔍 검색 트렌드 수집 중...")
    trend_api = NaverTrendAPI(naver_id, naver_secret)
    trend_data = trend_api.get_search_trend(car_model)
    
    print()
    
    # 3. 신차 일정
    print("🚗 신차 출시 일정 확인 중...")
    schedule = NewCarScheduleManager()
    schedule_data = schedule.check_upcoming_release(car_model)
    
    print()
    print("=" * 80)
    print("✅ 실제 데이터 수집 완료!")
    print("=" * 80)
    print()
    
    print("📌 수집된 데이터:")
    print(f"  ✅ 금리: {macro_data.get('interest_rate', 'N/A')}%")
    print(f"  ✅ 환율: {macro_data.get('exchange_rate', 'N/A')}원")
    print(f"  ✅ 유가: ${macro_data.get('oil_price', 'N/A')}")
    print(f"  ✅ 검색 트렌드: {trend_data.get('trend_change', 'N/A')}% 변화")
    print(f"  ✅ 신차 일정: {len(schedule_data.get('upcoming_releases', []))}개")
    print()
    
    return {
        'macro': macro_data,
        'trend': trend_data,
        'schedule': schedule_data,
        'car_model': car_model,
        'collection_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_sources': {
            'macro': '한국은행 API + Yahoo Finance',
            'trend': '네이버 데이터랩 API',
            'schedule': 'CSV 데이터'
        }
    }


def save_collected_data(data, car_model):
    """수집 데이터 저장"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"collected_data_real_{car_model}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 데이터 저장: {filename}")
    return filename


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        car_model = sys.argv[1]
    else:
        car_model = "그랜저"
    
    print("=" * 80)
    print("실제 데이터 수집기 테스트")
    print("=" * 80)
    print()
    
    # 데이터 수집
    data = collect_real_data_only(car_model)
    
    # 저장
    save_collected_data(data, car_model)
    
    print()
    print("=" * 80)
    print("✅ 테스트 완료!")
    print("=" * 80)

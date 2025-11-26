import requests
import json
import pandas as pd
import time
import random
import os

def scrape_encar_imported(output_file="encar_imported_data.csv", batch_size=100):
    """
    엔카에서 수입차 데이터 수집
    CarType.N = 수입차 (Imported Cars)
    """
    url = "http://api.encar.com/search/car/list/general"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "http://www.encar.com/"
    }
    
    # Initialize file
    if os.path.exists(output_file):
        print(f"⚠️  기존 파일 삭제: {output_file}")
        os.remove(output_file)
        
    columns = ["Id", "Manufacturer", "Model", "Badge", "Year", "FormYear", "Mileage", "FuelType", "Price", "OfficeCityState", "CarType"]
    dummy_df = pd.DataFrame(columns=columns)
    dummy_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    
    print("🚗 수입차 데이터 수집 시작...")
    print("=" * 60)
    
    # Define price ranges (50만원 단위)
    ranges = []
    step = 50  # 50만원 단위
    for i in range(0, 15000, step):
        ranges.append((i, i + step))
    ranges.append((15000, 999999))  # 고가 차량
    
    total_collected = 0
    collected_ids = set()
    
    for idx, (min_p, max_p) in enumerate(ranges, 1):
        print(f"\n[{idx}/{len(ranges)}] 가격대: {min_p:,}만원 ~ {max_p:,}만원")
        
        # Query: CarType.N = 수입차
        q = f"(And.Hidden.N._.CarType.N._.Price.range({min_p}..{max_p}).)"
        init_params = {
            "count": "true",
            "q": q,
            "sr": "|ModifiedDate|0|1",
            "inav": "|Metadata|Sort,0|List,0,1",
            "curid": "0",
            "usid": "0"
        }
        
        try:
            resp = requests.get(url, params=init_params, headers=headers, timeout=10)
            count = resp.json().get('Count', 0)
            print(f"  📊 발견: {count}대")
            
            if count == 0:
                continue
                
        except Exception as e:
            print(f"  ❌ 카운트 조회 실패: {e}")
            time.sleep(2)
            continue
            
        # Collect items
        start = 0
        range_collected = 0
        
        while start < count:
            # Safety limit
            if start >= 8000:
                print("  ⚠️  오프셋 한계 도달 (8000)")
                break
                
            params = {
                "count": "true",
                "q": q,
                "sr": f"|ModifiedDate|{start}|{batch_size}",
                "inav": f"|Metadata|Sort,0|List,{start},{batch_size}",
                "curid": "0",
                "usid": "0"
            }
            
            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                if response.status_code != 200:
                    print(f"  ⚠️  HTTP {response.status_code}")
                    time.sleep(2)
                    continue
                    
                data = response.json()
                items = data.get('SearchResults', [])
                
                if not items:
                    break
                
                extracted_data = []
                for item in items:
                    car_id = item.get("Id")
                    if car_id in collected_ids:
                        continue
                        
                    collected_ids.add(car_id)
                    extracted_data.append({
                        "Id": car_id,
                        "Manufacturer": item.get("Manufacturer"),
                        "Model": item.get("Model"),
                        "Badge": item.get("Badge"),
                        "Year": item.get("Year"),
                        "FormYear": item.get("FormYear"),
                        "Mileage": item.get("Mileage"),
                        "FuelType": item.get("FuelType"),
                        "Price": item.get("Price"),
                        "OfficeCityState": item.get("OfficeCityState"),
                        "CarType": "Imported"  # 수입차 표시
                    })
                
                if extracted_data:
                    df = pd.DataFrame(extracted_data)
                    df.to_csv(output_file, mode='a', header=False, index=False, encoding="utf-8-sig")
                    range_collected += len(extracted_data)
                    total_collected += len(extracted_data)
                    print(f"  ✓ 수집: {range_collected}대 (누적: {total_collected:,}대)", end='\r')
                
                start += batch_size
                time.sleep(0.1)
                
            except Exception as e:
                print(f"\n  ❌ 오류: {e}")
                time.sleep(2)
                continue
        
        if range_collected > 0:
            print(f"  ✓ 완료: {range_collected}대 수집 (누적 총합: {total_collected:,}대)")
    
    print("\n" + "=" * 60)
    print(f"✅ 수입차 데이터 수집 완료!")
    print(f"📁 저장 위치: {os.path.abspath(output_file)}")
    print(f"📊 총 수집량: {total_collected:,}대")
    
    return total_collected

if __name__ == "__main__":
    total = scrape_encar_imported()
    print(f"\n🎉 최종 결과: {total:,}대의 수입차 데이터 수집")

import requests
import json
import pandas as pd
import time
import random
import os

def scrape_encar_partitioned(output_file="encar_raw_domestic.csv", batch_size=100):
    url = "http://api.encar.com/search/car/list/general"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "http://www.encar.com/"
    }
    
    # Initialize file
    if os.path.exists(output_file):
        os.remove(output_file)
        
    columns = ["Id", "Manufacturer", "Model", "Badge", "Year", "FormYear", "Mileage", "FuelType", "Price", "OfficeCityState"]
    dummy_df = pd.DataFrame(columns=columns)
    dummy_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    
    # Define price ranges (Man-won)
    # 0 to 20000 (200 million KRW) in steps of 100 (1 million KRW)
    # This should keep counts low enough per range
    ranges = []
    step = 50 # 50만원 단위로 더 잘게 쪼갬 (안전하게)
    for i in range(0, 15000, step):
        ranges.append((i, i + step))
    ranges.append((15000, 999999)) # High price cars
    
    total_collected = 0
    collected_ids = set()
    
    for min_p, max_p in ranges:
        print(f"\nScanning Price Range: {min_p} ~ {max_p}...")
        
        # Check count first
        q = f"(And.Hidden.N._.CarType.Y._.Price.range({min_p}..{max_p}).)"
        init_params = {
            "count": "true",
            "q": q,
            "sr": "|ModifiedDate|0|1",
            "inav": "|Metadata|Sort,0|List,0,1",
            "curid": "0",
            "usid": "0"
        }
        
        try:
            resp = requests.get(url, params=init_params, headers=headers)
            count = resp.json().get('Count', 0)
            print(f"  Found {count} cars in this range.")
            
            if count == 0:
                continue
                
        except Exception as e:
            print(f"  Error checking count: {e}")
            continue
            
        # Collect items
        start = 0
        range_collected = 0
        
        while start < count:
            # Safety limit for offset
            if start >= 8000: # If range has > 8000 items, we might miss some due to limit, but 50 step should prevent this
                print("  Reached safe offset limit for this range.")
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
                        "OfficeCityState": item.get("OfficeCityState")
                    })
                
                if extracted_data:
                    df = pd.DataFrame(extracted_data)
                    df.to_csv(output_file, mode='a', header=False, index=False, encoding="utf-8-sig")
                    range_collected += len(extracted_data)
                    total_collected += len(extracted_data)
                
                start += batch_size
                time.sleep(0.1) # Fast
                
            except Exception as e:
                print(f"  Error: {e}")
                time.sleep(2)
                continue
        
        print(f"  Collected {range_collected} items from this range. Total Unique: {total_collected}")
        
    return total_collected

if __name__ == "__main__":
    scrape_encar_partitioned()

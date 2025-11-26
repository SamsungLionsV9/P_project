"""
빠진 필드만 추가 수집 (보완 스크립트)
기존 fast_domestic_details.csv의 car_id 기반으로 추가 정보 수집
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import os
from datetime import datetime
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

class SupplementScraper:
    def __init__(self, checkpoint_file='data/supplement_checkpoint.json', 
                 output_file='data/supplement_details.csv'):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.checkpoint_file = checkpoint_file
        self.output_file = output_file
        self.lock = Lock()
        
    def load_checkpoint(self):
        """체크포인트 로드"""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'processed_ids': [], 'collected_data': []}
    
    def save_checkpoint(self, checkpoint_data):
        """체크포인트 저장"""
        os.makedirs('data', exist_ok=True)
        with self.lock:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False)
    
    def scrape_supplement_info(self, car_id):
        """빠진 필드만 수집"""
        url = f"https://fem.encar.com/cars/detail/{car_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            detail_info = {'car_id': car_id}
            
            # 빠진 옵션 5개만 추가 수집
            detail_info['has_led_lamp'] = 1 if soup.find(string=lambda t: t and 'LED' in str(t)) else 0
            detail_info['has_parking_sensor'] = 1 if soup.find(string=lambda t: t and '주차감지센서' in str(t)) else 0
            detail_info['has_auto_ac'] = 1 if soup.find(string=lambda t: t and '자동에어컨' in str(t)) else 0
            detail_info['has_heated_seat'] = 1 if soup.find(string=lambda t: t and '열선시트' in str(t)) else 0
            detail_info['has_ventilated_seat'] = 1 if soup.find(string=lambda t: t and '통풍시트' in str(t)) else 0
            
            # 지역 정보
            region_elem = soup.find(string=lambda t: t and ('서울' in str(t) or '경기' in str(t) or '인천' in str(t) or '부산' in str(t) or '대구' in str(t)))
            detail_info['region'] = region_elem.strip() if region_elem else 'Unknown'
            
            # 초단시간 대기
            time.sleep(random.uniform(0.05, 0.15))
            
            return detail_info
            
        except Exception as e:
            return None
    
    def scrape_batch(self, car_ids, checkpoint_data):
        """배치 크롤링 (멀티스레딩)"""
        collected = []
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_id = {executor.submit(self.scrape_supplement_info, car_id): car_id 
                           for car_id in car_ids}
            
            for future in as_completed(future_to_id):
                car_id = future_to_id[future]
                try:
                    result = future.result()
                    if result:
                        with self.lock:
                            collected.append(result)
                            checkpoint_data['processed_ids'].append(car_id)
                            print(f"✓ {car_id} ({len(checkpoint_data['processed_ids'])}개 완료)", end='\r')
                except Exception as e:
                    print(f"✗ {car_id} 실패: {e}")
        
        return collected
    
    def scrape_supplement(self, source_csv='data/fast_domestic_details.csv', batch_size=200):
        """기존 CSV 기반으로 보완 정보 수집"""
        print("="*80)
        print("🔧 보완 정보 수집 (빠진 필드만)")
        print("="*80)
        print(f"✓ 수집 필드: LED램프, 주차센서, 자동에어컨, 열선시트, 통풍시트, 지역")
        print("="*80)
        print()
        
        # 기존 CSV에서 car_id 로드
        if not os.path.exists(source_csv):
            print(f"❌ 파일 없음: {source_csv}")
            return
        
        df = pd.read_csv(source_csv)
        all_ids = df['car_id'].tolist()
        print(f"📊 총 {len(all_ids):,}개 차량")
        
        # 체크포인트 로드
        checkpoint_data = self.load_checkpoint()
        processed = set(checkpoint_data['processed_ids'])
        remaining = [cid for cid in all_ids if cid not in processed]
        
        print(f"✓ 이미 완료: {len(processed):,}개")
        print(f"✓ 남은 작업: {len(remaining):,}개")
        print()
        
        if not remaining:
            print("✅ 모두 완료!")
            return
        
        start_time = time.time()
        
        # 배치 처리
        for i in range(0, len(remaining), batch_size):
            batch = remaining[i:i+batch_size]
            batch_num = i // batch_size + 1
            
            print(f"\n{'='*80}")
            print(f"📦 배치 {batch_num} 처리 중... ({len(batch)}개)")
            print(f"{'='*80}")
            
            batch_start = time.time()
            collected = self.scrape_batch(batch, checkpoint_data)
            batch_time = time.time() - batch_start
            
            # 체크포인트 저장
            checkpoint_data['collected_data'].extend(collected)
            self.save_checkpoint(checkpoint_data)
            
            # 진행 상황
            total_collected = len(checkpoint_data['processed_ids'])
            progress = total_collected / len(all_ids) * 100
            elapsed = time.time() - start_time
            speed = total_collected / elapsed if elapsed > 0 else 0
            eta = (len(all_ids) - total_collected) / speed if speed > 0 else 0
            
            print(f"\n📊 진행 상황:")
            print(f"   ✓ 완료: {total_collected:,}/{len(all_ids):,} ({progress:.1f}%)")
            print(f"   ⚡ 속도: {speed:.1f}개/초")
            print(f"   ⏱️ 예상 남은 시간: {eta/60:.1f}분")
            
            # CSV 저장 (500개마다)
            if total_collected % 500 == 0:
                self.save_to_csv(checkpoint_data['collected_data'])
        
        # 최종 저장
        print(f"\n{'='*80}")
        print("💾 최종 저장 중...")
        self.save_to_csv(checkpoint_data['collected_data'])
        
        total_time = time.time() - start_time
        print(f"✅ 완료! 총 {len(checkpoint_data['processed_ids']):,}개")
        print(f"⏱️ 소요 시간: {total_time/60:.1f}분")
        print("="*80)
    
    def save_to_csv(self, data):
        """CSV 저장"""
        if data:
            df = pd.DataFrame(data)
            df.to_csv(self.output_file, index=False, encoding='utf-8-sig')
            print(f"✓ CSV 저장: {len(df)}행")


def merge_dataframes():
    """기존 데이터 + 보완 데이터 병합"""
    print("\n" + "="*80)
    print("🔀 데이터 병합 중...")
    print("="*80)
    
    # 1. 기존 데이터 로드
    df_base = pd.read_csv('data/fast_domestic_details.csv')
    print(f"✓ 기존 데이터: {len(df_base)}행")
    
    # 2. 보완 데이터 로드
    df_supplement = pd.read_csv('data/supplement_details.csv')
    print(f"✓ 보완 데이터: {len(df_supplement)}행")
    
    # 3. car_id 기준으로 병합
    df_merged = df_base.merge(df_supplement, on='car_id', how='left')
    print(f"✓ 병합 완료: {len(df_merged)}행")
    
    # 4. 저장
    df_merged.to_csv('data/complete_domestic_details.csv', index=False, encoding='utf-8-sig')
    print(f"✅ 최종 저장: data/complete_domestic_details.csv")
    print("="*80)
    
    return df_merged


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'merge':
        # 병합만 실행
        merge_dataframes()
    else:
        # 1. 국산차 보완 정보 수집
        print("="*80)
        print("🚗 국산차 보완 정보 수집 시작...")
        print("="*80)
        scraper_domestic = SupplementScraper(
            checkpoint_file='data/supplement_checkpoint_domestic.json',
            output_file='data/supplement_domestic.csv'
        )
        scraper_domestic.scrape_supplement(
            source_csv='data/fast_domestic_details.csv',
            batch_size=200
        )
        
        # 국산차 병합
        try:
            print("\n" + "="*80)
            print("🔀 국산차 데이터 병합 중...")
            print("="*80)
            
            df_base = pd.read_csv('data/fast_domestic_details.csv')
            print(f"✓ 기존 데이터: {len(df_base)}행")
            
            df_supplement = pd.read_csv('data/supplement_domestic.csv')
            print(f"✓ 보완 데이터: {len(df_supplement)}행")
            
            df_merged = df_base.merge(df_supplement, on='car_id', how='left')
            print(f"✓ 병합 완료: {len(df_merged)}행")
            
            df_merged.to_csv('data/complete_domestic_details.csv', index=False, encoding='utf-8-sig')
            print(f"✅ 최종 저장: data/complete_domestic_details.csv")
            print("="*80)
        except Exception as e:
            print(f"⚠️ 국산차 병합 실패: {e}")
        
        print("\n\n")
        
        # 2. 수입차 보완 정보 수집
        print("="*80)
        print("🚙 수입차 보완 정보 수집 시작...")
        print("="*80)
        scraper_imported = SupplementScraper(
            checkpoint_file='data/supplement_checkpoint_imported.json',
            output_file='data/supplement_imported.csv'
        )
        scraper_imported.scrape_supplement(
            source_csv='data/fast_imported_details.csv',
            batch_size=200
        )
        
        # 수입차 병합
        try:
            print("\n" + "="*80)
            print("🔀 수입차 데이터 병합 중...")
            print("="*80)
            
            df_base_imp = pd.read_csv('data/fast_imported_details.csv')
            print(f"✓ 기존 데이터: {len(df_base_imp)}행")
            
            df_supplement_imp = pd.read_csv('data/supplement_imported.csv')
            print(f"✓ 보완 데이터: {len(df_supplement_imp)}행")
            
            df_merged_imp = df_base_imp.merge(df_supplement_imp, on='car_id', how='left')
            print(f"✓ 병합 완료: {len(df_merged_imp)}행")
            
            df_merged_imp.to_csv('data/complete_imported_details.csv', index=False, encoding='utf-8-sig')
            print(f"✅ 최종 저장: data/complete_imported_details.csv")
            print("="*80)
        except Exception as e:
            print(f"⚠️ 수입차 병합 실패: {e}")
        
        print("\n\n")
        print("="*80)
        print("🎉 모든 보완 작업 완료!")
        print("="*80)
        print(f"✅ 국산차: data/complete_domestic_details.csv")
        print(f"✅ 수입차: data/complete_imported_details.csv")
        print("="*80)

"""
초고속 엔카 상세 페이지 크롤러
- 멀티스레딩 (동시 20개 요청)
- Sleep 시간 최소화 (0.05~0.15초)
- 핵심 데이터만 수집
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

class FastEncarScraper:
    def __init__(self, checkpoint_file='data/fast_checkpoint.json', 
                 output_file='data/fast_encar_data.csv'):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.checkpoint_file = checkpoint_file
        self.output_file = output_file
        self.lock = Lock()  # 스레드 안전성
        
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
    
    def scrape_detail_fast(self, car_id):
        """단일 차량 상세 정보 크롤링 (핵심만)"""
        url = f"https://fem.encar.com/cars/detail/{car_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            detail_info = {'car_id': car_id}
            
            # 핵심 정보만 수집 (속도 우선)
            # 1. 무사고
            detail_info['is_accident_free'] = 1 if soup.find(text=lambda t: t and '무사고' in str(t)) else 0
            
            # 2. 성능점검 등급
            if soup.find(text=lambda t: t and '우수' in str(t)):
                detail_info['inspection_grade'] = 'excellent'
            elif soup.find(text=lambda t: t and '양호' in str(t)):
                detail_info['inspection_grade'] = 'good'
            else:
                detail_info['inspection_grade'] = 'normal'
            
            # 3. 주요 옵션 5개만
            detail_info['has_sunroof'] = 1 if soup.find(text=lambda t: t and '선루프' in str(t)) else 0
            detail_info['has_navigation'] = 1 if soup.find(text=lambda t: t and '내비게이션' in str(t)) else 0
            detail_info['has_leather_seat'] = 1 if soup.find(text=lambda t: t and '가죽시트' in str(t)) else 0
            detail_info['has_smart_key'] = 1 if soup.find(text=lambda t: t and '스마트키' in str(t)) else 0
            detail_info['has_rear_camera'] = 1 if soup.find(text=lambda t: t and '후방카메라' in str(t)) else 0
            
            # 초단시간 대기 (IP 차단 방지)
            time.sleep(random.uniform(0.05, 0.15))
            
            return detail_info
            
        except Exception as e:
            return None
    
    def scrape_batch(self, car_ids, checkpoint_data):
        """배치 크롤링 (멀티스레딩)"""
        collected = []
        
        # 최대 20개 동시 실행
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_id = {executor.submit(self.scrape_detail_fast, car_id): car_id 
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
    
    def scrape_all_fast(self, source_file='encar_raw_domestic.csv', batch_size=100):
        """전체 고속 수집"""
        print("="*80)
        print("🚀 초고속 엔카 크롤러 (멀티스레딩)")
        print("="*80)
        print(f"✓ 동시 요청: 20개")
        print(f"✓ Sleep: 0.05~0.15초")
        print(f"✓ 배치 크기: {batch_size}개")
        print("="*80)
        print()
        
        # 소스 데이터 로드
        if not os.path.exists(source_file):
            print(f"❌ 파일 없음: {source_file}")
            return
        
        df = pd.read_csv(source_file)
        
        # ID 컬럼 찾기
        id_column = None
        for col in ['Id', 'id', 'car_id', 'ID']:
            if col in df.columns:
                id_column = col
                break
        
        if not id_column:
            print("❌ ID 컬럼 없음")
            return
        
        all_ids = df[id_column].dropna().astype(int).unique().tolist()
        print(f"📊 총 {len(all_ids):,}개 ID")
        
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
            
            # 멀티스레딩 수집
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
            print(f"   ⚡ 속도: {speed:.1f}개/초 ({batch_time:.1f}초/{len(batch)}개)")
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
        print(f"⚡ 평균 속도: {len(checkpoint_data['processed_ids'])/total_time:.1f}개/초")
        print("="*80)
    
    def save_to_csv(self, data):
        """CSV 저장"""
        if data:
            df = pd.DataFrame(data)
            df.to_csv(self.output_file, index=False, encoding='utf-8-sig')
            print(f"✓ CSV 저장: {len(df)}행")


if __name__ == "__main__":
    # 국산차 고속 수집
    print("🚗 국산차 고속 수집 시작...")
    scraper_dom = FastEncarScraper(
        checkpoint_file='data/fast_checkpoint_domestic.json',
        output_file='data/fast_domestic_details.csv'
    )
    scraper_dom.scrape_all_fast(source_file='encar_raw_domestic.csv', batch_size=200)
    
    print("\n\n")
    
    # 수입차 고속 수집
    print("🚙 수입차 고속 수집 시작...")
    scraper_imp = FastEncarScraper(
        checkpoint_file='data/fast_checkpoint_imported.json',
        output_file='data/fast_imported_details.csv'
    )
    scraper_imp.scrape_all_fast(source_file='encar_imported_data.csv', batch_size=200)

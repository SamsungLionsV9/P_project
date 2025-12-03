#!/usr/bin/env python3
"""
CSV 파일을 MySQL 데이터베이스에 import하는 스크립트

사용법:
    python setup/import_csv_to_mysql.py

환경 변수 설정:
    MYSQL_HOST=localhost
    MYSQL_PORT=3306
    MYSQL_USER=root
    MYSQL_PASSWORD=your_password
    MYSQL_DATABASE=car_database
"""

import os
import sys
import pandas as pd
import pymysql
from pathlib import Path
from typing import Optional
import argparse
from tqdm import tqdm

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def get_mysql_connection():
    """MySQL 연결 생성"""
    host = os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("MYSQL_PORT", 3306))
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "Project1!")
    database = os.getenv("MYSQL_DATABASE", "car_database")
    
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            local_infile=True  # LOAD DATA LOCAL INFILE 허용
        )
        print(f"✅ MySQL 연결 성공: {user}@{host}:{port}/{database}")
        return connection
    except Exception as e:
        print(f"❌ MySQL 연결 실패: {e}")
        sys.exit(1)


def import_domestic_details(connection, csv_path: Path, batch_size: int = 1000):
    """국산차 상세 정보 import"""
    print(f"\n📊 국산차 상세 정보 import 시작: {csv_path.name}")
    
    try:
        # CSV 파일 읽기 (청크 단위로 처리)
        chunk_size = batch_size
        total_rows = sum(1 for _ in open(csv_path, 'r', encoding='utf-8')) - 1
        print(f"   총 {total_rows:,}개 행 처리 예정")
        
        cursor = connection.cursor()
        imported = 0
        skipped = 0
        
        for chunk in tqdm(pd.read_csv(csv_path, chunksize=chunk_size, encoding='utf-8'), 
                         total=(total_rows // chunk_size) + 1, desc="   처리 중"):
            # BOM 제거
            chunk.columns = chunk.columns.str.replace('\ufeff', '')
            
            # 데이터 정리
            chunk = chunk.fillna(0)
            
            # SQL 쿼리 생성
            values = []
            for _, row in chunk.iterrows():
                try:
                    values.append((
                        str(row.get('car_id', '')),
                        int(row.get('is_accident_free', 0)),
                        str(row.get('inspection_grade', 'normal')),
                        int(row.get('has_sunroof', 0)),
                        int(row.get('has_navigation', 0)),
                        int(row.get('has_leather_seat', 0)),
                        int(row.get('has_smart_key', 0)),
                        int(row.get('has_rear_camera', 0)),
                        int(row.get('has_led_lamp', 0)),
                        int(row.get('has_parking_sensor', 0)),
                        int(row.get('has_auto_ac', 0)),
                        int(row.get('has_heated_seat', 0)),
                        int(row.get('has_ventilated_seat', 0)),
                        str(row.get('region', ''))[:500] if pd.notna(row.get('region')) else ''
                    ))
                except Exception as e:
                    skipped += 1
                    continue
            
            if values:
                sql = """
                INSERT INTO domestic_car_details 
                (car_id, is_accident_free, inspection_grade, has_sunroof, has_navigation,
                 has_leather_seat, has_smart_key, has_rear_camera, has_led_lamp,
                 has_parking_sensor, has_auto_ac, has_heated_seat, has_ventilated_seat, region)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    is_accident_free=VALUES(is_accident_free),
                    inspection_grade=VALUES(inspection_grade),
                    region=VALUES(region),
                    updated_at=CURRENT_TIMESTAMP(6)
                """
                cursor.executemany(sql, values)
                imported += len(values)
                connection.commit()
        
        cursor.close()
        print(f"   ✅ 완료: {imported:,}개 행 import, {skipped:,}개 행 건너뜀")
        return imported, skipped
        
    except Exception as e:
        print(f"   ❌ 오류 발생: {e}")
        connection.rollback()
        return 0, 0


def import_imported_details(connection, csv_path: Path, batch_size: int = 1000):
    """외제차 상세 정보 import"""
    print(f"\n📊 외제차 상세 정보 import 시작: {csv_path.name}")
    
    try:
        chunk_size = batch_size
        total_rows = sum(1 for _ in open(csv_path, 'r', encoding='utf-8')) - 1
        print(f"   총 {total_rows:,}개 행 처리 예정")
        
        cursor = connection.cursor()
        imported = 0
        skipped = 0
        
        for chunk in tqdm(pd.read_csv(csv_path, chunksize=chunk_size, encoding='utf-8'),
                         total=(total_rows // chunk_size) + 1, desc="   처리 중"):
            chunk.columns = chunk.columns.str.replace('\ufeff', '')
            chunk = chunk.fillna(0)
            
            values = []
            for _, row in chunk.iterrows():
                try:
                    values.append((
                        str(row.get('car_id', '')),
                        int(row.get('is_accident_free', 0)),
                        str(row.get('inspection_grade', 'normal')),
                        int(row.get('has_sunroof', 0)),
                        int(row.get('has_navigation', 0)),
                        int(row.get('has_leather_seat', 0)),
                        int(row.get('has_smart_key', 0)),
                        int(row.get('has_rear_camera', 0)),
                        int(row.get('has_led_lamp', 0)),
                        int(row.get('has_parking_sensor', 0)),
                        int(row.get('has_auto_ac', 0)),
                        int(row.get('has_heated_seat', 0)),
                        int(row.get('has_ventilated_seat', 0)),
                        str(row.get('region', ''))[:500] if pd.notna(row.get('region')) else ''
                    ))
                except Exception as e:
                    skipped += 1
                    continue
            
            if values:
                sql = """
                INSERT INTO imported_car_details 
                (car_id, is_accident_free, inspection_grade, has_sunroof, has_navigation,
                 has_leather_seat, has_smart_key, has_rear_camera, has_led_lamp,
                 has_parking_sensor, has_auto_ac, has_heated_seat, has_ventilated_seat, region)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    is_accident_free=VALUES(is_accident_free),
                    inspection_grade=VALUES(inspection_grade),
                    region=VALUES(region),
                    updated_at=CURRENT_TIMESTAMP(6)
                """
                cursor.executemany(sql, values)
                imported += len(values)
                connection.commit()
        
        cursor.close()
        print(f"   ✅ 완료: {imported:,}개 행 import, {skipped:,}개 행 건너뜀")
        return imported, skipped
        
    except Exception as e:
        print(f"   ❌ 오류 발생: {e}")
        connection.rollback()
        return 0, 0


def import_new_car_schedule(connection, csv_path: Path):
    """신차 출시 일정 import"""
    print(f"\n📊 신차 출시 일정 import 시작: {csv_path.name}")
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        df.columns = df.columns.str.replace('\ufeff', '')
        
        print(f"   총 {len(df):,}개 행 처리 예정")
        
        cursor = connection.cursor()
        imported = 0
        skipped = 0
        
        for _, row in tqdm(df.iterrows(), total=len(df), desc="   처리 중"):
            try:
                brand = str(row.get('brand', '')).strip()
                model = str(row.get('model', '')).strip()
                release_date = str(row.get('release_date', '')).strip()
                car_type = str(row.get('type', '')).strip() if pd.notna(row.get('type')) else ''
                
                if not brand or not model or not release_date:
                    skipped += 1
                    continue
                
                sql = """
                INSERT INTO new_car_schedule (brand, model, release_date, type)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    release_date=VALUES(release_date),
                    type=VALUES(type),
                    updated_at=CURRENT_TIMESTAMP(6)
                """
                cursor.execute(sql, (brand, model, release_date, car_type))
                imported += 1
            except Exception as e:
                skipped += 1
                continue
        
        connection.commit()
        cursor.close()
        print(f"   ✅ 완료: {imported:,}개 행 import, {skipped:,}개 행 건너뜀")
        return imported, skipped
        
    except Exception as e:
        print(f"   ❌ 오류 발생: {e}")
        connection.rollback()
        return 0, 0


def main():
    parser = argparse.ArgumentParser(description='CSV 파일을 MySQL에 import')
    parser.add_argument('--all', action='store_true', help='모든 CSV 파일 import')
    parser.add_argument('--domestic', action='store_true', help='국산차 상세 정보만 import')
    parser.add_argument('--imported', action='store_true', help='외제차 상세 정보만 import')
    parser.add_argument('--schedule', action='store_true', help='신차 출시 일정만 import')
    parser.add_argument('--batch-size', type=int, default=1000, help='배치 크기 (기본: 1000)')
    
    args = parser.parse_args()
    
    # 모든 옵션이 없으면 --all 기본값
    if not (args.domestic or args.imported or args.schedule):
        args.all = True
    
    print("=" * 60)
    print("🚀 CSV → MySQL Import 시작")
    print("=" * 60)
    
    # MySQL 연결
    connection = get_mysql_connection()
    
    total_imported = 0
    total_skipped = 0
    
    try:
        # 국산차 상세 정보
        if args.all or args.domestic:
            csv_path = DATA_DIR / "complete_domestic_details.csv"
            if csv_path.exists():
                imported, skipped = import_domestic_details(connection, csv_path, args.batch_size)
                total_imported += imported
                total_skipped += skipped
            else:
                print(f"\n⚠️ 파일 없음: {csv_path}")
        
        # 외제차 상세 정보
        if args.all or args.imported:
            csv_path = DATA_DIR / "complete_imported_details.csv"
            if csv_path.exists():
                imported, skipped = import_imported_details(connection, csv_path, args.batch_size)
                total_imported += imported
                total_skipped += skipped
            else:
                print(f"\n⚠️ 파일 없음: {csv_path}")
        
        # 신차 출시 일정
        if args.all or args.schedule:
            csv_path = DATA_DIR / "new_car_schedule.csv"
            if csv_path.exists():
                imported, skipped = import_new_car_schedule(connection, csv_path)
                total_imported += imported
                total_skipped += skipped
            else:
                print(f"\n⚠️ 파일 없음: {csv_path}")
        
        print("\n" + "=" * 60)
        print(f"✅ Import 완료!")
        print(f"   총 {total_imported:,}개 행 import")
        print(f"   총 {total_skipped:,}개 행 건너뜀")
        print("=" * 60)
        
    finally:
        connection.close()
        print("\n🔌 MySQL 연결 종료")


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
MySQL 협업 설정 자동화 스크립트
- 외부 접근용 사용자 생성
- CSV 테이블 생성
- CSV 데이터 import
"""

import pymysql
import os
import sys
from pathlib import Path

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent

# MySQL 설정
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'Project1!'),
    'database': os.getenv('MYSQL_DATABASE', 'car_database'),
    'charset': 'utf8mb4'
}


def get_connection():
    """MySQL 연결 생성"""
    try:
        connection = pymysql.connect(**MYSQL_CONFIG)
        print(f"✅ MySQL 연결 성공: {MYSQL_CONFIG['user']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}")
        return connection
    except Exception as e:
        print(f"❌ MySQL 연결 실패: {e}")
        sys.exit(1)


def create_remote_user(connection):
    """외부 접근용 사용자 생성"""
    print("\n" + "=" * 60)
    print("🔐 외부 접근용 사용자 생성")
    print("=" * 60)
    
    cursor = connection.cursor()
    
    try:
        # 기존 사용자 확인
        cursor.execute("SELECT user, host FROM mysql.user WHERE user = 'team_user'")
        existing = cursor.fetchall()
        
        if existing:
            print("⚠️ team_user 사용자가 이미 존재합니다.")
            response = input("기존 사용자를 삭제하고 재생성하시겠습니까? (y/n): ")
            if response.lower() == 'y':
                cursor.execute("DROP USER IF EXISTS 'team_user'@'%'")
                print("✅ 기존 사용자 삭제 완료")
            else:
                print("⏭️ 사용자 생성 건너뜀")
                return
        
        # 새 사용자 생성
        # 자동 모드: 환경 변수 또는 기본값 사용
        password = os.getenv('TEAM_USER_PASSWORD', 'TeamPassword123!@#')
        print(f"   비밀번호: {password} (환경 변수 TEAM_USER_PASSWORD로 변경 가능)")
        
        cursor.execute(f"CREATE USER 'team_user'@'%' IDENTIFIED BY '{password}'")
        cursor.execute("GRANT ALL PRIVILEGES ON car_database.* TO 'team_user'@'%'")
        cursor.execute("FLUSH PRIVILEGES")
        
        print(f"✅ 외부 접근용 사용자 생성 완료!")
        print(f"   사용자: team_user")
        print(f"   비밀번호: {password}")
        print(f"   ⚠️ 이 비밀번호를 팀원들에게 안전하게 공유하세요!")
        
    except Exception as e:
        print(f"❌ 사용자 생성 실패: {e}")
        connection.rollback()
    finally:
        cursor.close()


def create_csv_tables(connection):
    """CSV 테이블 생성"""
    print("\n" + "=" * 60)
    print("📊 CSV 테이블 생성")
    print("=" * 60)
    
    sql_file = PROJECT_ROOT / "setup" / "create_csv_tables.sql"
    
    if not sql_file.exists():
        print(f"❌ SQL 파일을 찾을 수 없습니다: {sql_file}")
        return
    
    cursor = connection.cursor()
    
    try:
        # SQL 파일 읽기
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 주석 제거 및 명령어 분리
        statements = []
        current_statement = []
        
        for line in sql_content.split('\n'):
            line = line.strip()
            if not line or line.startswith('--'):
                continue
            if line.startswith('USE '):
                continue  # USE 문은 이미 연결된 DB 사용
            current_statement.append(line)
            if line.endswith(';'):
                statements.append(' '.join(current_statement))
                current_statement = []
        
        # SQL 실행
        for i, statement in enumerate(statements, 1):
            try:
                cursor.execute(statement)
                if 'CREATE TABLE' in statement.upper():
                    table_name = statement.split('IF NOT EXISTS')[1].split('(')[0].strip()
                    print(f"   ✅ 테이블 생성: {table_name}")
            except Exception as e:
                if 'already exists' not in str(e).lower():
                    print(f"   ⚠️ 경고: {e}")
        
        connection.commit()
        print("\n✅ CSV 테이블 생성 완료!")
        
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        connection.rollback()
    finally:
        cursor.close()


def check_csv_data(connection):
    """CSV 데이터 확인"""
    print("\n" + "=" * 60)
    print("📊 CSV 데이터 확인")
    print("=" * 60)
    
    cursor = connection.cursor()
    
    tables = [
        ('domestic_car_details', '국산차 상세 정보'),
        ('imported_car_details', '외제차 상세 정보'),
        ('new_car_schedule', '신차 출시 일정')
    ]
    
    for table_name, description in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   {description}: {count:,}개 행")
        except Exception as e:
            print(f"   {description}: ❌ 테이블 없음 또는 오류")
    
    cursor.close()


def main():
    print("=" * 60)
    print("🚀 MySQL 협업 설정 자동화")
    print("=" * 60)
    
    connection = get_connection()
    
    try:
        # 1. 외부 접근용 사용자 생성
        create_remote_user(connection)
        
        # 2. CSV 테이블 생성
        create_csv_tables(connection)
        
        # 3. CSV 데이터 확인
        check_csv_data(connection)
        
        print("\n" + "=" * 60)
        print("✅ 협업 설정 완료!")
        print("=" * 60)
        print("\n📝 다음 단계:")
        print("1. ngrok 터널 시작: ./setup/start_ngrok_tunnel.sh")
        print("2. 출력된 URL을 팀원들에게 공유")
        print("3. 팀원들은 setup/application.yml.remote.example 참고하여 설정")
        
    finally:
        connection.close()
        print("\n🔌 MySQL 연결 종료")


if __name__ == "__main__":
    main()


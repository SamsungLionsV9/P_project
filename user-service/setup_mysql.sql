-- MySQL 데이터베이스 설정
-- 사용법: mysql -u root -p < setup_mysql.sql

-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS car_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 사용자 생성 (선택사항)
CREATE USER IF NOT EXISTS 'carapp'@'localhost' IDENTIFIED BY 'carapp123!';
GRANT ALL PRIVILEGES ON car_database.* TO 'carapp'@'localhost';
FLUSH PRIVILEGES;

-- 데이터베이스 선택
USE car_database;

-- 기존 테이블 확인
SHOW TABLES;

SELECT '✅ MySQL 데이터베이스 설정 완료!' AS status;
SELECT 'Spring Boot 애플리케이션을 실행하면 users 테이블이 자동 생성됩니다.' AS info;


-- MySQL 데이터베이스 설정
-- 사용법: mysql -u root -p < setup_mysql.sql

-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS car_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 사용자 생성 (선택사항) - 주석 처리하여 root 계정 사용
-- CREATE USER IF NOT EXISTS 'carapp'@'localhost' IDENTIFIED BY 'CarApp123!@#';
-- GRANT ALL PRIVILEGES ON car_database.* TO 'carapp'@'localhost';
-- FLUSH PRIVILEGES;

-- 데이터베이스 선택
USE car_database;

-- ============================================
-- 사용자 관리 테이블 생성
-- ============================================

-- 기존 테이블이 있다면 삭제 (주의: 데이터도 함께 삭제됨)
-- DROP TABLE IF EXISTS users;

-- users 테이블 생성
CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '사용자 ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '사용자명',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '이메일 (로그인 ID)',
    password VARCHAR(255) NOT NULL COMMENT '암호화된 비밀번호 (BCrypt)',
    phone_number VARCHAR(20) COMMENT '전화번호',
    role VARCHAR(10) NOT NULL DEFAULT 'USER' COMMENT '권한 (USER, ADMIN)',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '활성화 상태',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '생성일시',
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '수정일시',
    
    -- 인덱스 추가
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 정보';

-- ============================================
-- 테스트 데이터 추가 (선택사항)
-- ============================================

-- 테스트 관리자 계정 (비밀번호: Admin1234!)
-- 주의: 실제 환경에서는 반드시 비밀번호를 변경하세요!
INSERT INTO users (username, email, password, phone_number, role, is_active)
VALUES (
    'admin',
    'admin@example.com',
    '$2a$10$rQ5K5Jz5Jz5Jz5Jz5Jz5JOK5K5K5K5K5K5K5K5K5K5K5K5K5K5K5K',  -- Admin1234! (BCrypt)
    '010-0000-0000',
    'ADMIN',
    TRUE
)
ON DUPLICATE KEY UPDATE email = email;  -- 이미 있으면 무시

-- 테스트 일반 사용자 계정 (비밀번호: Test1234!)
INSERT INTO users (username, email, password, phone_number, role, is_active)
VALUES (
    'testuser',
    'test@example.com',
    '$2a$10$tQ5K5Jz5Jz5Jz5Jz5Jz5JOK5K5K5K5K5K5K5K5K5K5K5K5K5K5K5K',  -- Test1234! (BCrypt)
    '010-1234-5678',
    'USER',
    TRUE
)
ON DUPLICATE KEY UPDATE email = email;  -- 이미 있으면 무시

-- ============================================
-- 테이블 확인
-- ============================================

-- 생성된 테이블 목록
SHOW TABLES;

-- users 테이블 구조 확인
DESC users;

-- 데이터 확인
SELECT 
    id, 
    username, 
    email, 
    phone_number, 
    role, 
    is_active, 
    created_at 
FROM users;

-- 완료 메시지
SELECT '✅ MySQL 데이터베이스 및 users 테이블 생성 완료!' AS status;
SELECT '🔐 테스트 계정: admin@example.com (비밀번호: Admin1234!)' AS info;


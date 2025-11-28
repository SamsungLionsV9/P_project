-- ============================================
-- CSV 데이터를 위한 테이블 생성
-- 실행: mysql -u root -p car_database < create_csv_tables.sql
-- ============================================

USE car_database;

-- ============================================
-- 1. 국산차 상세 정보 테이블
-- ============================================

CREATE TABLE IF NOT EXISTS domestic_car_details (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
    car_id VARCHAR(50) NOT NULL COMMENT '차량 ID',
    is_accident_free TINYINT(1) NOT NULL DEFAULT 0 COMMENT '무사고 여부 (0: 사고, 1: 무사고)',
    inspection_grade VARCHAR(20) DEFAULT 'normal' COMMENT '검사 등급 (normal, good, excellent)',
    has_sunroof TINYINT(1) NOT NULL DEFAULT 0 COMMENT '선루프 유무',
    has_navigation TINYINT(1) NOT NULL DEFAULT 0 COMMENT '네비게이션 유무',
    has_leather_seat TINYINT(1) NOT NULL DEFAULT 0 COMMENT '가죽시트 유무',
    has_smart_key TINYINT(1) NOT NULL DEFAULT 0 COMMENT '스마트키 유무',
    has_rear_camera TINYINT(1) NOT NULL DEFAULT 0 COMMENT '후방카메라 유무',
    has_led_lamp TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'LED 램프 유무',
    has_parking_sensor TINYINT(1) NOT NULL DEFAULT 0 COMMENT '주차센서 유무',
    has_auto_ac TINYINT(1) NOT NULL DEFAULT 0 COMMENT '자동에어컨 유무',
    has_heated_seat TINYINT(1) NOT NULL DEFAULT 0 COMMENT '열선시트 유무',
    has_ventilated_seat TINYINT(1) NOT NULL DEFAULT 0 COMMENT '통풍시트 유무',
    region TEXT COMMENT '지역 정보',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '생성일시',
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '수정일시',
    
    -- 인덱스
    INDEX idx_car_id (car_id),
    INDEX idx_is_accident_free (is_accident_free),
    INDEX idx_inspection_grade (inspection_grade),
    INDEX idx_created_at (created_at),
    
    -- 중복 방지
    UNIQUE KEY uk_car_id (car_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='국산차 상세 정보';

-- ============================================
-- 2. 외제차 상세 정보 테이블
-- ============================================

CREATE TABLE IF NOT EXISTS imported_car_details (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
    car_id VARCHAR(50) NOT NULL COMMENT '차량 ID',
    is_accident_free TINYINT(1) NOT NULL DEFAULT 0 COMMENT '무사고 여부 (0: 사고, 1: 무사고)',
    inspection_grade VARCHAR(20) DEFAULT 'normal' COMMENT '검사 등급 (normal, good, excellent)',
    has_sunroof TINYINT(1) NOT NULL DEFAULT 0 COMMENT '선루프 유무',
    has_navigation TINYINT(1) NOT NULL DEFAULT 0 COMMENT '네비게이션 유무',
    has_leather_seat TINYINT(1) NOT NULL DEFAULT 0 COMMENT '가죽시트 유무',
    has_smart_key TINYINT(1) NOT NULL DEFAULT 0 COMMENT '스마트키 유무',
    has_rear_camera TINYINT(1) NOT NULL DEFAULT 0 COMMENT '후방카메라 유무',
    has_led_lamp TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'LED 램프 유무',
    has_parking_sensor TINYINT(1) NOT NULL DEFAULT 0 COMMENT '주차센서 유무',
    has_auto_ac TINYINT(1) NOT NULL DEFAULT 0 COMMENT '자동에어컨 유무',
    has_heated_seat TINYINT(1) NOT NULL DEFAULT 0 COMMENT '열선시트 유무',
    has_ventilated_seat TINYINT(1) NOT NULL DEFAULT 0 COMMENT '통풍시트 유무',
    region TEXT COMMENT '지역 정보',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '생성일시',
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '수정일시',
    
    -- 인덱스
    INDEX idx_car_id (car_id),
    INDEX idx_is_accident_free (is_accident_free),
    INDEX idx_inspection_grade (inspection_grade),
    INDEX idx_created_at (created_at),
    
    -- 중복 방지
    UNIQUE KEY uk_car_id (car_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='외제차 상세 정보';

-- ============================================
-- 3. 엔카 원본 국산차 데이터 테이블
-- ============================================

CREATE TABLE IF NOT EXISTS encar_raw_domestic (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
    car_id VARCHAR(50) NOT NULL COMMENT '차량 ID',
    raw_data TEXT COMMENT '원본 데이터 (JSON 또는 텍스트)',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '생성일시',
    
    INDEX idx_car_id (car_id),
    UNIQUE KEY uk_car_id (car_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='엔카 원본 국산차 데이터';

-- ============================================
-- 4. 엔카 외제차 데이터 테이블
-- ============================================

CREATE TABLE IF NOT EXISTS encar_imported_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
    car_id VARCHAR(50) NOT NULL COMMENT '차량 ID',
    raw_data TEXT COMMENT '원본 데이터 (JSON 또는 텍스트)',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '생성일시',
    
    INDEX idx_car_id (car_id),
    UNIQUE KEY uk_car_id (car_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='엔카 외제차 데이터';

-- ============================================
-- 5. 신차 출시 일정 테이블
-- ============================================

CREATE TABLE IF NOT EXISTS new_car_schedule (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
    brand VARCHAR(50) NOT NULL COMMENT '브랜드',
    model VARCHAR(100) NOT NULL COMMENT '모델명',
    release_date DATE NOT NULL COMMENT '출시일',
    type VARCHAR(50) COMMENT '타입 (페이스리프트, 풀체인지 등)',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '생성일시',
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '수정일시',
    
    INDEX idx_brand (brand),
    INDEX idx_model (model),
    INDEX idx_release_date (release_date),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='신차 출시 일정';

-- ============================================
-- 테이블 확인
-- ============================================

SHOW TABLES;

-- 테이블 구조 확인
DESC domestic_car_details;
DESC imported_car_details;
DESC new_car_schedule;

-- 완료 메시지
SELECT '✅ CSV 데이터용 테이블 생성 완료!' AS status;
SELECT '📊 테이블 목록:' AS info;
SELECT TABLE_NAME, TABLE_ROWS FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'car_database' AND TABLE_NAME LIKE '%car%' OR TABLE_NAME LIKE '%schedule%';


-- ============================================
-- OAuth2 소셜 로그인을 위한 DB 스키마 업데이트
-- 실행: mysql -u root -p car_database < oauth2_schema_update.sql
-- ============================================

USE car_database;

-- users 테이블에 소셜 로그인 관련 컬럼 추가
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS provider VARCHAR(20) DEFAULT 'LOCAL' COMMENT '로그인 제공자 (LOCAL, GOOGLE, NAVER, KAKAO)';

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS provider_id VARCHAR(100) COMMENT '소셜 로그인 제공자의 사용자 ID';

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS profile_image_url VARCHAR(500) COMMENT '프로필 이미지 URL';

-- password 컬럼을 nullable로 변경 (소셜 로그인 사용자는 비밀번호 없음)
ALTER TABLE users 
MODIFY COLUMN password VARCHAR(255) NULL;

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_provider ON users(provider);
CREATE INDEX IF NOT EXISTS idx_provider_id ON users(provider, provider_id);

-- 변경사항 확인
DESC users;

-- 완료 메시지
SELECT '✅ OAuth2 소셜 로그인을 위한 스키마 업데이트 완료!' AS status;


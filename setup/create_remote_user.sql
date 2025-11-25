-- ============================================
-- MySQL 외부 접근용 사용자 생성
-- 실행: mysql -u root -p < create_remote_user.sql
-- ============================================

-- 외부 접근용 사용자 생성 (모든 IP 허용)
-- MySQL 8.0+ 기본 인증 방식 사용 (caching_sha2_password)
-- 비밀번호는 반드시 변경하세요!
CREATE USER IF NOT EXISTS 'team_user'@'%' IDENTIFIED BY 'TeamPassword123!@#';

-- 권한 부여
GRANT ALL PRIVILEGES ON car_database.* TO 'team_user'@'%';

-- 특정 IP만 허용하려면 (예시)
-- CREATE USER 'team_user'@'123.456.789.0' IDENTIFIED BY 'TeamPassword123!@#';
-- GRANT ALL PRIVILEGES ON car_database.* TO 'team_user'@'123.456.789.0';

-- 변경사항 적용
FLUSH PRIVILEGES;

-- 사용자 확인
SELECT user, host FROM mysql.user WHERE user = 'team_user';

-- 완료 메시지
SELECT '✅ 외부 접근용 사용자 생성 완료!' AS status;
SELECT '⚠️ 비밀번호를 반드시 변경하세요!' AS warning;
SELECT 'ALTER USER '\''team_user'\''@'\''%'\'' IDENTIFIED BY '\''새로운강력한비밀번호'\'';' AS change_password_command;


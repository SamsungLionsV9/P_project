package com.example.carproject.config;

import com.example.carproject.entity.User;
import com.example.carproject.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * 애플리케이션 시작 시 초기 데이터 생성
 * - 관리자 계정 생성
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    
    // 기본 관리자 계정 정보
    private static final String ADMIN_EMAIL = "admin@carsentix.com";
    private static final String ADMIN_PASSWORD = "admin1234!";
    private static final String ADMIN_USERNAME = "admin";
    
    @Override
    public void run(String... args) {
        createAdminIfNotExists();
    }
    
    /**
     * 관리자 계정이 없으면 생성
     */
    private void createAdminIfNotExists() {
        if (userRepository.findByEmail(ADMIN_EMAIL).isEmpty()) {
            User admin = User.builder()
                    .email(ADMIN_EMAIL)
                    .username(ADMIN_USERNAME)
                    .password(passwordEncoder.encode(ADMIN_PASSWORD))
                    .role(User.Role.ADMIN)
                    .isActive(true)
                    .build();
            
            userRepository.save(admin);
            log.info("✅ 관리자 계정 생성 완료: {}", ADMIN_EMAIL);
            log.info("   비밀번호: {}", ADMIN_PASSWORD);
        } else {
            log.info("ℹ️ 관리자 계정이 이미 존재합니다: {}", ADMIN_EMAIL);
        }
    }
}


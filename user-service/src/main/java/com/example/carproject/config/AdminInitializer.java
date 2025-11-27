package com.example.carproject.config;

import com.example.carproject.entity.User;
import com.example.carproject.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * 애플리케이션 시작 시 기본 관리자 계정 생성
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class AdminInitializer implements CommandLineRunner {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    
    // 기본 관리자 계정 정보
    private static final String ADMIN_EMAIL = "admin@carsentix.com";
    private static final String ADMIN_USERNAME = "admin";
    private static final String ADMIN_PASSWORD = "admin1234!";  // 운영 환경에서는 변경 필요
    
    @Override
    public void run(String... args) {
        // 관리자 계정이 없으면 생성
        if (!userRepository.existsByEmail(ADMIN_EMAIL)) {
            User admin = User.builder()
                    .email(ADMIN_EMAIL)
                    .username(ADMIN_USERNAME)
                    .password(passwordEncoder.encode(ADMIN_PASSWORD))
                    .role(User.Role.ADMIN)
                    .provider(User.Provider.LOCAL)
                    .isActive(true)
                    .build();
            
            userRepository.save(admin);
            
            log.info("======================================");
            log.info("기본 관리자 계정이 생성되었습니다.");
            log.info("이메일: {}", ADMIN_EMAIL);
            log.info("비밀번호: {}", ADMIN_PASSWORD);
            log.info("⚠️ 운영 환경에서는 비밀번호를 변경하세요!");
            log.info("======================================");
        } else {
            log.info("관리자 계정이 이미 존재합니다: {}", ADMIN_EMAIL);
        }
    }
}


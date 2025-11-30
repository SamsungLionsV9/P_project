package com.example.carproject.service;

import com.example.carproject.entity.EmailVerification;
import com.example.carproject.repository.EmailVerificationRepository;
import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class EmailVerificationService {
    
    private final EmailVerificationRepository verificationRepository;
    private final JavaMailSender mailSender;
    
    @Value("${app.mail.verification-code-expiry:300}")
    private int codeExpirySeconds;
    
    private static final SecureRandom random = new SecureRandom();
    
    /**
     * 인증 코드 생성 및 이메일 발송
     */
    @Transactional(rollbackFor = Exception.class)
    public void sendVerificationCode(String email) {
        // 6자리 인증 코드 생성
        String code = generateCode();
        
        // 기존 인증 코드 삭제
        verificationRepository.deleteByEmail(email);
        
        // 새 인증 코드 저장
        EmailVerification verification = EmailVerification.builder()
                .email(email)
                .code(code)
                .expiryTime(LocalDateTime.now().plusSeconds(codeExpirySeconds))
                .verified(false)
                .build();
        verificationRepository.save(verification);
        
        // 개발 환경: 항상 콘솔에 인증 코드 출력
        log.info("========================================");
        log.info("🔐 [인증 코드] {} -> {}", email, code);
        log.info("========================================");
        System.out.println("========================================");
        System.out.println("🔐 [인증 코드] " + email + " -> " + code);
        System.out.println("========================================");
        
        // 이메일 발송 시도
        try {
            sendEmail(email, code);
            log.info("✅ 이메일 발송 성공: {}", email);
        } catch (Exception e) {
            log.warn("⚠️ 이메일 발송 실패 (개발 환경에서는 위 콘솔 코드 사용): {}", e.getMessage());
        }
    }
    
    /**
     * 인증 코드 검증
     */
    @Transactional(rollbackFor = Exception.class)
    public boolean verifyCode(String email, String code) {
        Optional<EmailVerification> verificationOpt = 
            verificationRepository.findByEmailAndCodeAndVerifiedFalse(email, code);
        
        if (verificationOpt.isEmpty()) {
            log.warn("인증 코드 없음 또는 이미 사용됨: {}", email);
            return false;
        }
        
        EmailVerification verification = verificationOpt.get();
        
        if (verification.isExpired()) {
            log.warn("인증 코드 만료됨: {}", email);
            return false;
        }
        
        // 인증 완료 처리
        verification.setVerified(true);
        verificationRepository.save(verification);
        
        log.info("이메일 인증 완료: {}", email);
        return true;
    }
    
    /**
     * 이메일 인증 완료 여부 확인
     */
    @Transactional(readOnly = true)
    public boolean isEmailVerified(String email) {
        Optional<EmailVerification> verificationOpt = 
            verificationRepository.findTopByEmailOrderByCreatedAtDesc(email);
        
        return verificationOpt.map(EmailVerification::isVerified).orElse(false);
    }
    
    /**
     * 6자리 숫자 코드 생성
     */
    private String generateCode() {
        int code = 100000 + random.nextInt(900000);
        return String.valueOf(code);
    }
    
    /**
     * 인증 이메일 발송
     */
    private void sendEmail(String to, String code) throws MessagingException {
        MimeMessage message = mailSender.createMimeMessage();
        MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
        
        helper.setTo(to);
        helper.setSubject("[중고차 시세 예측] 이메일 인증 코드");
        
        String htmlContent = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
            </head>
            <body style="font-family: 'Malgun Gothic', sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #0066FF, #00AAFF); padding: 30px; border-radius: 10px; text-align: center;">
                    <h1 style="color: white; margin: 0;">🚗 중고차 시세 예측</h1>
                </div>
                <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #333;">이메일 인증 코드</h2>
                    <p style="color: #666; font-size: 16px;">아래 인증 코드를 입력해주세요.</p>
                    <div style="background: white; border: 2px solid #0066FF; border-radius: 10px; padding: 20px; text-align: center; margin: 20px 0;">
                        <span style="font-size: 32px; font-weight: bold; color: #0066FF; letter-spacing: 8px;">%s</span>
                    </div>
                    <p style="color: #999; font-size: 14px;">
                        • 인증 코드는 <strong>5분간</strong> 유효합니다.<br>
                        • 본인이 요청하지 않은 경우 이 메일을 무시하세요.
                    </p>
                </div>
                <p style="color: #aaa; font-size: 12px; text-align: center; margin-top: 20px;">
                    © 2025 중고차 시세 예측 AI. All rights reserved.
                </p>
            </body>
            </html>
            """.formatted(code);
        
        helper.setText(htmlContent, true);
        mailSender.send(message);
    }
}

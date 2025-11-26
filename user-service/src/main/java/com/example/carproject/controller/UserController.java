package com.example.carproject.controller;

import com.example.carproject.dto.UserLoginDto;
import com.example.carproject.dto.UserResponseDto;
import com.example.carproject.dto.UserSignupDto;
import com.example.carproject.service.EmailVerificationService;
import com.example.carproject.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class UserController {
    
    private final UserService userService;
    private final EmailVerificationService emailVerificationService;
    
    /**
     * 헬스체크
     * GET /api/health
     */
    @GetMapping("/health")
    public ResponseEntity<?> health() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "healthy");
        response.put("message", "Spring Boot User Management API");
        response.put("version", "1.0.0");
        
        return ResponseEntity.ok(response);
    }
    
    /**
     * 이메일 인증 코드 발송
     * POST /api/auth/email/send-code
     */
    @PostMapping("/email/send-code")
    public ResponseEntity<?> sendVerificationCode(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        
        if (email == null || email.isBlank()) {
            return ResponseEntity.badRequest().body(Map.of(
                "success", false,
                "message", "이메일을 입력해주세요"
            ));
        }
        
        // 이메일 형식 검증
        if (!email.matches("^[A-Za-z0-9+_.-]+@(.+)$")) {
            return ResponseEntity.badRequest().body(Map.of(
                "success", false,
                "message", "올바른 이메일 형식이 아닙니다"
            ));
        }
        
        try {
            emailVerificationService.sendVerificationCode(email);
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "인증 코드가 발송되었습니다. 이메일을 확인해주세요."
            ));
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of(
                "success", false,
                "message", "인증 코드 발송에 실패했습니다: " + e.getMessage()
            ));
        }
    }
    
    /**
     * 이메일 인증 코드 확인
     * POST /api/auth/email/verify-code
     */
    @PostMapping("/email/verify-code")
    public ResponseEntity<?> verifyCode(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String code = request.get("code");
        
        if (email == null || code == null) {
            return ResponseEntity.badRequest().body(Map.of(
                "success", false,
                "message", "이메일과 인증 코드를 입력해주세요"
            ));
        }
        
        boolean verified = emailVerificationService.verifyCode(email, code);
        
        if (verified) {
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "이메일 인증이 완료되었습니다"
            ));
        } else {
            return ResponseEntity.badRequest().body(Map.of(
                "success", false,
                "message", "인증 코드가 올바르지 않거나 만료되었습니다"
            ));
        }
    }
    
    /**
     * 회원가입 (이메일 인증 필수)
     * POST /api/auth/signup
     */
    @PostMapping("/signup")
    public ResponseEntity<?> signup(@Valid @RequestBody UserSignupDto dto) {
        try {
            // 이메일 인증 확인
            if (!emailVerificationService.isEmailVerified(dto.getEmail())) {
                return ResponseEntity.badRequest().body(Map.of(
                    "success", false,
                    "message", "이메일 인증이 필요합니다"
                ));
            }
            
            UserResponseDto user = userService.signup(dto);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "회원가입이 완료되었습니다");
            response.put("user", user);
            
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 로그인
     * POST /api/auth/login
     */
    @PostMapping("/login")
    public ResponseEntity<?> login(@Valid @RequestBody UserLoginDto dto) {
        try {
            String token = userService.login(dto);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "로그인 성공");
            response.put("token", token);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "이메일 또는 비밀번호가 올바르지 않습니다");
            
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 로그아웃 (클라이언트에서 토큰 삭제)
     * POST /api/auth/logout
     */
    @PostMapping("/logout")
    public ResponseEntity<?> logout() {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "로그아웃되었습니다");
        
        return ResponseEntity.ok(response);
    }
    
    /**
     * 회원 정보 조회
     * GET /api/auth/me
     */
    @GetMapping("/me")
    public ResponseEntity<?> getCurrentUser(Authentication authentication) {
        if (authentication == null) {
            return ResponseEntity.status(401).body("인증되지 않은 사용자입니다");
        }
        
        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        UserResponseDto user = userService.getUserInfo(userDetails.getUsername());
        
        return ResponseEntity.ok(user);
    }
    
    /**
     * 회원 탈퇴
     * DELETE /api/auth/me
     */
    @DeleteMapping("/me")
    public ResponseEntity<?> deleteAccount(Authentication authentication) {
        if (authentication == null) {
            return ResponseEntity.status(401).body("인증되지 않은 사용자입니다");
        }
        
        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        userService.deleteUser(userDetails.getUsername());
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "회원 탈퇴가 완료되었습니다");
        
        return ResponseEntity.ok(response);
    }
}


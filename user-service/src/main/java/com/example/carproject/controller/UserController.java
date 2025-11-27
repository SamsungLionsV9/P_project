package com.example.carproject.controller;

import com.example.carproject.dto.OAuthSignupDto;
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
    
    /**k 
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
     * 회원가입
     * POST /api/auth/signup
     */
    @PostMapping("/signup")
    public ResponseEntity<?> signup(@Valid @RequestBody UserSignupDto dto) {
        try {
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
     * OAuth 회원가입 (이메일 인증 불필요)
     * POST /api/auth/oauth/signup
     */
    @PostMapping("/oauth/signup")
    public ResponseEntity<?> oauthSignup(@Valid @RequestBody OAuthSignupDto dto) {
        try {
            UserResponseDto user = userService.oauthSignup(dto);
            
            // JWT 토큰 생성
            String token = userService.generateTokenForUser(user.getEmail());
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "회원가입이 완료되었습니다");
            response.put("user", user);
            response.put("token", token);
            
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
            UserResponseDto user = userService.getUserInfo(dto.getEmail());  // 사용자 정보 조회
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "로그인 성공");
            response.put("token", token);
            response.put("user", user);  // 사용자 정보 추가
            
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
    
    /**
     * 이메일 인증 코드 발송
     * POST /api/auth/email/send-code
     */
    @PostMapping("/email/send-code")
    public ResponseEntity<?> sendVerificationCode(@RequestBody Map<String, String> request) {
        try {
            String email = request.get("email");
            if (email == null || email.isEmpty()) {
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("message", "이메일을 입력해주세요");
                return ResponseEntity.badRequest().body(response);
            }
            
            emailVerificationService.sendVerificationCode(email);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "인증 코드가 발송되었습니다");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "인증 코드 발송 실패: " + e.getMessage());
            
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 이메일 인증 코드 확인
     * POST /api/auth/email/verify-code
     */
    @PostMapping("/email/verify-code")
    public ResponseEntity<?> verifyCode(@RequestBody Map<String, String> request) {
        try {
            String email = request.get("email");
            String code = request.get("code");
            
            if (email == null || email.isEmpty() || code == null || code.isEmpty()) {
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("message", "이메일과 인증 코드를 입력해주세요");
                return ResponseEntity.badRequest().body(response);
            }
            
            boolean verified = emailVerificationService.verifyCode(email, code);
            
            Map<String, Object> response = new HashMap<>();
            if (verified) {
                response.put("success", true);
                response.put("message", "이메일 인증이 완료되었습니다");
            } else {
                response.put("success", false);
                response.put("message", "인증 코드가 올바르지 않거나 만료되었습니다");
            }
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "인증 실패: " + e.getMessage());
            
            return ResponseEntity.badRequest().body(response);
        }
    }
}


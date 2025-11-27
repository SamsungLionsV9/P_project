package com.example.carproject.controller;

import com.example.carproject.dto.UserLoginDto;
import com.example.carproject.dto.UserResponseDto;
import com.example.carproject.entity.User;
import com.example.carproject.service.UserService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
@Slf4j
public class AdminController {
    
    private final UserService userService;
    
    /**
     * 관리자 로그인
     * POST /api/admin/login
     */
    @PostMapping("/login")
    public ResponseEntity<?> adminLogin(@Valid @RequestBody UserLoginDto dto) {
        try {
            // 먼저 일반 로그인 시도
            String token = userService.login(dto);
            
            // 관리자인지 확인
            UserResponseDto user = userService.getUserInfo(dto.getEmail());
            if (!"ADMIN".equals(user.getRole())) {
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("message", "관리자 권한이 없습니다");
                return ResponseEntity.status(403).body(response);
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "관리자 로그인 성공");
            response.put("token", token);
            response.put("user", user);
            
            log.info("관리자 로그인 성공: {}", dto.getEmail());
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("관리자 로그인 실패: {}", e.getMessage());
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "이메일 또는 비밀번호가 올바르지 않습니다");
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 관리자 정보 조회
     * GET /api/admin/me
     */
    @GetMapping("/me")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> getAdminInfo(Authentication authentication) {
        if (authentication == null) {
            return ResponseEntity.status(401).body("인증되지 않은 사용자입니다");
        }
        
        UserResponseDto user = userService.getUserInfo(authentication.getName());
        return ResponseEntity.ok(user);
    }
    
    /**
     * 전체 사용자 목록 조회 (관리자 전용)
     * GET /api/admin/users
     */
    @GetMapping("/users")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> getAllUsers(Authentication authentication) {
        if (authentication == null) {
            return ResponseEntity.status(401).body("인증되지 않은 사용자입니다");
        }
        
        List<UserResponseDto> users = userService.getAllUsers();
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("users", users);
        response.put("total", users.size());
        
        return ResponseEntity.ok(response);
    }
    
    /**
     * 사용자 역할 변경 (관리자 전용)
     * PUT /api/admin/users/{userId}/role
     */
    @PutMapping("/users/{userId}/role")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> updateUserRole(
            @PathVariable Long userId,
            @RequestBody Map<String, String> request,
            Authentication authentication) {
        
        try {
            String newRole = request.get("role");
            if (newRole == null || (!newRole.equals("USER") && !newRole.equals("ADMIN"))) {
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("message", "유효하지 않은 역할입니다 (USER 또는 ADMIN)");
                return ResponseEntity.badRequest().body(response);
            }
            
            userService.updateUserRole(userId, User.Role.valueOf(newRole));
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "사용자 역할이 변경되었습니다");
            
            log.info("사용자 역할 변경: userId={}, newRole={}", userId, newRole);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 사용자 비활성화 (관리자 전용)
     * PUT /api/admin/users/{userId}/deactivate
     */
    @PutMapping("/users/{userId}/deactivate")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> deactivateUser(
            @PathVariable Long userId,
            Authentication authentication) {
        
        try {
            userService.deactivateUser(userId);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "사용자가 비활성화되었습니다");
            
            log.info("사용자 비활성화: userId={}", userId);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 사용자 활성화 (관리자 전용)
     * PUT /api/admin/users/{userId}/activate
     */
    @PutMapping("/users/{userId}/activate")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> activateUser(
            @PathVariable Long userId,
            Authentication authentication) {
        
        try {
            userService.activateUser(userId);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "사용자가 활성화되었습니다");
            
            log.info("사용자 활성화: userId={}", userId);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 대시보드 통계 조회 (관리자 전용)
     * GET /api/admin/dashboard/stats
     */
    @GetMapping("/dashboard/stats")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> getDashboardStats(Authentication authentication) {
        Map<String, Object> stats = userService.getDashboardStats();
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("stats", stats);
        
        return ResponseEntity.ok(response);
    }
}


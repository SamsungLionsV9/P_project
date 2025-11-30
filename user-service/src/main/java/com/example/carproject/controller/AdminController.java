package com.example.carproject.controller;

import com.example.carproject.entity.User;
import com.example.carproject.repository.UserRepository;
import com.example.carproject.service.JwtService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 관리자용 API 컨트롤러
 * admin-dashboard에서 사용하는 사용자 관리 API
 */
@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class AdminController {

    private final UserRepository userRepository;
    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;
    
    /**
     * 관리자 로그인
     * POST /api/admin/login
     */
    @PostMapping("/login")
    public ResponseEntity<?> adminLogin(@RequestBody Map<String, String> credentials) {
        Map<String, Object> response = new HashMap<>();

        String email = credentials.get("email");
        String password = credentials.get("password");

        return userRepository.findByEmail(email)
                .map(user -> {
                    // 비밀번호 확인
                    if (!passwordEncoder.matches(password, user.getPassword())) {
                        response.put("success", false);
                        response.put("message", "이메일 또는 비밀번호가 올바르지 않습니다");
                        return ResponseEntity.badRequest().body(response);
                    }

                    // 관리자 권한 확인
                    if (user.getRole() != User.Role.ADMIN) {
                        response.put("success", false);
                        response.put("message", "관리자 권한이 필요합니다");
                        return ResponseEntity.status(403).body(response);
                    }

                    // 활성 상태 확인
                    if (!user.getIsActive()) {
                        response.put("success", false);
                        response.put("message", "비활성화된 계정입니다");
                        return ResponseEntity.status(403).body(response);
                    }

                    // JWT 토큰 생성
                    String token = jwtService.generateToken(user);

                    response.put("success", true);
                    response.put("message", "로그인 성공");
                    response.put("token", token);
                    response.put("user", convertUserToMap(user));

                    return ResponseEntity.ok(response);
                })
                .orElseGet(() -> {
                    response.put("success", false);
                    response.put("message", "이메일 또는 비밀번호가 올바르지 않습니다");
                    return ResponseEntity.badRequest().body(response);
                });
    }

    /**
     * 현재 관리자 정보 조회
     * GET /api/admin/me
     */
    @GetMapping("/me")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> getCurrentAdmin(Authentication authentication) {
        if (authentication == null) {
            return ResponseEntity.status(401).body(Map.of("error", "인증되지 않은 사용자입니다"));
        }

        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        return userRepository.findByEmail(userDetails.getUsername())
                .map(user -> ResponseEntity.ok(convertUserToMap(user)))
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * 전체 사용자 목록 조회 (공개 - admin-dashboard용)
     * GET /api/admin/users-public
     */
    @GetMapping("/users-public")
    public ResponseEntity<?> getAllUsersPublic() {
        List<User> users = userRepository.findAll();
        
        List<Map<String, Object>> userList = users.stream()
                .map(this::convertUserToMap)
                .collect(Collectors.toList());
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("users", userList);
        response.put("total", userList.size());
        
        return ResponseEntity.ok(response);
    }
    
    /**
     * 전체 사용자 목록 조회
     * GET /api/admin/users
     */
    @GetMapping("/users")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> getAllUsers() {
        List<User> users = userRepository.findAll();
        
        List<Map<String, Object>> userList = users.stream()
                .map(this::convertUserToMap)
                .collect(Collectors.toList());
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("users", userList);
        response.put("total", userList.size());
        
        return ResponseEntity.ok(response);
    }
    
    /**
     * 사용자 정보 수정
     * PUT /api/admin/users/{id}
     */
    @PutMapping("/users/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> updateUser(@PathVariable Long id, @RequestBody Map<String, Object> updates) {
        Map<String, Object> response = new HashMap<>();
        
        return userRepository.findById(id)
                .map(user -> {
                    if (updates.containsKey("username")) {
                        user.setUsername((String) updates.get("username"));
                    }
                    if (updates.containsKey("phoneNumber")) {
                        user.setPhoneNumber((String) updates.get("phoneNumber"));
                    }
                    if (updates.containsKey("role")) {
                        String roleStr = (String) updates.get("role");
                        user.setRole(User.Role.valueOf(roleStr));
                    }
                    
                    userRepository.save(user);
                    
                    response.put("success", true);
                    response.put("message", "사용자 정보가 수정되었습니다");
                    response.put("user", convertUserToMap(user));
                    
                    return ResponseEntity.ok(response);
                })
                .orElseGet(() -> {
                    response.put("success", false);
                    response.put("message", "사용자를 찾을 수 없습니다");
                    return ResponseEntity.badRequest().body(response);
                });
    }
    
    /**
     * 사용자 삭제
     * DELETE /api/admin/users/{id}
     */
    @DeleteMapping("/users/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> deleteUser(@PathVariable Long id) {
        Map<String, Object> response = new HashMap<>();
        
        return userRepository.findById(id)
                .map(user -> {
                    userRepository.delete(user);
                    
                    response.put("success", true);
                    response.put("message", "사용자가 삭제되었습니다");
                    
                    return ResponseEntity.ok(response);
                })
                .orElseGet(() -> {
                    response.put("success", false);
                    response.put("message", "사용자를 찾을 수 없습니다");
                    return ResponseEntity.badRequest().body(response);
                });
    }
    
    /**
     * 사용자 활성화
     * PUT /api/admin/users/{id}/activate
     */
    @PutMapping("/users/{id}/activate")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> activateUser(@PathVariable Long id) {
        return toggleUserActive(id, true);
    }
    
    /**
     * 사용자 비활성화
     * PUT /api/admin/users/{id}/deactivate
     */
    @PutMapping("/users/{id}/deactivate")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> deactivateUser(@PathVariable Long id) {
        return toggleUserActive(id, false);
    }
    
    private ResponseEntity<?> toggleUserActive(Long id, boolean active) {
        Map<String, Object> response = new HashMap<>();
        
        return userRepository.findById(id)
                .map(user -> {
                    user.setIsActive(active);
                    userRepository.save(user);
                    
                    response.put("success", true);
                    response.put("message", active ? "사용자가 활성화되었습니다" : "사용자가 비활성화되었습니다");
                    response.put("user", convertUserToMap(user));
                    
                    return ResponseEntity.ok(response);
                })
                .orElseGet(() -> {
                    response.put("success", false);
                    response.put("message", "사용자를 찾을 수 없습니다");
                    return ResponseEntity.badRequest().body(response);
                });
    }
    
    /**
     * User 엔티티를 Map으로 변환 (비밀번호 제외)
     */
    private Map<String, Object> convertUserToMap(User user) {
        Map<String, Object> map = new HashMap<>();
        map.put("id", user.getId());
        map.put("email", user.getEmail());
        map.put("username", user.getUsername());
        map.put("phoneNumber", user.getPhoneNumber());
        map.put("role", user.getRole().name());
        map.put("provider", user.getProvider().name());
        map.put("isActive", user.getIsActive());
        map.put("createdAt", user.getCreatedAt());
        map.put("updatedAt", user.getUpdatedAt());
        return map;
    }
}


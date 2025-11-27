package com.example.carproject.service;

import com.example.carproject.dto.OAuthSignupDto;
import com.example.carproject.dto.UserLoginDto;
import com.example.carproject.dto.UserResponseDto;
import com.example.carproject.dto.UserSignupDto;
import com.example.carproject.entity.User;
import com.example.carproject.repository.UserRepository;
import org.springframework.context.annotation.Lazy;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class UserService implements UserDetailsService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private final JwtService jwtService;
    private final EmailVerificationService emailVerificationService;
    
    public UserService(UserRepository userRepository,
                      PasswordEncoder passwordEncoder,
                      @Lazy AuthenticationManager authenticationManager,
                      JwtService jwtService,
                      EmailVerificationService emailVerificationService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.authenticationManager = authenticationManager;
        this.jwtService = jwtService;
        this.emailVerificationService = emailVerificationService;
    }
    
    /**
     * 회원가입
     */
    @Transactional
    public UserResponseDto signup(UserSignupDto dto) {
        // 이메일 인증 확인
        if (!emailVerificationService.isEmailVerified(dto.getEmail())) {
            throw new IllegalArgumentException("이메일 인증이 완료되지 않았습니다. 먼저 이메일 인증을 완료해주세요.");
        }
        
        // 기존 사용자 확인 (비활성화된 사용자 포함)
        Optional<User> existingUserByEmail = userRepository.findByEmail(dto.getEmail());
        if (existingUserByEmail.isPresent()) {
            User existingUser = existingUserByEmail.get();
            if (existingUser.getIsActive()) {
                throw new IllegalArgumentException("이미 사용 중인 이메일입니다");
            } else {
                // 비활성화된 사용자가 있으면 삭제
                userRepository.delete(existingUser);
            }
        }
        
        // 사용자명 중복 체크 (활성 사용자만)
        Optional<User> existingUserByUsername = userRepository.findByUsername(dto.getUsername());
        if (existingUserByUsername.isPresent() && existingUserByUsername.get().getIsActive()) {
            throw new IllegalArgumentException("이미 사용 중인 사용자명입니다");
        }
        
        // 사용자 생성
        User user = User.builder()
                .username(dto.getUsername())
                .email(dto.getEmail())
                .password(passwordEncoder.encode(dto.getPassword()))
                .phoneNumber(dto.getPhoneNumber())
                .role(User.Role.USER)
                .isActive(true)
                .build();
        
        User savedUser = userRepository.save(user);
        
        return UserResponseDto.from(savedUser);
    }
    
    /**
     * OAuth 회원가입 (이메일 인증 불필요)
     */
    @Transactional
    public UserResponseDto oauthSignup(OAuthSignupDto dto) {
        // Provider 검증
        User.Provider provider;
        try {
            provider = User.Provider.valueOf(dto.getProvider().toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("지원하지 않는 OAuth 제공자입니다: " + dto.getProvider());
        }
        
        // 기존 사용자 확인 (비활성화된 사용자 포함)
        Optional<User> existingUserByEmail = userRepository.findByEmail(dto.getEmail());
        if (existingUserByEmail.isPresent()) {
            User existingUser = existingUserByEmail.get();
            if (existingUser.getIsActive()) {
                throw new IllegalArgumentException("이미 사용 중인 이메일입니다");
            } else {
                // 비활성화된 사용자가 있으면 삭제
                userRepository.delete(existingUser);
            }
        }
        
        // 사용자명 중복 체크 (활성 사용자만)
        Optional<User> existingUserByUsername = userRepository.findByUsername(dto.getUsername());
        if (existingUserByUsername.isPresent() && existingUserByUsername.get().getIsActive()) {
            throw new IllegalArgumentException("이미 사용 중인 사용자명입니다");
        }
        
        // Provider ID 중복 체크
        Optional<User> existingUserByProviderId = userRepository.findByProviderAndProviderId(provider, dto.getProviderId());
        if (existingUserByProviderId.isPresent() && existingUserByProviderId.get().getIsActive()) {
            throw new IllegalArgumentException("이미 가입된 소셜 계정입니다");
        }
        
        // 사용자 생성 (비밀번호 없음)
        User user = User.builder()
                .username(dto.getUsername())
                .email(dto.getEmail())
                .password(null)  // OAuth 사용자는 비밀번호 없음
                .phoneNumber(dto.getPhoneNumber())
                .provider(provider)
                .providerId(dto.getProviderId())
                .profileImageUrl(dto.getProfileImageUrl())
                .role(User.Role.USER)
                .isActive(true)
                .build();
        
        User savedUser = userRepository.save(user);
        
        return UserResponseDto.from(savedUser);
    }
    
    /**
     * 사용자 이메일로 JWT 토큰 생성 (OAuth 회원가입 후 사용)
     */
    public String generateTokenForUser(String email) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("사용자를 찾을 수 없습니다: " + email));
        return jwtService.generateToken(user);
    }
    
    /**
     * 로그인
     */
    public String login(UserLoginDto dto) {
        // 인증
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(dto.getEmail(), dto.getPassword())
        );
        
        // JWT 토큰 생성
        User user = (User) authentication.getPrincipal();
        return jwtService.generateToken(user);
    }
    
    /**
     * 회원 정보 조회
     */
    @Transactional(readOnly = true)
    public UserResponseDto getUserInfo(String email) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("사용자를 찾을 수 없습니다"));
        
        return UserResponseDto.from(user);
    }
    
    /**
     * 회원 탈퇴
     */
    @Transactional
    public void deleteUser(String email) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("사용자를 찾을 수 없습니다"));
        
        // 소프트 삭제 (isActive = false)
        user.setIsActive(false);
        userRepository.save(user);
        
        // 하드 삭제 (완전 삭제)를 원하면:
        // userRepository.delete(user);
    }
    
    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("사용자를 찾을 수 없습니다: " + email));
    }
    
    // ========== 관리자 전용 메서드 ==========
    
    /**
     * 전체 사용자 목록 조회
     */
    @Transactional(readOnly = true)
    public List<UserResponseDto> getAllUsers() {
        return userRepository.findAll().stream()
                .map(UserResponseDto::from)
                .collect(Collectors.toList());
    }
    
    /**
     * 사용자 역할 변경
     */
    @Transactional
    public void updateUserRole(Long userId, User.Role newRole) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다: " + userId));
        
        user.setRole(newRole);
        userRepository.save(user);
    }
    
    /**
     * 사용자 비활성화
     */
    @Transactional
    public void deactivateUser(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다: " + userId));
        
        user.setIsActive(false);
        userRepository.save(user);
    }
    
    /**
     * 사용자 활성화
     */
    @Transactional
    public void activateUser(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다: " + userId));
        
        user.setIsActive(true);
        userRepository.save(user);
    }
    
    /**
     * 대시보드 통계
     */
    @Transactional(readOnly = true)
    public Map<String, Object> getDashboardStats() {
        Map<String, Object> stats = new HashMap<>();
        
        long totalUsers = userRepository.count();
        long activeUsers = userRepository.countByIsActive(true);
        long adminCount = userRepository.countByRole(User.Role.ADMIN);
        
        stats.put("totalUsers", totalUsers);
        stats.put("activeUsers", activeUsers);
        stats.put("inactiveUsers", totalUsers - activeUsers);
        stats.put("adminCount", adminCount);
        stats.put("userCount", totalUsers - adminCount);
        
        return stats;
    }
}


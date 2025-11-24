package com.example.carproject.service;

import com.example.carproject.dto.UserLoginDto;
import com.example.carproject.dto.UserResponseDto;
import com.example.carproject.dto.UserSignupDto;
import com.example.carproject.entity.User;
import com.example.carproject.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class UserService implements UserDetailsService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private final JwtService jwtService;
    
    /**
     * 회원가입
     */
    @Transactional
    public UserResponseDto signup(UserSignupDto dto) {
        // 중복 체크
        if (userRepository.existsByEmail(dto.getEmail())) {
            throw new IllegalArgumentException("이미 사용 중인 이메일입니다");
        }
        if (userRepository.existsByUsername(dto.getUsername())) {
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
}


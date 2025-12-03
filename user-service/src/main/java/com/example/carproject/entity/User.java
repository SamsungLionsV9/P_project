package com.example.carproject.entity;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.time.LocalDateTime;
import java.util.Collection;
import java.util.Collections;

@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User implements UserDetails {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(unique = true, nullable = false, length = 50)
    private String username;
    
    @Column(unique = true, nullable = false, length = 100)
    private String email;
    
    @Column(nullable = true)  // 소셜 로그인 시 비밀번호 없음
    private String password;
    
    @Column(length = 20)
    private String phoneNumber;
    
    // 소셜 로그인 관련 필드
    @Column(length = 20)
    @Enumerated(EnumType.STRING)
    @Builder.Default
    private Provider provider = Provider.LOCAL;
    
    @Column(length = 100)
    private String providerId;  // 소셜 로그인 제공자의 사용자 ID
    
    @Column(length = 500)
    private String profileImageUrl;  // 프로필 이미지 URL
    
    @Column(length = 100)
    private String displayName;  // 표시 이름 (소셜 로그인 시 사용)
    
    @Column(length = 10)
    @Enumerated(EnumType.STRING)
    @Builder.Default
    private Role role = Role.USER;
    
    @Column(nullable = false)
    @Builder.Default
    private Boolean isActive = true;
    
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @Column(nullable = false)
    private LocalDateTime updatedAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
    
    // UserDetails 구현
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return Collections.singletonList(new SimpleGrantedAuthority("ROLE_" + role.name()));
    }
    
    @Override
    public String getUsername() {
        return email;  // Spring Security용 - 이메일을 username으로 사용
    }
    
    /**
     * 실제 사용자명(닉네임) 반환 - DB의 username 필드
     */
    public String getDisplayName() {
        return username;
    }
    
    /**
     * 사용자명(닉네임) 설정 - DB의 username 필드
     */
    public void setDisplayName(String displayName) {
        this.username = displayName;
    }
    
    @Override
    public boolean isAccountNonExpired() {
        return true;
    }
    
    @Override
    public boolean isAccountNonLocked() {
        return isActive;
    }
    
    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }
    
    @Override
    public boolean isEnabled() {
        return isActive;
    }
    
    public enum Role {
        USER, ADMIN
    }
    
    // 소셜 로그인 제공자
    public enum Provider {
        LOCAL,   // 일반 회원가입
        GOOGLE,  // 구글
        NAVER,   // 네이버
        KAKAO    // 카카오
    }
}


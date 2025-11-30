package com.example.carproject.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * OAuth 소셜 로그인 회원가입 DTO
 * - 네이버, 카카오, 구글 등 OAuth 제공자를 통한 회원가입 시 사용
 * - 비밀번호 불필요 (OAuth 인증으로 대체)
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class OAuthSignupDto {
    
    @NotBlank(message = "사용자명은 필수입니다")
    @Size(min = 1, max = 50, message = "사용자명은 1-50자 사이여야 합니다")
    private String username;
    
    @NotBlank(message = "이메일은 필수입니다")
    @Email(message = "올바른 이메일 형식이 아닙니다")
    private String email;
    
    @NotBlank(message = "OAuth 제공자는 필수입니다")
    private String provider;  // NAVER, KAKAO, GOOGLE
    
    @NotBlank(message = "OAuth 제공자 ID는 필수입니다")
    private String providerId;  // OAuth 제공자가 부여한 사용자 고유 ID
    
    @Pattern(regexp = "^$|^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$", message = "올바른 전화번호 형식이 아닙니다")
    private String phoneNumber;
    
    private String profileImageUrl;  // 프로필 이미지 URL (선택)
}

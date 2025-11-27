package com.example.carproject.oauth2;

import java.util.Map;

/**
 * Kakao OAuth2 사용자 정보
 */
@SuppressWarnings("unchecked")
public class KakaoOAuth2UserInfo extends OAuth2UserInfo {
    
    public KakaoOAuth2UserInfo(Map<String, Object> attributes) {
        super(attributes);
    }
    
    @Override
    public String getId() {
        return String.valueOf(attributes.get("id"));
    }
    
    @Override
    public String getName() {
        Map<String, Object> properties = getMapAttribute("properties");
        if (properties == null) {
            Map<String, Object> kakaoAccount = getMapAttribute("kakao_account");
            if (kakaoAccount != null) {
                Map<String, Object> profile = (Map<String, Object>) kakaoAccount.get("profile");
                if (profile != null) {
                    return (String) profile.get("nickname");
                }
            }
            return null;
        }
        return (String) properties.get("nickname");
    }
    
    @Override
    public String getEmail() {
        Map<String, Object> kakaoAccount = getMapAttribute("kakao_account");
        if (kakaoAccount != null) {
            String email = (String) kakaoAccount.get("email");
            if (email != null && !email.isEmpty()) {
                return email;
            }
        }
        // 이메일이 없는 경우 카카오 ID 기반 임시 이메일 생성
        // 카카오 비즈 앱이 아니면 이메일을 받지 못할 수 있음
        String kakaoId = getId();
        if (kakaoId != null) {
            return "kakao_" + kakaoId + "@kakao.user";
        }
        return null;
    }
    
    @Override
    public String getImageUrl() {
        Map<String, Object> properties = getMapAttribute("properties");
        if (properties == null) {
            Map<String, Object> kakaoAccount = getMapAttribute("kakao_account");
            if (kakaoAccount != null) {
                Map<String, Object> profile = (Map<String, Object>) kakaoAccount.get("profile");
                if (profile != null) {
                    return (String) profile.get("profile_image_url");
                }
            }
            return null;
        }
        return (String) properties.get("profile_image");
    }
    
    private Map<String, Object> getMapAttribute(String key) {
        return (Map<String, Object>) attributes.get(key);
    }
}


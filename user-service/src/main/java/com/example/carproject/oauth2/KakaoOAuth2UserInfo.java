package com.example.carproject.oauth2;

import java.util.Map;

/**
 * Kakao OAuth2 사용자 정보
 */
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
        Map<String, Object> properties = (Map<String, Object>) attributes.get("properties");
        if (properties == null) {
            Map<String, Object> kakaoAccount = (Map<String, Object>) attributes.get("kakao_account");
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
        Map<String, Object> kakaoAccount = (Map<String, Object>) attributes.get("kakao_account");
        if (kakaoAccount == null) {
            return null;
        }
        return (String) kakaoAccount.get("email");
    }
    
    @Override
    public String getImageUrl() {
        Map<String, Object> properties = (Map<String, Object>) attributes.get("properties");
        if (properties == null) {
            Map<String, Object> kakaoAccount = (Map<String, Object>) attributes.get("kakao_account");
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
}


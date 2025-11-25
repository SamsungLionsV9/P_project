package com.example.carproject.oauth2;

import com.example.carproject.entity.User;

import java.util.Map;

/**
 * OAuth2 사용자 정보 팩토리
 * 제공자에 따라 적절한 OAuth2UserInfo 객체 생성
 */
public class OAuth2UserInfoFactory {
    
    public static OAuth2UserInfo getOAuth2UserInfo(String registrationId, Map<String, Object> attributes) {
        if (registrationId.equalsIgnoreCase(User.Provider.GOOGLE.name())) {
            return new GoogleOAuth2UserInfo(attributes);
        } else if (registrationId.equalsIgnoreCase(User.Provider.NAVER.name())) {
            return new NaverOAuth2UserInfo(attributes);
        } else if (registrationId.equalsIgnoreCase(User.Provider.KAKAO.name())) {
            return new KakaoOAuth2UserInfo(attributes);
        } else {
            throw new IllegalArgumentException("지원하지 않는 소셜 로그인입니다: " + registrationId);
        }
    }
}


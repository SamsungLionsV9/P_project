package com.example.carproject.oauth2;

import java.util.Map;

/**
 * OAuth2 사용자 정보 추상 클래스
 * 각 소셜 로그인 제공자별로 구현
 */
public abstract class OAuth2UserInfo {
    
    protected Map<String, Object> attributes;
    
    public OAuth2UserInfo(Map<String, Object> attributes) {
        this.attributes = attributes;
    }
    
    public Map<String, Object> getAttributes() {
        return attributes;
    }
    
    public abstract String getId();
    
    public abstract String getName();
    
    public abstract String getEmail();
    
    public abstract String getImageUrl();
}


package com.example.carproject.oauth2;

import java.util.Map;

/**
 * Naver OAuth2 사용자 정보
 */
@SuppressWarnings("unchecked")
public class NaverOAuth2UserInfo extends OAuth2UserInfo {
    
    private final Map<String, Object> response;
    
    public NaverOAuth2UserInfo(Map<String, Object> attributes) {
        super(attributes);
        this.response = (Map<String, Object>) attributes.get("response");
    }
    
    @Override
    public String getId() {
        if (response == null) {
            return null;
        }
        return (String) response.get("id");
    }
    
    @Override
    public String getName() {
        if (response == null) {
            return null;
        }
        return (String) response.get("name");
    }
    
    @Override
    public String getEmail() {
        if (response == null) {
            return null;
        }
        return (String) response.get("email");
    }
    
    @Override
    public String getImageUrl() {
        if (response == null) {
            return null;
        }
        return (String) response.get("profile_image");
    }
}


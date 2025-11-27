package com.example.carproject.oauth2;

import com.example.carproject.entity.User;
import lombok.Getter;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.oauth2.core.user.OAuth2User;

import java.util.Collection;
import java.util.Map;

/**
 * 커스텀 OAuth2 사용자
 * Spring Security의 OAuth2User를 구현하고 User 엔티티 정보를 포함
 */
@Getter
public class CustomOAuth2User implements OAuth2User {
    
    private final User user;
    private final Map<String, Object> attributes;
    private final String nameAttributeKey;
    private final boolean isNewUser;  // 신규 사용자 여부
    
    public CustomOAuth2User(User user, Map<String, Object> attributes, String nameAttributeKey) {
        this(user, attributes, nameAttributeKey, false);
    }
    
    public CustomOAuth2User(User user, Map<String, Object> attributes, String nameAttributeKey, boolean isNewUser) {
        this.user = user;
        this.attributes = attributes;
        this.nameAttributeKey = nameAttributeKey;
        this.isNewUser = isNewUser;
    }
    
    @Override
    public Map<String, Object> getAttributes() {
        return attributes;
    }
    
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return user.getAuthorities();
    }
    
    @Override
    public String getName() {
        return user.getEmail();
    }
    
    public Long getId() {
        return user.getId();
    }
    
    public String getEmail() {
        return user.getEmail();
    }
    
    public User.Role getRole() {
        return user.getRole();
    }
}


package com.example.carproject.oauth2;

import com.example.carproject.entity.User;
import com.example.carproject.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

/**
 * 커스텀 OAuth2 사용자 서비스
 * 소셜 로그인 후 사용자 정보를 처리
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CustomOAuth2UserService extends DefaultOAuth2UserService {
    
    private final UserRepository userRepository;
    
    @Override
    @Transactional
    public OAuth2User loadUser(OAuth2UserRequest userRequest) throws OAuth2AuthenticationException {
        OAuth2User oAuth2User = super.loadUser(userRequest);
        
        return processOAuth2User(userRequest, oAuth2User);
    }
    
    private OAuth2User processOAuth2User(OAuth2UserRequest userRequest, OAuth2User oAuth2User) {
        String registrationId = userRequest.getClientRegistration().getRegistrationId();
        String userNameAttributeName = userRequest.getClientRegistration()
                .getProviderDetails()
                .getUserInfoEndpoint()
                .getUserNameAttributeName();
        
        // OAuth2UserInfo 객체 생성
        OAuth2UserInfo oAuth2UserInfo = OAuth2UserInfoFactory.getOAuth2UserInfo(
                registrationId, 
                oAuth2User.getAttributes()
        );
        
        // 이메일 확인
        String email = oAuth2UserInfo.getEmail();
        if (email == null || email.isEmpty()) {
            log.error("소셜 로그인 이메일을 가져올 수 없습니다. Provider: {}", registrationId);
            throw new OAuth2AuthenticationException("소셜 계정에서 이메일 정보를 가져올 수 없습니다.");
        }
        
        // Provider 결정
        User.Provider provider = User.Provider.valueOf(registrationId.toUpperCase());
        
        // 기존 사용자 확인 또는 새 사용자 생성
        Optional<User> userOptional = userRepository.findByEmail(email);
        User user;
        
        if (userOptional.isPresent()) {
            user = userOptional.get();
            // 기존 LOCAL 사용자가 소셜 로그인 시도하는 경우
            if (user.getProvider() == User.Provider.LOCAL) {
                log.info("기존 로컬 사용자가 소셜 로그인으로 연동: {}", email);
                user.setProvider(provider);
                user.setProviderId(oAuth2UserInfo.getId());
                if (oAuth2UserInfo.getImageUrl() != null) {
                    user.setProfileImageUrl(oAuth2UserInfo.getImageUrl());
                }
            }
            // 다른 소셜 제공자로 로그인 시도하는 경우
            else if (user.getProvider() != provider) {
                log.warn("이미 {} 계정으로 가입된 이메일입니다: {}", user.getProvider(), email);
                throw new OAuth2AuthenticationException(
                        "이미 " + user.getProvider() + " 계정으로 가입된 이메일입니다."
                );
            }
            // 동일 제공자로 로그인하는 경우 - 정보 업데이트
            else {
                user = updateExistingUser(user, oAuth2UserInfo);
            }
        } else {
            // 새 사용자 생성
            user = registerNewUser(provider, oAuth2UserInfo);
        }
        
        return new CustomOAuth2User(user, oAuth2User.getAttributes(), userNameAttributeName);
    }
    
    /**
     * 새 소셜 로그인 사용자 등록
     */
    private User registerNewUser(User.Provider provider, OAuth2UserInfo oAuth2UserInfo) {
        log.info("새 소셜 로그인 사용자 등록: {} ({})", oAuth2UserInfo.getEmail(), provider);
        
        User user = User.builder()
                .username(generateUsername(oAuth2UserInfo.getName(), provider))
                .email(oAuth2UserInfo.getEmail())
                .provider(provider)
                .providerId(oAuth2UserInfo.getId())
                .profileImageUrl(oAuth2UserInfo.getImageUrl())
                .role(User.Role.USER)
                .isActive(true)
                .build();
        
        return userRepository.save(user);
    }
    
    /**
     * 기존 사용자 정보 업데이트
     */
    private User updateExistingUser(User user, OAuth2UserInfo oAuth2UserInfo) {
        log.info("소셜 로그인 사용자 정보 업데이트: {}", user.getEmail());
        
        if (oAuth2UserInfo.getImageUrl() != null) {
            user.setProfileImageUrl(oAuth2UserInfo.getImageUrl());
        }
        
        return userRepository.save(user);
    }
    
    /**
     * 사용자명 생성 (중복 방지)
     */
    private String generateUsername(String name, User.Provider provider) {
        String baseName = name != null ? name : provider.name().toLowerCase() + "_user";
        String username = baseName;
        int suffix = 1;
        
        while (userRepository.existsByUsername(username)) {
            username = baseName + "_" + suffix++;
        }
        
        return username;
    }
}


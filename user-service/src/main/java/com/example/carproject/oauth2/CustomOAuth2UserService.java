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
        try {
            OAuth2User oAuth2User = super.loadUser(userRequest);
            return processOAuth2User(userRequest, oAuth2User);
        } catch (OAuth2AuthenticationException e) {
            log.error("OAuth2 인증 예외: {}", e.getMessage(), e);
            throw e;
        } catch (Exception e) {
            log.error("OAuth2 사용자 로드 중 예외 발생: {}", e.getMessage(), e);
            throw new OAuth2AuthenticationException("소셜 로그인 처리 중 오류가 발생했습니다: " + e.getMessage());
        }
    }

    private OAuth2User processOAuth2User(OAuth2UserRequest userRequest, OAuth2User oAuth2User) {
        try {
            String registrationId = userRequest.getClientRegistration().getRegistrationId();
            String userNameAttributeName = userRequest.getClientRegistration()
                    .getProviderDetails()
                    .getUserInfoEndpoint()
                    .getUserNameAttributeName();

            log.debug("OAuth2 사용자 처리 시작: Provider={}", registrationId);

            // OAuth2UserInfo 객체 생성
            OAuth2UserInfo oAuth2UserInfo;
            try {
                oAuth2UserInfo = OAuth2UserInfoFactory.getOAuth2UserInfo(
                        registrationId,
                        oAuth2User.getAttributes());
            } catch (IllegalArgumentException e) {
                log.error("지원하지 않는 OAuth 제공자: {}", registrationId);
                throw new OAuth2AuthenticationException("지원하지 않는 소셜 로그인입니다: " + registrationId);
            }

            // 이메일 확인
            String email = oAuth2UserInfo.getEmail();
            if (email == null || email.isEmpty()) {
                log.error("소셜 로그인 이메일을 가져올 수 없습니다. Provider: {}", registrationId);
                throw new OAuth2AuthenticationException("소셜 계정에서 이메일 정보를 가져올 수 없습니다.");
            }

            // Provider 결정
            User.Provider provider;
            try {
                provider = User.Provider.valueOf(registrationId.toUpperCase());
            } catch (IllegalArgumentException e) {
                log.error("잘못된 Provider: {}", registrationId);
                throw new OAuth2AuthenticationException("지원하지 않는 소셜 로그인 제공자입니다: " + registrationId);
            }

            // 기존 사용자 확인 (활성 사용자만)
            Optional<User> userOptional = userRepository.findByEmail(email);
            User user;
            boolean isNewUser = false;

            if (userOptional.isPresent()) {
                user = userOptional.get();

                // 비활성화된 사용자는 신규 사용자로 처리
                if (!user.getIsActive()) {
                    log.info("비활성화된 사용자 감지, 신규 사용자로 처리: {}", email);
                    isNewUser = true;
                    user = createTemporaryUser(provider, oAuth2UserInfo);
                }
                // 기존 LOCAL 사용자가 소셜 로그인 시도하는 경우
                else if (user.getProvider() == User.Provider.LOCAL) {
                    log.info("기존 로컬 사용자가 소셜 로그인으로 연동: {}", email);
                    user.setProvider(provider);
                    user.setProviderId(oAuth2UserInfo.getId());
                    if (oAuth2UserInfo.getImageUrl() != null) {
                        user.setProfileImageUrl(oAuth2UserInfo.getImageUrl());
                    }
                    userRepository.save(user);
                }
                // 다른 소셜 제공자로 로그인 시도하는 경우
                else if (user.getProvider() != provider) {
                    log.warn("이미 {} 계정으로 가입된 이메일입니다: {}", user.getProvider(), email);
                    throw new OAuth2AuthenticationException(
                            "이미 " + user.getProvider() + " 계정으로 가입된 이메일입니다.");
                }
                // 동일 제공자로 로그인하는 경우 - 정보 업데이트
                else {
                    user = updateExistingUser(user, oAuth2UserInfo);
                }
            } else {
                // 새 사용자 - 임시 사용자 객체 생성 (DB에 저장하지 않음)
                // 회원가입 페이지에서 추가 정보를 입력받아 저장
                isNewUser = true;
                user = createTemporaryUser(provider, oAuth2UserInfo);
                log.info("신규 OAuth 사용자 감지: {} ({}), 회원가입 페이지로 이동", email, provider);
            }

            return new CustomOAuth2User(user, oAuth2User.getAttributes(), userNameAttributeName, isNewUser);

        } catch (OAuth2AuthenticationException e) {
            log.error("OAuth2 인증 처리 중 예외: {}", e.getMessage(), e);
            throw e;
        } catch (Exception e) {
            log.error("OAuth2 사용자 처리 중 예외 발생: {}", e.getMessage(), e);
            throw new OAuth2AuthenticationException("소셜 로그인 처리 중 오류가 발생했습니다: " + e.getMessage());
        }
    }

    /**
     * 임시 사용자 객체 생성 (DB에 저장하지 않음)
     * 회원가입 페이지에서 추가 정보를 입력받아 저장
     */
    private User createTemporaryUser(User.Provider provider, OAuth2UserInfo oAuth2UserInfo) {
        return User.builder()
                .username(generateUsername(oAuth2UserInfo.getName(), provider))
                .email(oAuth2UserInfo.getEmail())
                .provider(provider)
                .providerId(oAuth2UserInfo.getId())
                .profileImageUrl(oAuth2UserInfo.getImageUrl())
                .role(User.Role.USER)
                .isActive(false) // 임시 사용자는 비활성화
                .build();
    }

    /**
     * 새 소셜 로그인 사용자 등록 (회원가입 완료 시 호출)
     */
    public User registerNewUser(User.Provider provider, OAuth2UserInfo oAuth2UserInfo, String username) {
        log.info("새 소셜 로그인 사용자 등록: {} ({})", oAuth2UserInfo.getEmail(), provider);

        User user = User.builder()
                .username(username != null ? username : generateUsername(oAuth2UserInfo.getName(), provider))
                .email(oAuth2UserInfo.getEmail())
                .provider(provider)
                .providerId(oAuth2UserInfo.getId())
                .profileImageUrl(oAuth2UserInfo.getImageUrl())
                .role(User.Role.USER)
                .isActive(true)
                .build();

        return userRepository.save(java.util.Objects.requireNonNull(user));
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

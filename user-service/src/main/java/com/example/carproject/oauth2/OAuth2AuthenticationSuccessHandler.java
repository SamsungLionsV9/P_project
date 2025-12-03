package com.example.carproject.oauth2;

import com.example.carproject.entity.User;
import com.example.carproject.service.JwtService;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationSuccessHandler;
import org.springframework.stereotype.Component;
import org.springframework.web.util.UriComponentsBuilder;

import java.io.IOException;

/**
 * OAuth2 인증 성공 핸들러
 * - 기존 사용자: JWT 토큰 발급 후 바로 로그인
 * - 신규 사용자: 회원가입 페이지로 리다이렉트
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class OAuth2AuthenticationSuccessHandler extends SimpleUrlAuthenticationSuccessHandler {
    
    private final JwtService jwtService;
    
    @Value("${app.oauth2.redirect-uri:http://localhost:3000/oauth2/redirect}")
    private String redirectUri;
    
    @Override
    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response,
                                        Authentication authentication) throws IOException, ServletException {
        try {
            CustomOAuth2User oAuth2User = (CustomOAuth2User) authentication.getPrincipal();
            User user = oAuth2User.getUser();
            
            log.info("OAuth2 로그인 성공: {} ({})", user.getEmail(), user.getProvider());
            
            // 리다이렉트 URI 결정 (쿼리 파라미터 > Referer > 기본값)
            String targetRedirectUri = determineRedirectUri(request);
            
            // null 체크 및 기본값 설정
            if (targetRedirectUri == null || targetRedirectUri.isEmpty()) {
                targetRedirectUri = redirectUri;
                log.warn("리다이렉트 URI가 null이거나 빈 문자열입니다. 기본값 사용: {}", targetRedirectUri);
            }
            
            // 사용자 정보 null 체크
            String userEmail = user.getEmail();
            if (userEmail == null || userEmail.isEmpty()) {
                log.error("사용자 이메일이 null이거나 빈 문자열입니다.");
                redirectToError(request, response, targetRedirectUri, "사용자 이메일 정보를 가져올 수 없습니다.");
                return;
            }
            
            User.Provider userProvider = user.getProvider();
            if (userProvider == null) {
                log.error("사용자 Provider가 null입니다.");
                redirectToError(request, response, targetRedirectUri, "사용자 Provider 정보를 가져올 수 없습니다.");
                return;
            }
            
            // 리다이렉트 URI에서 /oauth2/redirect 제거
            String baseUri = targetRedirectUri;
            if (baseUri != null && baseUri.endsWith("/oauth2/redirect")) {
                baseUri = baseUri.substring(0, baseUri.length() - "/oauth2/redirect".length());
            }
            
            // null 체크
            if (baseUri == null || baseUri.isEmpty()) {
                log.error("baseUri가 null이거나 빈 문자열입니다.");
                redirectToError(request, response, targetRedirectUri, "리다이렉트 URI를 생성할 수 없습니다.");
                return;
            }
            
            // ★★★ 핵심 변경: 기존 사용자는 바로 로그인, 신규 사용자는 회원가입 페이지로 ★★★
            if (!oAuth2User.isNewUser()) {
                // 기존 사용자: JWT 토큰 발급 후 바로 로그인
                log.info("기존 OAuth 사용자 로그인: {} ({})", userEmail, userProvider);
                
                String jwtToken = jwtService.generateToken(user);
                
                UriComponentsBuilder builder = UriComponentsBuilder.fromUriString(baseUri)
                        .path("/oauth2/redirect")
                        .queryParam("token", jwtToken)
                        .queryParam("email", userEmail)
                        .queryParam("provider", userProvider.name());
                
                String redirectUrl = builder.build().toUriString();
                log.info("OAuth2 로그인 리다이렉트 (기존 사용자): {}", redirectUrl);
                getRedirectStrategy().sendRedirect(request, response, redirectUrl);
            } else {
                // 신규 사용자: 회원가입 페이지로 리다이렉트
                log.info("신규 OAuth 사용자 회원가입 페이지로 리다이렉트: {} ({})", userEmail, userProvider);
                
                UriComponentsBuilder builder = UriComponentsBuilder.fromUriString(baseUri)
                        .path("/signup")
                        .queryParam("oauth", "true")
                        .queryParam("provider", userProvider.name())
                        .queryParam("email", userEmail);
                
                String providerId = user.getProviderId();
                if (providerId != null && !providerId.isEmpty()) {
                    builder.queryParam("providerId", providerId);
                }
                
                String imageUrl = user.getProfileImageUrl();
                if (imageUrl != null && !imageUrl.isEmpty()) {
                    builder.queryParam("imageUrl", imageUrl);
                }
                
                String signupUrl = builder.build().toUriString();
                log.info("OAuth2 회원가입 리다이렉트 (신규 사용자): {}", signupUrl);
                getRedirectStrategy().sendRedirect(request, response, signupUrl);
            }
            
        } catch (Exception e) {
            log.error("OAuth2 인증 성공 처리 중 오류 발생: {}", e.getMessage(), e);
            String targetRedirectUri = determineRedirectUri(request);
            if (targetRedirectUri == null || targetRedirectUri.isEmpty()) {
                targetRedirectUri = redirectUri;
            }
            redirectToError(request, response, targetRedirectUri, "OAuth2 인증 처리 중 오류가 발생했습니다: " + e.getMessage());
        }
    }
    
    /**
     * 에러 페이지로 리다이렉트
     */
    private void redirectToError(HttpServletRequest request, HttpServletResponse response, 
                                 String targetRedirectUri, String errorMessage) throws IOException {
        try {
            String baseUri = targetRedirectUri;
            if (baseUri != null && baseUri.endsWith("/oauth2/redirect")) {
                baseUri = baseUri.substring(0, baseUri.length() - "/oauth2/redirect".length());
            }
            
            if (baseUri == null || baseUri.isEmpty()) {
                baseUri = "http://localhost:3000";
            }
            
            String errorUrl = UriComponentsBuilder.fromUriString(baseUri)
                    .path("/oauth2/redirect")
                    .queryParam("error", java.net.URLEncoder.encode(errorMessage, java.nio.charset.StandardCharsets.UTF_8))
                .build().toUriString();
        
            log.info("OAuth2 에러 리다이렉트: {}", errorUrl);
            getRedirectStrategy().sendRedirect(request, response, errorUrl);
        } catch (Exception e) {
            log.error("에러 리다이렉트 실패: {}", e.getMessage(), e);
            response.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR, errorMessage);
        }
    }
    
    /**
     * 리다이렉트 URI 결정
     * 1. 세션에서 저장된 redirect_uri 확인
     * 2. 쿼리 파라미터의 redirect_uri 확인
     * 3. Referer 헤더에서 origin 추출
     * 4. 기본값 사용
     */
    private String determineRedirectUri(HttpServletRequest request) {
        // 1. 세션에서 저장된 redirect_uri 확인 (OAuth 시작 시 저장됨)
        String sessionRedirectUri = (String) request.getSession().getAttribute("oauth2_redirect_uri");
        if (sessionRedirectUri != null && !sessionRedirectUri.isEmpty()) {
            log.debug("리다이렉트 URI (세션): {}", sessionRedirectUri);
            request.getSession().removeAttribute("oauth2_redirect_uri"); // 사용 후 제거
            return sessionRedirectUri;
        }
        
        // 2. 쿼리 파라미터 확인
        String redirectUriParam = request.getParameter("redirect_uri");
        if (redirectUriParam != null && !redirectUriParam.isEmpty()) {
            log.debug("리다이렉트 URI (쿼리 파라미터): {}", redirectUriParam);
            if (!redirectUriParam.endsWith("/oauth2/redirect")) {
                return redirectUriParam + "/oauth2/redirect";
            }
            return redirectUriParam;
        }
        
        // 3. Referer 헤더 확인
        String referer = request.getHeader("Referer");
        if (referer != null && !referer.isEmpty()) {
            try {
                java.net.URI refererUri = java.net.URI.create(referer);
                String origin = refererUri.getScheme() + "://" + refererUri.getAuthority();
                log.debug("리다이렉트 URI (Referer): {}", origin + "/oauth2/redirect");
                return origin + "/oauth2/redirect";
            } catch (Exception e) {
                log.warn("Referer 파싱 실패: {}", referer, e);
            }
        }
        
        // 4. 기본값 사용
        log.debug("리다이렉트 URI (기본값): {}", redirectUri);
        return redirectUri;
    }
}


package com.example.carproject.oauth2;

import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationFailureHandler;
import org.springframework.stereotype.Component;
import org.springframework.web.util.UriComponentsBuilder;

import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

/**
 * OAuth2 인증 실패 핸들러
 * 소셜 로그인 실패 시 에러 처리
 */
@Slf4j
@Component
public class OAuth2AuthenticationFailureHandler extends SimpleUrlAuthenticationFailureHandler {

    @Value("${app.oauth2.redirect-uri:http://localhost:3000/oauth2/redirect}")
    private String redirectUri;

    @Override
    public void onAuthenticationFailure(HttpServletRequest request, HttpServletResponse response,
            AuthenticationException exception) throws IOException, ServletException {

        log.error("OAuth2 로그인 실패: {}", exception.getMessage());

        // 리다이렉트 URI 결정 (Referer 확인)
        String targetRedirectUri = determineRedirectUri(request);

        String targetUrl = UriComponentsBuilder.fromUriString(java.util.Objects.requireNonNull(targetRedirectUri))
                .queryParam("error", URLEncoder.encode(exception.getMessage(), StandardCharsets.UTF_8))
                .build().toUriString();

        log.info("OAuth2 실패 리다이렉트: {}", targetUrl);
        getRedirectStrategy().sendRedirect(request, response, targetUrl);
    }

    /**
     * 리다이렉트 URI 결정
     * 1. Referer 헤더에서 origin 추출
     * 2. 기본값 사용
     */
    private String determineRedirectUri(HttpServletRequest request) {
        // Referer 헤더 확인
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

        // 기본값 사용
        log.debug("리다이렉트 URI (기본값): {}", redirectUri);
        return redirectUri;
    }
}

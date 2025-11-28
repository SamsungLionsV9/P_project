package com.example.carproject.oauth2;

import jakarta.servlet.Filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

import java.io.IOException;

/**
 * OAuth2 리다이렉트 URI 저장 필터
 * OAuth 로그인 시작 시 Referer에서 리다이렉트 URI를 추출하여 세션에 저장
 */
@Slf4j
@Component
@Order(1)
public class OAuth2RedirectUriFilter implements Filter {
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        
        String requestURI = httpRequest.getRequestURI();
        
        // OAuth2 인증 시작 요청인지 확인
        if (requestURI != null && requestURI.startsWith("/oauth2/authorization/")) {
            // Referer 헤더에서 origin 추출
            String referer = httpRequest.getHeader("Referer");
            if (referer != null && !referer.isEmpty()) {
                try {
                    java.net.URI refererUri = java.net.URI.create(referer);
                    String origin = refererUri.getScheme() + "://" + refererUri.getAuthority();
                    String redirectUri = origin + "/oauth2/redirect";
                    
                    // 세션에 리다이렉트 URI 저장
                    httpRequest.getSession().setAttribute("oauth2_redirect_uri", redirectUri);
                    log.info("OAuth2 리다이렉트 URI 저장: {} (Referer: {})", redirectUri, referer);
                } catch (Exception e) {
                    log.warn("Referer 파싱 실패: {}", referer, e);
                }
            }
            
            // 쿼리 파라미터에서 redirect_uri 확인
            String redirectUriParam = httpRequest.getParameter("redirect_uri");
            if (redirectUriParam != null && !redirectUriParam.isEmpty()) {
                String redirectUri = redirectUriParam;
                if (!redirectUri.endsWith("/oauth2/redirect")) {
                    redirectUri = redirectUri + "/oauth2/redirect";
                }
                httpRequest.getSession().setAttribute("oauth2_redirect_uri", redirectUri);
                log.info("OAuth2 리다이렉트 URI 저장 (쿼리 파라미터): {}", redirectUri);
            }
        }
        
        chain.doFilter(request, response);
    }
}


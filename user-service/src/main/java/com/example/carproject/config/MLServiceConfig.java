package com.example.carproject.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

/**
 * ML Service 연동 설정
 */
@Configuration
public class MLServiceConfig {
    
    @Value("${ml.service.url:http://localhost:8000}")
    private String mlServiceUrl;
    
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
    
    public String getMlServiceUrl() {
        return mlServiceUrl;
    }
}

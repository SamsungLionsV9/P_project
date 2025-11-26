package com.example.carproject.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

/**
 * ML Service API Gateway
 * Flutter → Spring Boot → Python ML Service
 */
@Slf4j
@RestController
@RequestMapping("/api/ml")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class MLGatewayController {
    
    private final RestTemplate restTemplate;
    
    @Value("${ml.service.url:http://localhost:8000}")
    private String mlServiceUrl;
    
    /**
     * 가격 예측 (Gateway)
     * POST /api/ml/predict
     */
    @PostMapping("/predict")
    public ResponseEntity<?> predict(@RequestBody Map<String, Object> request) {
        log.info("🚗 가격 예측 요청: {}", request.get("model"));
        
        try {
            String url = mlServiceUrl + "/api/predict";
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);
            ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
            
            log.info("✅ 예측 완료: {}만원", response.getBody().get("predicted_price"));
            return ResponseEntity.ok(response.getBody());
            
        } catch (Exception e) {
            log.error("❌ ML 서비스 호출 실패: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of(
                        "error", "ML 서비스 연결 실패",
                        "message", e.getMessage()
                    ));
        }
    }
    
    /**
     * 타이밍 분석 (Gateway)
     * POST /api/ml/timing
     */
    @PostMapping("/timing")
    public ResponseEntity<?> timing(@RequestBody Map<String, Object> request) {
        log.info("⏱️ 타이밍 분석 요청: {}", request.get("model"));
        
        try {
            String url = mlServiceUrl + "/api/timing";
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);
            ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
            
            return ResponseEntity.ok(response.getBody());
            
        } catch (Exception e) {
            log.error("❌ 타이밍 분석 실패: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "ML 서비스 연결 실패"));
        }
    }
    
    /**
     * 통합 스마트 분석 (Gateway)
     * POST /api/ml/smart-analysis
     */
    @PostMapping("/smart-analysis")
    public ResponseEntity<?> smartAnalysis(@RequestBody Map<String, Object> request) {
        log.info("🤖 통합 분석 요청: {} {}", request.get("brand"), request.get("model"));
        
        try {
            String url = mlServiceUrl + "/api/smart-analysis";
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);
            ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
            
            return ResponseEntity.ok(response.getBody());
            
        } catch (Exception e) {
            log.error("❌ 통합 분석 실패: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "ML 서비스 연결 실패"));
        }
    }
    
    /**
     * 비슷한 차량 분포 (Gateway)
     * POST /api/ml/similar
     */
    @PostMapping("/similar")
    public ResponseEntity<?> similar(@RequestBody Map<String, Object> request) {
        try {
            String url = mlServiceUrl + "/api/similar";
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);
            ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
            
            return ResponseEntity.ok(response.getBody());
            
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "ML 서비스 연결 실패"));
        }
    }
    
    /**
     * 인기 차량 (Gateway)
     * GET /api/ml/popular
     */
    @GetMapping("/popular")
    public ResponseEntity<?> popular(
            @RequestParam(defaultValue = "all") String category,
            @RequestParam(defaultValue = "5") int limit) {
        try {
            String url = mlServiceUrl + "/api/popular?category=" + category + "&limit=" + limit;
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            
            return ResponseEntity.ok(response.getBody());
            
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "ML 서비스 연결 실패"));
        }
    }
    
    /**
     * 브랜드 목록 (Gateway)
     * GET /api/ml/brands
     */
    @GetMapping("/brands")
    public ResponseEntity<?> brands() {
        try {
            String url = mlServiceUrl + "/api/brands";
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            
            return ResponseEntity.ok(response.getBody());
            
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "ML 서비스 연결 실패"));
        }
    }
    
    /**
     * 모델 목록 (Gateway)
     * GET /api/ml/models/{brand}
     */
    @GetMapping("/models/{brand}")
    public ResponseEntity<?> models(@PathVariable String brand) {
        try {
            String url = mlServiceUrl + "/api/models/" + brand;
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            
            return ResponseEntity.ok(response.getBody());
            
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "ML 서비스 연결 실패"));
        }
    }
    
    /**
     * ML 서비스 헬스체크
     * GET /api/ml/health
     */
    @GetMapping("/health")
    public ResponseEntity<?> health() {
        try {
            String url = mlServiceUrl + "/api/health";
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            
            return ResponseEntity.ok(Map.of(
                "gateway", "healthy",
                "ml_service", response.getBody()
            ));
            
        } catch (Exception e) {
            return ResponseEntity.ok(Map.of(
                "gateway", "healthy",
                "ml_service", "unavailable",
                "error", e.getMessage()
            ));
        }
    }
}

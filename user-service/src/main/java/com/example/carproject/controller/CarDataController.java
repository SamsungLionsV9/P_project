package com.example.carproject.controller;

import com.example.carproject.dto.DomesticCarDetailsDto;
import com.example.carproject.dto.ImportedCarDetailsDto;
import com.example.carproject.dto.NewCarScheduleDto;
import com.example.carproject.entity.DomesticCarDetails;
import com.example.carproject.entity.ImportedCarDetails;
import com.example.carproject.entity.NewCarSchedule;
import com.example.carproject.service.CarDataService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/cars")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class CarDataController {
    
    private final CarDataService carDataService;
    
    /**
     * 국산차 상세 정보 저장
     * POST /api/cars/domestic
     */
    @PostMapping("/domestic")
    public ResponseEntity<?> saveDomesticCarDetails(@Valid @RequestBody DomesticCarDetailsDto dto) {
        try {
            DomesticCarDetails saved = carDataService.saveDomesticCarDetails(dto);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "국산차 상세 정보가 저장되었습니다");
            response.put("data", saved);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 외제차 상세 정보 저장
     * POST /api/cars/imported
     */
    @PostMapping("/imported")
    public ResponseEntity<?> saveImportedCarDetails(@Valid @RequestBody ImportedCarDetailsDto dto) {
        try {
            ImportedCarDetails saved = carDataService.saveImportedCarDetails(dto);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "외제차 상세 정보가 저장되었습니다");
            response.put("data", saved);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 신차 출시 일정 저장
     * POST /api/cars/schedule
     */
    @PostMapping("/schedule")
    public ResponseEntity<?> saveNewCarSchedule(@Valid @RequestBody NewCarScheduleDto dto) {
        try {
            NewCarSchedule saved = carDataService.saveNewCarSchedule(dto);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "신차 출시 일정이 저장되었습니다");
            response.put("data", saved);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 국산차 상세 정보 조회
     * GET /api/cars/domestic/{carId}
     */
    @GetMapping("/domestic/{carId}")
    public ResponseEntity<?> getDomesticCarDetails(@PathVariable String carId) {
        try {
            DomesticCarDetails carDetails = carDataService.getDomesticCarDetails(carId);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", carDetails);
            
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            
            return ResponseEntity.notFound().build();
        }
    }
    
    /**
     * 외제차 상세 정보 조회
     * GET /api/cars/imported/{carId}
     */
    @GetMapping("/imported/{carId}")
    public ResponseEntity<?> getImportedCarDetails(@PathVariable String carId) {
        try {
            ImportedCarDetails carDetails = carDataService.getImportedCarDetails(carId);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", carDetails);
            
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            
            return ResponseEntity.notFound().build();
        }
    }
}


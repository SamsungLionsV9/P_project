package com.example.carproject.service;

import com.example.carproject.dto.DomesticCarDetailsDto;
import com.example.carproject.dto.ImportedCarDetailsDto;
import com.example.carproject.dto.NewCarScheduleDto;
import com.example.carproject.entity.DomesticCarDetails;
import com.example.carproject.entity.ImportedCarDetails;
import com.example.carproject.entity.NewCarSchedule;
import com.example.carproject.repository.DomesticCarDetailsRepository;
import com.example.carproject.repository.ImportedCarDetailsRepository;
import com.example.carproject.repository.NewCarScheduleRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class CarDataService {
    
    private final DomesticCarDetailsRepository domesticCarDetailsRepository;
    private final ImportedCarDetailsRepository importedCarDetailsRepository;
    private final NewCarScheduleRepository newCarScheduleRepository;
    
    /**
     * 국산차 상세 정보 저장
     */
    @Transactional
    public DomesticCarDetails saveDomesticCarDetails(DomesticCarDetailsDto dto) {
        // 기존 데이터 확인
        DomesticCarDetails existing = domesticCarDetailsRepository.findByCarId(dto.getCarId())
                .orElse(null);
        
        if (existing != null) {
            // 업데이트
            existing.setIsAccidentFree(dto.getIsAccidentFree());
            existing.setInspectionGrade(dto.getInspectionGrade() != null ? dto.getInspectionGrade() : "normal");
            existing.setHasSunroof(dto.getHasSunroof());
            existing.setHasNavigation(dto.getHasNavigation());
            existing.setHasLeatherSeat(dto.getHasLeatherSeat());
            existing.setHasSmartKey(dto.getHasSmartKey());
            existing.setHasRearCamera(dto.getHasRearCamera());
            existing.setHasLedLamp(dto.getHasLedLamp());
            existing.setHasParkingSensor(dto.getHasParkingSensor());
            existing.setHasAutoAc(dto.getHasAutoAc());
            existing.setHasHeatedSeat(dto.getHasHeatedSeat());
            existing.setHasVentilatedSeat(dto.getHasVentilatedSeat());
            existing.setRegion(dto.getRegion());
            return domesticCarDetailsRepository.save(existing);
        } else {
            // 새로 생성
            DomesticCarDetails carDetails = DomesticCarDetails.builder()
                    .carId(dto.getCarId())
                    .isAccidentFree(dto.getIsAccidentFree())
                    .inspectionGrade(dto.getInspectionGrade() != null ? dto.getInspectionGrade() : "normal")
                    .hasSunroof(dto.getHasSunroof())
                    .hasNavigation(dto.getHasNavigation())
                    .hasLeatherSeat(dto.getHasLeatherSeat())
                    .hasSmartKey(dto.getHasSmartKey())
                    .hasRearCamera(dto.getHasRearCamera())
                    .hasLedLamp(dto.getHasLedLamp())
                    .hasParkingSensor(dto.getHasParkingSensor())
                    .hasAutoAc(dto.getHasAutoAc())
                    .hasHeatedSeat(dto.getHasHeatedSeat())
                    .hasVentilatedSeat(dto.getHasVentilatedSeat())
                    .region(dto.getRegion())
                    .build();
            return domesticCarDetailsRepository.save(carDetails);
        }
    }
    
    /**
     * 외제차 상세 정보 저장
     */
    @Transactional
    public ImportedCarDetails saveImportedCarDetails(ImportedCarDetailsDto dto) {
        // 기존 데이터 확인
        ImportedCarDetails existing = importedCarDetailsRepository.findByCarId(dto.getCarId())
                .orElse(null);
        
        if (existing != null) {
            // 업데이트
            existing.setIsAccidentFree(dto.getIsAccidentFree());
            existing.setInspectionGrade(dto.getInspectionGrade() != null ? dto.getInspectionGrade() : "normal");
            existing.setHasSunroof(dto.getHasSunroof());
            existing.setHasNavigation(dto.getHasNavigation());
            existing.setHasLeatherSeat(dto.getHasLeatherSeat());
            existing.setHasSmartKey(dto.getHasSmartKey());
            existing.setHasRearCamera(dto.getHasRearCamera());
            existing.setHasLedLamp(dto.getHasLedLamp());
            existing.setHasParkingSensor(dto.getHasParkingSensor());
            existing.setHasAutoAc(dto.getHasAutoAc());
            existing.setHasHeatedSeat(dto.getHasHeatedSeat());
            existing.setHasVentilatedSeat(dto.getHasVentilatedSeat());
            existing.setRegion(dto.getRegion());
            return importedCarDetailsRepository.save(existing);
        } else {
            // 새로 생성
            ImportedCarDetails carDetails = ImportedCarDetails.builder()
                    .carId(dto.getCarId())
                    .isAccidentFree(dto.getIsAccidentFree())
                    .inspectionGrade(dto.getInspectionGrade() != null ? dto.getInspectionGrade() : "normal")
                    .hasSunroof(dto.getHasSunroof())
                    .hasNavigation(dto.getHasNavigation())
                    .hasLeatherSeat(dto.getHasLeatherSeat())
                    .hasSmartKey(dto.getHasSmartKey())
                    .hasRearCamera(dto.getHasRearCamera())
                    .hasLedLamp(dto.getHasLedLamp())
                    .hasParkingSensor(dto.getHasParkingSensor())
                    .hasAutoAc(dto.getHasAutoAc())
                    .hasHeatedSeat(dto.getHasHeatedSeat())
                    .hasVentilatedSeat(dto.getHasVentilatedSeat())
                    .region(dto.getRegion())
                    .build();
            return importedCarDetailsRepository.save(carDetails);
        }
    }
    
    /**
     * 신차 출시 일정 저장
     */
    @Transactional
    public NewCarSchedule saveNewCarSchedule(NewCarScheduleDto dto) {
        // 기존 데이터 확인
        NewCarSchedule existing = newCarScheduleRepository.findByBrandAndModel(dto.getBrand(), dto.getModel())
                .orElse(null);
        
        if (existing != null) {
            // 업데이트
            existing.setReleaseDate(dto.getReleaseDate());
            existing.setType(dto.getType());
            return newCarScheduleRepository.save(existing);
        } else {
            // 새로 생성
            NewCarSchedule schedule = NewCarSchedule.builder()
                    .brand(dto.getBrand())
                    .model(dto.getModel())
                    .releaseDate(dto.getReleaseDate())
                    .type(dto.getType())
                    .build();
            return newCarScheduleRepository.save(schedule);
        }
    }
    
    /**
     * 국산차 상세 정보 조회
     */
    public DomesticCarDetails getDomesticCarDetails(String carId) {
        return domesticCarDetailsRepository.findByCarId(carId)
                .orElseThrow(() -> new IllegalArgumentException("차량 정보를 찾을 수 없습니다: " + carId));
    }
    
    /**
     * 외제차 상세 정보 조회
     */
    public ImportedCarDetails getImportedCarDetails(String carId) {
        return importedCarDetailsRepository.findByCarId(carId)
                .orElseThrow(() -> new IllegalArgumentException("차량 정보를 찾을 수 없습니다: " + carId));
    }
}


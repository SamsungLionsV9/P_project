package com.example.carproject.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DomesticCarDetailsDto {
    
    @NotBlank(message = "차량 ID는 필수입니다")
    private String carId;
    
    @NotNull(message = "무사고 여부는 필수입니다")
    private Boolean isAccidentFree;
    
    private String inspectionGrade;  // normal, good, excellent
    
    @NotNull(message = "선루프 유무는 필수입니다")
    private Boolean hasSunroof;
    
    @NotNull(message = "네비게이션 유무는 필수입니다")
    private Boolean hasNavigation;
    
    @NotNull(message = "가죽시트 유무는 필수입니다")
    private Boolean hasLeatherSeat;
    
    @NotNull(message = "스마트키 유무는 필수입니다")
    private Boolean hasSmartKey;
    
    @NotNull(message = "후방카메라 유무는 필수입니다")
    private Boolean hasRearCamera;
    
    @NotNull(message = "LED 램프 유무는 필수입니다")
    private Boolean hasLedLamp;
    
    @NotNull(message = "주차센서 유무는 필수입니다")
    private Boolean hasParkingSensor;
    
    @NotNull(message = "자동에어컨 유무는 필수입니다")
    private Boolean hasAutoAc;
    
    @NotNull(message = "열선시트 유무는 필수입니다")
    private Boolean hasHeatedSeat;
    
    @NotNull(message = "통풍시트 유무는 필수입니다")
    private Boolean hasVentilatedSeat;
    
    private String region;
}


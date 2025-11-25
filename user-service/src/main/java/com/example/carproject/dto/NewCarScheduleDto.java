package com.example.carproject.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class NewCarScheduleDto {
    
    @NotBlank(message = "브랜드는 필수입니다")
    private String brand;
    
    @NotBlank(message = "모델명은 필수입니다")
    private String model;
    
    @NotNull(message = "출시일은 필수입니다")
    private LocalDate releaseDate;
    
    private String type;  // 페이스리프트, 풀체인지 등
}


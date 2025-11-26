package com.example.carproject.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "domestic_car_details", 
       uniqueConstraints = @UniqueConstraint(columnNames = "car_id"))
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DomesticCarDetails {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "car_id", unique = true, nullable = false, length = 50)
    private String carId;
    
    @Column(name = "is_accident_free", nullable = false)
    @Builder.Default
    private Boolean isAccidentFree = false;
    
    @Column(name = "inspection_grade", length = 20)
    @Builder.Default
    private String inspectionGrade = "normal";
    
    @Column(name = "has_sunroof", nullable = false)
    @Builder.Default
    private Boolean hasSunroof = false;
    
    @Column(name = "has_navigation", nullable = false)
    @Builder.Default
    private Boolean hasNavigation = false;
    
    @Column(name = "has_leather_seat", nullable = false)
    @Builder.Default
    private Boolean hasLeatherSeat = false;
    
    @Column(name = "has_smart_key", nullable = false)
    @Builder.Default
    private Boolean hasSmartKey = false;
    
    @Column(name = "has_rear_camera", nullable = false)
    @Builder.Default
    private Boolean hasRearCamera = false;
    
    @Column(name = "has_led_lamp", nullable = false)
    @Builder.Default
    private Boolean hasLedLamp = false;
    
    @Column(name = "has_parking_sensor", nullable = false)
    @Builder.Default
    private Boolean hasParkingSensor = false;
    
    @Column(name = "has_auto_ac", nullable = false)
    @Builder.Default
    private Boolean hasAutoAc = false;
    
    @Column(name = "has_heated_seat", nullable = false)
    @Builder.Default
    private Boolean hasHeatedSeat = false;
    
    @Column(name = "has_ventilated_seat", nullable = false)
    @Builder.Default
    private Boolean hasVentilatedSeat = false;
    
    @Column(name = "region", columnDefinition = "TEXT")
    private String region;
    
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}


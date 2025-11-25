package com.example.carproject.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "new_car_schedule")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class NewCarSchedule {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, length = 50)
    private String brand;
    
    @Column(nullable = false, length = 100)
    private String model;
    
    @Column(name = "release_date", nullable = false)
    private LocalDate releaseDate;
    
    @Column(length = 50)
    private String type;  // 페이스리프트, 풀체인지 등
    
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


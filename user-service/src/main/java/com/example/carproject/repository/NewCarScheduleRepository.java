package com.example.carproject.repository;

import com.example.carproject.entity.NewCarSchedule;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface NewCarScheduleRepository extends JpaRepository<NewCarSchedule, Long> {
    
    List<NewCarSchedule> findByBrand(String brand);
    
    List<NewCarSchedule> findByModel(String model);
    
    Optional<NewCarSchedule> findByBrandAndModel(String brand, String model);
}


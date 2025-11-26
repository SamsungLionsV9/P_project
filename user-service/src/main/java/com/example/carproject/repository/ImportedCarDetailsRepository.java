package com.example.carproject.repository;

import com.example.carproject.entity.ImportedCarDetails;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface ImportedCarDetailsRepository extends JpaRepository<ImportedCarDetails, Long> {
    
    Optional<ImportedCarDetails> findByCarId(String carId);
    
    boolean existsByCarId(String carId);
}


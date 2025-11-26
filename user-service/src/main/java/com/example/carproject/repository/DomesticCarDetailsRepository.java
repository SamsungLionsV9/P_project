package com.example.carproject.repository;

import com.example.carproject.entity.DomesticCarDetails;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface DomesticCarDetailsRepository extends JpaRepository<DomesticCarDetails, Long> {
    
    Optional<DomesticCarDetails> findByCarId(String carId);
    
    boolean existsByCarId(String carId);
}


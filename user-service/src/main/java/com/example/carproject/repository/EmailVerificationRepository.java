package com.example.carproject.repository;

import com.example.carproject.entity.EmailVerification;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface EmailVerificationRepository extends JpaRepository<EmailVerification, Long> {
    
    Optional<EmailVerification> findTopByEmailOrderByCreatedAtDesc(String email);
    
    Optional<EmailVerification> findByEmailAndCodeAndVerifiedFalse(String email, String code);
    
    void deleteByEmail(String email);
}

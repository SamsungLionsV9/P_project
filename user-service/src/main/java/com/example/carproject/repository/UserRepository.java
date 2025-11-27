package com.example.carproject.repository;

import com.example.carproject.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    Optional<User> findByEmail(String email);
    
    Optional<User> findByUsername(String username);
    
    Optional<User> findByProviderAndProviderId(User.Provider provider, String providerId);
    
    boolean existsByEmail(String email);
    
    boolean existsByUsername(String username);
    
    // 관리자 대시보드용 카운트 메서드
    long countByIsActive(Boolean isActive);
    
    long countByRole(User.Role role);
}


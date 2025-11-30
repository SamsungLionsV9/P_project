package com.example.carproject.repository;

import com.example.carproject.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    Optional<User> findByEmail(String email);
    
    Optional<User> findByUsername(String username);
    
    boolean existsByEmail(String email);
    
    boolean existsByUsername(String username);
    
    // OAuth 관련 메서드
    Optional<User> findByProviderAndProviderId(User.Provider provider, String providerId);
    
    // 통계용 메서드
    long countByIsActive(boolean isActive);
    
    long countByRole(User.Role role);
}


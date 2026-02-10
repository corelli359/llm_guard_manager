package com.llmguard.manager.repository;

import com.llmguard.manager.domain.entity.Scenario;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface ScenarioRepository extends JpaRepository<Scenario, String> {
    Optional<Scenario> findByAppId(String appId);
    boolean existsByAppId(String appId);
}

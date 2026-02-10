package com.llmguard.manager.repository;

import com.llmguard.manager.domain.entity.ScenarioAdminPermission;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface ScenarioAdminPermissionRepository extends JpaRepository<ScenarioAdminPermission, String> {
    Optional<ScenarioAdminPermission> findByUserIdAndScenarioId(String userId, String scenarioId);
    List<ScenarioAdminPermission> findByUserId(String userId);
    void deleteByUserIdAndScenarioId(String userId, String scenarioId);
}

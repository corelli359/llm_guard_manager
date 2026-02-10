package com.llmguard.manager.repository;

import com.llmguard.manager.domain.entity.UserScenarioRole;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface UserScenarioRoleRepository extends JpaRepository<UserScenarioRole, String> {
    List<UserScenarioRole> findByUserId(String userId);
    List<UserScenarioRole> findByUserIdAndScenarioId(String userId, String scenarioId);
    void deleteByUserIdAndScenarioId(String userId, String scenarioId);
}

package com.llmguard.manager.repository;

import com.llmguard.manager.domain.entity.UserScenarioAssignment;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface UserScenarioAssignmentRepository extends JpaRepository<UserScenarioAssignment, String> {
    List<UserScenarioAssignment> findByUserId(String userId);
    List<UserScenarioAssignment> findByScenarioId(String scenarioId);
    Optional<UserScenarioAssignment> findByUserIdAndScenarioId(String userId, String scenarioId);
    boolean existsByUserIdAndScenarioId(String userId, String scenarioId);
}

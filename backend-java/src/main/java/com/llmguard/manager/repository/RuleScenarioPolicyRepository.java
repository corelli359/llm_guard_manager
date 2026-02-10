package com.llmguard.manager.repository;

import com.llmguard.manager.domain.entity.RuleScenarioPolicy;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface RuleScenarioPolicyRepository extends JpaRepository<RuleScenarioPolicy, String> {
    List<RuleScenarioPolicy> findByScenarioId(String scenarioId);
    Optional<RuleScenarioPolicy> findByScenarioIdAndRuleModeAndMatchTypeAndMatchValue(
            String scenarioId, Integer ruleMode, String matchType, String matchValue);
    boolean existsByScenarioIdAndRuleModeAndMatchTypeAndMatchValue(
            String scenarioId, Integer ruleMode, String matchType, String matchValue);
}

package com.llmguard.manager.repository;

import com.llmguard.manager.domain.entity.ScenarioKeyword;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface ScenarioKeywordRepository extends JpaRepository<ScenarioKeyword, String> {
    List<ScenarioKeyword> findByScenarioId(String scenarioId);
    List<ScenarioKeyword> findByScenarioIdAndRuleMode(String scenarioId, Integer ruleMode);
    Optional<ScenarioKeyword> findByScenarioIdAndKeywordAndRuleMode(String scenarioId, String keyword, Integer ruleMode);
    boolean existsByScenarioIdAndKeywordAndRuleMode(String scenarioId, String keyword, Integer ruleMode);
}

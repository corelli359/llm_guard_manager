package com.llmguard.manager.repository;

import com.llmguard.manager.domain.entity.RuleGlobalDefault;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface RuleGlobalDefaultRepository extends JpaRepository<RuleGlobalDefault, String> {
    Optional<RuleGlobalDefault> findByTagCodeAndExtraCondition(String tagCode, String extraCondition);
    List<RuleGlobalDefault> findByTagCode(String tagCode);
}

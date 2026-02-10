package com.llmguard.manager.service;

import com.llmguard.manager.domain.dto.*;
import com.llmguard.manager.domain.entity.RuleGlobalDefault;
import com.llmguard.manager.domain.entity.RuleScenarioPolicy;
import com.llmguard.manager.repository.RuleGlobalDefaultRepository;
import com.llmguard.manager.repository.RuleScenarioPolicyRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class RulePolicyService {

    private final RuleScenarioPolicyRepository scenarioPolicyRepository;
    private final RuleGlobalDefaultRepository globalDefaultRepository;

    // --- Scenario Policies ---

    public List<RuleScenarioPolicy> getScenarioPolicies(String scenarioId) {
        return scenarioPolicyRepository.findByScenarioId(scenarioId);
    }

    public RuleScenarioPolicy getScenarioPolicyById(String id) {
        return scenarioPolicyRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Policy not found"));
    }
    @Transactional
    public RuleScenarioPolicy createScenarioPolicy(RuleScenarioPolicyCreate dto) {
        // Validate match_type
        if (!"KEYWORD".equals(dto.getMatchType()) && !"TAG".equals(dto.getMatchType())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "match_type must be KEYWORD or TAG");
        }

        // For TAG type, validate extra_condition
        if ("TAG".equals(dto.getMatchType()) && dto.getExtraCondition() != null) {
            if (!List.of("safe", "unsafe", "controversial").contains(dto.getExtraCondition())) {
                throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                        "For TAG match type, extra_condition must be 'safe', 'unsafe', or 'controversial'");
            }
        }

        // Check for duplicates
        if (scenarioPolicyRepository.existsByScenarioIdAndRuleModeAndMatchTypeAndMatchValue(
                dto.getScenarioId(), dto.getRuleMode(), dto.getMatchType(), dto.getMatchValue())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    String.format("Duplicate policy: Scenario '%s' already has a rule for Mode %d, Type %s, Value '%s'",
                            dto.getScenarioId(), dto.getRuleMode(), dto.getMatchType(), dto.getMatchValue()));
        }

        RuleScenarioPolicy policy = RuleScenarioPolicy.builder()
                .id(UUID.randomUUID().toString())
                .scenarioId(dto.getScenarioId())
                .matchType(dto.getMatchType())
                .matchValue(dto.getMatchValue())
                .ruleMode(dto.getRuleMode() != null ? dto.getRuleMode() : 2)
                .extraCondition(dto.getExtraCondition())
                .strategy(dto.getStrategy())
                .isActive(dto.getIsActive() != null ? dto.getIsActive() : true)
                .build();

        return scenarioPolicyRepository.save(policy);
    }

    @Transactional
    public RuleScenarioPolicy updateScenarioPolicy(String id, RuleScenarioPolicyUpdate dto) {
        RuleScenarioPolicy policy = scenarioPolicyRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Policy not found"));

        if (dto.getMatchType() != null) {
            policy.setMatchType(dto.getMatchType());
        }
        if (dto.getMatchValue() != null) {
            policy.setMatchValue(dto.getMatchValue());
        }
        if (dto.getRuleMode() != null) {
            policy.setRuleMode(dto.getRuleMode());
        }
        if (dto.getExtraCondition() != null) {
            policy.setExtraCondition(dto.getExtraCondition());
        }
        if (dto.getStrategy() != null) {
            policy.setStrategy(dto.getStrategy());
        }
        if (dto.getIsActive() != null) {
            policy.setIsActive(dto.getIsActive());
        }

        return scenarioPolicyRepository.save(policy);
    }

    @Transactional
    public RuleScenarioPolicy deleteScenarioPolicy(String id) {
        RuleScenarioPolicy policy = scenarioPolicyRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Policy not found"));
        scenarioPolicyRepository.delete(policy);
        return policy;
    }

    // --- Global Defaults ---

    public List<RuleGlobalDefault> getAllGlobalDefaults() {
        return globalDefaultRepository.findAll();
    }

    @Transactional
    public RuleGlobalDefault createGlobalDefault(RuleGlobalDefaultCreate dto) {
        // Validation: if tag_code is empty, extra_condition must be provided
        if ((dto.getTagCode() == null || dto.getTagCode().isBlank())
                && (dto.getExtraCondition() == null || dto.getExtraCondition().isBlank())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "When tag_code is empty, extra_condition must be provided");
        }

        // Check for duplicates
        String tagCode = dto.getTagCode() != null ? dto.getTagCode() : "";
        String extraCondition = dto.getExtraCondition() != null ? dto.getExtraCondition() : "";
        if (globalDefaultRepository.findByTagCodeAndExtraCondition(tagCode, extraCondition).isPresent()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    String.format("Duplicate global default: Rule for Tag '%s' with condition '%s' already exists",
                            tagCode.isEmpty() ? "(empty)" : tagCode,
                            extraCondition.isEmpty() ? "(none)" : extraCondition));
        }

        RuleGlobalDefault globalDefault = RuleGlobalDefault.builder()
                .id(UUID.randomUUID().toString())
                .tagCode(dto.getTagCode())
                .extraCondition(dto.getExtraCondition())
                .strategy(dto.getStrategy())
                .isActive(dto.getIsActive() != null ? dto.getIsActive() : true)
                .build();

        return globalDefaultRepository.save(globalDefault);
    }

    @Transactional
    public RuleGlobalDefault updateGlobalDefault(String id, RuleGlobalDefaultUpdate dto) {
        RuleGlobalDefault globalDefault = globalDefaultRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Global Default not found"));

        if (dto.getTagCode() != null) {
            globalDefault.setTagCode(dto.getTagCode());
        }
        if (dto.getExtraCondition() != null) {
            globalDefault.setExtraCondition(dto.getExtraCondition());
        }
        if (dto.getStrategy() != null) {
            globalDefault.setStrategy(dto.getStrategy());
        }
        if (dto.getIsActive() != null) {
            globalDefault.setIsActive(dto.getIsActive());
        }

        // Validate: if tag_code is empty, extra_condition must be provided
        String updatedTagCode = globalDefault.getTagCode();
        String updatedExtraCondition = globalDefault.getExtraCondition();
        if ((updatedTagCode == null || updatedTagCode.isBlank())
                && (updatedExtraCondition == null || updatedExtraCondition.isBlank())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "When tag_code is empty, extra_condition must be provided");
        }

        return globalDefaultRepository.save(globalDefault);
    }

    @Transactional
    public RuleGlobalDefault deleteGlobalDefault(String id) {
        RuleGlobalDefault globalDefault = globalDefaultRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Global Default not found"));
        globalDefaultRepository.delete(globalDefault);
        return globalDefault;
    }
}

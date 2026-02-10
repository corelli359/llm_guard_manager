package com.llmguard.manager.service;

import com.llmguard.manager.domain.dto.ScenarioKeywordCreate;
import com.llmguard.manager.domain.dto.ScenarioKeywordUpdate;
import com.llmguard.manager.domain.entity.ScenarioKeyword;
import com.llmguard.manager.repository.ScenarioKeywordRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ScenarioKeywordService {

    private final ScenarioKeywordRepository scenarioKeywordRepository;

    public List<ScenarioKeyword> getByScenario(String scenarioId, Integer ruleMode) {
        if (ruleMode != null) {
            return scenarioKeywordRepository.findByScenarioIdAndRuleMode(scenarioId, ruleMode);
        }
        return scenarioKeywordRepository.findByScenarioId(scenarioId);
    }

    public ScenarioKeyword getKeyword(String id) {
        return scenarioKeywordRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Scenario keyword not found"));
    }

    @Transactional
    public ScenarioKeyword createKeyword(ScenarioKeywordCreate dto) {
        if (dto.getTagCode() == null || dto.getTagCode().isEmpty()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "tag_code is required");
        }

        int ruleMode = dto.getRuleMode() != null ? dto.getRuleMode() : 1;

        if (scenarioKeywordRepository.existsByScenarioIdAndKeywordAndRuleMode(
                dto.getScenarioId(), dto.getKeyword(), ruleMode)) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "Keyword already exists for this scenario and rule mode");
        }

        ScenarioKeyword keyword = ScenarioKeyword.builder()
                .id(UUID.randomUUID().toString())
                .scenarioId(dto.getScenarioId())
                .keyword(dto.getKeyword())
                .tagCode(dto.getTagCode())
                .ruleMode(ruleMode)
                .riskLevel(dto.getRiskLevel())
                .isActive(true)
                .category(dto.getCategory() != null ? dto.getCategory() : 1)
                .build();

        return scenarioKeywordRepository.save(keyword);
    }

    @Transactional
    public ScenarioKeyword updateKeyword(String id, ScenarioKeywordUpdate dto) {
        ScenarioKeyword keyword = getKeyword(id);

        if (dto.getKeyword() != null) {
            keyword.setKeyword(dto.getKeyword());
        }
        if (dto.getTagCode() != null) {
            keyword.setTagCode(dto.getTagCode());
        }
        if (dto.getRuleMode() != null) {
            keyword.setRuleMode(dto.getRuleMode());
        }
        if (dto.getRiskLevel() != null) {
            keyword.setRiskLevel(dto.getRiskLevel());
        }
        if (dto.getIsActive() != null) {
            keyword.setIsActive(dto.getIsActive());
        }
        if (dto.getCategory() != null) {
            keyword.setCategory(dto.getCategory());
        }

        return scenarioKeywordRepository.save(keyword);
    }

    @Transactional
    public void deleteKeyword(String id) {
        ScenarioKeyword keyword = getKeyword(id);
        scenarioKeywordRepository.delete(keyword);
    }
}

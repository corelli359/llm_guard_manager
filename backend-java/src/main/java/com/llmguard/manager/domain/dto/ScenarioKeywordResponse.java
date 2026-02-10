package com.llmguard.manager.domain.dto;

import com.llmguard.manager.domain.entity.ScenarioKeyword;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ScenarioKeywordResponse {
    private String id;
    private String scenarioId;
    private String keyword;
    private String tagCode;
    private Integer ruleMode;
    private String riskLevel;
    private Boolean isActive;
    private Integer category;

    public static ScenarioKeywordResponse fromEntity(ScenarioKeyword kw) {
        return ScenarioKeywordResponse.builder()
                .id(kw.getId())
                .scenarioId(kw.getScenarioId())
                .keyword(kw.getKeyword())
                .tagCode(kw.getTagCode())
                .ruleMode(kw.getRuleMode())
                .riskLevel(kw.getRiskLevel())
                .isActive(kw.getIsActive())
                .category(kw.getCategory())
                .build();
    }
}

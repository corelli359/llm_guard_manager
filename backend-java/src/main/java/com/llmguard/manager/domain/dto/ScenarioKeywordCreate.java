package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ScenarioKeywordCreate {
    private String scenarioId;
    private String keyword;
    private String tagCode;
    @Builder.Default
    private Integer ruleMode = 1;
    private String riskLevel;
    @Builder.Default
    private Integer category = 1;
}

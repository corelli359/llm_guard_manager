package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RuleScenarioPolicyCreate {
    private String scenarioId;
    private String matchType;
    private String matchValue;
    @Builder.Default
    private Integer ruleMode = 2;
    private String extraCondition;
    private String strategy;
    @Builder.Default
    private Boolean isActive = true;
}

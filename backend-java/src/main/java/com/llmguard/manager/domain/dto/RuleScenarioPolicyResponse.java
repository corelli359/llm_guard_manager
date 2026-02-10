package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RuleScenarioPolicyResponse {
    private String id;
    private String scenarioId;
    private String matchType;
    private String matchValue;
    private Integer ruleMode;
    private String extraCondition;
    private String strategy;
    private Boolean isActive;
}

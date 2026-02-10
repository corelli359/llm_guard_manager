package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RuleGlobalDefaultResponse {
    private String id;
    private String tagCode;
    private String extraCondition;
    private String strategy;
    private Boolean isActive;
}

package com.llmguard.manager.domain.dto;

import lombok.Data;

@Data
public class StagingRuleReview {
    private String finalStrategy;
    private String extraCondition;
    private String status; // REVIEWED or IGNORED
}

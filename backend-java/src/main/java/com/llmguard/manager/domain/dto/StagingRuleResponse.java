package com.llmguard.manager.domain.dto;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Builder
public class StagingRuleResponse {
    private String id;
    private String tagCode;
    private String predictedStrategy;
    private String finalStrategy;
    private String extraCondition;
    private String status;
    private Boolean isModified;
    private String claimedBy;
    private LocalDateTime claimedAt;
    private String batchId;
    private String annotator;
    private LocalDateTime annotatedAt;
    private LocalDateTime createdAt;
}

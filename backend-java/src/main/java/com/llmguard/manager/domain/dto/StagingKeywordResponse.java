package com.llmguard.manager.domain.dto;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Builder
public class StagingKeywordResponse {
    private String id;
    private String keyword;
    private String predictedTag;
    private String predictedRisk;
    private String finalTag;
    private String finalRisk;
    private String status;
    private Boolean isModified;
    private String claimedBy;
    private LocalDateTime claimedAt;
    private String batchId;
    private String annotator;
    private LocalDateTime annotatedAt;
    private LocalDateTime createdAt;
}

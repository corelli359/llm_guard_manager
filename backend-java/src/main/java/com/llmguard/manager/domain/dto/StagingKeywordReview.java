package com.llmguard.manager.domain.dto;

import lombok.Data;

@Data
public class StagingKeywordReview {
    private String finalTag;
    private String finalRisk;
    private String status; // REVIEWED or IGNORED
}

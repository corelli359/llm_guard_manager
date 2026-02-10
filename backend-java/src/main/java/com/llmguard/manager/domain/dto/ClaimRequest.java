package com.llmguard.manager.domain.dto;

import lombok.Data;

@Data
public class ClaimRequest {
    private Integer batchSize = 50;
    private String taskType; // "keywords" or "rules"
}

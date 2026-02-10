package com.llmguard.manager.domain.dto;

import lombok.Data;

import java.util.List;

@Data
public class StagingRuleBatchReviewRequest {
    private List<StagingRuleBatchReviewItem> reviews;

    @Data
    public static class StagingRuleBatchReviewItem {
        private String id;
        private String finalStrategy;
        private String extraCondition;
        private String status;
    }
}

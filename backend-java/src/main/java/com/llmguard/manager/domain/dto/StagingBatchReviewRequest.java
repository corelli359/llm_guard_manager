package com.llmguard.manager.domain.dto;

import lombok.Data;

import java.util.List;

@Data
public class StagingBatchReviewRequest {
    private List<StagingBatchReviewItem> reviews;

    @Data
    public static class StagingBatchReviewItem {
        private String id;
        private String finalTag;
        private String finalRisk;
        private String status;
    }
}

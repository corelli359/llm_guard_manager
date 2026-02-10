package com.llmguard.manager.domain.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class StagingOverviewResponse {
    private StatusCounts keywords;
    private StatusCounts rules;

    @Data
    @Builder
    public static class StatusCounts {
        private long pending;
        private long claimed;
        private long reviewed;
        private long synced;
        private long ignored;
        private long total;
    }
}

package com.llmguard.manager.domain.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class MyTaskStatsResponse {
    private TaskCounts keywords;
    private TaskCounts rules;

    @Data
    @Builder
    public static class TaskCounts {
        private long claimed;
        private long reviewed;
        private long ignored;
    }
}

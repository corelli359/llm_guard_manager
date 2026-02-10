package com.llmguard.manager.domain.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class StagingStatsResponse {
    private List<AnnotatorStat> annotators;

    @Data
    @Builder
    public static class AnnotatorStat {
        private String annotator;
        private long keywordsReviewed;
        private long rulesReviewed;
    }
}

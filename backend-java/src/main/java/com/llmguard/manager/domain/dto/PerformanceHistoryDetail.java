package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PerformanceHistoryDetail {

    private PerformanceHistoryMeta meta;
    private Map<String, Object> config;
    private Map<String, Object> stats;
    private List<Map<String, Object>> history;
    private PerformanceAnalysis analysis;
}

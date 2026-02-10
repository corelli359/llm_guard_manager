package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PerformanceStatusResponse {

    private boolean isRunning;
    private int duration;
    private int currentUsers;
    private long totalRequests;
    private long successRequests;
    private long errorRequests;
    private double currentRps;
    private double avgLatency;
    private double p95Latency;
    private double p99Latency;

    @Builder.Default
    private List<Map<String, Object>> history = new ArrayList<>();

    private String error;
}

package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PlaygroundHistoryResponse {
    private String id;
    private String requestId;
    private String playgroundType;
    private String appId;
    private Object inputData;
    private Object configSnapshot;
    private Object outputData;
    private Integer score;
    private Integer latency;
    private Integer upstreamLatency;
    private LocalDateTime createdAt;
}

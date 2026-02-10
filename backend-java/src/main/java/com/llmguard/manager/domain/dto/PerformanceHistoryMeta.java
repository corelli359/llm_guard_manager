package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PerformanceHistoryMeta {

    private String testId;
    private String startTime;
    private String endTime;
    private int duration;
    private String testType;
    private String appId;
    private String status;
}

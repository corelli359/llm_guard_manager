package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PerformanceAnalysis {

    @Builder.Default
    private int score = 100;

    private String conclusion;

    @Builder.Default
    private List<String> suggestions = List.of();
}

package com.llmguard.manager.domain.dto;

import jakarta.validation.constraints.Min;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StepLoadConfig {

    @Min(1)
    @Builder.Default
    private int initialUsers = 1;

    @Min(1)
    @Builder.Default
    private int stepSize = 1;

    @Min(5)
    @Builder.Default
    private int stepDuration = 10;

    @Min(1)
    @Builder.Default
    private int maxUsers = 50;
}

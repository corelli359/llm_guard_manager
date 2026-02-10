package com.llmguard.manager.domain.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PerformanceTestStartRequest {

    @NotNull
    private String testType; // "FATIGUE" or "STEP"

    @NotNull
    @Valid
    private GuardrailConfig targetConfig;

    @Valid
    private StepLoadConfig stepConfig;

    @Valid
    private FatigueLoadConfig fatigueConfig;
}

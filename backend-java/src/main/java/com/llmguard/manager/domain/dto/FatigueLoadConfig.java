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
public class FatigueLoadConfig {

    @Min(1)
    @Builder.Default
    private int concurrency = 10;

    @Min(10)
    @Builder.Default
    private int duration = 60;
}

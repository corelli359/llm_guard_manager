package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ScenarioPermissionDetail {
    private Boolean scenarioBasicInfo;
    private Boolean scenarioKeywords;
    private Boolean scenarioPolicies;
    private Boolean playground;
    private Boolean performanceTest;
}

package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ScenarioPermissionUpdate {
    private Boolean scenarioBasicInfo;
    private Boolean scenarioKeywords;
    private Boolean scenarioPolicies;
    private Boolean playground;
    private Boolean performanceTest;
}

package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ScenarioUpdate {
    private String appName;
    private String description;
    private Boolean isActive;
    private Boolean enableWhitelist;
    private Boolean enableBlacklist;
    private Boolean enableCustomPolicy;
}

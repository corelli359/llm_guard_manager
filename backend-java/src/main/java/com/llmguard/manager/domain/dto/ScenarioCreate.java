package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ScenarioCreate {
    private String appId;
    private String appName;
    private String description;
    @Builder.Default
    private Boolean enableWhitelist = true;
    @Builder.Default
    private Boolean enableBlacklist = true;
    @Builder.Default
    private Boolean enableCustomPolicy = true;
}

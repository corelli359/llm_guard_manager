package com.llmguard.manager.domain.dto;

import com.llmguard.manager.domain.entity.Scenario;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ScenarioResponse {
    private String id;
    private String appId;
    private String appName;
    private String description;
    private Boolean isActive;
    private Boolean enableWhitelist;
    private Boolean enableBlacklist;
    private Boolean enableCustomPolicy;

    public static ScenarioResponse fromEntity(Scenario s) {
        return ScenarioResponse.builder()
                .id(s.getId())
                .appId(s.getAppId())
                .appName(s.getAppName())
                .description(s.getDescription())
                .isActive(s.getIsActive())
                .enableWhitelist(s.getEnableWhitelist())
                .enableBlacklist(s.getEnableBlacklist())
                .enableCustomPolicy(s.getEnableCustomPolicy())
                .build();
    }
}

package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserPermissionResponse {
    private String role;
    private List<ScenarioPermission> scenarios;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ScenarioPermission {
        private String scenarioId;
        private String scenarioName;
        private String role;
        private Map<String, Boolean> permissions;
    }
}

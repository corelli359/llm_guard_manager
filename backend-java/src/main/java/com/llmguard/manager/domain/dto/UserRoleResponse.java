package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserRoleResponse {
    private String id;
    private String userId;
    private String scenarioId;
    private String roleId;
    private String roleName;
    private String roleCode;
    private LocalDateTime createdAt;
}

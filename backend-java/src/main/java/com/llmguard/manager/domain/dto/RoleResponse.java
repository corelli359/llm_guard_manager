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
public class RoleResponse {
    private String id;
    private String roleCode;
    private String roleName;
    private String roleType;
    private String description;
    private Boolean isSystem;
    private Boolean isActive;
    private LocalDateTime createdAt;
    private Integer permissionCount;
}

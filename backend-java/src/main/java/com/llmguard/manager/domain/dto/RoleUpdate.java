package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RoleUpdate {
    private String roleName;
    private String roleType;
    private String description;
    private Boolean isActive;
}

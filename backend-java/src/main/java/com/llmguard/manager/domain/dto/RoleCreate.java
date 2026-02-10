package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RoleCreate {
    private String roleCode;
    private String roleName;
    private String roleType;
    private String description;
}

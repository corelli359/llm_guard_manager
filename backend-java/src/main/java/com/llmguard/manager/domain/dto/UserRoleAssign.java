package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserRoleAssign {
    private String roleId;
    private String scenarioId;
}

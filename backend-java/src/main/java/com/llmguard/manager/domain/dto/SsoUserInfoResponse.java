package com.llmguard.manager.domain.dto;

import lombok.Builder;
import lombok.Data;

import java.util.Map;

@Data
@Builder
public class SsoUserInfoResponse {
    private String userId;
    private String userName;
    private String email;
    private String department;
    private String role;
    private String displayName;
    private Map<String, Object> permissions;
}

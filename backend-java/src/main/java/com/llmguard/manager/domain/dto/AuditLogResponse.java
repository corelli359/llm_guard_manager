package com.llmguard.manager.domain.dto;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Builder
public class AuditLogResponse {
    private String id;
    private String userId;
    private String username;
    private String action;
    private String resourceType;
    private String resourceId;
    private String scenarioId;
    private String details;
    private String ipAddress;
    private String userAgent;
    private LocalDateTime createdAt;
}

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
public class UserListResponse {
    private String id;
    private String userId;
    private String username;
    private String displayName;
    private String role;
    private String email;
    private Boolean isActive;
    private LocalDateTime createdAt;
}

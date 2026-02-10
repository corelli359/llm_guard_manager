package com.llmguard.manager.domain.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class SsoLoginResponse {
    private String accessToken;
    private String tokenType;
    private long expiresIn;
    private String userId;
    private String role;
}

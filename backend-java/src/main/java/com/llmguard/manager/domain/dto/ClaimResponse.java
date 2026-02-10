package com.llmguard.manager.domain.dto;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Builder
public class ClaimResponse {
    private int claimedCount;
    private String batchId;
    private LocalDateTime expiresAt;
    private int timeoutMinutes;
}

package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GlobalKeywordUpdate {
    private String keyword;
    private String tagCode;
    private String riskLevel;
    private Boolean isActive;
}

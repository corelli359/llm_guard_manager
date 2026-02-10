package com.llmguard.manager.domain.dto;

import com.llmguard.manager.domain.entity.GlobalKeyword;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GlobalKeywordResponse {
    private String id;
    private String keyword;
    private String tagCode;
    private String riskLevel;
    private Boolean isActive;

    public static GlobalKeywordResponse fromEntity(GlobalKeyword kw) {
        return GlobalKeywordResponse.builder()
                .id(kw.getId())
                .keyword(kw.getKeyword())
                .tagCode(kw.getTagCode())
                .riskLevel(kw.getRiskLevel())
                .isActive(kw.getIsActive())
                .build();
    }
}

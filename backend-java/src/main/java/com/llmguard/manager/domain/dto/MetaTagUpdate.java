package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MetaTagUpdate {
    private String tagName;
    private String parentCode;
    private Integer level;
    private Boolean isActive;
}

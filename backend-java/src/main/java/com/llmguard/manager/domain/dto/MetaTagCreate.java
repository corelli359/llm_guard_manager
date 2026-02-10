package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MetaTagCreate {
    private String tagCode;
    private String tagName;
    private String parentCode;
    @Builder.Default
    private Integer level = 2;
}

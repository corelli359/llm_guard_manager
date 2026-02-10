package com.llmguard.manager.domain.dto;

import com.llmguard.manager.domain.entity.MetaTag;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MetaTagResponse {
    private String id;
    private String tagCode;
    private String tagName;
    private String parentCode;
    private Integer level;
    private Boolean isActive;

    public static MetaTagResponse fromEntity(MetaTag tag) {
        return MetaTagResponse.builder()
                .id(tag.getId())
                .tagCode(tag.getTagCode())
                .tagName(tag.getTagName())
                .parentCode(tag.getParentCode())
                .level(tag.getLevel())
                .isActive(tag.getIsActive())
                .build();
    }
}

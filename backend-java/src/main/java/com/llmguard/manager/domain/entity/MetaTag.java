package com.llmguard.manager.domain.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "meta_tags")
public class MetaTag {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "tag_code", length = 64, unique = true, nullable = false)
    private String tagCode;

    @Column(name = "tag_name", length = 128, nullable = false)
    private String tagName;

    @Column(name = "parent_code", length = 64)
    private String parentCode;

    @Column(nullable = false)
    private Integer level;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive;
}

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
@Table(name = "rule_global_defaults")
public class RuleGlobalDefault {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "tag_code", length = 64)
    private String tagCode;

    @Column(name = "extra_condition", length = 64)
    private String extraCondition;

    @Column(length = 32, nullable = false)
    private String strategy;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive;
}

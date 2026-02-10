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
@Table(name = "lib_global_keywords")
public class GlobalKeyword {

    @Id
    @Column(length = 36)
    private String id;

    @Column(length = 255, nullable = false)
    private String keyword;

    @Column(name = "tag_code", length = 64, nullable = false)
    private String tagCode;

    @Column(name = "risk_level", length = 32, nullable = false)
    private String riskLevel;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive;
}

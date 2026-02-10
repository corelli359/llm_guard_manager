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
@Table(name = "lib_scenario_keywords")
public class ScenarioKeyword {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "scenario_id", length = 64, nullable = false)
    private String scenarioId;

    @Column(length = 255, nullable = false)
    private String keyword;

    @Column(name = "tag_code", length = 64)
    private String tagCode;

    @Column(name = "rule_mode", nullable = false)
    private Integer ruleMode;

    @Column(name = "risk_level", length = 32)
    private String riskLevel;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive;

    @Column(nullable = false)
    private Integer category;
}

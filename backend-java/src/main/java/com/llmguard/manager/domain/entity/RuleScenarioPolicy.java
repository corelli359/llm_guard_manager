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
@Table(name = "rule_scenario_policy")
public class RuleScenarioPolicy {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "scenario_id", length = 64, nullable = false)
    private String scenarioId;

    @Column(name = "match_type", length = 16, nullable = false)
    private String matchType;

    @Column(name = "match_value", length = 255, nullable = false)
    private String matchValue;

    @Column(name = "rule_mode", nullable = false)
    private Integer ruleMode;

    @Column(name = "extra_condition", length = 64)
    private String extraCondition;

    @Column(length = 32, nullable = false)
    private String strategy;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive;
}

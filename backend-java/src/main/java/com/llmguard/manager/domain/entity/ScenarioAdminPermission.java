package com.llmguard.manager.domain.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "scenario_admin_permissions")
public class ScenarioAdminPermission {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "user_id", length = 36, nullable = false)
    private String userId;

    @Column(name = "scenario_id", length = 64, nullable = false)
    private String scenarioId;

    @Column(name = "scenario_basic_info", nullable = false)
    private Boolean scenarioBasicInfo;

    @Column(name = "scenario_keywords", nullable = false)
    private Boolean scenarioKeywords;

    @Column(name = "scenario_policies", nullable = false)
    private Boolean scenarioPolicies;

    @Column(nullable = false)
    private Boolean playground;

    @Column(name = "performance_test", nullable = false)
    private Boolean performanceTest;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "created_by", length = 36)
    private String createdBy;
}

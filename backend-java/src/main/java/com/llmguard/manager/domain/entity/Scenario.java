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
@Table(name = "scenarios")
public class Scenario {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "app_id", length = 64, unique = true, nullable = false)
    private String appId;

    @Column(name = "app_name", length = 128, nullable = false)
    private String appName;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive;

    @Column(name = "enable_whitelist", nullable = false)
    private Boolean enableWhitelist;

    @Column(name = "enable_blacklist", nullable = false)
    private Boolean enableBlacklist;

    @Column(name = "enable_custom_policy", nullable = false)
    private Boolean enableCustomPolicy;
}

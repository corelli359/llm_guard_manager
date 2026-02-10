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
@Table(name = "roles")
public class Role {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "role_code", length = 64, unique = true, nullable = false)
    private String roleCode;

    @Column(name = "role_name", length = 128, nullable = false)
    private String roleName;

    @Column(name = "role_type", length = 16, nullable = false)
    private String roleType;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(name = "is_system", nullable = false)
    private Boolean isSystem;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}

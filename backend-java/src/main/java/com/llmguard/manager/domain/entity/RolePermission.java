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
@Table(name = "role_permissions")
public class RolePermission {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "role_id", length = 36, nullable = false)
    private String roleId;

    @Column(name = "permission_id", length = 36, nullable = false)
    private String permissionId;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
}

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
@Table(name = "permissions")
public class Permission {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "permission_code", length = 64, unique = true, nullable = false)
    private String permissionCode;

    @Column(name = "permission_name", length = 128, nullable = false)
    private String permissionName;

    @Column(name = "permission_type", length = 16, nullable = false)
    private String permissionType;

    @Column(length = 16, nullable = false)
    private String scope;

    @Column(name = "parent_code", length = 64)
    private String parentCode;

    @Column(name = "sort_order", nullable = false)
    private Integer sortOrder;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive;
}

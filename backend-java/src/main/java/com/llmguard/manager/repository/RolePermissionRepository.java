package com.llmguard.manager.repository;

import com.llmguard.manager.domain.entity.RolePermission;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface RolePermissionRepository extends JpaRepository<RolePermission, String> {
    List<RolePermission> findByRoleId(String roleId);
    void deleteByRoleId(String roleId);
}

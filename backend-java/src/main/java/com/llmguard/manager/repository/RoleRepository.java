package com.llmguard.manager.repository;

import com.llmguard.manager.domain.entity.Role;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface RoleRepository extends JpaRepository<Role, String> {
    Optional<Role> findByRoleCode(String roleCode);
    boolean existsByRoleCode(String roleCode);
}

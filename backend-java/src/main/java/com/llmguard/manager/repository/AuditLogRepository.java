package com.llmguard.manager.repository;

import com.llmguard.manager.domain.entity.AuditLog;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface AuditLogRepository extends JpaRepository<AuditLog, String>, JpaSpecificationExecutor<AuditLog> {
    Page<AuditLog> findByUserId(String userId, Pageable pageable);
    Page<AuditLog> findByResourceType(String resourceType, Pageable pageable);
    Page<AuditLog> findByAction(String action, Pageable pageable);
}

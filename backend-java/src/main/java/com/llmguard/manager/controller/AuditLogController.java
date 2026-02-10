package com.llmguard.manager.controller;

import com.llmguard.manager.domain.dto.AuditLogResponse;
import com.llmguard.manager.domain.entity.AuditLog;
import com.llmguard.manager.repository.AuditLogRepository;
import jakarta.persistence.criteria.Predicate;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/audit-logs")
@RequiredArgsConstructor
public class AuditLogController {

    private final AuditLogRepository auditLogRepository;

    @GetMapping("/")
    @PreAuthorize("hasAnyRole('SYSTEM_ADMIN', 'AUDITOR')")
    public ResponseEntity<List<AuditLogResponse>> queryAuditLogs(
            @RequestParam(required = false) String userId,
            @RequestParam(required = false) String username,
            @RequestParam(required = false) String action,
            @RequestParam(required = false) String resourceType,
            @RequestParam(required = false) String scenarioId,
            @RequestParam(required = false) LocalDateTime startDate,
            @RequestParam(required = false) LocalDateTime endDate,
            @RequestParam(defaultValue = "0") int skip,
            @RequestParam(defaultValue = "50") int limit) {

        Specification<AuditLog> spec = buildSpec(userId, username, action, resourceType, scenarioId, startDate, endDate);
        int page = skip / Math.max(limit, 1);
        Page<AuditLog> results = auditLogRepository.findAll(spec,
                PageRequest.of(page, limit, Sort.by(Sort.Direction.DESC, "createdAt")));

        List<AuditLogResponse> response = results.getContent().stream()
                .map(this::toResponse)
                .toList();

        return ResponseEntity.ok(response);
    }

    @GetMapping("/count")
    @PreAuthorize("hasAnyRole('SYSTEM_ADMIN', 'AUDITOR')")
    public ResponseEntity<Map<String, Long>> countAuditLogs(
            @RequestParam(required = false) String userId,
            @RequestParam(required = false) String username,
            @RequestParam(required = false) String action,
            @RequestParam(required = false) String resourceType,
            @RequestParam(required = false) String scenarioId,
            @RequestParam(required = false) LocalDateTime startDate,
            @RequestParam(required = false) LocalDateTime endDate) {

        Specification<AuditLog> spec = buildSpec(userId, username, action, resourceType, scenarioId, startDate, endDate);
        long count = auditLogRepository.count(spec);
        return ResponseEntity.ok(Map.of("count", count));
    }

    private Specification<AuditLog> buildSpec(String userId, String username, String action,
                                               String resourceType, String scenarioId,
                                               LocalDateTime startDate, LocalDateTime endDate) {
        return (root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();
            if (userId != null) {
                predicates.add(cb.equal(root.get("userId"), userId));
            }
            if (username != null) {
                predicates.add(cb.like(root.get("username"), "%" + username + "%"));
            }
            if (action != null) {
                predicates.add(cb.equal(root.get("action"), action));
            }
            if (resourceType != null) {
                predicates.add(cb.equal(root.get("resourceType"), resourceType));
            }
            if (scenarioId != null) {
                predicates.add(cb.equal(root.get("scenarioId"), scenarioId));
            }
            if (startDate != null) {
                predicates.add(cb.greaterThanOrEqualTo(root.get("createdAt"), startDate));
            }
            if (endDate != null) {
                predicates.add(cb.lessThanOrEqualTo(root.get("createdAt"), endDate));
            }
            return cb.and(predicates.toArray(new Predicate[0]));
        };
    }

    private AuditLogResponse toResponse(AuditLog log) {
        return AuditLogResponse.builder()
                .id(log.getId())
                .userId(log.getUserId())
                .username(log.getUsername())
                .action(log.getAction())
                .resourceType(log.getResourceType())
                .resourceId(log.getResourceId())
                .scenarioId(log.getScenarioId())
                .details(log.getDetails())
                .ipAddress(log.getIpAddress())
                .userAgent(log.getUserAgent())
                .createdAt(log.getCreatedAt())
                .build();
    }
}

package com.llmguard.manager.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.llmguard.manager.domain.entity.AuditLog;
import com.llmguard.manager.repository.AuditLogRepository;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuditService {

    private final AuditLogRepository auditLogRepository;
    private final ObjectMapper objectMapper;

    @Transactional
    public void log(String userId, String username, String action,
                    String resourceType, String resourceId, String scenarioId,
                    Object details, HttpServletRequest request) {
        String detailsJson = null;
        if (details != null) {
            try {
                detailsJson = objectMapper.writeValueAsString(details);
            } catch (JsonProcessingException e) {
                log.warn("Failed to serialize audit details", e);
                detailsJson = "{}";
            }
        }

        AuditLog auditLog = AuditLog.builder()
                .id(UUID.randomUUID().toString())
                .userId(userId)
                .username(username)
                .action(action)
                .resourceType(resourceType)
                .resourceId(resourceId)
                .scenarioId(scenarioId)
                .details(detailsJson)
                .ipAddress(extractIp(request))
                .userAgent(request != null ? request.getHeader("User-Agent") : null)
                .createdAt(LocalDateTime.now())
                .build();

        auditLogRepository.save(auditLog);
    }

    @Transactional
    public void logCreate(String userId, String username, String resourceType,
                          String resourceId, Object details, HttpServletRequest request) {
        log(userId, username, "CREATE", resourceType, resourceId, null, details, request);
    }

    @Transactional
    public void logUpdate(String userId, String username, String resourceType,
                          String resourceId, Object details, HttpServletRequest request) {
        log(userId, username, "UPDATE", resourceType, resourceId, null, details, request);
    }

    @Transactional
    public void logDelete(String userId, String username, String resourceType,
                          String resourceId, Object details, HttpServletRequest request) {
        log(userId, username, "DELETE", resourceType, resourceId, null, details, request);
    }

    private String extractIp(HttpServletRequest request) {
        if (request == null) {
            return null;
        }
        String ip = request.getHeader("X-Forwarded-For");
        if (ip != null && !ip.isEmpty()) {
            return ip.split(",")[0].trim();
        }
        ip = request.getHeader("X-Real-IP");
        if (ip != null && !ip.isEmpty()) {
            return ip;
        }
        return request.getRemoteAddr();
    }
}

package com.llmguard.manager.controller;

import com.llmguard.manager.domain.dto.*;
import com.llmguard.manager.domain.entity.User;
import com.llmguard.manager.service.AuditService;
import com.llmguard.manager.service.PerformanceService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/performance")
@RequiredArgsConstructor
public class PerformanceController {

    private final PerformanceService performanceService;
    private final AuditService auditService;

    @PostMapping("/dry-run")
    public ResponseEntity<PerformanceDryRunResponse> dryRun(
            @RequestBody GuardrailConfig config,
            @AuthenticationPrincipal User currentUser,
            HttpServletRequest request) {

        requireAdminOrScenarioAdmin(currentUser);

        if (performanceService.isRunning()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "A performance test is currently running.");
        }

        PerformanceDryRunResponse result = performanceService.dryRun(config);

        auditService.logCreate(
                currentUser.getId(), currentUser.getUsername(),
                "PERFORMANCE_DRY_RUN", null,
                Map.of("app_id", config.getAppId()),
                request);

        return ResponseEntity.ok(result);
    }

    @PostMapping("/start")
    public ResponseEntity<Map<String, Object>> startTest(
            @RequestBody PerformanceTestStartRequest testRequest,
            @AuthenticationPrincipal User currentUser,
            HttpServletRequest request) {

        requireAdminOrScenarioAdmin(currentUser);

        if (performanceService.isRunning()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Test already running");
        }

        performanceService.startTest(testRequest);

        auditService.logCreate(
                currentUser.getId(), currentUser.getUsername(),
                "PERFORMANCE_TEST_START", null,
                Map.of("test_type", testRequest.getTestType(),
                        "app_id", testRequest.getTargetConfig().getAppId()),
                request);

        return ResponseEntity.ok(Map.of(
                "message", "Performance test started",
                "test_type", testRequest.getTestType()));
    }

    @PostMapping("/stop")
    public ResponseEntity<Map<String, String>> stopTest(
            @AuthenticationPrincipal User currentUser,
            HttpServletRequest request) {

        requireAdminOrScenarioAdmin(currentUser);

        performanceService.stopTest();

        auditService.logCreate(
                currentUser.getId(), currentUser.getUsername(),
                "PERFORMANCE_TEST_STOP", null, Map.of(), request);

        return ResponseEntity.ok(Map.of("message", "Stop signal sent"));
    }

    @GetMapping("/status")
    public ResponseEntity<PerformanceStatusResponse> getStatus(
            @AuthenticationPrincipal User currentUser) {

        requireAdminOrScenarioAdmin(currentUser);
        return ResponseEntity.ok(performanceService.getStatus());
    }

    @GetMapping("/history")
    public ResponseEntity<List<PerformanceHistoryMeta>> getHistory(
            @AuthenticationPrincipal User currentUser) {

        requireAdminOrScenarioAdmin(currentUser);
        return ResponseEntity.ok(performanceService.getHistoryList());
    }

    @GetMapping("/history/{testId}")
    public ResponseEntity<PerformanceHistoryDetail> getHistoryDetail(
            @PathVariable String testId,
            @AuthenticationPrincipal User currentUser) {

        requireAdminOrScenarioAdmin(currentUser);

        PerformanceHistoryDetail detail = performanceService.getHistoryDetail(testId);
        if (detail == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Test history not found");
        }
        return ResponseEntity.ok(detail);
    }

    @DeleteMapping("/history/{testId}")
    public ResponseEntity<Map<String, String>> deleteHistory(
            @PathVariable String testId,
            @AuthenticationPrincipal User currentUser,
            HttpServletRequest request) {

        requireSystemAdmin(currentUser);

        performanceService.deleteHistory(testId);

        auditService.logDelete(
                currentUser.getId(), currentUser.getUsername(),
                "PERFORMANCE_TEST_HISTORY", testId, null, request);

        return ResponseEntity.ok(Map.of("message", "History deleted"));
    }

    // ======================== Permission Helpers ========================

    private void requireAdminOrScenarioAdmin(User user) {
        String role = user.getRole();
        if (!"SYSTEM_ADMIN".equals(role) && !"SCENARIO_ADMIN".equals(role)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Insufficient permissions");
        }
    }

    private void requireSystemAdmin(User user) {
        if (!"SYSTEM_ADMIN".equals(user.getRole())) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Insufficient permissions");
        }
    }
}
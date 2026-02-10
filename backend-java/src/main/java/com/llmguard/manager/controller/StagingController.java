package com.llmguard.manager.controller;

import com.llmguard.manager.domain.dto.*;
import com.llmguard.manager.domain.entity.User;
import com.llmguard.manager.service.StagingService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/staging")
@RequiredArgsConstructor
public class StagingController {

    private final StagingService stagingService;

    // ==================== Keywords ====================

    @GetMapping("/keywords")
    public ResponseEntity<Page<StagingKeywordResponse>> listKeywords(
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "50") int size,
            @AuthenticationPrincipal User currentUser) {
        return ResponseEntity.ok(stagingService.getKeywords(status, null, page, size, currentUser));
    }

    @PatchMapping("/keywords/{keywordId}")
    public ResponseEntity<StagingKeywordResponse> reviewKeyword(
            @PathVariable String keywordId,
            @RequestBody StagingKeywordReview review,
            @AuthenticationPrincipal User currentUser) {
        return ResponseEntity.ok(stagingService.reviewKeyword(keywordId, review, currentUser));
    }

    @PostMapping("/keywords/batch-review")
    public ResponseEntity<List<StagingKeywordResponse>> batchReviewKeywords(
            @RequestBody StagingBatchReviewRequest request,
            @AuthenticationPrincipal User currentUser) {
        return ResponseEntity.ok(stagingService.batchReviewKeywords(request, currentUser));
    }
    @PostMapping("/keywords/sync")
    @PreAuthorize("hasRole('SYSTEM_ADMIN')")
    public ResponseEntity<Map<String, Object>> syncKeywords() {
        return ResponseEntity.ok(stagingService.syncKeywords());
    }

    @PostMapping("/keywords/import-mock")
    public ResponseEntity<Map<String, Object>> importMockKeywords(
            @RequestParam(defaultValue = "100") int count) {
        return ResponseEntity.ok(stagingService.importMockKeywords(count));
    }

    @DeleteMapping("/keywords/{keywordId}")
    public ResponseEntity<Void> deleteKeyword(@PathVariable String keywordId) {
        stagingService.deleteKeyword(keywordId);
        return ResponseEntity.noContent().build();
    }

    // ==================== Rules ====================

    @GetMapping("/rules")
    public ResponseEntity<Page<StagingRuleResponse>> listRules(
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "50") int size,
            @AuthenticationPrincipal User currentUser) {
        return ResponseEntity.ok(stagingService.getRules(status, null, page, size, currentUser));
    }

    @PatchMapping("/rules/{ruleId}")
    public ResponseEntity<StagingRuleResponse> reviewRule(
            @PathVariable String ruleId,
            @RequestBody StagingRuleReview review,
            @AuthenticationPrincipal User currentUser) {
        return ResponseEntity.ok(stagingService.reviewRule(ruleId, review, currentUser));
    }

    @PostMapping("/rules/batch-review")
    public ResponseEntity<List<StagingRuleResponse>> batchReviewRules(
            @RequestBody StagingRuleBatchReviewRequest request,
            @AuthenticationPrincipal User currentUser) {
        return ResponseEntity.ok(stagingService.batchReviewRules(request, currentUser));
    }

    @PostMapping("/rules/sync")
    @PreAuthorize("hasRole('SYSTEM_ADMIN')")
    public ResponseEntity<Map<String, Object>> syncRules() {
        return ResponseEntity.ok(stagingService.syncRules());
    }

    @PostMapping("/rules/import-mock")
    public ResponseEntity<Map<String, Object>> importMockRules(
            @RequestParam(defaultValue = "100") int count) {
        return ResponseEntity.ok(stagingService.importMockRules(count));
    }

    @DeleteMapping("/rules/{ruleId}")
    public ResponseEntity<Void> deleteRule(@PathVariable String ruleId) {
        stagingService.deleteRule(ruleId);
        return ResponseEntity.noContent().build();
    }
    // ==================== Task Management ====================

    @PostMapping("/claim")
    public ResponseEntity<ClaimResponse> claimTasks(
            @RequestBody ClaimRequest request,
            @AuthenticationPrincipal User currentUser) {
        int batchSize = request.getBatchSize() != null ? request.getBatchSize() : 50;
        return ResponseEntity.ok(stagingService.claimTasks(batchSize, request.getTaskType(), currentUser));
    }

    @PostMapping("/release-expired")
    public ResponseEntity<Map<String, Object>> releaseExpiredTasks() {
        return ResponseEntity.ok(stagingService.releaseExpiredTasks());
    }

    // ==================== Stats ====================

    @GetMapping("/stats/annotators")
    public ResponseEntity<StagingStatsResponse> getAnnotatorStats() {
        return ResponseEntity.ok(stagingService.getAnnotatorStats());
    }

    @GetMapping("/my-tasks/stats")
    public ResponseEntity<MyTaskStatsResponse> getMyTaskStats(
            @AuthenticationPrincipal User currentUser) {
        return ResponseEntity.ok(stagingService.getMyTaskStats(currentUser));
    }

    @GetMapping("/overview")
    public ResponseEntity<StagingOverviewResponse> getOverview() {
        return ResponseEntity.ok(stagingService.getOverview());
    }
}

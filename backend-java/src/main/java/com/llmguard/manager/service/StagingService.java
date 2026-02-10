package com.llmguard.manager.service;

import com.llmguard.manager.domain.dto.*;
import com.llmguard.manager.domain.entity.GlobalKeyword;
import com.llmguard.manager.domain.entity.RuleGlobalDefault;
import com.llmguard.manager.domain.entity.StagingGlobalKeyword;
import com.llmguard.manager.domain.entity.StagingGlobalRule;
import com.llmguard.manager.domain.entity.User;
import com.llmguard.manager.repository.GlobalKeywordRepository;
import com.llmguard.manager.repository.RuleGlobalDefaultRepository;
import com.llmguard.manager.repository.StagingGlobalKeywordRepository;
import com.llmguard.manager.repository.StagingGlobalRuleRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class StagingService {

    private final StagingGlobalKeywordRepository keywordRepo;
    private final StagingGlobalRuleRepository ruleRepo;
    private final GlobalKeywordRepository globalKeywordRepo;
    private final RuleGlobalDefaultRepository globalDefaultRepo;

    // ==================== Keywords ====================

    public Page<StagingKeywordResponse> getKeywords(String status, String claimedBy,
                                                     int page, int size, User currentUser) {
        PageRequest pageRequest = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "createdAt"));

        Page<StagingGlobalKeyword> results;
        if ("ANNOTATOR".equals(currentUser.getRole())) {
            // Annotators only see their own tasks
            if (status != null) {
                results = keywordRepo.findAll((root, query, cb) -> cb.and(
                        cb.equal(root.get("status"), status),
                        cb.equal(root.get("claimedBy"), currentUser.getUserId())
                ), pageRequest);
            } else {
                results = keywordRepo.findAll((root, query, cb) ->
                        cb.equal(root.get("claimedBy"), currentUser.getUserId()), pageRequest);
            }
        } else {
            // SYSTEM_ADMIN / AUDITOR see all
            if (status != null) {
                results = keywordRepo.findByStatus(status, pageRequest);
            } else {
                results = keywordRepo.findAll(pageRequest);
            }
        }

        return results.map(this::toKeywordResponse);
    }
    @Transactional
    public StagingKeywordResponse reviewKeyword(String id, StagingKeywordReview review, User currentUser) {
        StagingGlobalKeyword kw = keywordRepo.findById(id)
                .orElseThrow(() -> new NoSuchElementException("Staging keyword not found: " + id));

        kw.setFinalTag(review.getFinalTag());
        kw.setFinalRisk(review.getFinalRisk());
        kw.setStatus(review.getStatus());
        kw.setAnnotator(currentUser.getUserId());
        kw.setAnnotatedAt(LocalDateTime.now());
        kw.setIsModified(!Objects.equals(kw.getPredictedTag(), review.getFinalTag())
                || !Objects.equals(kw.getPredictedRisk(), review.getFinalRisk()));

        return toKeywordResponse(keywordRepo.save(kw));
    }

    @Transactional
    public List<StagingKeywordResponse> batchReviewKeywords(StagingBatchReviewRequest request, User currentUser) {
        List<StagingKeywordResponse> results = new ArrayList<>();
        for (StagingBatchReviewRequest.StagingBatchReviewItem item : request.getReviews()) {
            StagingKeywordReview review = new StagingKeywordReview();
            review.setFinalTag(item.getFinalTag());
            review.setFinalRisk(item.getFinalRisk());
            review.setStatus(item.getStatus());
            results.add(reviewKeyword(item.getId(), review, currentUser));
        }
        return results;
    }

    @Transactional
    public Map<String, Object> syncKeywords() {
        List<StagingGlobalKeyword> reviewed = keywordRepo.findByStatusIn(List.of("REVIEWED"));
        int synced = 0;
        for (StagingGlobalKeyword sk : reviewed) {
            GlobalKeyword gk = GlobalKeyword.builder()
                    .id(UUID.randomUUID().toString())
                    .keyword(sk.getKeyword())
                    .tagCode(sk.getFinalTag() != null ? sk.getFinalTag() : sk.getPredictedTag())
                    .riskLevel(sk.getFinalRisk() != null ? sk.getFinalRisk() : sk.getPredictedRisk())
                    .isActive(true)
                    .build();
            globalKeywordRepo.save(gk);
            sk.setStatus("SYNCED");
            keywordRepo.save(sk);
            synced++;
        }
        return Map.of("synced_count", synced);
    }

    @Transactional
    public Map<String, Object> importMockKeywords(int count) {
        String[] tags = {"POLITICS", "VIOLENCE", "ADULT", "GAMBLING", "DRUGS"};
        String[] risks = {"High", "Medium", "Low"};
        Random random = new Random();
        List<StagingGlobalKeyword> keywords = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            keywords.add(StagingGlobalKeyword.builder()
                    .id(UUID.randomUUID().toString())
                    .keyword("mock_keyword_" + UUID.randomUUID().toString().substring(0, 8))
                    .predictedTag(tags[random.nextInt(tags.length)])
                    .predictedRisk(risks[random.nextInt(risks.length)])
                    .status("PENDING")
                    .isModified(false)
                    .createdAt(LocalDateTime.now())
                    .build());
        }
        keywordRepo.saveAll(keywords);
        return Map.of("imported_count", count);
    }

    @Transactional
    public void deleteKeyword(String id) {
        keywordRepo.deleteById(id);
    }
    // ==================== Rules ====================

    public Page<StagingRuleResponse> getRules(String status, String claimedBy,
                                               int page, int size, User currentUser) {
        PageRequest pageRequest = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "createdAt"));

        Page<StagingGlobalRule> results;
        if ("ANNOTATOR".equals(currentUser.getRole())) {
            if (status != null) {
                results = ruleRepo.findAll((root, query, cb) -> cb.and(
                        cb.equal(root.get("status"), status),
                        cb.equal(root.get("claimedBy"), currentUser.getUserId())
                ), pageRequest);
            } else {
                results = ruleRepo.findAll((root, query, cb) ->
                        cb.equal(root.get("claimedBy"), currentUser.getUserId()), pageRequest);
            }
        } else {
            if (status != null) {
                results = ruleRepo.findByStatus(status, pageRequest);
            } else {
                results = ruleRepo.findAll(pageRequest);
            }
        }

        return results.map(this::toRuleResponse);
    }

    @Transactional
    public StagingRuleResponse reviewRule(String id, StagingRuleReview review, User currentUser) {
        StagingGlobalRule rule = ruleRepo.findById(id)
                .orElseThrow(() -> new NoSuchElementException("Staging rule not found: " + id));

        rule.setFinalStrategy(review.getFinalStrategy());
        rule.setExtraCondition(review.getExtraCondition());
        rule.setStatus(review.getStatus());
        rule.setAnnotator(currentUser.getUserId());
        rule.setAnnotatedAt(LocalDateTime.now());
        rule.setIsModified(!Objects.equals(rule.getPredictedStrategy(), review.getFinalStrategy()));

        return toRuleResponse(ruleRepo.save(rule));
    }

    @Transactional
    public List<StagingRuleResponse> batchReviewRules(StagingRuleBatchReviewRequest request, User currentUser) {
        List<StagingRuleResponse> results = new ArrayList<>();
        for (StagingRuleBatchReviewRequest.StagingRuleBatchReviewItem item : request.getReviews()) {
            StagingRuleReview review = new StagingRuleReview();
            review.setFinalStrategy(item.getFinalStrategy());
            review.setExtraCondition(item.getExtraCondition());
            review.setStatus(item.getStatus());
            results.add(reviewRule(item.getId(), review, currentUser));
        }
        return results;
    }
    @Transactional
    public Map<String, Object> syncRules() {
        List<StagingGlobalRule> reviewed = ruleRepo.findByStatusIn(List.of("REVIEWED"));
        int synced = 0;
        for (StagingGlobalRule sr : reviewed) {
            RuleGlobalDefault gd = RuleGlobalDefault.builder()
                    .id(UUID.randomUUID().toString())
                    .tagCode(sr.getTagCode())
                    .strategy(sr.getFinalStrategy() != null ? sr.getFinalStrategy() : sr.getPredictedStrategy())
                    .extraCondition(sr.getExtraCondition())
                    .isActive(true)
                    .build();
            globalDefaultRepo.save(gd);
            sr.setStatus("SYNCED");
            ruleRepo.save(sr);
            synced++;
        }
        return Map.of("synced_count", synced);
    }

    @Transactional
    public Map<String, Object> importMockRules(int count) {
        String[] tags = {"POLITICS", "VIOLENCE", "ADULT", "GAMBLING", "DRUGS"};
        String[] strategies = {"BLOCK", "REWRITE", "PASS", "MANUAL_REVIEW"};
        Random random = new Random();
        List<StagingGlobalRule> rules = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            rules.add(StagingGlobalRule.builder()
                    .id(UUID.randomUUID().toString())
                    .tagCode(tags[random.nextInt(tags.length)])
                    .predictedStrategy(strategies[random.nextInt(strategies.length)])
                    .status("PENDING")
                    .isModified(false)
                    .createdAt(LocalDateTime.now())
                    .build());
        }
        ruleRepo.saveAll(rules);
        return Map.of("imported_count", count);
    }

    @Transactional
    public void deleteRule(String id) {
        ruleRepo.deleteById(id);
    }

    // ==================== Task Management ====================

    @Transactional
    public ClaimResponse claimTasks(int batchSize, String taskType, User currentUser) {
        String batchId = UUID.randomUUID().toString();
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime expiresAt = now.plusMinutes(30);
        int claimed = 0;

        if ("keywords".equals(taskType)) {
            Page<StagingGlobalKeyword> pending = keywordRepo.findPendingForClaim(
                    PageRequest.of(0, batchSize));
            for (StagingGlobalKeyword kw : pending.getContent()) {
                kw.setStatus("CLAIMED");
                kw.setClaimedBy(currentUser.getUserId());
                kw.setClaimedAt(now);
                kw.setBatchId(batchId);
                keywordRepo.save(kw);
                claimed++;
            }
        } else if ("rules".equals(taskType)) {
            Page<StagingGlobalRule> pending = ruleRepo.findPendingForClaim(
                    PageRequest.of(0, batchSize));
            for (StagingGlobalRule rule : pending.getContent()) {
                rule.setStatus("CLAIMED");
                rule.setClaimedBy(currentUser.getUserId());
                rule.setClaimedAt(now);
                rule.setBatchId(batchId);
                ruleRepo.save(rule);
                claimed++;
            }
        }

        return ClaimResponse.builder()
                .claimedCount(claimed)
                .batchId(batchId)
                .expiresAt(expiresAt)
                .timeoutMinutes(30)
                .build();
    }

    @Transactional
    public Map<String, Object> releaseExpiredTasks() {
        LocalDateTime expiry = LocalDateTime.now().minusMinutes(30);
        int releasedKeywords = keywordRepo.releaseExpired(expiry);
        int releasedRules = ruleRepo.releaseExpired(expiry);
        return Map.of(
                "released_keywords", releasedKeywords,
                "released_rules", releasedRules
        );
    }
    // ==================== Stats ====================

    public StagingStatsResponse getAnnotatorStats() {
        // Get all reviewed/ignored keywords and rules, group by annotator
        List<StagingGlobalKeyword> reviewedKeywords = keywordRepo.findByStatusIn(List.of("REVIEWED", "IGNORED", "SYNCED"));
        List<StagingGlobalRule> reviewedRules = ruleRepo.findByStatusIn(List.of("REVIEWED", "IGNORED", "SYNCED"));

        Map<String, Long> kwByAnnotator = reviewedKeywords.stream()
                .filter(k -> k.getAnnotator() != null)
                .collect(Collectors.groupingBy(StagingGlobalKeyword::getAnnotator, Collectors.counting()));

        Map<String, Long> rulesByAnnotator = reviewedRules.stream()
                .filter(r -> r.getAnnotator() != null)
                .collect(Collectors.groupingBy(StagingGlobalRule::getAnnotator, Collectors.counting()));

        Set<String> allAnnotators = new HashSet<>();
        allAnnotators.addAll(kwByAnnotator.keySet());
        allAnnotators.addAll(rulesByAnnotator.keySet());

        List<StagingStatsResponse.AnnotatorStat> stats = allAnnotators.stream()
                .map(a -> StagingStatsResponse.AnnotatorStat.builder()
                        .annotator(a)
                        .keywordsReviewed(kwByAnnotator.getOrDefault(a, 0L))
                        .rulesReviewed(rulesByAnnotator.getOrDefault(a, 0L))
                        .build())
                .sorted(Comparator.comparing(StagingStatsResponse.AnnotatorStat::getAnnotator))
                .toList();

        return StagingStatsResponse.builder().annotators(stats).build();
    }

    public MyTaskStatsResponse getMyTaskStats(User currentUser) {
        String uid = currentUser.getUserId();
        return MyTaskStatsResponse.builder()
                .keywords(MyTaskStatsResponse.TaskCounts.builder()
                        .claimed(keywordRepo.findByStatusAndClaimedBy("CLAIMED", uid).size())
                        .reviewed(countKeywordsByAnnotatorAndStatus(uid, "REVIEWED"))
                        .ignored(countKeywordsByAnnotatorAndStatus(uid, "IGNORED"))
                        .build())
                .rules(MyTaskStatsResponse.TaskCounts.builder()
                        .claimed(ruleRepo.findByStatusAndClaimedBy("CLAIMED", uid).size())
                        .reviewed(countRulesByAnnotatorAndStatus(uid, "REVIEWED"))
                        .ignored(countRulesByAnnotatorAndStatus(uid, "IGNORED"))
                        .build())
                .build();
    }

    public StagingOverviewResponse getOverview() {
        return StagingOverviewResponse.builder()
                .keywords(StagingOverviewResponse.StatusCounts.builder()
                        .pending(keywordRepo.countByStatus("PENDING"))
                        .claimed(keywordRepo.countByStatus("CLAIMED"))
                        .reviewed(keywordRepo.countByStatus("REVIEWED"))
                        .synced(keywordRepo.countByStatus("SYNCED"))
                        .ignored(keywordRepo.countByStatus("IGNORED"))
                        .total(keywordRepo.count())
                        .build())
                .rules(StagingOverviewResponse.StatusCounts.builder()
                        .pending(ruleRepo.countByStatus("PENDING"))
                        .claimed(ruleRepo.countByStatus("CLAIMED"))
                        .reviewed(ruleRepo.countByStatus("REVIEWED"))
                        .synced(ruleRepo.countByStatus("SYNCED"))
                        .ignored(ruleRepo.countByStatus("IGNORED"))
                        .total(ruleRepo.count())
                        .build())
                .build();
    }

    // ==================== Helpers ====================

    private long countKeywordsByAnnotatorAndStatus(String annotator, String status) {
        return keywordRepo.findByStatusIn(List.of(status)).stream()
                .filter(k -> annotator.equals(k.getAnnotator()))
                .count();
    }

    private long countRulesByAnnotatorAndStatus(String annotator, String status) {
        return ruleRepo.findByStatusIn(List.of(status)).stream()
                .filter(r -> annotator.equals(r.getAnnotator()))
                .count();
    }

    private StagingKeywordResponse toKeywordResponse(StagingGlobalKeyword kw) {
        return StagingKeywordResponse.builder()
                .id(kw.getId())
                .keyword(kw.getKeyword())
                .predictedTag(kw.getPredictedTag())
                .predictedRisk(kw.getPredictedRisk())
                .finalTag(kw.getFinalTag())
                .finalRisk(kw.getFinalRisk())
                .status(kw.getStatus())
                .isModified(kw.getIsModified())
                .claimedBy(kw.getClaimedBy())
                .claimedAt(kw.getClaimedAt())
                .batchId(kw.getBatchId())
                .annotator(kw.getAnnotator())
                .annotatedAt(kw.getAnnotatedAt())
                .createdAt(kw.getCreatedAt())
                .build();
    }

    private StagingRuleResponse toRuleResponse(StagingGlobalRule rule) {
        return StagingRuleResponse.builder()
                .id(rule.getId())
                .tagCode(rule.getTagCode())
                .predictedStrategy(rule.getPredictedStrategy())
                .finalStrategy(rule.getFinalStrategy())
                .extraCondition(rule.getExtraCondition())
                .status(rule.getStatus())
                .isModified(rule.getIsModified())
                .claimedBy(rule.getClaimedBy())
                .claimedAt(rule.getClaimedAt())
                .batchId(rule.getBatchId())
                .annotator(rule.getAnnotator())
                .annotatedAt(rule.getAnnotatedAt())
                .createdAt(rule.getCreatedAt())
                .build();
    }
}

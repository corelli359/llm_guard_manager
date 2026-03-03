/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.controller;

import com.llmguard.common.result.R;
import com.llmguard.service.IStagingService;
import com.llmguard.vo.staging.StagingKeywordRespVO;
import com.llmguard.vo.staging.StagingRuleRespVO;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 功能描述：暂存区控制器
 *
 * @date 2024/07/13 16:06
 */
@RestController
@RequestMapping("/api/v1/staging")
public class StagingController {

    private final IStagingService stagingService;

    public StagingController(IStagingService stagingService) {
        this.stagingService = stagingService;
    }

    /**
     * 获取暂存敏感词列表
     *
     * @param status 状态过滤
     * @param skip   跳过条数
     * @param limit  限制条数
     * @return 暂存敏感词列表
     */
    @GetMapping("/keywords")
    public R<List<StagingKeywordRespVO>> listKeywords(
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "0") int skip,
            @RequestParam(defaultValue = "100") int limit) {
        return R.ok(stagingService.listStagingKeywords(status, skip, limit));
    }

    /**
     * 认领暂存敏感词
     *
     * @param body 请求体，包含 batchId 和 count
     * @return 被认领的敏感词列表
     */
    @SuppressWarnings("unchecked")
    @PostMapping("/keywords/claim")
    public R<List<StagingKeywordRespVO>> claimKeywords(@RequestBody Map<String, Object> body) {
        String batchId = (String) body.get("batchId");
        int count = body.get("count") != null ? ((Number) body.get("count")).intValue() : 10;
        String claimedBy = (String) body.get("claimedBy");
        return R.ok(stagingService.claimKeywords(batchId, count, claimedBy));
    }

    /**
     * 审核暂存敏感词
     *
     * @param id   敏感词ID
     * @param body 请求体，包含 finalTag 和 finalRisk
     * @return 审核后的敏感词
     */
    @PutMapping("/keywords/{id}/review")
    public R<StagingKeywordRespVO> reviewKeyword(@PathVariable String id,
                                                  @RequestBody Map<String, String> body) {
        String finalTag = body.get("finalTag");
        String finalRisk = body.get("finalRisk");
        return R.ok(stagingService.reviewKeyword(id, finalTag, finalRisk));
    }

    /**
     * 同步暂存敏感词到正式库
     *
     * @param body 请求体，包含 ids 列表
     * @return 同步成功的数量
     */
    @SuppressWarnings("unchecked")
    @PostMapping("/keywords/sync")
    public R<Integer> syncKeywords(@RequestBody Map<String, Object> body) {
        List<String> ids = (List<String>) body.get("ids");
        return R.ok(stagingService.syncKeywords(ids));
    }
    /**
     * 获取暂存规则列表
     *
     * @param status 状态过滤
     * @param skip   跳过条数
     * @param limit  限制条数
     * @return 暂存规则列表
     */
    @GetMapping("/rules")
    public R<List<StagingRuleRespVO>> listRules(
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "0") int skip,
            @RequestParam(defaultValue = "100") int limit) {
        return R.ok(stagingService.listStagingRules(status, skip, limit));
    }

    /**
     * 认领暂存规则
     *
     * @param body 请求体，包含 batchId 和 count
     * @return 被认领的规则列表
     */
    @SuppressWarnings("unchecked")
    @PostMapping("/rules/claim")
    public R<List<StagingRuleRespVO>> claimRules(@RequestBody Map<String, Object> body) {
        String batchId = (String) body.get("batchId");
        int count = body.get("count") != null ? ((Number) body.get("count")).intValue() : 10;
        String claimedBy = (String) body.get("claimedBy");
        return R.ok(stagingService.claimRules(batchId, count, claimedBy));
    }

    /**
     * 审核暂存规则
     *
     * @param id   规则ID
     * @param body 请求体，包含 finalStrategy 和 extraCondition
     * @return 审核后的规则
     */
    @PutMapping("/rules/{id}/review")
    public R<StagingRuleRespVO> reviewRule(@PathVariable String id,
                                            @RequestBody Map<String, String> body) {
        String finalStrategy = body.get("finalStrategy");
        String extraCondition = body.get("extraCondition");
        return R.ok(stagingService.reviewRule(id, finalStrategy, extraCondition));
    }

    /**
     * 同步暂存规则到正式库
     *
     * @param body 请求体，包含 ids 列表
     * @return 同步成功的数量
     */
    @SuppressWarnings("unchecked")
    @PostMapping("/rules/sync")
    public R<Integer> syncRules(@RequestBody Map<String, Object> body) {
        List<String> ids = (List<String>) body.get("ids");
        return R.ok(stagingService.syncRules(ids));
    }
}

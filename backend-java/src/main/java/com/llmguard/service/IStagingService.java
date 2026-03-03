/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service;

import com.llmguard.vo.staging.StagingKeywordRespVO;
import com.llmguard.vo.staging.StagingRuleRespVO;

import java.util.List;

/**
 * 功能描述：暂存区服务接口
 *
 * @date 2024/07/13 16:06
 */
public interface IStagingService {

    /**
     * 获取暂存敏感词列表
     *
     * @param status 状态过滤
     * @param skip   跳过条数
     * @param limit  限制条数
     * @return 暂存敏感词列表
     */
    List<StagingKeywordRespVO> listStagingKeywords(String status, int skip, int limit);

    /**
     * 获取暂存规则列表
     *
     * @param status 状态过滤
     * @param skip   跳过条数
     * @param limit  限制条数
     * @return 暂存规则列表
     */
    List<StagingRuleRespVO> listStagingRules(String status, int skip, int limit);

    /**
     * 认领暂存敏感词
     *
     * @param batchId   批次ID
     * @param count     认领数量
     * @param claimedBy 认领人
     * @return 被认领的敏感词列表
     */
    List<StagingKeywordRespVO> claimKeywords(String batchId, int count, String claimedBy);

    /**
     * 认领暂存规则
     *
     * @param batchId   批次ID
     * @param count     认领数量
     * @param claimedBy 认领人
     * @return 被认领的规则列表
     */
    List<StagingRuleRespVO> claimRules(String batchId, int count, String claimedBy);

    /**
     * 审核暂存敏感词
     *
     * @param id       敏感词ID
     * @param finalTag  最终标签
     * @param finalRisk 最终风险等级
     * @return 审核后的敏感词
     */
    StagingKeywordRespVO reviewKeyword(String id, String finalTag, String finalRisk);

    /**
     * 审核暂存规则
     *
     * @param id             规则ID
     * @param finalStrategy  最终策略
     * @param extraCondition 附加条件
     * @return 审核后的规则
     */
    StagingRuleRespVO reviewRule(String id, String finalStrategy, String extraCondition);

    /**
     * 同步暂存敏感词到正式库
     *
     * @param ids 敏感词ID列表
     * @return 同步成功的数量
     */
    int syncKeywords(List<String> ids);

    /**
     * 同步暂存规则到正式库
     *
     * @param ids 规则ID列表
     * @return 同步成功的数量
     */
    int syncRules(List<String> ids);
}

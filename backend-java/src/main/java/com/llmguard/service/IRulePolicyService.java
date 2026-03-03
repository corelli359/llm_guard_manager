/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service;

import com.llmguard.vo.policy.GlobalDefaultCreateVO;
import com.llmguard.vo.policy.GlobalDefaultRespVO;
import com.llmguard.vo.policy.GlobalDefaultUpdateVO;
import com.llmguard.vo.policy.ScenarioPolicyCreateVO;
import com.llmguard.vo.policy.ScenarioPolicyRespVO;
import com.llmguard.vo.policy.ScenarioPolicyUpdateVO;

import java.util.List;

/**
 * 功能描述：规则策略服务接口，包含场景策略和全局默认策略
 *
 * @date 2024/07/13 16:06
 */
public interface IRulePolicyService {

    // ==================== 场景策略 ====================

    /**
     * 根据场景ID查询策略列表
     *
     * @param scenarioId 场景ID
     * @return 场景策略列表
     */
    List<ScenarioPolicyRespVO> listByScenarioId(String scenarioId);

    /**
     * 创建场景策略
     *
     * @param createVO 创建参数
     * @return 创建后的场景策略
     */
    ScenarioPolicyRespVO createScenarioPolicy(ScenarioPolicyCreateVO createVO);

    /**
     * 更新场景策略
     *
     * @param policyId 策略ID
     * @param updateVO 更新参数
     * @return 更新后的场景策略
     */
    ScenarioPolicyRespVO updateScenarioPolicy(String policyId, ScenarioPolicyUpdateVO updateVO);

    /**
     * 删除场景策略
     *
     * @param policyId 策略ID
     * @return 被删除的场景策略
     */
    ScenarioPolicyRespVO deleteScenarioPolicy(String policyId);

    // ==================== 全局默认策略 ====================

    /**
     * 查询全局默认策略列表
     *
     * @param skip  跳过条数
     * @param limit 限制条数
     * @return 全局默认策略列表
     */
    List<GlobalDefaultRespVO> listGlobalDefaults(int skip, int limit);

    /**
     * 创建全局默认策略
     *
     * @param createVO 创建参数
     * @return 创建后的全局默认策略
     */
    GlobalDefaultRespVO createGlobalDefault(GlobalDefaultCreateVO createVO);

    /**
     * 更新全局默认策略
     *
     * @param defaultId 默认策略ID
     * @param updateVO  更新参数
     * @return 更新后的全局默认策略
     */
    GlobalDefaultRespVO updateGlobalDefault(String defaultId, GlobalDefaultUpdateVO updateVO);

    /**
     * 删除全局默认策略
     *
     * @param defaultId 默认策略ID
     * @return 被删除的全局默认策略
     */
    GlobalDefaultRespVO deleteGlobalDefault(String defaultId);
}

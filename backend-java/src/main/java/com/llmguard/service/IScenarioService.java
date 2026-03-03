/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service;

import com.llmguard.vo.scenario.ScenarioCreateVO;
import com.llmguard.vo.scenario.ScenarioRespVO;
import com.llmguard.vo.scenario.ScenarioUpdateVO;

import java.util.List;

/**
 * 功能描述：场景管理服务接口
 *
 * @date 2024/07/13 16:06
 */
public interface IScenarioService {

    /**
     * 获取场景列表
     *
     * @param skip  跳过条数
     * @param limit 限制条数
     * @return 场景列表
     */
    List<ScenarioRespVO> listScenarios(int skip, int limit);

    /**
     * 创建场景
     *
     * @param createVO 创建参数
     * @return 创建后的场景
     */
    ScenarioRespVO createScenario(ScenarioCreateVO createVO);

    /**
     * 根据 appId 获取场景
     *
     * @param appId 应用ID
     * @return 场景信息
     */
    ScenarioRespVO getByAppId(String appId);

    /**
     * 更新场景
     *
     * @param scenarioId 场景主键ID
     * @param updateVO   更新参数
     * @return 更新后的场景
     */
    ScenarioRespVO updateScenario(String scenarioId, ScenarioUpdateVO updateVO);

    /**
     * 删除场景
     *
     * @param scenarioId 场景主键ID
     * @return 被删除的场景
     */
    ScenarioRespVO deleteScenario(String scenarioId);
}

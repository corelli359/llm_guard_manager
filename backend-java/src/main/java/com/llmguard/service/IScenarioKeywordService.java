/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service;

import com.llmguard.vo.keyword.ScenarioKeywordCreateVO;
import com.llmguard.vo.keyword.ScenarioKeywordRespVO;
import com.llmguard.vo.keyword.ScenarioKeywordUpdateVO;

import java.util.List;

/**
 * 功能描述：场景敏感词服务接口
 *
 * @date 2024/07/13 16:06
 */
public interface IScenarioKeywordService {

    /**
     * 根据场景ID获取敏感词列表
     *
     * @param scenarioId 场景ID
     * @param ruleMode   规则模式（可选）
     * @return 敏感词列表
     */
    List<ScenarioKeywordRespVO> listByScenarioId(String scenarioId, Integer ruleMode);

    /**
     * 创建场景敏感词
     *
     * @param createVO 创建参数
     * @return 创建后的敏感词
     */
    ScenarioKeywordRespVO createKeyword(ScenarioKeywordCreateVO createVO);

    /**
     * 更新场景敏感词
     *
     * @param keywordId 敏感词ID
     * @param updateVO  更新参数
     * @return 更新后的敏感词
     */
    ScenarioKeywordRespVO updateKeyword(String keywordId, ScenarioKeywordUpdateVO updateVO);

    /**
     * 删除场景敏感词
     *
     * @param keywordId 敏感词ID
     * @return 被删除的敏感词
     */
    ScenarioKeywordRespVO deleteKeyword(String keywordId);
}

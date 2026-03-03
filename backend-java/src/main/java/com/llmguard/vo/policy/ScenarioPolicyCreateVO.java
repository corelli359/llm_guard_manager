/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.policy;

import javax.validation.constraints.NotBlank;

/**
 * 功能描述：创建场景规则策略请求 VO
 *
 * @date 2024/07/13 16:06
 */
public class ScenarioPolicyCreateVO {

    @NotBlank(message = "场景ID不能为空")
    private String scenarioId;

    @NotBlank(message = "匹配类型不能为空")
    private String matchType;

    @NotBlank(message = "匹配值不能为空")
    private String matchValue;

    private Integer ruleMode = 1;

    private String extraCondition;

    @NotBlank(message = "策略不能为空")
    private String strategy;

    private Boolean isActive = true;

    public String getScenarioId() {
        return scenarioId;
    }

    public void setScenarioId(String scenarioId) {
        this.scenarioId = scenarioId;
    }

    public String getMatchType() {
        return matchType;
    }

    public void setMatchType(String matchType) {
        this.matchType = matchType;
    }

    public String getMatchValue() {
        return matchValue;
    }

    public void setMatchValue(String matchValue) {
        this.matchValue = matchValue;
    }

    public Integer getRuleMode() {
        return ruleMode;
    }

    public void setRuleMode(Integer ruleMode) {
        this.ruleMode = ruleMode;
    }

    public String getExtraCondition() {
        return extraCondition;
    }

    public void setExtraCondition(String extraCondition) {
        this.extraCondition = extraCondition;
    }

    public String getStrategy() {
        return strategy;
    }

    public void setStrategy(String strategy) {
        this.strategy = strategy;
    }

    public Boolean getIsActive() {
        return isActive;
    }

    public void setIsActive(Boolean isActive) {
        this.isActive = isActive;
    }
}

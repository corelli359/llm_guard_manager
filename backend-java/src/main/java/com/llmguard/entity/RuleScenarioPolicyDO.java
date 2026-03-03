/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.entity;

import com.baomidou.mybatisplus.annotation.TableName;

/**
 * 功能描述：场景规则策略实体
 *
 * @date 2024/07/13 16:06
 */
@TableName("rule_scenario_policy")
public class RuleScenarioPolicyDO extends BaseDO {

    private String scenarioId;
    private String matchType;
    private String matchValue;
    private Integer ruleMode;
    private String extraCondition;
    private String strategy;
    private Boolean isActive;

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

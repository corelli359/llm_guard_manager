/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.keyword;

import java.util.List;

/**
 * 功能描述：更新场景敏感词请求 VO
 *
 * @date 2024/07/13 16:06
 */
public class ScenarioKeywordUpdateVO {

    private String scenarioId;
    private String keyword;
    private String tagCode;
    private Integer ruleMode;
    private String riskLevel;
    private Boolean isActive;
    private Integer category;
    private List<String> exemptions;

    public String getScenarioId() {
        return scenarioId;
    }

    public void setScenarioId(String scenarioId) {
        this.scenarioId = scenarioId;
    }

    public String getKeyword() {
        return keyword;
    }

    public void setKeyword(String keyword) {
        this.keyword = keyword;
    }

    public String getTagCode() {
        return tagCode;
    }

    public void setTagCode(String tagCode) {
        this.tagCode = tagCode;
    }

    public Integer getRuleMode() {
        return ruleMode;
    }

    public void setRuleMode(Integer ruleMode) {
        this.ruleMode = ruleMode;
    }

    public String getRiskLevel() {
        return riskLevel;
    }

    public void setRiskLevel(String riskLevel) {
        this.riskLevel = riskLevel;
    }

    public Boolean getIsActive() {
        return isActive;
    }

    public void setIsActive(Boolean isActive) {
        this.isActive = isActive;
    }

    public Integer getCategory() {
        return category;
    }

    public void setCategory(Integer category) {
        this.category = category;
    }

    public List<String> getExemptions() {
        return exemptions;
    }

    public void setExemptions(List<String> exemptions) {
        this.exemptions = exemptions;
    }
}

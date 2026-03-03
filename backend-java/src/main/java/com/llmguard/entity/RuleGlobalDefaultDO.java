/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.entity;

import com.baomidou.mybatisplus.annotation.TableName;

/**
 * 功能描述：全局默认规则实体
 *
 * @date 2024/07/13 16:06
 */
@TableName("rule_global_defaults")
public class RuleGlobalDefaultDO extends BaseDO {

    private String tagCode;
    private String extraCondition;
    private String strategy;
    private Boolean isActive;

    public String getTagCode() {
        return tagCode;
    }

    public void setTagCode(String tagCode) {
        this.tagCode = tagCode;
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

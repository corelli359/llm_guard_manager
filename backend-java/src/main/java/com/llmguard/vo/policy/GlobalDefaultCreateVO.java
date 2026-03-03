/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.policy;

import javax.validation.constraints.NotBlank;

/**
 * 功能描述：创建全局默认规则请求 VO
 *
 * @date 2024/07/13 16:06
 */
public class GlobalDefaultCreateVO {

    private String tagCode;

    private String extraCondition;

    @NotBlank(message = "策略不能为空")
    private String strategy;

    private Boolean isActive = true;

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

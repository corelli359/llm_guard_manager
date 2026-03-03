/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.entity;

import com.baomidou.mybatisplus.annotation.TableName;

/**
 * 功能描述：全局敏感词实体
 *
 * @date 2024/07/13 16:06
 */
@TableName("lib_global_keywords")
public class GlobalKeywordDO extends BaseDO {

    private String keyword;
    private String tagCode;
    private String riskLevel;
    private Boolean isActive;

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
}

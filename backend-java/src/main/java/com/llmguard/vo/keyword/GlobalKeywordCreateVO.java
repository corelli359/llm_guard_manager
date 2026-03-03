/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.keyword;

import javax.validation.constraints.NotBlank;

/**
 * 功能描述：创建全局敏感词请求 VO
 *
 * @date 2024/07/13 16:06
 */
public class GlobalKeywordCreateVO {

    @NotBlank(message = "关键词不能为空")
    private String keyword;

    @NotBlank(message = "标签编码不能为空")
    private String tagCode;

    @NotBlank(message = "风险等级不能为空")
    private String riskLevel;

    private Boolean isActive = true;

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

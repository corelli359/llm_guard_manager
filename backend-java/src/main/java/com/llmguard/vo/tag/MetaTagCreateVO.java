/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.tag;

import javax.validation.constraints.NotBlank;

/**
 * 功能描述：创建标签请求 VO
 *
 * @date 2024/07/13 16:06
 */
public class MetaTagCreateVO {

    @NotBlank(message = "标签编码不能为空")
    private String tagCode;

    @NotBlank(message = "标签名称不能为空")
    private String tagName;

    private String parentCode;
    private Integer level = 2;
    private Boolean isActive = true;

    public String getTagCode() {
        return tagCode;
    }

    public void setTagCode(String tagCode) {
        this.tagCode = tagCode;
    }

    public String getTagName() {
        return tagName;
    }

    public void setTagName(String tagName) {
        this.tagName = tagName;
    }

    public String getParentCode() {
        return parentCode;
    }

    public void setParentCode(String parentCode) {
        this.parentCode = parentCode;
    }

    public Integer getLevel() {
        return level;
    }

    public void setLevel(Integer level) {
        this.level = level;
    }

    public Boolean getIsActive() {
        return isActive;
    }

    public void setIsActive(Boolean isActive) {
        this.isActive = isActive;
    }
}

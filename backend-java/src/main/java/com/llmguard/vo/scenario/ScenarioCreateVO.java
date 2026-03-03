/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.scenario;

import javax.validation.constraints.NotBlank;

/**
 * 功能描述：创建场景请求 VO
 *
 * @date 2024/07/13 16:06
 */
public class ScenarioCreateVO {

    @NotBlank(message = "应用ID不能为空")
    private String appId;

    @NotBlank(message = "应用名称不能为空")
    private String appName;

    private String description;
    private Boolean isActive = true;
    private Boolean enableWhitelist = true;
    private Boolean enableBlacklist = true;
    private Boolean enableCustomPolicy = true;

    public String getAppId() {
        return appId;
    }

    public void setAppId(String appId) {
        this.appId = appId;
    }

    public String getAppName() {
        return appName;
    }

    public void setAppName(String appName) {
        this.appName = appName;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Boolean getIsActive() {
        return isActive;
    }

    public void setIsActive(Boolean isActive) {
        this.isActive = isActive;
    }

    public Boolean getEnableWhitelist() {
        return enableWhitelist;
    }

    public void setEnableWhitelist(Boolean enableWhitelist) {
        this.enableWhitelist = enableWhitelist;
    }

    public Boolean getEnableBlacklist() {
        return enableBlacklist;
    }

    public void setEnableBlacklist(Boolean enableBlacklist) {
        this.enableBlacklist = enableBlacklist;
    }

    public Boolean getEnableCustomPolicy() {
        return enableCustomPolicy;
    }

    public void setEnableCustomPolicy(Boolean enableCustomPolicy) {
        this.enableCustomPolicy = enableCustomPolicy;
    }
}

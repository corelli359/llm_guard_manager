/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.scenario;

/**
 * 功能描述：更新场景请求 VO
 *
 * @date 2024/07/13 16:06
 */
public class ScenarioUpdateVO {

    private String appName;
    private String description;
    private Boolean isActive;
    private Boolean enableWhitelist;
    private Boolean enableBlacklist;
    private Boolean enableCustomPolicy;

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

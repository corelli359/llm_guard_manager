/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.entity;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;

import java.util.Date;

/**
 * 功能描述：场景管理员权限配置实体
 *
 * @date 2024/07/13 16:06
 */
@TableName("scenario_admin_permissions")
public class ScenarioAdminPermissionDO extends BaseDO {

    private String userId;
    private String scenarioId;
    private Boolean scenarioBasicInfo;
    private Boolean scenarioKeywords;
    private Boolean scenarioPolicies;
    private Boolean playground;
    private Boolean performanceTest;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private Date updatedAt;

    private String createdBy;

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public String getScenarioId() {
        return scenarioId;
    }

    public void setScenarioId(String scenarioId) {
        this.scenarioId = scenarioId;
    }

    public Boolean getScenarioBasicInfo() {
        return scenarioBasicInfo;
    }

    public void setScenarioBasicInfo(Boolean scenarioBasicInfo) {
        this.scenarioBasicInfo = scenarioBasicInfo;
    }

    public Boolean getScenarioKeywords() {
        return scenarioKeywords;
    }

    public void setScenarioKeywords(Boolean scenarioKeywords) {
        this.scenarioKeywords = scenarioKeywords;
    }

    public Boolean getScenarioPolicies() {
        return scenarioPolicies;
    }

    public void setScenarioPolicies(Boolean scenarioPolicies) {
        this.scenarioPolicies = scenarioPolicies;
    }

    public Boolean getPlayground() {
        return playground;
    }

    public void setPlayground(Boolean playground) {
        this.playground = playground;
    }

    public Boolean getPerformanceTest() {
        return performanceTest;
    }

    public void setPerformanceTest(Boolean performanceTest) {
        this.performanceTest = performanceTest;
    }

    public Date getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(Date updatedAt) {
        this.updatedAt = updatedAt;
    }

    public String getCreatedBy() {
        return createdBy;
    }

    public void setCreatedBy(String createdBy) {
        this.createdBy = createdBy;
    }
}

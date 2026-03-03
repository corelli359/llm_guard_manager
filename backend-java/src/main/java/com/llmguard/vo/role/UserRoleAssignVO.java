/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.role;

import javax.validation.constraints.NotBlank;

/**
 * 功能描述：为用户分配角色请求 VO
 *
 * @date 2024/07/13 16:06
 */
public class UserRoleAssignVO {

    @NotBlank(message = "角色ID不能为空")
    private String roleId;

    private String scenarioId;

    public String getRoleId() {
        return roleId;
    }

    public void setRoleId(String roleId) {
        this.roleId = roleId;
    }

    public String getScenarioId() {
        return scenarioId;
    }

    public void setScenarioId(String scenarioId) {
        this.scenarioId = scenarioId;
    }
}

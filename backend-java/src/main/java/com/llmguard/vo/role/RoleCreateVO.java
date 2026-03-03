/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.role;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;

/**
 * 功能描述：创建角色请求 VO
 *
 * @date 2024/07/13 16:06
 */
public class RoleCreateVO {

    @NotBlank(message = "角色编码不能为空")
    @Size(max = 64, message = "角色编码长度不能超过64")
    private String roleCode;

    @NotBlank(message = "角色名称不能为空")
    @Size(max = 128, message = "角色名称长度不能超过128")
    private String roleName;

    private String roleType = "SCENARIO";

    private String description;

    public String getRoleCode() {
        return roleCode;
    }

    public void setRoleCode(String roleCode) {
        this.roleCode = roleCode;
    }

    public String getRoleName() {
        return roleName;
    }

    public void setRoleName(String roleName) {
        this.roleName = roleName;
    }

    public String getRoleType() {
        return roleType;
    }

    public void setRoleType(String roleType) {
        this.roleType = roleType;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }
}

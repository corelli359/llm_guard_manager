/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.entity;

import com.baomidou.mybatisplus.annotation.TableName;

/**
 * 功能描述：角色-权限关联实体
 *
 * @date 2024/07/13 16:06
 */
@TableName("role_permissions")
public class RolePermissionDO extends BaseDO {

    private String roleId;
    private String permissionId;

    public String getRoleId() {
        return roleId;
    }

    public void setRoleId(String roleId) {
        this.roleId = roleId;
    }

    public String getPermissionId() {
        return permissionId;
    }

    public void setPermissionId(String permissionId) {
        this.permissionId = permissionId;
    }
}

/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.role;

import java.util.List;

import javax.validation.constraints.NotNull;

/**
 * 功能描述：更新角色权限请求 VO
 *
 * @date 2024/07/13 16:06
 */
public class RolePermissionUpdateVO {

    @NotNull(message = "权限ID列表不能为空")
    private List<String> permissionIds;

    public List<String> getPermissionIds() {
        return permissionIds;
    }

    public void setPermissionIds(List<String> permissionIds) {
        this.permissionIds = permissionIds;
    }
}

/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.user;

import javax.validation.constraints.NotBlank;

/**
 * 功能描述：更新用户角色请求 VO
 *
 * @date 2024/07/13 16:06
 */
public class UserRoleUpdateVO {

    @NotBlank(message = "角色不能为空")
    private String role;

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }
}

/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.user;

import javax.validation.constraints.NotNull;

/**
 * 功能描述：更新用户状态请求 VO
 *
 * @date 2024/07/13 16:06
 */
public class UserStatusUpdateVO {

    @NotNull(message = "状态不能为空")
    private Boolean isActive;

    public Boolean getIsActive() {
        return isActive;
    }

    public void setIsActive(Boolean isActive) {
        this.isActive = isActive;
    }
}

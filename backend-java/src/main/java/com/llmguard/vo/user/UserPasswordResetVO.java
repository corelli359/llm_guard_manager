/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.user;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;

/**
 * 功能描述：重置用户密码请求 VO
 *
 * @date 2024/07/13 16:06
 */
public class UserPasswordResetVO {

    @NotBlank(message = "密码不能为空")
    @Size(min = 6, max = 128, message = "密码长度必须在6-128之间")
    private String password;

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }
}

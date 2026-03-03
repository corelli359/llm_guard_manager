/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service;

import com.llmguard.vo.auth.LoginRespVO;

/**
 * 功能描述：认证服务接口
 *
 * @date 2024/07/13 16:06
 */
public interface IAuthService {

    /**
     * 用户登录
     *
     * @param username 用户名
     * @param password 密码
     * @return 登录响应（含 token）
     */
    LoginRespVO login(String username, String password);
}

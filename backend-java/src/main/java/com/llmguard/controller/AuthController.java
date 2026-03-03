/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.controller;

import com.llmguard.common.result.R;
import com.llmguard.service.IAuthService;
import com.llmguard.vo.auth.LoginRespVO;
import com.llmguard.vo.auth.LoginVO;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.validation.Valid;

/**
 * 功能描述：认证控制器，处理登录请求
 *
 * @date 2024/07/13 16:06
 */
@RestController
@RequestMapping("/api/v1/login")
public class AuthController {

    private final IAuthService authService;

    public AuthController(IAuthService authService) {
        this.authService = authService;
    }

    /**
     * OAuth2 兼容的 token 登录接口
     *
     * @param loginVO 登录请求参数
     * @return 包含 access_token 的响应
     */
    @PostMapping("/access-token")
    public R<LoginRespVO> accessToken(@Valid LoginVO loginVO) {
        LoginRespVO resp = authService.login(loginVO.getUsername(), loginVO.getPassword());
        return R.ok(resp);
    }
}

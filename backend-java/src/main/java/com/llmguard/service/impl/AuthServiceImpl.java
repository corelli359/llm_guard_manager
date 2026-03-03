/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.llmguard.common.exception.BusinessException;
import com.llmguard.entity.UserDO;
import com.llmguard.mapper.UserMapper;
import com.llmguard.security.JwtTokenProvider;
import com.llmguard.service.IAuthService;
import com.llmguard.vo.auth.LoginRespVO;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.UUID;

/**
 * 功能描述：认证服务实现
 *
 * @date 2024/07/13 16:06
 */
@Service
public class AuthServiceImpl implements IAuthService {

    private static final Logger log = LoggerFactory.getLogger(AuthServiceImpl.class);

    // 硬编码管理员账号
    private static final String HARDCODED_USERNAME = "llm_guard";
    private static final String HARDCODED_PASSWORD = "68-8CtBhug";

    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;

    public AuthServiceImpl(UserMapper userMapper, PasswordEncoder passwordEncoder,
                           JwtTokenProvider jwtTokenProvider) {
        this.userMapper = userMapper;
        this.passwordEncoder = passwordEncoder;
        this.jwtTokenProvider = jwtTokenProvider;
    }

    /**
     * 用户登录，验证凭据并生成 JWT token
     *
     * @param username 用户名
     * @param password 密码
     * @return 登录响应
     */
    @Override
    public LoginRespVO login(String username, String password) {
        String userRole;

        // 1. 检查硬编码管理员
        if (HARDCODED_USERNAME.equals(username)) {
            if (!HARDCODED_PASSWORD.equals(password)) {
                throw new BusinessException(401, "Incorrect username or password");
            }
            userRole = "SYSTEM_ADMIN";
            // 自动同步到数据库
            ensureHardcodedUserExists();
        } else {
            // 2. 检查数据库用户
            UserDO user = userMapper.selectOne(
                    new LambdaQueryWrapper<UserDO>().eq(UserDO::getUsername, username)
            );
            if (user == null || !passwordEncoder.matches(password, user.getHashedPassword())) {
                throw new BusinessException(401, "Incorrect username or password");
            }
            if (user.getIsActive() == null || !user.getIsActive()) {
                throw new BusinessException(400, "Inactive user");
            }
            userRole = user.getRole();
        }

        String token = jwtTokenProvider.generateToken(username);
        return new LoginRespVO(token, "bearer", userRole);
    }

    /**
     * 确保硬编码管理员用户存在于数据库中
     */
    private void ensureHardcodedUserExists() {
        UserDO existing = userMapper.selectOne(
                new LambdaQueryWrapper<UserDO>().eq(UserDO::getUsername, HARDCODED_USERNAME)
        );
        if (existing == null) {
            UserDO user = new UserDO();
            user.setId(UUID.randomUUID().toString());
            user.setUsername(HARDCODED_USERNAME);
            user.setHashedPassword(passwordEncoder.encode(HARDCODED_PASSWORD));
            user.setRole("SYSTEM_ADMIN");
            user.setDisplayName("系统管理员");
            user.setIsActive(true);
            userMapper.insert(user);
            log.info("硬编码管理员用户已同步到数据库");
        }
    }
}

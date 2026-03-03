/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.llmguard.common.exception.BusinessException;
import com.llmguard.entity.RoleDO;
import com.llmguard.entity.UserDO;
import com.llmguard.entity.UserScenarioRoleDO;
import com.llmguard.mapper.RoleMapper;
import com.llmguard.mapper.UserMapper;
import com.llmguard.mapper.UserScenarioRoleMapper;
import com.llmguard.service.IUserService;
import com.llmguard.vo.role.UserRoleAssignVO;
import com.llmguard.vo.role.UserRoleRespVO;
import com.llmguard.vo.user.UserCreateVO;
import com.llmguard.vo.user.UserPasswordResetVO;
import com.llmguard.vo.user.UserRespVO;
import com.llmguard.vo.user.UserRoleUpdateVO;
import com.llmguard.vo.user.UserStatusUpdateVO;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * 功能描述：用户管理服务实现
 *
 * @date 2024/07/13 16:06
 */
@Service
public class UserServiceImpl implements IUserService {

    private static final Logger log = LoggerFactory.getLogger(UserServiceImpl.class);

    private final UserMapper userMapper;
    private final UserScenarioRoleMapper userScenarioRoleMapper;
    private final RoleMapper roleMapper;
    private final PasswordEncoder passwordEncoder;

    public UserServiceImpl(UserMapper userMapper,
                           UserScenarioRoleMapper userScenarioRoleMapper,
                           RoleMapper roleMapper,
                           PasswordEncoder passwordEncoder) {
        this.userMapper = userMapper;
        this.userScenarioRoleMapper = userScenarioRoleMapper;
        this.roleMapper = roleMapper;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public List<UserRespVO> listUsers(int skip, int limit) {
        Page<UserDO> page = new Page<>(skip / Math.max(limit, 1) + 1, limit);
        Page<UserDO> result = userMapper.selectPage(page, null);
        return result.getRecords().stream().map(this::toRespVO).collect(Collectors.toList());
    }

    @Override
    public UserRespVO createUser(UserCreateVO createVO, String currentUser) {
        // 用户名唯一性校验
        Long count = userMapper.selectCount(
                new LambdaQueryWrapper<UserDO>().eq(UserDO::getUsername, createVO.getUsername())
        );
        if (count > 0) {
            throw new BusinessException("用户名已存在: " + createVO.getUsername());
        }

        UserDO entity = new UserDO();
        entity.setUserId(UUID.randomUUID().toString());
        entity.setUsername(createVO.getUsername());
        entity.setHashedPassword(passwordEncoder.encode(createVO.getPassword()));
        entity.setDisplayName(createVO.getDisplayName());
        entity.setRole(createVO.getRole());
        entity.setIsActive(true);
        entity.setCreatedBy(currentUser);
        userMapper.insert(entity);
        log.info("用户创建成功: {}, 操作人: {}", createVO.getUsername(), currentUser);
        return toRespVO(entity);
    }
    @Override
    public UserRespVO updateUserRole(String userId, UserRoleUpdateVO updateVO, String currentUser) {
        UserDO entity = getAndCheckUser(userId, currentUser);
        entity.setRole(updateVO.getRole());
        userMapper.updateById(entity);
        log.info("用户角色更新: userId={}, newRole={}, 操作人: {}", userId, updateVO.getRole(), currentUser);
        return toRespVO(entity);
    }

    @Override
    public UserRespVO resetPassword(String userId, UserPasswordResetVO resetVO, String currentUser) {
        UserDO entity = getAndCheckUser(userId, currentUser);
        entity.setHashedPassword(passwordEncoder.encode(resetVO.getPassword()));
        userMapper.updateById(entity);
        log.info("用户密码重置: userId={}, 操作人: {}", userId, currentUser);
        return toRespVO(entity);
    }

    @Override
    public UserRespVO toggleStatus(String userId, UserStatusUpdateVO statusVO, String currentUser) {
        UserDO entity = getAndCheckUser(userId, currentUser);
        entity.setIsActive(statusVO.getIsActive());
        userMapper.updateById(entity);
        log.info("用户状态变更: userId={}, isActive={}, 操作人: {}", userId, statusVO.getIsActive(), currentUser);
        return toRespVO(entity);
    }

    @Override
    public UserRespVO deleteUser(String userId, String currentUser) {
        UserDO entity = getAndCheckUser(userId, currentUser);
        // 同时删除用户的角色分配
        userScenarioRoleMapper.delete(
                new LambdaQueryWrapper<UserScenarioRoleDO>().eq(UserScenarioRoleDO::getUserId, userId)
        );
        userMapper.deleteById(userId);
        log.info("用户删除: userId={}, username={}, 操作人: {}", userId, entity.getUsername(), currentUser);
        return toRespVO(entity);
    }
    @Override
    public List<UserRoleRespVO> getUserRoles(String userId) {
        UserDO user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(404, "用户不存在");
        }
        List<UserScenarioRoleDO> assignments = userScenarioRoleMapper.selectList(
                new LambdaQueryWrapper<UserScenarioRoleDO>().eq(UserScenarioRoleDO::getUserId, userId)
        );
        return assignments.stream().map(this::toUserRoleRespVO).collect(Collectors.toList());
    }

    @Override
    public UserRoleRespVO assignRole(String userId, UserRoleAssignVO assignVO, String currentUser) {
        UserDO user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(404, "用户不存在");
        }
        RoleDO role = roleMapper.selectById(assignVO.getRoleId());
        if (role == null) {
            throw new BusinessException(404, "角色不存在");
        }

        UserScenarioRoleDO entity = new UserScenarioRoleDO();
        entity.setUserId(userId);
        entity.setRoleId(assignVO.getRoleId());
        entity.setScenarioId(assignVO.getScenarioId());
        entity.setCreatedBy(currentUser);
        userScenarioRoleMapper.insert(entity);
        log.info("角色分配: userId={}, roleId={}, 操作人: {}", userId, assignVO.getRoleId(), currentUser);
        return toUserRoleRespVO(entity);
    }

    @Override
    public UserRoleRespVO removeRole(String userId, String assignmentId) {
        UserScenarioRoleDO entity = userScenarioRoleMapper.selectById(assignmentId);
        if (entity == null || !userId.equals(entity.getUserId())) {
            throw new BusinessException(404, "角色分配记录不存在");
        }
        userScenarioRoleMapper.deleteById(assignmentId);
        log.info("角色移除: userId={}, assignmentId={}", userId, assignmentId);
        return toUserRoleRespVO(entity);
    }
    /**
     * 获取用户并校验不能操作自己
     *
     * @param userId      目标用户ID
     * @param currentUser 当前操作用户名
     * @return 用户实体
     */
    private UserDO getAndCheckUser(String userId, String currentUser) {
        UserDO entity = userMapper.selectById(userId);
        if (entity == null) {
            throw new BusinessException(404, "用户不存在");
        }
        if (entity.getUsername().equals(currentUser)) {
            throw new BusinessException("不能对自己执行此操作");
        }
        return entity;
    }

    /**
     * UserDO 转 UserRespVO
     *
     * @param entity 用户实体
     * @return 用户响应 VO
     */
    private UserRespVO toRespVO(UserDO entity) {
        UserRespVO vo = new UserRespVO();
        vo.setId(entity.getId());
        vo.setUsername(entity.getUsername());
        vo.setDisplayName(entity.getDisplayName());
        vo.setRole(entity.getRole());
        vo.setIsActive(entity.getIsActive());
        vo.setCreatedAt(entity.getCreatedAt());
        return vo;
    }

    /**
     * UserScenarioRoleDO 转 UserRoleRespVO
     *
     * @param entity 角色分配实体
     * @return 角色分配响应 VO
     */
    private UserRoleRespVO toUserRoleRespVO(UserScenarioRoleDO entity) {
        UserRoleRespVO vo = new UserRoleRespVO();
        vo.setId(entity.getId());
        vo.setUserId(entity.getUserId());
        vo.setScenarioId(entity.getScenarioId());
        vo.setRoleId(entity.getRoleId());
        vo.setCreatedAt(entity.getCreatedAt());
        // 查询角色信息填充 roleCode/roleName/roleType
        RoleDO role = roleMapper.selectById(entity.getRoleId());
        if (role != null) {
            vo.setRoleCode(role.getRoleCode());
            vo.setRoleName(role.getRoleName());
            vo.setRoleType(role.getRoleType());
        }
        return vo;
    }
}

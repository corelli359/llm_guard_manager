/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service;

import com.llmguard.vo.role.UserRoleAssignVO;
import com.llmguard.vo.role.UserRoleRespVO;
import com.llmguard.vo.user.UserCreateVO;
import com.llmguard.vo.user.UserPasswordResetVO;
import com.llmguard.vo.user.UserRespVO;
import com.llmguard.vo.user.UserRoleUpdateVO;
import com.llmguard.vo.user.UserStatusUpdateVO;

import java.util.List;

/**
 * 功能描述：用户管理服务接口
 *
 * @date 2024/07/13 16:06
 */
public interface IUserService {

    /**
     * 获取用户列表
     *
     * @param skip  跳过条数
     * @param limit 限制条数
     * @return 用户列表
     */
    List<UserRespVO> listUsers(int skip, int limit);

    /**
     * 创建用户
     *
     * @param createVO    创建参数
     * @param currentUser 当前操作用户名
     * @return 创建后的用户信息
     */
    UserRespVO createUser(UserCreateVO createVO, String currentUser);

    /**
     * 更新用户角色
     *
     * @param userId      用户ID
     * @param updateVO    更新参数
     * @param currentUser 当前操作用户名
     * @return 更新后的用户信息
     */
    UserRespVO updateUserRole(String userId, UserRoleUpdateVO updateVO, String currentUser);

    /**
     * 重置用户密码
     *
     * @param userId      用户ID
     * @param resetVO     重置参数
     * @param currentUser 当前操作用户名
     * @return 更新后的用户信息
     */
    UserRespVO resetPassword(String userId, UserPasswordResetVO resetVO, String currentUser);

    /**
     * 切换用户启用/禁用状态
     *
     * @param userId      用户ID
     * @param statusVO    状态参数
     * @param currentUser 当前操作用户名
     * @return 更新后的用户信息
     */
    UserRespVO toggleStatus(String userId, UserStatusUpdateVO statusVO, String currentUser);

    /**
     * 删除用户
     *
     * @param userId      用户ID
     * @param currentUser 当前操作用户名
     * @return 被删除的用户信息
     */
    UserRespVO deleteUser(String userId, String currentUser);

    /**
     * 获取用户的角色分配列表
     *
     * @param userId 用户ID
     * @return 角色分配列表
     */
    List<UserRoleRespVO> getUserRoles(String userId);

    /**
     * 为用户分配角色
     *
     * @param userId      用户ID
     * @param assignVO    分配参数
     * @param currentUser 当前操作用户名
     * @return 分配结果
     */
    UserRoleRespVO assignRole(String userId, UserRoleAssignVO assignVO, String currentUser);

    /**
     * 移除用户的角色分配
     *
     * @param userId       用户ID
     * @param assignmentId 分配记录ID
     * @return 被移除的分配信息
     */
    UserRoleRespVO removeRole(String userId, String assignmentId);
}

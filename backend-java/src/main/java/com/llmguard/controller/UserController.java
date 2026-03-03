/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.controller;

import com.llmguard.common.result.R;
import com.llmguard.security.SecurityUser;
import com.llmguard.service.IUserService;
import com.llmguard.vo.role.UserRoleAssignVO;
import com.llmguard.vo.role.UserRoleRespVO;
import com.llmguard.vo.user.UserCreateVO;
import com.llmguard.vo.user.UserPasswordResetVO;
import com.llmguard.vo.user.UserRespVO;
import com.llmguard.vo.user.UserRoleUpdateVO;
import com.llmguard.vo.user.UserStatusUpdateVO;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * 功能描述：用户管理控制器
 *
 * @date 2024/07/13 16:06
 */
@RestController
@RequestMapping("/api/v1/users")
public class UserController {

    private final IUserService userService;

    public UserController(IUserService userService) {
        this.userService = userService;
    }

    /**
     * 获取用户列表
     *
     * @param skip  跳过条数
     * @param limit 限制条数
     * @return 用户列表
     */
    @GetMapping
    public R<List<UserRespVO>> list(@RequestParam(defaultValue = "0") int skip,
                                    @RequestParam(defaultValue = "100") int limit) {
        return R.ok(userService.listUsers(skip, limit));
    }
    /**
     * 创建用户
     *
     * @param createVO    创建参数
     * @param currentUser 当前登录用户
     * @return 创建后的用户信息
     */
    @PostMapping
    public R<UserRespVO> create(@Valid @RequestBody UserCreateVO createVO,
                                @AuthenticationPrincipal SecurityUser currentUser) {
        return R.ok(userService.createUser(createVO, currentUser.getUsername()));
    }

    /**
     * 更新用户角色
     *
     * @param userId      用户ID
     * @param updateVO    更新参数
     * @param currentUser 当前登录用户
     * @return 更新后的用户信息
     */
    @PutMapping("/{userId}/role")
    public R<UserRespVO> updateRole(@PathVariable String userId,
                                    @Valid @RequestBody UserRoleUpdateVO updateVO,
                                    @AuthenticationPrincipal SecurityUser currentUser) {
        return R.ok(userService.updateUserRole(userId, updateVO, currentUser.getUsername()));
    }

    /**
     * 重置用户密码
     *
     * @param userId      用户ID
     * @param resetVO     重置参数
     * @param currentUser 当前登录用户
     * @return 更新后的用户信息
     */
    @PutMapping("/{userId}/password")
    public R<UserRespVO> resetPassword(@PathVariable String userId,
                                       @Valid @RequestBody UserPasswordResetVO resetVO,
                                       @AuthenticationPrincipal SecurityUser currentUser) {
        return R.ok(userService.resetPassword(userId, resetVO, currentUser.getUsername()));
    }

    /**
     * 切换用户启用/禁用状态
     *
     * @param userId      用户ID
     * @param statusVO    状态参数
     * @param currentUser 当前登录用户
     * @return 更新后的用户信息
     */
    @PatchMapping("/{userId}/status")
    public R<UserRespVO> toggleStatus(@PathVariable String userId,
                                      @Valid @RequestBody UserStatusUpdateVO statusVO,
                                      @AuthenticationPrincipal SecurityUser currentUser) {
        return R.ok(userService.toggleStatus(userId, statusVO, currentUser.getUsername()));
    }
    /**
     * 删除用户
     *
     * @param userId      用户ID
     * @param currentUser 当前登录用户
     * @return 被删除的用户信息
     */
    @DeleteMapping("/{userId}")
    public R<UserRespVO> delete(@PathVariable String userId,
                                @AuthenticationPrincipal SecurityUser currentUser) {
        return R.ok(userService.deleteUser(userId, currentUser.getUsername()));
    }

    /**
     * 获取用户的角色分配列表
     *
     * @param userId 用户ID
     * @return 角色分配列表
     */
    @GetMapping("/{userId}/roles")
    public R<List<UserRoleRespVO>> getUserRoles(@PathVariable String userId) {
        return R.ok(userService.getUserRoles(userId));
    }

    /**
     * 为用户分配角色
     *
     * @param userId      用户ID
     * @param assignVO    分配参数
     * @param currentUser 当前登录用户
     * @return 分配结果
     */
    @PostMapping("/{userId}/roles")
    public R<UserRoleRespVO> assignRole(@PathVariable String userId,
                                        @Valid @RequestBody UserRoleAssignVO assignVO,
                                        @AuthenticationPrincipal SecurityUser currentUser) {
        return R.ok(userService.assignRole(userId, assignVO, currentUser.getUsername()));
    }

    /**
     * 移除用户的角色分配
     *
     * @param userId       用户ID
     * @param assignmentId 分配记录ID
     * @return 被移除的分配信息
     */
    @DeleteMapping("/{userId}/roles/{assignmentId}")
    public R<UserRoleRespVO> removeRole(@PathVariable String userId,
                                        @PathVariable String assignmentId) {
        return R.ok(userService.removeRole(userId, assignmentId));
    }
}

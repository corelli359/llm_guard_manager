/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.controller;

import com.llmguard.common.result.R;
import com.llmguard.service.IRoleService;
import com.llmguard.vo.role.PermissionRespVO;
import com.llmguard.vo.role.RoleCreateVO;
import com.llmguard.vo.role.RolePermissionUpdateVO;
import com.llmguard.vo.role.RoleRespVO;
import com.llmguard.vo.role.RoleUpdateVO;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * 功能描述：角色管理控制器
 *
 * @date 2024/07/13 16:06
 */
@RestController
@RequestMapping("/api/v1/roles")
public class RoleController {

    private final IRoleService roleService;

    public RoleController(IRoleService roleService) {
        this.roleService = roleService;
    }

    /**
     * 获取角色列表
     *
     * @param skip  跳过条数
     * @param limit 限制条数
     * @return 角色列表
     */
    @GetMapping
    public R<List<RoleRespVO>> list(@RequestParam(defaultValue = "0") int skip,
                                    @RequestParam(defaultValue = "100") int limit) {
        return R.ok(roleService.listRoles(skip, limit));
    }
    /**
     * 创建角色
     *
     * @param createVO 创建参数
     * @return 创建后的角色信息
     */
    @PostMapping
    public R<RoleRespVO> create(@Valid @RequestBody RoleCreateVO createVO) {
        return R.ok(roleService.createRole(createVO));
    }

    /**
     * 更新角色
     *
     * @param roleId   角色ID
     * @param updateVO 更新参数
     * @return 更新后的角色信息
     */
    @PutMapping("/{roleId}")
    public R<RoleRespVO> update(@PathVariable String roleId,
                                @RequestBody RoleUpdateVO updateVO) {
        return R.ok(roleService.updateRole(roleId, updateVO));
    }

    /**
     * 删除角色
     *
     * @param roleId 角色ID
     * @return 被删除的角色信息
     */
    @DeleteMapping("/{roleId}")
    public R<RoleRespVO> delete(@PathVariable String roleId) {
        return R.ok(roleService.deleteRole(roleId));
    }

    /**
     * 获取角色的权限列表
     *
     * @param roleId 角色ID
     * @return 权限列表
     */
    @GetMapping("/{roleId}/permissions")
    public R<List<PermissionRespVO>> getRolePermissions(@PathVariable String roleId) {
        return R.ok(roleService.getRolePermissions(roleId));
    }

    /**
     * 更新角色的权限列表（全量替换）
     *
     * @param roleId   角色ID
     * @param updateVO 权限ID列表
     * @return 更新后的权限列表
     */
    @PutMapping("/{roleId}/permissions")
    public R<List<PermissionRespVO>> updateRolePermissions(@PathVariable String roleId,
                                                           @Valid @RequestBody RolePermissionUpdateVO updateVO) {
        return R.ok(roleService.updateRolePermissions(roleId, updateVO));
    }

    /**
     * 获取所有权限列表
     *
     * @return 权限列表
     */
    @GetMapping("/permissions/all")
    public R<List<PermissionRespVO>> listAllPermissions() {
        return R.ok(roleService.listAllPermissions());
    }
}

/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service;

import com.llmguard.vo.role.PermissionRespVO;
import com.llmguard.vo.role.RoleCreateVO;
import com.llmguard.vo.role.RolePermissionUpdateVO;
import com.llmguard.vo.role.RoleRespVO;
import com.llmguard.vo.role.RoleUpdateVO;

import java.util.List;

/**
 * 功能描述：角色管理服务接口
 *
 * @date 2024/07/13 16:06
 */
public interface IRoleService {

    /**
     * 获取角色列表
     *
     * @param skip  跳过条数
     * @param limit 限制条数
     * @return 角色列表
     */
    List<RoleRespVO> listRoles(int skip, int limit);

    /**
     * 创建角色
     *
     * @param createVO 创建参数
     * @return 创建后的角色信息
     */
    RoleRespVO createRole(RoleCreateVO createVO);

    /**
     * 更新角色
     *
     * @param roleId   角色ID
     * @param updateVO 更新参数
     * @return 更新后的角色信息
     */
    RoleRespVO updateRole(String roleId, RoleUpdateVO updateVO);

    /**
     * 删除角色（系统角色不可删除）
     *
     * @param roleId 角色ID
     * @return 被删除的角色信息
     */
    RoleRespVO deleteRole(String roleId);

    /**
     * 获取角色的权限列表
     *
     * @param roleId 角色ID
     * @return 权限列表
     */
    List<PermissionRespVO> getRolePermissions(String roleId);

    /**
     * 更新角色的权限列表（全量替换）
     *
     * @param roleId   角色ID
     * @param updateVO 权限ID列表
     * @return 更新后的权限列表
     */
    List<PermissionRespVO> updateRolePermissions(String roleId, RolePermissionUpdateVO updateVO);

    /**
     * 获取所有权限列表
     *
     * @return 权限列表
     */
    List<PermissionRespVO> listAllPermissions();
}

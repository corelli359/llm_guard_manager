/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.llmguard.common.exception.BusinessException;
import com.llmguard.entity.PermissionDO;
import com.llmguard.entity.RoleDO;
import com.llmguard.entity.RolePermissionDO;
import com.llmguard.mapper.PermissionMapper;
import com.llmguard.mapper.RoleMapper;
import com.llmguard.mapper.RolePermissionMapper;
import com.llmguard.service.IRoleService;
import com.llmguard.vo.role.PermissionRespVO;
import com.llmguard.vo.role.RoleCreateVO;
import com.llmguard.vo.role.RolePermissionUpdateVO;
import com.llmguard.vo.role.RoleRespVO;
import com.llmguard.vo.role.RoleUpdateVO;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * 功能描述：角色管理服务实现
 *
 * @date 2024/07/13 16:06
 */
@Service
public class RoleServiceImpl implements IRoleService {

    private static final Logger log = LoggerFactory.getLogger(RoleServiceImpl.class);

    private final RoleMapper roleMapper;
    private final PermissionMapper permissionMapper;
    private final RolePermissionMapper rolePermissionMapper;

    public RoleServiceImpl(RoleMapper roleMapper,
                           PermissionMapper permissionMapper,
                           RolePermissionMapper rolePermissionMapper) {
        this.roleMapper = roleMapper;
        this.permissionMapper = permissionMapper;
        this.rolePermissionMapper = rolePermissionMapper;
    }
    @Override
    public List<RoleRespVO> listRoles(int skip, int limit) {
        Page<RoleDO> page = new Page<>(skip / Math.max(limit, 1) + 1, limit);
        Page<RoleDO> result = roleMapper.selectPage(page, null);
        return result.getRecords().stream().map(this::toRespVO).collect(Collectors.toList());
    }

    @Override
    public RoleRespVO createRole(RoleCreateVO createVO) {
        // roleCode 唯一性校验
        Long count = roleMapper.selectCount(
                new LambdaQueryWrapper<RoleDO>().eq(RoleDO::getRoleCode, createVO.getRoleCode())
        );
        if (count > 0) {
            throw new BusinessException("角色编码已存在: " + createVO.getRoleCode());
        }

        RoleDO entity = new RoleDO();
        entity.setRoleCode(createVO.getRoleCode());
        entity.setRoleName(createVO.getRoleName());
        entity.setRoleType(createVO.getRoleType());
        entity.setDescription(createVO.getDescription());
        entity.setIsSystem(false);
        entity.setIsActive(true);
        roleMapper.insert(entity);
        log.info("角色创建成功: {}", createVO.getRoleCode());
        return toRespVO(entity);
    }

    @Override
    public RoleRespVO updateRole(String roleId, RoleUpdateVO updateVO) {
        RoleDO entity = roleMapper.selectById(roleId);
        if (entity == null) {
            throw new BusinessException(404, "角色不存在");
        }
        if (updateVO.getRoleName() != null) {
            entity.setRoleName(updateVO.getRoleName());
        }
        if (updateVO.getRoleType() != null) {
            entity.setRoleType(updateVO.getRoleType());
        }
        if (updateVO.getDescription() != null) {
            entity.setDescription(updateVO.getDescription());
        }
        if (updateVO.getIsActive() != null) {
            entity.setIsActive(updateVO.getIsActive());
        }
        roleMapper.updateById(entity);
        log.info("角色更新: roleId={}", roleId);
        return toRespVO(entity);
    }
    @Override
    public RoleRespVO deleteRole(String roleId) {
        RoleDO entity = roleMapper.selectById(roleId);
        if (entity == null) {
            throw new BusinessException(404, "角色不存在");
        }
        if (Boolean.TRUE.equals(entity.getIsSystem())) {
            throw new BusinessException("系统内置角色不可删除");
        }
        // 同时删除角色的权限关联
        rolePermissionMapper.delete(
                new LambdaQueryWrapper<RolePermissionDO>().eq(RolePermissionDO::getRoleId, roleId)
        );
        roleMapper.deleteById(roleId);
        log.info("角色删除: roleId={}, roleCode={}", roleId, entity.getRoleCode());
        return toRespVO(entity);
    }

    @Override
    public List<PermissionRespVO> getRolePermissions(String roleId) {
        RoleDO role = roleMapper.selectById(roleId);
        if (role == null) {
            throw new BusinessException(404, "角色不存在");
        }
        List<RolePermissionDO> rpList = rolePermissionMapper.selectList(
                new LambdaQueryWrapper<RolePermissionDO>().eq(RolePermissionDO::getRoleId, roleId)
        );
        if (rpList.isEmpty()) {
            return new ArrayList<>();
        }
        Set<String> permIds = rpList.stream()
                .map(RolePermissionDO::getPermissionId).collect(Collectors.toSet());
        List<PermissionDO> perms = permissionMapper.selectBatchIds(permIds);
        return perms.stream().map(this::toPermRespVO).collect(Collectors.toList());
    }
    @Override
    @Transactional(rollbackFor = Exception.class)
    public List<PermissionRespVO> updateRolePermissions(String roleId, RolePermissionUpdateVO updateVO) {
        RoleDO role = roleMapper.selectById(roleId);
        if (role == null) {
            throw new BusinessException(404, "角色不存在");
        }
        // 先删除旧的权限关联
        rolePermissionMapper.delete(
                new LambdaQueryWrapper<RolePermissionDO>().eq(RolePermissionDO::getRoleId, roleId)
        );
        // 再插入新的权限关联
        for (String permId : updateVO.getPermissionIds()) {
            RolePermissionDO rp = new RolePermissionDO();
            rp.setRoleId(roleId);
            rp.setPermissionId(permId);
            rolePermissionMapper.insert(rp);
        }
        log.info("角色权限更新: roleId={}, permCount={}", roleId, updateVO.getPermissionIds().size());
        return getRolePermissions(roleId);
    }

    @Override
    public List<PermissionRespVO> listAllPermissions() {
        List<PermissionDO> perms = permissionMapper.selectList(
                new LambdaQueryWrapper<PermissionDO>()
                        .eq(PermissionDO::getIsActive, true)
                        .orderByAsc(PermissionDO::getSortOrder)
        );
        return perms.stream().map(this::toPermRespVO).collect(Collectors.toList());
    }

    /**
     * RoleDO 转 RoleRespVO
     *
     * @param entity 角色实体
     * @return 角色响应 VO
     */
    private RoleRespVO toRespVO(RoleDO entity) {
        RoleRespVO vo = new RoleRespVO();
        vo.setId(entity.getId());
        vo.setRoleCode(entity.getRoleCode());
        vo.setRoleName(entity.getRoleName());
        vo.setRoleType(entity.getRoleType());
        vo.setDescription(entity.getDescription());
        vo.setIsSystem(entity.getIsSystem());
        vo.setIsActive(entity.getIsActive());
        vo.setCreatedAt(entity.getCreatedAt());
        // 查询权限数量
        Long permCount = rolePermissionMapper.selectCount(
                new LambdaQueryWrapper<RolePermissionDO>().eq(RolePermissionDO::getRoleId, entity.getId())
        );
        vo.setPermissionCount(permCount != null ? permCount.intValue() : 0);
        return vo;
    }

    /**
     * PermissionDO 转 PermissionRespVO
     *
     * @param entity 权限实体
     * @return 权限响应 VO
     */
    private PermissionRespVO toPermRespVO(PermissionDO entity) {
        PermissionRespVO vo = new PermissionRespVO();
        vo.setId(entity.getId());
        vo.setPermissionCode(entity.getPermissionCode());
        vo.setPermissionName(entity.getPermissionName());
        vo.setPermissionType(entity.getPermissionType());
        vo.setScope(entity.getScope());
        vo.setParentCode(entity.getParentCode());
        vo.setSortOrder(entity.getSortOrder() != null ? entity.getSortOrder() : 0);
        return vo;
    }
}

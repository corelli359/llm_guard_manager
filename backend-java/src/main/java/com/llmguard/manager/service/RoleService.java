package com.llmguard.manager.service;

import com.llmguard.manager.domain.dto.*;
import com.llmguard.manager.domain.entity.Permission;
import com.llmguard.manager.domain.entity.Role;
import com.llmguard.manager.domain.entity.RolePermission;
import com.llmguard.manager.repository.PermissionRepository;
import com.llmguard.manager.repository.RolePermissionRepository;
import com.llmguard.manager.repository.RoleRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class RoleService {

    private final RoleRepository roleRepository;
    private final RolePermissionRepository rolePermissionRepository;
    private final PermissionRepository permissionRepository;

    public List<RoleResponse> getAllRoles() {
        return roleRepository.findAll().stream()
                .map(role -> {
                    int permCount = rolePermissionRepository.findByRoleId(role.getId()).size();
                    return toRoleResponse(role, permCount);
                })
                .collect(Collectors.toList());
    }

    @Transactional
    public RoleResponse createRole(RoleCreate dto) {
        if (roleRepository.existsByRoleCode(dto.getRoleCode())) {
            throw new IllegalArgumentException("Role code already exists: " + dto.getRoleCode());
        }
        Role role = Role.builder()
                .id(UUID.randomUUID().toString())
                .roleCode(dto.getRoleCode())
                .roleName(dto.getRoleName())
                .roleType(dto.getRoleType() != null ? dto.getRoleType() : "GLOBAL")
                .description(dto.getDescription())
                .isSystem(false)
                .isActive(true)
                .createdAt(LocalDateTime.now())
                .build();
        roleRepository.save(role);
        return toRoleResponse(role, 0);
    }

    @Transactional
    public RoleResponse updateRole(String id, RoleUpdate dto) {
        Role role = roleRepository.findById(id)
                .orElseThrow(() -> new NoSuchElementException("Role not found"));

        if (dto.getRoleName() != null) role.setRoleName(dto.getRoleName());
        if (dto.getRoleType() != null) role.setRoleType(dto.getRoleType());
        if (dto.getDescription() != null) role.setDescription(dto.getDescription());
        if (dto.getIsActive() != null) role.setIsActive(dto.getIsActive());
        role.setUpdatedAt(LocalDateTime.now());

        roleRepository.save(role);
        int permCount = rolePermissionRepository.findByRoleId(role.getId()).size();
        return toRoleResponse(role, permCount);
    }

    @Transactional
    public void deleteRole(String id) {
        Role role = roleRepository.findById(id)
                .orElseThrow(() -> new NoSuchElementException("Role not found"));
        if (Boolean.TRUE.equals(role.getIsSystem())) {
            throw new IllegalArgumentException("Cannot delete system role");
        }
        rolePermissionRepository.deleteByRoleId(id);
        roleRepository.delete(role);
    }

    public List<PermissionResponse> getRolePermissions(String roleId) {
        roleRepository.findById(roleId)
                .orElseThrow(() -> new NoSuchElementException("Role not found"));
        List<RolePermission> rps = rolePermissionRepository.findByRoleId(roleId);
        List<String> permIds = rps.stream()
                .map(RolePermission::getPermissionId)
                .collect(Collectors.toList());
        if (permIds.isEmpty()) return Collections.emptyList();
        return permissionRepository.findAllById(permIds).stream()
                .map(this::toPermissionResponse)
                .collect(Collectors.toList());
    }

    @Transactional
    public List<PermissionResponse> updateRolePermissions(String roleId, List<String> permissionIds) {
        roleRepository.findById(roleId)
                .orElseThrow(() -> new NoSuchElementException("Role not found"));
        rolePermissionRepository.deleteByRoleId(roleId);
        List<RolePermission> newRps = new ArrayList<>();
        for (String permId : permissionIds) {
            RolePermission rp = RolePermission.builder()
                    .id(UUID.randomUUID().toString())
                    .roleId(roleId)
                    .permissionId(permId)
                    .createdAt(LocalDateTime.now())
                    .build();
            newRps.add(rp);
        }
        rolePermissionRepository.saveAll(newRps);
        return getRolePermissions(roleId);
    }

    public List<PermissionResponse> getAllPermissions() {
        return permissionRepository.findAll().stream()
                .map(this::toPermissionResponse)
                .collect(Collectors.toList());
    }

    private RoleResponse toRoleResponse(Role role, int permissionCount) {
        return RoleResponse.builder()
                .id(role.getId())
                .roleCode(role.getRoleCode())
                .roleName(role.getRoleName())
                .roleType(role.getRoleType())
                .description(role.getDescription())
                .isSystem(role.getIsSystem())
                .isActive(role.getIsActive())
                .createdAt(role.getCreatedAt())
                .permissionCount(permissionCount)
                .build();
    }

    private PermissionResponse toPermissionResponse(Permission p) {
        return PermissionResponse.builder()
                .id(p.getId())
                .permissionCode(p.getPermissionCode())
                .permissionName(p.getPermissionName())
                .permissionType(p.getPermissionType())
                .scope(p.getScope())
                .parentCode(p.getParentCode())
                .sortOrder(p.getSortOrder())
                .description(p.getDescription())
                .isActive(p.getIsActive())
                .build();
    }
}

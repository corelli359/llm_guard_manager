package com.llmguard.manager.service;

import com.llmguard.manager.domain.dto.*;
import com.llmguard.manager.domain.entity.*;
import com.llmguard.manager.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class UserManagementService {

    private final UserRepository userRepository;
    private final UserScenarioAssignmentRepository assignmentRepository;
    private final ScenarioAdminPermissionRepository permissionRepository;
    private final UserScenarioRoleRepository scenarioRoleRepository;
    private final RoleRepository roleRepository;
    private final RolePermissionRepository rolePermissionRepository;
    private final PermissionRepository permRepo;

    private static final Set<String> VALID_ROLES = Set.of(
            "SYSTEM_ADMIN", "SCENARIO_ADMIN", "ANNOTATOR", "AUDITOR"
    );

    public List<UserListResponse> getAllUsers() {
        return userRepository.findAll().stream()
                .map(this::toUserListResponse)
                .collect(Collectors.toList());
    }

    @Transactional
    public UserListResponse updateUserRole(String userId, String newRole, User currentUser) {
        if (currentUser.getId().equals(userId)) {
            throw new IllegalArgumentException("Cannot modify your own account");
        }
        if (!VALID_ROLES.contains(newRole)) {
            throw new IllegalArgumentException("Invalid role: " + newRole);
        }
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new NoSuchElementException("User not found"));
        user.setRole(newRole);
        user.setUpdatedAt(LocalDateTime.now());
        userRepository.save(user);
        return toUserListResponse(user);
    }

    @Transactional
    public UserListResponse updateUserStatus(String userId, Boolean isActive, User currentUser) {
        if (currentUser.getId().equals(userId)) {
            throw new IllegalArgumentException("Cannot modify your own account");
        }
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new NoSuchElementException("User not found"));
        user.setIsActive(isActive);
        user.setUpdatedAt(LocalDateTime.now());
        userRepository.save(user);
        return toUserListResponse(user);
    }

    @Transactional
    public void deleteUser(String userId, User currentUser) {
        if (currentUser.getId().equals(userId)) {
            throw new IllegalArgumentException("Cannot modify your own account");
        }
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new NoSuchElementException("User not found"));
        // Delete associated scenario assignments and permissions
        List<UserScenarioAssignment> assignments = assignmentRepository.findByUserId(userId);
        for (UserScenarioAssignment a : assignments) {
            permissionRepository.findByUserIdAndScenarioId(userId, a.getScenarioId())
                    .ifPresent(permissionRepository::delete);
        }
        assignmentRepository.deleteAll(assignments);
        scenarioRoleRepository.findByUserId(userId).forEach(scenarioRoleRepository::delete);
        userRepository.delete(user);
    }

    @Transactional
    public ScenarioAssignmentResponse assignScenario(String userId, ScenarioAssignmentCreate dto, User currentUser) {
        userRepository.findById(userId)
                .orElseThrow(() -> new NoSuchElementException("User not found"));
        if (assignmentRepository.existsByUserIdAndScenarioId(userId, dto.getScenarioId())) {
            throw new IllegalArgumentException("User already assigned to this scenario");
        }
        UserScenarioAssignment assignment = UserScenarioAssignment.builder()
                .id(UUID.randomUUID().toString())
                .userId(userId)
                .scenarioId(dto.getScenarioId())
                .role(dto.getRole())
                .createdAt(LocalDateTime.now())
                .createdBy(currentUser.getId())
                .build();
        assignmentRepository.save(assignment);
        return toAssignmentResponse(assignment);
    }

    @Transactional
    public void removeScenarioAssignment(String assignmentId) {
        UserScenarioAssignment assignment = assignmentRepository.findById(assignmentId)
                .orElseThrow(() -> new NoSuchElementException("Assignment not found"));
        permissionRepository.findByUserIdAndScenarioId(assignment.getUserId(), assignment.getScenarioId())
                .ifPresent(permissionRepository::delete);
        assignmentRepository.delete(assignment);
    }

    @Transactional
    public ScenarioPermissionDetail configurePermissions(String userId, String scenarioId,
                                                          ScenarioPermissionUpdate dto, User currentUser) {
        userRepository.findById(userId)
                .orElseThrow(() -> new NoSuchElementException("User not found"));

        ScenarioAdminPermission perm = permissionRepository.findByUserIdAndScenarioId(userId, scenarioId)
                .orElse(ScenarioAdminPermission.builder()
                        .id(UUID.randomUUID().toString())
                        .userId(userId)
                        .scenarioId(scenarioId)
                        .scenarioBasicInfo(false)
                        .scenarioKeywords(false)
                        .scenarioPolicies(false)
                        .playground(false)
                        .performanceTest(false)
                        .createdAt(LocalDateTime.now())
                        .createdBy(currentUser.getId())
                        .build());

        if (dto.getScenarioBasicInfo() != null) perm.setScenarioBasicInfo(dto.getScenarioBasicInfo());
        if (dto.getScenarioKeywords() != null) perm.setScenarioKeywords(dto.getScenarioKeywords());
        if (dto.getScenarioPolicies() != null) perm.setScenarioPolicies(dto.getScenarioPolicies());
        if (dto.getPlayground() != null) perm.setPlayground(dto.getPlayground());
        if (dto.getPerformanceTest() != null) perm.setPerformanceTest(dto.getPerformanceTest());
        perm.setUpdatedAt(LocalDateTime.now());

        permissionRepository.save(perm);
        return toPermissionDetail(perm);
    }

    public List<ScenarioAssignmentResponse> getUserScenarios(String userId) {
        List<UserScenarioAssignment> assignments = assignmentRepository.findByUserId(userId);
        return assignments.stream()
                .map(this::toAssignmentResponse)
                .collect(Collectors.toList());
    }

    public List<UserRoleResponse> getUserRoleAssignments(String userId) {
        List<UserScenarioRole> roles = scenarioRoleRepository.findByUserId(userId);
        return roles.stream().map(usr -> {
            UserRoleResponse.UserRoleResponseBuilder builder = UserRoleResponse.builder()
                    .id(usr.getId())
                    .userId(usr.getUserId())
                    .scenarioId(usr.getScenarioId())
                    .roleId(usr.getRoleId())
                    .createdAt(usr.getCreatedAt());
            roleRepository.findById(usr.getRoleId()).ifPresent(role -> {
                builder.roleName(role.getRoleName());
                builder.roleCode(role.getRoleCode());
            });
            return builder.build();
        }).collect(Collectors.toList());
    }

    @Transactional
    public UserRoleResponse assignRole(String userId, UserRoleAssign dto, User currentUser) {
        userRepository.findById(userId)
                .orElseThrow(() -> new NoSuchElementException("User not found"));
        Role role = roleRepository.findById(dto.getRoleId())
                .orElseThrow(() -> new NoSuchElementException("Role not found"));

        UserScenarioRole usr = UserScenarioRole.builder()
                .id(UUID.randomUUID().toString())
                .userId(userId)
                .scenarioId(dto.getScenarioId())
                .roleId(dto.getRoleId())
                .createdAt(LocalDateTime.now())
                .createdBy(currentUser.getId())
                .build();
        scenarioRoleRepository.save(usr);

        return UserRoleResponse.builder()
                .id(usr.getId())
                .userId(usr.getUserId())
                .scenarioId(usr.getScenarioId())
                .roleId(usr.getRoleId())
                .roleName(role.getRoleName())
                .roleCode(role.getRoleCode())
                .createdAt(usr.getCreatedAt())
                .build();
    }

    @Transactional
    public void removeRoleAssignment(String assignmentId) {
        UserScenarioRole usr = scenarioRoleRepository.findById(assignmentId)
                .orElseThrow(() -> new NoSuchElementException("Role assignment not found"));
        scenarioRoleRepository.delete(usr);
    }

    public Map<String, Object> getCurrentUserPermissions(User user) {
        // 查询用户所有角色分配 (RBAC V2)
        List<UserScenarioRole> assignments = scenarioRoleRepository.findByUserId(user.getId());

        Set<String> globalPerms = new LinkedHashSet<>();
        Map<String, Set<String>> scenarioPerms = new LinkedHashMap<>();

        for (UserScenarioRole assignment : assignments) {
            // 获取该角色的所有权限
            List<RolePermission> rps = rolePermissionRepository.findByRoleId(assignment.getRoleId());
            List<String> permCodes = new ArrayList<>();
            for (RolePermission rp : rps) {
                permRepo.findById(rp.getPermissionId())
                        .filter(Permission::getIsActive)
                        .ifPresent(p -> permCodes.add(p.getPermissionCode()));
            }

            if (assignment.getScenarioId() == null) {
                // 全局角色
                globalPerms.addAll(permCodes);
            } else {
                // 场景角色
                scenarioPerms.computeIfAbsent(assignment.getScenarioId(), k -> new LinkedHashSet<>())
                        .addAll(permCodes);
            }
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("user_id", user.getUserId() != null ? user.getUserId() : user.getId());
        result.put("global_permissions", new ArrayList<>(globalPerms));
        Map<String, List<String>> scenarioPermsList = new LinkedHashMap<>();
        scenarioPerms.forEach((k, v) -> scenarioPermsList.put(k, new ArrayList<>(v)));
        result.put("scenario_permissions", scenarioPermsList);
        return result;
    }

    private UserListResponse toUserListResponse(User user) {
        return UserListResponse.builder()
                .id(user.getId())
                .userId(user.getUserId())
                .username(user.getUsername())
                .displayName(user.getDisplayName())
                .role(user.getRole())
                .email(user.getEmail())
                .isActive(user.getIsActive())
                .createdAt(user.getCreatedAt())
                .build();
    }

    private ScenarioAssignmentResponse toAssignmentResponse(UserScenarioAssignment assignment) {
        ScenarioPermissionDetail permDetail = permissionRepository
                .findByUserIdAndScenarioId(assignment.getUserId(), assignment.getScenarioId())
                .map(this::toPermissionDetail)
                .orElse(null);

        return ScenarioAssignmentResponse.builder()
                .id(assignment.getId())
                .userId(assignment.getUserId())
                .scenarioId(assignment.getScenarioId())
                .role(assignment.getRole())
                .createdAt(assignment.getCreatedAt())
                .permissions(permDetail)
                .build();
    }

    private ScenarioPermissionDetail toPermissionDetail(ScenarioAdminPermission perm) {
        return ScenarioPermissionDetail.builder()
                .scenarioBasicInfo(perm.getScenarioBasicInfo())
                .scenarioKeywords(perm.getScenarioKeywords())
                .scenarioPolicies(perm.getScenarioPolicies())
                .playground(perm.getPlayground())
                .performanceTest(perm.getPerformanceTest())
                .build();
    }
}

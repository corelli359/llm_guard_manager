package com.llmguard.manager.service;

import com.llmguard.manager.domain.dto.UserPermissionResponse;
import com.llmguard.manager.domain.entity.Scenario;
import com.llmguard.manager.domain.entity.ScenarioAdminPermission;
import com.llmguard.manager.domain.entity.User;
import com.llmguard.manager.domain.entity.UserScenarioAssignment;
import com.llmguard.manager.repository.ScenarioAdminPermissionRepository;
import com.llmguard.manager.repository.ScenarioRepository;
import com.llmguard.manager.repository.UserScenarioAssignmentRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class PermissionService {

    private final ScenarioAdminPermissionRepository permissionRepository;
    private final UserScenarioAssignmentRepository assignmentRepository;
    private final ScenarioRepository scenarioRepository;

    public boolean checkScenarioPermission(User user, String scenarioId, String permission) {
        if (user == null) {
            return false;
        }

        String role = user.getRole();

        // SYSTEM_ADMIN has all permissions
        if ("SYSTEM_ADMIN".equals(role)) {
            return true;
        }

        // AUDITOR has read-only, no modification permissions
        if ("AUDITOR".equals(role)) {
            return false;
        }

        // ANNOTATOR has no scenario config permissions
        if ("ANNOTATOR".equals(role)) {
            return false;
        }

        // SCENARIO_ADMIN: check fine-grained permissions
        if ("SCENARIO_ADMIN".equals(role)) {
            // Check if user has access to this scenario
            if (!assignmentRepository.existsByUserIdAndScenarioId(user.getId(), scenarioId)) {
                return false;
            }

            // Check fine-grained permission
            Optional<ScenarioAdminPermission> permConfig =
                    permissionRepository.findByUserIdAndScenarioId(user.getId(), scenarioId);

            if (permConfig.isEmpty()) {
                return false;
            }

            return getPermissionValue(permConfig.get(), permission);
        }

        return false;
    }

    private boolean getPermissionValue(ScenarioAdminPermission perm, String permission) {
        return switch (permission) {
            case "scenario_basic_info" -> Boolean.TRUE.equals(perm.getScenarioBasicInfo());
            case "scenario_keywords" -> Boolean.TRUE.equals(perm.getScenarioKeywords());
            case "scenario_policies" -> Boolean.TRUE.equals(perm.getScenarioPolicies());
            case "playground" -> Boolean.TRUE.equals(perm.getPlayground());
            case "performance_test" -> Boolean.TRUE.equals(perm.getPerformanceTest());
            default -> false;
        };
    }
    public UserPermissionResponse getUserPermissions(User user) {
        if (user == null) {
            return UserPermissionResponse.builder()
                    .role(null)
                    .scenarios(Collections.emptyList())
                    .build();
        }

        String role = user.getRole();
        List<UserPermissionResponse.ScenarioPermission> scenarioPermissions = new ArrayList<>();

        if ("SYSTEM_ADMIN".equals(role)) {
            // SYSTEM_ADMIN gets all active scenarios with full permissions
            List<Scenario> scenarios = scenarioRepository.findAll().stream()
                    .filter(s -> Boolean.TRUE.equals(s.getIsActive()))
                    .collect(Collectors.toList());

            Map<String, Boolean> fullPerms = Map.of(
                    "scenario_basic_info", true,
                    "scenario_keywords", true,
                    "scenario_policies", true,
                    "playground", true,
                    "performance_test", true
            );

            for (Scenario scenario : scenarios) {
                scenarioPermissions.add(UserPermissionResponse.ScenarioPermission.builder()
                        .scenarioId(scenario.getAppId())
                        .scenarioName(scenario.getAppName())
                        .role("SYSTEM_ADMIN")
                        .permissions(new LinkedHashMap<>(fullPerms))
                        .build());
            }
        } else if ("AUDITOR".equals(role)) {
            // AUDITOR gets all active scenarios with no modification permissions
            List<Scenario> scenarios = scenarioRepository.findAll().stream()
                    .filter(s -> Boolean.TRUE.equals(s.getIsActive()))
                    .collect(Collectors.toList());

            Map<String, Boolean> noPerms = Map.of(
                    "scenario_basic_info", false,
                    "scenario_keywords", false,
                    "scenario_policies", false,
                    "playground", false,
                    "performance_test", false
            );

            for (Scenario scenario : scenarios) {
                scenarioPermissions.add(UserPermissionResponse.ScenarioPermission.builder()
                        .scenarioId(scenario.getAppId())
                        .scenarioName(scenario.getAppName())
                        .role("AUDITOR")
                        .permissions(new LinkedHashMap<>(noPerms))
                        .build());
            }

        } else if ("SCENARIO_ADMIN".equals(role) || "ANNOTATOR".equals(role)) {
            // Get assigned scenarios
            List<UserScenarioAssignment> assignments = assignmentRepository.findByUserId(user.getId());

            for (UserScenarioAssignment assignment : assignments) {
                Optional<Scenario> scenarioOpt = scenarioRepository.findByAppId(assignment.getScenarioId());
                if (scenarioOpt.isEmpty()) {
                    continue;
                }
                Scenario scenario = scenarioOpt.get();

                Map<String, Boolean> perms;
                if ("SCENARIO_ADMIN".equals(assignment.getRole())) {
                    Optional<ScenarioAdminPermission> permConfig =
                            permissionRepository.findByUserIdAndScenarioId(user.getId(), assignment.getScenarioId());

                    if (permConfig.isPresent()) {
                        ScenarioAdminPermission p = permConfig.get();
                        perms = new LinkedHashMap<>();
                        perms.put("scenario_basic_info", Boolean.TRUE.equals(p.getScenarioBasicInfo()));
                        perms.put("scenario_keywords", Boolean.TRUE.equals(p.getScenarioKeywords()));
                        perms.put("scenario_policies", Boolean.TRUE.equals(p.getScenarioPolicies()));
                        perms.put("playground", Boolean.TRUE.equals(p.getPlayground()));
                        perms.put("performance_test", Boolean.TRUE.equals(p.getPerformanceTest()));
                    } else {
                        // Default permissions for SCENARIO_ADMIN without config
                        perms = new LinkedHashMap<>();
                        perms.put("scenario_basic_info", true);
                        perms.put("scenario_keywords", true);
                        perms.put("scenario_policies", false);
                        perms.put("playground", true);
                        perms.put("performance_test", false);
                    }
                } else {
                    // ANNOTATOR has no config permissions
                    perms = new LinkedHashMap<>();
                    perms.put("scenario_basic_info", false);
                    perms.put("scenario_keywords", false);
                    perms.put("scenario_policies", false);
                    perms.put("playground", false);
                    perms.put("performance_test", false);
                }

                scenarioPermissions.add(UserPermissionResponse.ScenarioPermission.builder()
                        .scenarioId(assignment.getScenarioId())
                        .scenarioName(scenario.getAppName())
                        .role(assignment.getRole())
                        .permissions(perms)
                        .build());
            }
        }

        return UserPermissionResponse.builder()
                .role(role)
                .scenarios(scenarioPermissions)
                .build();
    }

    public List<String> getUserScenarioIds(User user) {
        if (user == null) {
            return Collections.emptyList();
        }

        // SYSTEM_ADMIN and AUDITOR can access all scenarios
        if ("SYSTEM_ADMIN".equals(user.getRole()) || "AUDITOR".equals(user.getRole())) {
            return scenarioRepository.findAll().stream()
                    .filter(s -> Boolean.TRUE.equals(s.getIsActive()))
                    .map(Scenario::getAppId)
                    .collect(Collectors.toList());
        }

        // SCENARIO_ADMIN and ANNOTATOR only access assigned scenarios
        return assignmentRepository.findByUserId(user.getId()).stream()
                .map(UserScenarioAssignment::getScenarioId)
                .collect(Collectors.toList());
    }
}

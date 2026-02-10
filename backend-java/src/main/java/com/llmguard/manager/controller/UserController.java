package com.llmguard.manager.controller;

import com.llmguard.manager.domain.dto.*;
import com.llmguard.manager.domain.entity.User;
import com.llmguard.manager.service.UserManagementService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;

@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {

    private final UserManagementService userManagementService;

    private User getCurrentUser() {
        return (User) SecurityContextHolder.getContext()
                .getAuthentication().getPrincipal();
    }

    private boolean isSystemAdmin(User user) {
        return "SYSTEM_ADMIN".equals(user.getRole());
    }

    @GetMapping("/")
    public ResponseEntity<?> listUsers() {
        User current = getCurrentUser();
        if (!isSystemAdmin(current)) {
            return ResponseEntity.status(403)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can access this resource"));
        }
        List<UserListResponse> users = userManagementService.getAllUsers();
        return ResponseEntity.ok(users);
    }

    @PutMapping("/{userId}/role")
    public ResponseEntity<?> updateUserRole(@PathVariable String userId,
                                            @RequestBody UserRoleUpdate dto) {
        User current = getCurrentUser();
        if (!isSystemAdmin(current)) {
            return ResponseEntity.status(403)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can access this resource"));
        }
        try {
            UserListResponse updated = userManagementService.updateUserRole(userId, dto.getRole(), current);
            return ResponseEntity.ok(updated);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("detail", e.getMessage()));
        } catch (NoSuchElementException e) {
            return ResponseEntity.status(404).body(Map.of("detail", e.getMessage()));
        }
    }

    @PatchMapping("/{userId}/status")
    public ResponseEntity<?> updateUserStatus(@PathVariable String userId,
                                              @RequestBody UserStatusUpdate dto) {
        User current = getCurrentUser();
        if (!isSystemAdmin(current)) {
            return ResponseEntity.status(403)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can access this resource"));
        }
        try {
            UserListResponse updated = userManagementService.updateUserStatus(userId, dto.getIsActive(), current);
            return ResponseEntity.ok(updated);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("detail", e.getMessage()));
        } catch (NoSuchElementException e) {
            return ResponseEntity.status(404).body(Map.of("detail", e.getMessage()));
        }
    }

    @DeleteMapping("/{userId}")
    public ResponseEntity<?> deleteUser(@PathVariable String userId) {
        User current = getCurrentUser();
        if (!isSystemAdmin(current)) {
            return ResponseEntity.status(403)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can access this resource"));
        }
        try {
            userManagementService.deleteUser(userId, current);
            return ResponseEntity.ok(Map.of("detail", "User deleted"));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("detail", e.getMessage()));
        } catch (NoSuchElementException e) {
            return ResponseEntity.status(404).body(Map.of("detail", e.getMessage()));
        }
    }

    @GetMapping("/{userId}/scenarios")
    public ResponseEntity<?> getUserScenarios(@PathVariable String userId) {
        User current = getCurrentUser();
        if (!isSystemAdmin(current)) {
            return ResponseEntity.status(403)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can access this resource"));
        }
        try {
            List<ScenarioAssignmentResponse> scenarios = userManagementService.getUserScenarios(userId);
            return ResponseEntity.ok(scenarios);
        } catch (NoSuchElementException e) {
            return ResponseEntity.status(404).body(Map.of("detail", e.getMessage()));
        }
    }

    @PostMapping("/{userId}/scenarios")
    public ResponseEntity<?> assignScenario(@PathVariable String userId,
                                            @RequestBody ScenarioAssignmentCreate dto) {
        User current = getCurrentUser();
        if (!isSystemAdmin(current)) {
            return ResponseEntity.status(403)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can access this resource"));
        }
        try {
            ScenarioAssignmentResponse resp = userManagementService.assignScenario(userId, dto, current);
            return ResponseEntity.ok(resp);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("detail", e.getMessage()));
        } catch (NoSuchElementException e) {
            return ResponseEntity.status(404).body(Map.of("detail", e.getMessage()));
        }
    }

    @DeleteMapping("/{userId}/scenarios/{assignmentId}")
    public ResponseEntity<?> removeScenarioAssignment(@PathVariable String userId,
                                                       @PathVariable String assignmentId) {
        User current = getCurrentUser();
        if (!isSystemAdmin(current)) {
            return ResponseEntity.status(403)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can access this resource"));
        }
        try {
            userManagementService.removeScenarioAssignment(assignmentId);
            return ResponseEntity.ok(Map.of("detail", "Assignment removed"));
        } catch (NoSuchElementException e) {
            return ResponseEntity.status(404).body(Map.of("detail", e.getMessage()));
        }
    }

    @PutMapping("/{userId}/scenarios/{scenarioId}/permissions")
    public ResponseEntity<?> configurePermissions(@PathVariable String userId,
                                                   @PathVariable String scenarioId,
                                                   @RequestBody ScenarioPermissionUpdate dto) {
        User current = getCurrentUser();
        if (!isSystemAdmin(current)) {
            return ResponseEntity.status(403)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can access this resource"));
        }
        try {
            ScenarioPermissionDetail detail = userManagementService.configurePermissions(
                    userId, scenarioId, dto, current);
            return ResponseEntity.ok(detail);
        } catch (NoSuchElementException e) {
            return ResponseEntity.status(404).body(Map.of("detail", e.getMessage()));
        }
    }

    @GetMapping("/{userId}/roles")
    public ResponseEntity<?> getUserRoles(@PathVariable String userId) {
        try {
            List<UserRoleResponse> roles = userManagementService.getUserRoleAssignments(userId);
            return ResponseEntity.ok(roles);
        } catch (NoSuchElementException e) {
            return ResponseEntity.status(404).body(Map.of("detail", e.getMessage()));
        }
    }

    @PostMapping("/{userId}/roles")
    public ResponseEntity<?> assignRole(@PathVariable String userId,
                                        @RequestBody UserRoleAssign dto) {
        User current = getCurrentUser();
        if (!isSystemAdmin(current)) {
            return ResponseEntity.status(403)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can access this resource"));
        }
        try {
            UserRoleResponse resp = userManagementService.assignRole(userId, dto, current);
            return ResponseEntity.ok(resp);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("detail", e.getMessage()));
        } catch (NoSuchElementException e) {
            return ResponseEntity.status(404).body(Map.of("detail", e.getMessage()));
        }
    }

    @DeleteMapping("/{userId}/roles/{assignmentId}")
    public ResponseEntity<?> removeRoleAssignment(@PathVariable String userId,
                                                   @PathVariable String assignmentId) {
        User current = getCurrentUser();
        if (!isSystemAdmin(current)) {
            return ResponseEntity.status(403)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can access this resource"));
        }
        try {
            userManagementService.removeRoleAssignment(assignmentId);
            return ResponseEntity.ok(Map.of("detail", "Role assignment removed"));
        } catch (NoSuchElementException e) {
            return ResponseEntity.status(404).body(Map.of("detail", e.getMessage()));
        }
    }

    @GetMapping("/me/permissions")
    public ResponseEntity<?> getMyPermissions() {
        User current = getCurrentUser();
        Map<String, Object> perms = userManagementService.getCurrentUserPermissions(current);
        return ResponseEntity.ok(perms);
    }
}

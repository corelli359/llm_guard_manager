package com.llmguard.manager.controller;

import com.llmguard.manager.domain.dto.*;
import com.llmguard.manager.domain.entity.User;
import com.llmguard.manager.service.RoleService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;

@RestController
@RequestMapping("/roles")
@RequiredArgsConstructor
public class RoleController {

    private final RoleService roleService;

    private User getCurrentUser() {
        return (User) SecurityContextHolder.getContext()
                .getAuthentication().getPrincipal();
    }

    private boolean isSystemAdmin(User user) {
        return "SYSTEM_ADMIN".equals(user.getRole());
    }

    @GetMapping("/")
    public ResponseEntity<List<RoleResponse>> listRoles() {
        return ResponseEntity.ok(roleService.getAllRoles());
    }

    @PostMapping("/")
    public ResponseEntity<?> createRole(@RequestBody RoleCreate dto) {
        User current = getCurrentUser();
        if (!isSystemAdmin(current)) {
            return ResponseEntity.status(403)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can access this resource"));
        }
        try {
            RoleResponse created = roleService.createRole(dto);
            return ResponseEntity.ok(created);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("detail", e.getMessage()));
        }
    }

    @PutMapping("/{roleId}")
    public ResponseEntity<?> updateRole(@PathVariable String roleId,
                                        @RequestBody RoleUpdate dto) {
        User current = getCurrentUser();
        if (!isSystemAdmin(current)) {
            return ResponseEntity.status(403)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can access this resource"));
        }
        try {
            RoleResponse updated = roleService.updateRole(roleId, dto);
            return ResponseEntity.ok(updated);
        } catch (NoSuchElementException e) {
            return ResponseEntity.status(404).body(Map.of("detail", e.getMessage()));
        }
    }

    @DeleteMapping("/{roleId}")
    public ResponseEntity<?> deleteRole(@PathVariable String roleId) {
        User current = getCurrentUser();
        if (!isSystemAdmin(current)) {
            return ResponseEntity.status(403)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can access this resource"));
        }
        try {
            roleService.deleteRole(roleId);
            return ResponseEntity.ok(Map.of("detail", "Role deleted"));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("detail", e.getMessage()));
        } catch (NoSuchElementException e) {
            return ResponseEntity.status(404).body(Map.of("detail", e.getMessage()));
        }
    }

    @GetMapping("/{roleId}/permissions")
    public ResponseEntity<?> getRolePermissions(@PathVariable String roleId) {
        try {
            List<PermissionResponse> perms = roleService.getRolePermissions(roleId);
            return ResponseEntity.ok(perms);
        } catch (NoSuchElementException e) {
            return ResponseEntity.status(404).body(Map.of("detail", e.getMessage()));
        }
    }

    @PutMapping("/{roleId}/permissions")
    public ResponseEntity<?> updateRolePermissions(@PathVariable String roleId,
                                                    @RequestBody RolePermissionUpdate dto) {
        User current = getCurrentUser();
        if (!isSystemAdmin(current)) {
            return ResponseEntity.status(403)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can access this resource"));
        }
        try {
            List<PermissionResponse> perms = roleService.updateRolePermissions(roleId, dto.getPermissionIds());
            return ResponseEntity.ok(perms);
        } catch (NoSuchElementException e) {
            return ResponseEntity.status(404).body(Map.of("detail", e.getMessage()));
        }
    }

    @GetMapping("/permissions/all")
    public ResponseEntity<List<PermissionResponse>> listAllPermissions() {
        return ResponseEntity.ok(roleService.getAllPermissions());
    }
}

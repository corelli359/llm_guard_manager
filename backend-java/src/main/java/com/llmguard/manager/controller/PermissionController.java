package com.llmguard.manager.controller;

import com.llmguard.manager.domain.dto.PermissionCheckRequest;
import com.llmguard.manager.domain.dto.PermissionCheckResponse;
import com.llmguard.manager.domain.dto.UserPermissionResponse;
import com.llmguard.manager.domain.entity.User;
import com.llmguard.manager.service.PermissionService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/permissions")
@RequiredArgsConstructor
public class PermissionController {

    private final PermissionService permissionService;

    @GetMapping("/me")
    public ResponseEntity<UserPermissionResponse> getMyPermissions(
            @AuthenticationPrincipal User user) {
        UserPermissionResponse permissions = permissionService.getUserPermissions(user);
        return ResponseEntity.ok(permissions);
    }

    @PostMapping("/check")
    public ResponseEntity<PermissionCheckResponse> checkPermission(
            @RequestBody PermissionCheckRequest request,
            @AuthenticationPrincipal User user) {
        boolean hasPermission = permissionService.checkScenarioPermission(
                user, request.getScenarioId(), request.getPermission());

        return ResponseEntity.ok(PermissionCheckResponse.builder()
                .hasPermission(hasPermission)
                .build());
    }
}

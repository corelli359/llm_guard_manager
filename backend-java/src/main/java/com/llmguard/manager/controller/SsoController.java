package com.llmguard.manager.controller;

import com.llmguard.manager.domain.dto.*;
import com.llmguard.manager.domain.entity.User;
import com.llmguard.manager.service.SsoService;
import com.llmguard.manager.service.UsapClient;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/sso")
@RequiredArgsConstructor
public class SsoController {

    private final SsoService ssoService;
    private final UsapClient usapClient;

    @PostMapping("/login")
    public ResponseEntity<?> ssoLogin(@RequestBody SsoLoginRequest request) {
        try {
            return ResponseEntity.ok(ssoService.loginWithTicket(request.getTicket()));
        } catch (Exception e) {
            return ResponseEntity.status(401).body(Map.of("detail", e.getMessage() != null ? e.getMessage() : "SSO login failed"));
        }
    }

    @GetMapping("/user-info")
    public ResponseEntity<SsoUserInfoResponse> getUserInfo(@AuthenticationPrincipal User currentUser) {
        UsapClient.UsapUserInfo usapInfo = usapClient.getUserInfo(currentUser.getUserId());

        SsoUserInfoResponse response = SsoUserInfoResponse.builder()
                .userId(currentUser.getUserId())
                .userName(usapInfo.getUserName())
                .email(usapInfo.getEmail())
                .department(usapInfo.getDepartment())
                .role(currentUser.getRole())
                .displayName(currentUser.getDisplayName())
                .permissions(new HashMap<>())
                .build();

        return ResponseEntity.ok(response);
    }

    @PostMapping("/users/batch")
    public ResponseEntity<SsoBatchUsersResponse> batchFetchUsers(
            @RequestBody SsoBatchUsersRequest request) {
        UsapClient.UsapBatchUsersResult usapResult = usapClient.getUsersBatch(request.getUserIds());

        List<SsoUserInfoResponse> users = new ArrayList<>();
        if (usapResult.getUsers() != null) {
            for (UsapClient.UsapUserInfo info : usapResult.getUsers()) {
                users.add(SsoUserInfoResponse.builder()
                        .userId(info.getUserId())
                        .userName(info.getUserName())
                        .email(info.getEmail())
                        .department(info.getDepartment())
                        .displayName(info.getDisplayName())
                        .build());
            }
        }

        SsoBatchUsersResponse response = SsoBatchUsersResponse.builder()
                .users(users)
                .notFound(usapResult.getNotFound() != null ? usapResult.getNotFound() : List.of())
                .build();

        return ResponseEntity.ok(response);
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> healthCheck() {
        UsapClient.UsapHealthResult result = usapClient.healthCheck();
        Map<String, String> response = new HashMap<>();
        response.put("usap_status", result.getStatus());
        response.put("usap_service", result.getService());
        return ResponseEntity.ok(response);
    }
}

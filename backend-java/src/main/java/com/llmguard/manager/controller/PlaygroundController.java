package com.llmguard.manager.controller;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.llmguard.manager.domain.dto.PlaygroundHistoryResponse;
import com.llmguard.manager.domain.dto.PlaygroundInputRequest;
import com.llmguard.manager.domain.entity.PlaygroundHistory;
import com.llmguard.manager.domain.entity.User;
import com.llmguard.manager.service.AuditService;
import com.llmguard.manager.service.PermissionService;
import com.llmguard.manager.service.PlaygroundService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@RestController
@RequestMapping("/playground")
@RequiredArgsConstructor
public class PlaygroundController {

    private final PlaygroundService playgroundService;
    private final PermissionService permissionService;
    private final AuditService auditService;
    private final ObjectMapper objectMapper;

    @PostMapping("/input")
    public ResponseEntity<Map<String, Object>> runInputCheck(
            @RequestBody PlaygroundInputRequest dto,
            @AuthenticationPrincipal User user,
            HttpServletRequest request) {
        // Permission check: need playground permission
        checkScenarioPermission(user, dto.getAppId(), "playground");

        Map<String, Object> result = playgroundService.runInputCheck(dto);

        auditService.log(user.getId(), user.getUsername(), "CREATE",
                "PLAYGROUND_TEST", null, dto.getAppId(),
                Map.of("playground_type", dto.getPlaygroundType(),
                        "score", result.getOrDefault("score", -1)),
                request);

        return ResponseEntity.ok(result);
    }
    @GetMapping("/history")
    public ResponseEntity<List<PlaygroundHistoryResponse>> getHistory(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(name = "playground_type", required = false) String playgroundType,
            @RequestParam(name = "app_id", required = false) String appId,
            @AuthenticationPrincipal User user) {
        // If app_id is specified, check permission
        if (appId != null) {
            checkScenarioPermission(user, appId, "playground");
        }

        List<PlaygroundHistory> histories = playgroundService.getHistory(page, size, playgroundType, appId);
        return ResponseEntity.ok(histories.stream().map(this::toResponse).collect(Collectors.toList()));
    }

    private void checkScenarioPermission(User user, String scenarioId, String permission) {
        if (!permissionService.checkScenarioPermission(user, scenarioId, permission)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "No permission for this scenario");
        }
    }

    @SuppressWarnings("unchecked")
    private PlaygroundHistoryResponse toResponse(PlaygroundHistory history) {
        Object inputData = parseJson(history.getInputData());
        Object configSnapshot = parseJson(history.getConfigSnapshot());
        Object outputData = parseJson(history.getOutputData());

        return PlaygroundHistoryResponse.builder()
                .id(history.getId())
                .requestId(history.getRequestId())
                .playgroundType(history.getPlaygroundType())
                .appId(history.getAppId())
                .inputData(inputData)
                .configSnapshot(configSnapshot)
                .outputData(outputData)
                .score(history.getScore())
                .latency(history.getLatency())
                .upstreamLatency(history.getUpstreamLatency())
                .createdAt(history.getCreatedAt())
                .build();
    }

    private Object parseJson(String json) {
        if (json == null) {
            return null;
        }
        try {
            return objectMapper.readValue(json, Object.class);
        } catch (JsonProcessingException e) {
            return json;
        }
    }
}

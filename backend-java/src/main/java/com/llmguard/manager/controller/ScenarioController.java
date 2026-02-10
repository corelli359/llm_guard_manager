package com.llmguard.manager.controller;

import com.llmguard.manager.domain.dto.ScenarioCreate;
import com.llmguard.manager.domain.dto.ScenarioResponse;
import com.llmguard.manager.domain.dto.ScenarioUpdate;
import com.llmguard.manager.domain.entity.Scenario;
import com.llmguard.manager.domain.entity.User;
import com.llmguard.manager.service.AuditService;
import com.llmguard.manager.service.ScenarioService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/apps")
@RequiredArgsConstructor
public class ScenarioController {

    private final ScenarioService scenarioService;
    private final AuditService auditService;

    @GetMapping("/")
    public ResponseEntity<List<ScenarioResponse>> listScenarios() {
        List<ScenarioResponse> scenarios = scenarioService.getAllScenarios().stream()
                .map(ScenarioResponse::fromEntity)
                .collect(Collectors.toList());
        return ResponseEntity.ok(scenarios);
    }

    @PostMapping("/")
    public ResponseEntity<?> createScenario(@RequestBody ScenarioCreate dto,
                                            HttpServletRequest request) {
        User user = getCurrentUser();
        if (!isSystemAdmin(user)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can create scenarios"));
        }

        Scenario scenario = scenarioService.createScenario(dto);
        auditService.logCreate(user.getId(), user.getUsername(),
                "SCENARIO", scenario.getId(), dto, request);
        return ResponseEntity.ok(ScenarioResponse.fromEntity(scenario));
    }

    @GetMapping("/{appId}")
    public ResponseEntity<ScenarioResponse> getScenario(@PathVariable String appId) {
        Scenario scenario = scenarioService.getScenarioByAppId(appId);
        return ResponseEntity.ok(ScenarioResponse.fromEntity(scenario));
    }

    @PutMapping("/{scenarioId}")
    public ResponseEntity<?> updateScenario(@PathVariable String scenarioId,
                                            @RequestBody ScenarioUpdate dto,
                                            HttpServletRequest request) {
        User user = getCurrentUser();
        if (!isSystemAdmin(user)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can update scenarios"));
        }

        Scenario scenario = scenarioService.updateScenario(scenarioId, dto);
        auditService.logUpdate(user.getId(), user.getUsername(),
                "SCENARIO", scenario.getId(), dto, request);
        return ResponseEntity.ok(ScenarioResponse.fromEntity(scenario));
    }

    @DeleteMapping("/{scenarioId}")
    public ResponseEntity<?> deleteScenario(@PathVariable String scenarioId,
                                            HttpServletRequest request) {
        User user = getCurrentUser();
        if (!isSystemAdmin(user)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can delete scenarios"));
        }

        scenarioService.deleteScenario(scenarioId);
        auditService.logDelete(user.getId(), user.getUsername(),
                "SCENARIO", scenarioId, null, request);
        return ResponseEntity.ok(Map.of("detail", "Scenario deleted"));
    }

    private User getCurrentUser() {
        return (User) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
    }

    private boolean isSystemAdmin(User user) {
        return "SYSTEM_ADMIN".equals(user.getRole());
    }
}

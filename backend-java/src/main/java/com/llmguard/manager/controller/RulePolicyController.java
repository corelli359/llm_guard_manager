package com.llmguard.manager.controller;

import com.llmguard.manager.domain.dto.*;
import com.llmguard.manager.domain.entity.RuleGlobalDefault;
import com.llmguard.manager.domain.entity.RuleScenarioPolicy;
import com.llmguard.manager.domain.entity.User;
import com.llmguard.manager.service.AuditService;
import com.llmguard.manager.service.PermissionService;
import com.llmguard.manager.service.RulePolicyService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/policies")
@RequiredArgsConstructor
public class RulePolicyController {

    private final RulePolicyService rulePolicyService;
    private final PermissionService permissionService;
    private final AuditService auditService;

    // --- Scenario Policies ---

    @GetMapping("/scenario/{scenarioId}")
    public ResponseEntity<List<RuleScenarioPolicyResponse>> getScenarioPolicies(
            @PathVariable String scenarioId,
            @AuthenticationPrincipal User user) {
        checkScenarioPermission(user, scenarioId, "scenario_policies");
        List<RuleScenarioPolicy> policies = rulePolicyService.getScenarioPolicies(scenarioId);
        return ResponseEntity.ok(policies.stream().map(this::toResponse).collect(Collectors.toList()));
    }
    @PostMapping("/scenario/")
    public ResponseEntity<RuleScenarioPolicyResponse> createScenarioPolicy(
            @RequestBody RuleScenarioPolicyCreate dto,
            @AuthenticationPrincipal User user,
            HttpServletRequest request) {
        checkScenarioPermission(user, dto.getScenarioId(), "scenario_policies");
        RuleScenarioPolicy policy = rulePolicyService.createScenarioPolicy(dto);

        auditService.log(user.getId(), user.getUsername(), "CREATE",
                "SCENARIO_POLICY", policy.getId(), dto.getScenarioId(),
                Map.of("match_type", dto.getMatchType(), "strategy", dto.getStrategy()), request);

        return ResponseEntity.ok(toResponse(policy));
    }

    @PutMapping("/scenario/{policyId}")
    public ResponseEntity<RuleScenarioPolicyResponse> updateScenarioPolicy(
            @PathVariable String policyId,
            @RequestBody RuleScenarioPolicyUpdate dto,
            @AuthenticationPrincipal User user,
            HttpServletRequest request) {
        // Get existing policy to check scenario permission BEFORE update
        RuleScenarioPolicy existing = rulePolicyService.getScenarioPolicyById(policyId);
        checkScenarioPermission(user, existing.getScenarioId(), "scenario_policies");

        RuleScenarioPolicy policy = rulePolicyService.updateScenarioPolicy(policyId, dto);

        auditService.log(user.getId(), user.getUsername(), "UPDATE",
                "SCENARIO_POLICY", policyId, existing.getScenarioId(), dto, request);

        return ResponseEntity.ok(toResponse(policy));
    }

    @DeleteMapping("/scenario/{policyId}")
    public ResponseEntity<RuleScenarioPolicyResponse> deleteScenarioPolicy(
            @PathVariable String policyId,
            @AuthenticationPrincipal User user,
            HttpServletRequest request) {
        // Get existing policy to check scenario permission BEFORE delete
        RuleScenarioPolicy existing = rulePolicyService.getScenarioPolicyById(policyId);
        checkScenarioPermission(user, existing.getScenarioId(), "scenario_policies");

        RuleScenarioPolicy policy = rulePolicyService.deleteScenarioPolicy(policyId);

        auditService.log(user.getId(), user.getUsername(), "DELETE",
                "SCENARIO_POLICY", policyId, existing.getScenarioId(), null, request);

        return ResponseEntity.ok(toResponse(policy));
    }

    // --- Global Defaults ---

    @GetMapping("/defaults/")
    public ResponseEntity<List<RuleGlobalDefaultResponse>> getGlobalDefaults(
            @AuthenticationPrincipal User user) {
        List<RuleGlobalDefault> defaults = rulePolicyService.getAllGlobalDefaults();
        return ResponseEntity.ok(defaults.stream().map(this::toGlobalResponse).collect(Collectors.toList()));
    }
    @PostMapping("/defaults/")
    public ResponseEntity<RuleGlobalDefaultResponse> createGlobalDefault(
            @RequestBody RuleGlobalDefaultCreate dto,
            @AuthenticationPrincipal User user,
            HttpServletRequest request) {
        requireSystemAdmin(user);
        RuleGlobalDefault globalDefault = rulePolicyService.createGlobalDefault(dto);

        auditService.log(user.getId(), user.getUsername(), "CREATE",
                "GLOBAL_DEFAULT_POLICY", globalDefault.getId(), null,
                Map.of("tag_code", dto.getTagCode() != null ? dto.getTagCode() : "",
                        "strategy", dto.getStrategy()), request);

        return ResponseEntity.ok(toGlobalResponse(globalDefault));
    }

    @PutMapping("/defaults/{defaultId}")
    public ResponseEntity<RuleGlobalDefaultResponse> updateGlobalDefault(
            @PathVariable String defaultId,
            @RequestBody RuleGlobalDefaultUpdate dto,
            @AuthenticationPrincipal User user,
            HttpServletRequest request) {
        requireSystemAdmin(user);
        RuleGlobalDefault globalDefault = rulePolicyService.updateGlobalDefault(defaultId, dto);

        auditService.log(user.getId(), user.getUsername(), "UPDATE",
                "GLOBAL_DEFAULT_POLICY", defaultId, null, dto, request);

        return ResponseEntity.ok(toGlobalResponse(globalDefault));
    }

    @DeleteMapping("/defaults/{defaultId}")
    public ResponseEntity<RuleGlobalDefaultResponse> deleteGlobalDefault(
            @PathVariable String defaultId,
            @AuthenticationPrincipal User user,
            HttpServletRequest request) {
        requireSystemAdmin(user);
        RuleGlobalDefault globalDefault = rulePolicyService.deleteGlobalDefault(defaultId);

        auditService.log(user.getId(), user.getUsername(), "DELETE",
                "GLOBAL_DEFAULT_POLICY", defaultId, null, null, request);

        return ResponseEntity.ok(toGlobalResponse(globalDefault));
    }

    // --- Helper methods ---

    private void checkScenarioPermission(User user, String scenarioId, String permission) {
        if (!permissionService.checkScenarioPermission(user, scenarioId, permission)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "No permission for this scenario");
        }
    }

    private void requireSystemAdmin(User user) {
        if (!"SYSTEM_ADMIN".equals(user.getRole())) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Only SYSTEM_ADMIN can perform this action");
        }
    }

    private RuleScenarioPolicyResponse toResponse(RuleScenarioPolicy policy) {
        return RuleScenarioPolicyResponse.builder()
                .id(policy.getId())
                .scenarioId(policy.getScenarioId())
                .matchType(policy.getMatchType())
                .matchValue(policy.getMatchValue())
                .ruleMode(policy.getRuleMode())
                .extraCondition(policy.getExtraCondition())
                .strategy(policy.getStrategy())
                .isActive(policy.getIsActive())
                .build();
    }

    private RuleGlobalDefaultResponse toGlobalResponse(RuleGlobalDefault globalDefault) {
        return RuleGlobalDefaultResponse.builder()
                .id(globalDefault.getId())
                .tagCode(globalDefault.getTagCode())
                .extraCondition(globalDefault.getExtraCondition())
                .strategy(globalDefault.getStrategy())
                .isActive(globalDefault.getIsActive())
                .build();
    }
}

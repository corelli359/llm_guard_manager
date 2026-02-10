package com.llmguard.manager.controller;

import com.llmguard.manager.domain.dto.ScenarioKeywordCreate;
import com.llmguard.manager.domain.dto.ScenarioKeywordResponse;
import com.llmguard.manager.domain.dto.ScenarioKeywordUpdate;
import com.llmguard.manager.domain.entity.ScenarioKeyword;
import com.llmguard.manager.domain.entity.User;
import com.llmguard.manager.service.AuditService;
import com.llmguard.manager.service.ScenarioKeywordService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/keywords/scenario")
@RequiredArgsConstructor
public class ScenarioKeywordController {

    private final ScenarioKeywordService scenarioKeywordService;
    private final AuditService auditService;

    @GetMapping("/{scenarioId}")
    public ResponseEntity<List<ScenarioKeywordResponse>> listKeywords(
            @PathVariable String scenarioId,
            @RequestParam(name = "rule_mode", required = false) Integer ruleMode) {
        List<ScenarioKeywordResponse> keywords = scenarioKeywordService
                .getByScenario(scenarioId, ruleMode).stream()
                .map(ScenarioKeywordResponse::fromEntity)
                .collect(Collectors.toList());
        return ResponseEntity.ok(keywords);
    }

    @PostMapping("/")
    public ResponseEntity<ScenarioKeywordResponse> createKeyword(
            @RequestBody ScenarioKeywordCreate dto,
            HttpServletRequest request) {
        User user = getCurrentUser();
        ScenarioKeyword keyword = scenarioKeywordService.createKeyword(dto);
        auditService.logCreate(user.getId(), user.getUsername(),
                "SCENARIO_KEYWORD", keyword.getId(), dto, request);
        return ResponseEntity.ok(ScenarioKeywordResponse.fromEntity(keyword));
    }

    @PutMapping("/{keywordId}")
    public ResponseEntity<ScenarioKeywordResponse> updateKeyword(
            @PathVariable String keywordId,
            @RequestBody ScenarioKeywordUpdate dto,
            HttpServletRequest request) {
        User user = getCurrentUser();
        ScenarioKeyword keyword = scenarioKeywordService.updateKeyword(keywordId, dto);
        auditService.logUpdate(user.getId(), user.getUsername(),
                "SCENARIO_KEYWORD", keyword.getId(), dto, request);
        return ResponseEntity.ok(ScenarioKeywordResponse.fromEntity(keyword));
    }

    @DeleteMapping("/{keywordId}")
    public ResponseEntity<?> deleteKeyword(@PathVariable String keywordId,
                                           HttpServletRequest request) {
        User user = getCurrentUser();
        scenarioKeywordService.deleteKeyword(keywordId);
        auditService.logDelete(user.getId(), user.getUsername(),
                "SCENARIO_KEYWORD", keywordId, null, request);
        return ResponseEntity.ok(Map.of("detail", "Scenario keyword deleted"));
    }

    private User getCurrentUser() {
        return (User) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
    }
}

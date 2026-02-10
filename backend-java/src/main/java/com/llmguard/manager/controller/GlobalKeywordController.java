package com.llmguard.manager.controller;

import com.llmguard.manager.domain.dto.GlobalKeywordCreate;
import com.llmguard.manager.domain.dto.GlobalKeywordResponse;
import com.llmguard.manager.domain.dto.GlobalKeywordUpdate;
import com.llmguard.manager.domain.entity.GlobalKeyword;
import com.llmguard.manager.domain.entity.User;
import com.llmguard.manager.service.AuditService;
import com.llmguard.manager.service.GlobalKeywordService;
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
@RequestMapping("/keywords/global")
@RequiredArgsConstructor
public class GlobalKeywordController {

    private final GlobalKeywordService globalKeywordService;
    private final AuditService auditService;

    @GetMapping("/")
    public ResponseEntity<List<GlobalKeywordResponse>> listKeywords(
            @RequestParam(defaultValue = "0") int skip,
            @RequestParam(defaultValue = "100") int limit,
            @RequestParam(required = false) String q,
            @RequestParam(required = false) String tag) {
        List<GlobalKeywordResponse> keywords = globalKeywordService
                .getAllKeywords(q, tag, skip, limit).stream()
                .map(GlobalKeywordResponse::fromEntity)
                .collect(Collectors.toList());
        return ResponseEntity.ok(keywords);
    }

    @PostMapping("/")
    public ResponseEntity<?> createKeyword(@RequestBody GlobalKeywordCreate dto,
                                           HttpServletRequest request) {
        User user = getCurrentUser();
        if (!isSystemAdmin(user)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can create keywords"));
        }

        GlobalKeyword keyword = globalKeywordService.createKeyword(dto);
        auditService.logCreate(user.getId(), user.getUsername(),
                "GLOBAL_KEYWORD", keyword.getId(), dto, request);
        return ResponseEntity.ok(GlobalKeywordResponse.fromEntity(keyword));
    }

    @PutMapping("/{keywordId}")
    public ResponseEntity<?> updateKeyword(@PathVariable String keywordId,
                                           @RequestBody GlobalKeywordUpdate dto,
                                           HttpServletRequest request) {
        User user = getCurrentUser();
        if (!isSystemAdmin(user)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can update keywords"));
        }

        GlobalKeyword keyword = globalKeywordService.updateKeyword(keywordId, dto);
        auditService.logUpdate(user.getId(), user.getUsername(),
                "GLOBAL_KEYWORD", keyword.getId(), dto, request);
        return ResponseEntity.ok(GlobalKeywordResponse.fromEntity(keyword));
    }

    @DeleteMapping("/{keywordId}")
    public ResponseEntity<?> deleteKeyword(@PathVariable String keywordId,
                                           HttpServletRequest request) {
        User user = getCurrentUser();
        if (!isSystemAdmin(user)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can delete keywords"));
        }

        globalKeywordService.deleteKeyword(keywordId);
        auditService.logDelete(user.getId(), user.getUsername(),
                "GLOBAL_KEYWORD", keywordId, null, request);
        return ResponseEntity.ok(Map.of("detail", "Keyword deleted"));
    }

    private User getCurrentUser() {
        return (User) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
    }

    private boolean isSystemAdmin(User user) {
        return "SYSTEM_ADMIN".equals(user.getRole());
    }
}

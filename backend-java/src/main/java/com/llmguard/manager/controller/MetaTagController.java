package com.llmguard.manager.controller;

import com.llmguard.manager.domain.dto.MetaTagCreate;
import com.llmguard.manager.domain.dto.MetaTagResponse;
import com.llmguard.manager.domain.dto.MetaTagUpdate;
import com.llmguard.manager.domain.entity.MetaTag;
import com.llmguard.manager.domain.entity.User;
import com.llmguard.manager.service.AuditService;
import com.llmguard.manager.service.MetaTagService;
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
@RequestMapping("/tags")
@RequiredArgsConstructor
public class MetaTagController {

    private final MetaTagService metaTagService;
    private final AuditService auditService;

    @GetMapping("/")
    public ResponseEntity<List<MetaTagResponse>> listTags() {
        List<MetaTagResponse> tags = metaTagService.getAllTags().stream()
                .map(MetaTagResponse::fromEntity)
                .collect(Collectors.toList());
        return ResponseEntity.ok(tags);
    }

    @PostMapping("/")
    public ResponseEntity<?> createTag(@RequestBody MetaTagCreate dto,
                                       HttpServletRequest request) {
        User user = getCurrentUser();
        if (!isSystemAdmin(user)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can create tags"));
        }

        MetaTag tag = metaTagService.createTag(dto);
        auditService.logCreate(user.getId(), user.getUsername(),
                "META_TAG", tag.getId(), dto, request);
        return ResponseEntity.ok(MetaTagResponse.fromEntity(tag));
    }

    @PutMapping("/{tagId}")
    public ResponseEntity<?> updateTag(@PathVariable String tagId,
                                       @RequestBody MetaTagUpdate dto,
                                       HttpServletRequest request) {
        User user = getCurrentUser();
        if (!isSystemAdmin(user)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can update tags"));
        }

        MetaTag tag = metaTagService.updateTag(tagId, dto);
        auditService.logUpdate(user.getId(), user.getUsername(),
                "META_TAG", tag.getId(), dto, request);
        return ResponseEntity.ok(MetaTagResponse.fromEntity(tag));
    }

    @DeleteMapping("/{tagId}")
    public ResponseEntity<?> deleteTag(@PathVariable String tagId,
                                       HttpServletRequest request) {
        User user = getCurrentUser();
        if (!isSystemAdmin(user)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("detail", "Only SYSTEM_ADMIN can delete tags"));
        }

        metaTagService.deleteTag(tagId);
        auditService.logDelete(user.getId(), user.getUsername(),
                "META_TAG", tagId, null, request);
        return ResponseEntity.ok(Map.of("detail", "Tag deleted"));
    }

    private User getCurrentUser() {
        return (User) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
    }

    private boolean isSystemAdmin(User user) {
        return "SYSTEM_ADMIN".equals(user.getRole());
    }
}

package com.llmguard.manager.service;

import com.llmguard.manager.domain.dto.GlobalKeywordCreate;
import com.llmguard.manager.domain.dto.GlobalKeywordUpdate;
import com.llmguard.manager.domain.entity.GlobalKeyword;
import com.llmguard.manager.repository.GlobalKeywordRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class GlobalKeywordService {

    private final GlobalKeywordRepository globalKeywordRepository;

    public List<GlobalKeyword> getAllKeywords(String q, String tag, int skip, int limit) {
        List<GlobalKeyword> all;

        if (q != null && !q.isEmpty() && tag != null && !tag.isEmpty()) {
            all = globalKeywordRepository.findByKeywordContaining(q).stream()
                    .filter(kw -> tag.equals(kw.getTagCode()))
                    .collect(Collectors.toList());
        } else if (q != null && !q.isEmpty()) {
            all = globalKeywordRepository.findByKeywordContaining(q);
        } else if (tag != null && !tag.isEmpty()) {
            all = globalKeywordRepository.findByTagCode(tag);
        } else {
            all = globalKeywordRepository.findAll();
        }

        return all.stream()
                .skip(skip)
                .limit(limit)
                .collect(Collectors.toList());
    }

    public GlobalKeyword getKeyword(String id) {
        return globalKeywordRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Keyword not found"));
    }

    @Transactional
    public GlobalKeyword createKeyword(GlobalKeywordCreate dto) {
        if (globalKeywordRepository.existsByKeyword(dto.getKeyword())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Keyword already exists");
        }

        GlobalKeyword keyword = GlobalKeyword.builder()
                .id(UUID.randomUUID().toString())
                .keyword(dto.getKeyword())
                .tagCode(dto.getTagCode())
                .riskLevel(dto.getRiskLevel())
                .isActive(true)
                .build();

        return globalKeywordRepository.save(keyword);
    }

    @Transactional
    public GlobalKeyword updateKeyword(String id, GlobalKeywordUpdate dto) {
        GlobalKeyword keyword = getKeyword(id);

        if (dto.getKeyword() != null) {
            if (!dto.getKeyword().equals(keyword.getKeyword())
                    && globalKeywordRepository.existsByKeyword(dto.getKeyword())) {
                throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Keyword already exists");
            }
            keyword.setKeyword(dto.getKeyword());
        }
        if (dto.getTagCode() != null) {
            keyword.setTagCode(dto.getTagCode());
        }
        if (dto.getRiskLevel() != null) {
            keyword.setRiskLevel(dto.getRiskLevel());
        }
        if (dto.getIsActive() != null) {
            keyword.setIsActive(dto.getIsActive());
        }

        return globalKeywordRepository.save(keyword);
    }

    @Transactional
    public void deleteKeyword(String id) {
        GlobalKeyword keyword = getKeyword(id);
        globalKeywordRepository.delete(keyword);
    }
}

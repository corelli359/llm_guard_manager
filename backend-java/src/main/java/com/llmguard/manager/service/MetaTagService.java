package com.llmguard.manager.service;

import com.llmguard.manager.domain.dto.MetaTagCreate;
import com.llmguard.manager.domain.dto.MetaTagUpdate;
import com.llmguard.manager.domain.entity.MetaTag;
import com.llmguard.manager.repository.MetaTagRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class MetaTagService {

    private final MetaTagRepository metaTagRepository;

    public List<MetaTag> getAllTags() {
        return metaTagRepository.findAll();
    }

    public MetaTag getTag(String id) {
        return metaTagRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Tag not found"));
    }

    @Transactional
    public MetaTag createTag(MetaTagCreate dto) {
        if (metaTagRepository.existsByTagCode(dto.getTagCode())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Tag code already exists");
        }

        MetaTag tag = MetaTag.builder()
                .id(UUID.randomUUID().toString())
                .tagCode(dto.getTagCode())
                .tagName(dto.getTagName())
                .parentCode(dto.getParentCode())
                .level(dto.getLevel() != null ? dto.getLevel() : 2)
                .isActive(true)
                .build();

        return metaTagRepository.save(tag);
    }

    @Transactional
    public MetaTag updateTag(String id, MetaTagUpdate dto) {
        MetaTag tag = getTag(id);

        if (dto.getTagName() != null) {
            tag.setTagName(dto.getTagName());
        }
        if (dto.getParentCode() != null) {
            tag.setParentCode(dto.getParentCode());
        }
        if (dto.getLevel() != null) {
            tag.setLevel(dto.getLevel());
        }
        if (dto.getIsActive() != null) {
            tag.setIsActive(dto.getIsActive());
        }

        return metaTagRepository.save(tag);
    }

    @Transactional
    public void deleteTag(String id) {
        MetaTag tag = getTag(id);
        metaTagRepository.delete(tag);
    }
}

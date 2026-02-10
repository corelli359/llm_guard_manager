package com.llmguard.manager.repository;

import com.llmguard.manager.domain.entity.MetaTag;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface MetaTagRepository extends JpaRepository<MetaTag, String> {
    Optional<MetaTag> findByTagCode(String tagCode);
    boolean existsByTagCode(String tagCode);
}

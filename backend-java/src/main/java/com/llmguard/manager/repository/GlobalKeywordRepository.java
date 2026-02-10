package com.llmguard.manager.repository;

import com.llmguard.manager.domain.entity.GlobalKeyword;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface GlobalKeywordRepository extends JpaRepository<GlobalKeyword, String> {
    Optional<GlobalKeyword> findByKeyword(String keyword);
    List<GlobalKeyword> findByKeywordContaining(String keyword);
    List<GlobalKeyword> findByTagCode(String tagCode);
    boolean existsByKeyword(String keyword);
}

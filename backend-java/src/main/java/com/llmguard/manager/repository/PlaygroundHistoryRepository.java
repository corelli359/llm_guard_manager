package com.llmguard.manager.repository;

import com.llmguard.manager.domain.entity.PlaygroundHistory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PlaygroundHistoryRepository extends JpaRepository<PlaygroundHistory, String> {
    Page<PlaygroundHistory> findByAppId(String appId, Pageable pageable);
    Page<PlaygroundHistory> findByPlaygroundType(String playgroundType, Pageable pageable);
    Page<PlaygroundHistory> findByAppIdAndPlaygroundType(String appId, String playgroundType, Pageable pageable);
}

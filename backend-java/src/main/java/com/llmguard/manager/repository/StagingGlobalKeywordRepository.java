package com.llmguard.manager.repository;

import com.llmguard.manager.domain.entity.StagingGlobalKeyword;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;

public interface StagingGlobalKeywordRepository extends JpaRepository<StagingGlobalKeyword, String>, JpaSpecificationExecutor<StagingGlobalKeyword> {
    Page<StagingGlobalKeyword> findByStatus(String status, Pageable pageable);
    List<StagingGlobalKeyword> findByClaimedBy(String claimedBy);
    List<StagingGlobalKeyword> findByBatchId(String batchId);
    List<StagingGlobalKeyword> findByStatusAndClaimedBy(String status, String claimedBy);
    long countByStatus(String status);
    long countByAnnotator(String annotator);

    @Modifying
    @Query("UPDATE StagingGlobalKeyword s SET s.status = 'PENDING', s.claimedBy = null, s.claimedAt = null, s.batchId = null WHERE s.status = 'CLAIMED' AND s.claimedAt < :expiry")
    int releaseExpired(@Param("expiry") LocalDateTime expiry);

    @Query("SELECT s FROM StagingGlobalKeyword s WHERE s.status = 'PENDING' ORDER BY s.createdAt ASC")
    Page<StagingGlobalKeyword> findPendingForClaim(Pageable pageable);

    List<StagingGlobalKeyword> findByStatusIn(List<String> statuses);
}

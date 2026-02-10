package com.llmguard.manager.repository;

import com.llmguard.manager.domain.entity.StagingGlobalRule;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;

public interface StagingGlobalRuleRepository extends JpaRepository<StagingGlobalRule, String>, JpaSpecificationExecutor<StagingGlobalRule> {
    Page<StagingGlobalRule> findByStatus(String status, Pageable pageable);
    List<StagingGlobalRule> findByClaimedBy(String claimedBy);
    List<StagingGlobalRule> findByBatchId(String batchId);
    List<StagingGlobalRule> findByStatusAndClaimedBy(String status, String claimedBy);
    long countByStatus(String status);
    long countByAnnotator(String annotator);

    @Modifying
    @Query("UPDATE StagingGlobalRule s SET s.status = 'PENDING', s.claimedBy = null, s.claimedAt = null, s.batchId = null WHERE s.status = 'CLAIMED' AND s.claimedAt < :expiry")
    int releaseExpired(@Param("expiry") LocalDateTime expiry);

    @Query("SELECT s FROM StagingGlobalRule s WHERE s.status = 'PENDING' ORDER BY s.createdAt ASC")
    Page<StagingGlobalRule> findPendingForClaim(Pageable pageable);

    List<StagingGlobalRule> findByStatusIn(List<String> statuses);
}

package com.llmguard.manager.domain.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "staging_global_rules")
public class StagingGlobalRule {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "tag_code", length = 64, nullable = false)
    private String tagCode;

    @Column(name = "predicted_strategy", length = 32, nullable = false)
    private String predictedStrategy;

    @Column(name = "final_strategy", length = 32)
    private String finalStrategy;

    @Column(name = "extra_condition", length = 64)
    private String extraCondition;

    @Column(length = 32, nullable = false)
    private String status;

    @Column(name = "is_modified", nullable = false)
    private Boolean isModified;

    @Column(name = "claimed_by", length = 64)
    private String claimedBy;

    @Column(name = "claimed_at")
    private LocalDateTime claimedAt;

    @Column(name = "batch_id", length = 36)
    private String batchId;

    @Column(length = 64)
    private String annotator;

    @Column(name = "annotated_at")
    private LocalDateTime annotatedAt;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
}

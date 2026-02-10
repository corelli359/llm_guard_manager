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
@Table(name = "staging_global_keywords")
public class StagingGlobalKeyword {

    @Id
    @Column(length = 36)
    private String id;

    @Column(length = 255, nullable = false)
    private String keyword;

    @Column(name = "predicted_tag", length = 64, nullable = false)
    private String predictedTag;

    @Column(name = "predicted_risk", length = 32, nullable = false)
    private String predictedRisk;

    @Column(name = "final_tag", length = 64)
    private String finalTag;

    @Column(name = "final_risk", length = 32)
    private String finalRisk;

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

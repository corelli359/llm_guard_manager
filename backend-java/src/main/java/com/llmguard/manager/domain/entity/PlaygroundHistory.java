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
@Table(name = "playground_history")
public class PlaygroundHistory {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "request_id", length = 64, nullable = false)
    private String requestId;

    @Column(name = "playground_type", length = 32, nullable = false)
    private String playgroundType;

    @Column(name = "app_id", length = 64, nullable = false)
    private String appId;

    @Column(name = "input_data", columnDefinition = "JSON")
    private String inputData;

    @Column(name = "config_snapshot", columnDefinition = "JSON")
    private String configSnapshot;

    @Column(name = "output_data", columnDefinition = "JSON")
    private String outputData;

    @Column(nullable = false)
    private Integer score;

    private Integer latency;

    @Column(name = "upstream_latency")
    private Integer upstreamLatency;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
}

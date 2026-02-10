package com.llmguard.manager.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.llmguard.manager.domain.dto.PlaygroundInputRequest;
import com.llmguard.manager.domain.entity.PlaygroundHistory;
import com.llmguard.manager.repository.PlaygroundHistoryRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDateTime;
import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
public class PlaygroundService {

    private final PlaygroundHistoryRepository historyRepository;
    private final ObjectMapper objectMapper;

    private static final String GUARDRAIL_SERVICE_URL =
            "http://127.0.0.1:8000/api/input/instance/rule/run";

    @SuppressWarnings("unchecked")
    @Transactional
    public Map<String, Object> runInputCheck(PlaygroundInputRequest dto) {
        String requestId = UUID.randomUUID().toString();
        String randomApikey = "sk-" + UUID.randomUUID().toString().replace("-", "").substring(0, 32);

        // Build payload for guardrail service
        Map<String, Object> guardPayload = new LinkedHashMap<>();
        guardPayload.put("request_id", requestId);
        guardPayload.put("app_id", dto.getAppId());
        guardPayload.put("apikey", randomApikey);
        guardPayload.put("input_prompt", dto.getInputPrompt());
        guardPayload.put("use_customize_white", dto.getUseCustomizeWhite());
        guardPayload.put("use_customize_words", dto.getUseCustomizeWords());
        guardPayload.put("use_customize_rule", dto.getUseCustomizeRule());
        guardPayload.put("use_vip_black", dto.getUseVipBlack());
        guardPayload.put("use_vip_white", dto.getUseVipWhite());

        long startTime = System.currentTimeMillis();
        long upstreamLatencyMs = 0;
        Map<String, Object> responseData = new HashMap<>();
        boolean errorOccurred = false;
        String errorDetail = null;

        // Call Guardrail Service
        try {
            RestClient restClient = RestClient.builder()
                    .baseUrl(GUARDRAIL_SERVICE_URL)
                    .build();

            long upstreamStart = System.currentTimeMillis();
            String responseBody = restClient.post()
                    .body(guardPayload)
                    .retrieve()
                    .body(String.class);
            long upstreamEnd = System.currentTimeMillis();
            upstreamLatencyMs = upstreamEnd - upstreamStart;

            if (responseBody != null) {
                responseData = objectMapper.readValue(responseBody, Map.class);
            }
        } catch (Exception e) {
            if (upstreamLatencyMs == 0) {
                upstreamLatencyMs = System.currentTimeMillis() - startTime;
            }
            errorOccurred = true;
            errorDetail = e.getMessage();
            responseData = Map.of("error", e.getMessage());
        }

        long endTime = System.currentTimeMillis();
        long latencyMs = endTime - startTime;

        // Extract score
        int score = 0;
        if (errorOccurred) {
            score = -1;
        } else if (responseData.containsKey("final_decision")) {
            Object finalDecision = responseData.get("final_decision");
            if (finalDecision instanceof Map) {
                Object scoreObj = ((Map<?, ?>) finalDecision).get("score");
                if (scoreObj instanceof Number) {
                    score = ((Number) scoreObj).intValue();
                }
            }
        }
        // Save history
        try {
            Map<String, Object> inputDataMap = Map.of("input_prompt", dto.getInputPrompt());
            Map<String, Object> configSnapshot = new LinkedHashMap<>();
            configSnapshot.put("use_customize_white", dto.getUseCustomizeWhite());
            configSnapshot.put("use_customize_words", dto.getUseCustomizeWords());
            configSnapshot.put("use_customize_rule", dto.getUseCustomizeRule());
            configSnapshot.put("use_vip_black", dto.getUseVipBlack());
            configSnapshot.put("use_vip_white", dto.getUseVipWhite());

            PlaygroundHistory history = PlaygroundHistory.builder()
                    .id(UUID.randomUUID().toString())
                    .requestId(requestId)
                    .playgroundType("INPUT")
                    .appId(dto.getAppId())
                    .inputData(objectMapper.writeValueAsString(inputDataMap))
                    .configSnapshot(objectMapper.writeValueAsString(configSnapshot))
                    .outputData(objectMapper.writeValueAsString(responseData))
                    .score(score)
                    .latency((int) latencyMs)
                    .upstreamLatency((int) upstreamLatencyMs)
                    .createdAt(LocalDateTime.now())
                    .build();

            historyRepository.save(history);
        } catch (Exception dbErr) {
            log.warn("Failed to save playground history: {}", dbErr.getMessage());
        }

        if (errorOccurred) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR,
                    "Error processing playground request: " + errorDetail);
        }

        return responseData;
    }

    public List<PlaygroundHistory> getHistory(int page, int size, String playgroundType, String appId) {
        Pageable pageable = PageRequest.of(page - 1, size, Sort.by(Sort.Direction.DESC, "createdAt"));

        Page<PlaygroundHistory> result;
        if (appId != null && playgroundType != null) {
            result = historyRepository.findByAppIdAndPlaygroundType(appId, playgroundType, pageable);
        } else if (appId != null) {
            result = historyRepository.findByAppId(appId, pageable);
        } else if (playgroundType != null) {
            result = historyRepository.findByPlaygroundType(playgroundType, pageable);
        } else {
            result = historyRepository.findAll(pageable);
        }

        return result.getContent();
    }
}

/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.llmguard.entity.PlaygroundHistoryDO;
import com.llmguard.mapper.PlaygroundHistoryMapper;
import com.llmguard.service.IPlaygroundService;
import com.llmguard.vo.playground.PlaygroundHistoryRespVO;
import com.llmguard.vo.playground.PlaygroundInputVO;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * 功能描述：Playground 服务实现
 *
 * @date 2024/07/13 16:06
 */
@Service
public class PlaygroundServiceImpl implements IPlaygroundService {

    private static final Logger log = LoggerFactory.getLogger(PlaygroundServiceImpl.class);

    private final PlaygroundHistoryMapper playgroundHistoryMapper;
    private final RestTemplate restTemplate;

    @Value("${guardrail.service.url:http://127.0.0.1:8000/api/input/instance/rule/run}")
    private String guardrailServiceUrl;

    public PlaygroundServiceImpl(PlaygroundHistoryMapper playgroundHistoryMapper,
                                 RestTemplate restTemplate) {
        this.playgroundHistoryMapper = playgroundHistoryMapper;
        this.restTemplate = restTemplate;
    }

    @Override
    @SuppressWarnings("unchecked")
    public Map<String, Object> runInputCheck(PlaygroundInputVO inputVO) {
        String requestId = UUID.randomUUID().toString();

        // 构建请求体
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("app_id", inputVO.getAppId());
        requestBody.put("input_prompt", inputVO.getInputPrompt());
        requestBody.put("use_customize_white", inputVO.isUseCustomizeWhite());
        requestBody.put("use_customize_words", inputVO.isUseCustomizeWords());
        requestBody.put("use_customize_rule", inputVO.isUseCustomizeRule());
        requestBody.put("use_vip_black", inputVO.isUseVipBlack());
        requestBody.put("use_vip_white", inputVO.isUseVipWhite());

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Object>> httpEntity = new HttpEntity<>(requestBody, headers);

        Map<String, Object> outputData = new HashMap<>();
        int score = 0;
        Integer upstreamLatency = null;

        long startTime = System.currentTimeMillis();
        try {
            ResponseEntity<Map> response = restTemplate.postForEntity(
                    guardrailServiceUrl, httpEntity, Map.class);
            upstreamLatency = (int) (System.currentTimeMillis() - startTime);

            if (response.getBody() != null) {
                outputData = response.getBody();
                Object scoreObj = outputData.get("score");
                if (scoreObj instanceof Number) {
                    score = ((Number) scoreObj).intValue();
                }
            }
        } catch (Exception e) {
            upstreamLatency = (int) (System.currentTimeMillis() - startTime);
            log.error("调用护栏服务失败: {}", e.getMessage(), e);
            outputData.put("error", e.getMessage());
            score = -1;
        }
        int totalLatency = (int) (System.currentTimeMillis() - startTime);

        // 保存历史记录
        PlaygroundHistoryDO history = new PlaygroundHistoryDO();
        history.setRequestId(requestId);
        history.setPlaygroundType("input");
        history.setAppId(inputVO.getAppId());
        history.setInputData(requestBody);
        history.setOutputData(outputData);
        history.setScore(score);
        history.setLatency(totalLatency);
        history.setUpstreamLatency(upstreamLatency);
        playgroundHistoryMapper.insert(history);

        // 构建返回结果
        Map<String, Object> result = new HashMap<>();
        result.put("request_id", requestId);
        result.put("output", outputData);
        result.put("score", score);
        result.put("latency", totalLatency);
        result.put("upstream_latency", upstreamLatency);
        return result;
    }

    @Override
    public List<PlaygroundHistoryRespVO> getHistory(int page, int size,
                                                     String playgroundType, String appId) {
        LambdaQueryWrapper<PlaygroundHistoryDO> wrapper = new LambdaQueryWrapper<>();
        if (playgroundType != null && !playgroundType.isEmpty()) {
            wrapper.eq(PlaygroundHistoryDO::getPlaygroundType, playgroundType);
        }
        if (appId != null && !appId.isEmpty()) {
            wrapper.eq(PlaygroundHistoryDO::getAppId, appId);
        }
        wrapper.orderByDesc(PlaygroundHistoryDO::getCreatedAt);

        Page<PlaygroundHistoryDO> pageParam = new Page<>(page, size);
        Page<PlaygroundHistoryDO> result = playgroundHistoryMapper.selectPage(pageParam, wrapper);
        return result.getRecords().stream().map(this::toRespVO).collect(Collectors.toList());
    }

    /**
     * DO 转 RespVO
     *
     * @param entity 实体对象
     * @return 响应 VO
     */
    private PlaygroundHistoryRespVO toRespVO(PlaygroundHistoryDO entity) {
        PlaygroundHistoryRespVO vo = new PlaygroundHistoryRespVO();
        vo.setId(entity.getId());
        vo.setRequestId(entity.getRequestId());
        vo.setPlaygroundType(entity.getPlaygroundType());
        vo.setAppId(entity.getAppId());
        vo.setInputData(entity.getInputData());
        vo.setConfigSnapshot(entity.getConfigSnapshot());
        vo.setOutputData(entity.getOutputData());
        vo.setScore(entity.getScore() != null ? entity.getScore() : 0);
        vo.setLatency(entity.getLatency());
        vo.setUpstreamLatency(entity.getUpstreamLatency());
        vo.setCreatedAt(entity.getCreatedAt());
        return vo;
    }
}


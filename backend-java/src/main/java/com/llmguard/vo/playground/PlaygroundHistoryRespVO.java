/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.playground;

import java.util.Date;
import java.util.Map;

/**
 * 功能描述：Playground 历史记录响应 VO
 *
 * @date 2024/07/13 16:06
 */
public class PlaygroundHistoryRespVO {

    private String id;
    private String requestId;
    private String playgroundType;
    private String appId;
    private Map<String, Object> inputData;
    private Map<String, Object> configSnapshot;
    private Map<String, Object> outputData;
    private int score;
    private Integer latency;
    private Integer upstreamLatency;
    private Date createdAt;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getRequestId() {
        return requestId;
    }

    public void setRequestId(String requestId) {
        this.requestId = requestId;
    }

    public String getPlaygroundType() {
        return playgroundType;
    }

    public void setPlaygroundType(String playgroundType) {
        this.playgroundType = playgroundType;
    }

    public String getAppId() {
        return appId;
    }

    public void setAppId(String appId) {
        this.appId = appId;
    }

    public Map<String, Object> getInputData() {
        return inputData;
    }

    public void setInputData(Map<String, Object> inputData) {
        this.inputData = inputData;
    }

    public Map<String, Object> getConfigSnapshot() {
        return configSnapshot;
    }

    public void setConfigSnapshot(Map<String, Object> configSnapshot) {
        this.configSnapshot = configSnapshot;
    }

    public Map<String, Object> getOutputData() {
        return outputData;
    }

    public void setOutputData(Map<String, Object> outputData) {
        this.outputData = outputData;
    }

    public int getScore() {
        return score;
    }

    public void setScore(int score) {
        this.score = score;
    }

    public Integer getLatency() {
        return latency;
    }

    public void setLatency(Integer latency) {
        this.latency = latency;
    }

    public Integer getUpstreamLatency() {
        return upstreamLatency;
    }

    public void setUpstreamLatency(Integer upstreamLatency) {
        this.upstreamLatency = upstreamLatency;
    }

    public Date getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Date createdAt) {
        this.createdAt = createdAt;
    }
}
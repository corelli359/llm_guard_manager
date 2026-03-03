/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.eval;

import java.util.Date;
import java.util.List;
import java.util.Map;

/**
 * 功能描述：测评任务结果响应 VO
 *
 * @date 2024/07/13 16:06
 */
public class EvalTaskResultRespVO {

    private String id;
    private String taskId;
    private String testCaseId;
    private String content;
    private List<String> tagCodes;
    private String expectedResult;
    private Integer guardrailScore;
    private String guardrailResult;
    private Map<String, Object> guardrailRaw;
    private Integer guardrailLatency;
    private String llmJudgment;
    private String llmReason;
    private Double llmConfidence;
    private Boolean isConsistent;
    private Boolean isCorrect;
    private String status;
    private String errorMessage;
    private Date createdAt;
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getTaskId() {
        return taskId;
    }

    public void setTaskId(String taskId) {
        this.taskId = taskId;
    }

    public String getTestCaseId() {
        return testCaseId;
    }

    public void setTestCaseId(String testCaseId) {
        this.testCaseId = testCaseId;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public List<String> getTagCodes() {
        return tagCodes;
    }

    public void setTagCodes(List<String> tagCodes) {
        this.tagCodes = tagCodes;
    }

    public String getExpectedResult() {
        return expectedResult;
    }

    public void setExpectedResult(String expectedResult) {
        this.expectedResult = expectedResult;
    }
    public Integer getGuardrailScore() {
        return guardrailScore;
    }

    public void setGuardrailScore(Integer guardrailScore) {
        this.guardrailScore = guardrailScore;
    }

    public String getGuardrailResult() {
        return guardrailResult;
    }

    public void setGuardrailResult(String guardrailResult) {
        this.guardrailResult = guardrailResult;
    }

    public Map<String, Object> getGuardrailRaw() {
        return guardrailRaw;
    }

    public void setGuardrailRaw(Map<String, Object> guardrailRaw) {
        this.guardrailRaw = guardrailRaw;
    }

    public Integer getGuardrailLatency() {
        return guardrailLatency;
    }

    public void setGuardrailLatency(Integer guardrailLatency) {
        this.guardrailLatency = guardrailLatency;
    }

    public String getLlmJudgment() {
        return llmJudgment;
    }

    public void setLlmJudgment(String llmJudgment) {
        this.llmJudgment = llmJudgment;
    }

    public String getLlmReason() {
        return llmReason;
    }

    public void setLlmReason(String llmReason) {
        this.llmReason = llmReason;
    }
    public Double getLlmConfidence() {
        return llmConfidence;
    }

    public void setLlmConfidence(Double llmConfidence) {
        this.llmConfidence = llmConfidence;
    }

    public Boolean getIsConsistent() {
        return isConsistent;
    }

    public void setIsConsistent(Boolean isConsistent) {
        this.isConsistent = isConsistent;
    }

    public Boolean getIsCorrect() {
        return isCorrect;
    }

    public void setIsCorrect(Boolean isCorrect) {
        this.isCorrect = isCorrect;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public Date getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Date createdAt) {
        this.createdAt = createdAt;
    }
}

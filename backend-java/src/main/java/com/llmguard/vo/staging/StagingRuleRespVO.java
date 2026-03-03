/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.staging;

import java.util.Date;

/**
 * 功能描述：暂存规则响应 VO
 *
 * @date 2024/07/13 16:06
 */
public class StagingRuleRespVO {

    private String id;
    private String tagCode;
    private String predictedStrategy;
    private String finalStrategy;
    private String extraCondition;
    private String status;
    private Boolean isModified;
    private String claimedBy;
    private Date claimedAt;
    private String batchId;
    private String annotator;
    private Date annotatedAt;
    private Date createdAt;
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getTagCode() {
        return tagCode;
    }

    public void setTagCode(String tagCode) {
        this.tagCode = tagCode;
    }

    public String getPredictedStrategy() {
        return predictedStrategy;
    }

    public void setPredictedStrategy(String predictedStrategy) {
        this.predictedStrategy = predictedStrategy;
    }

    public String getFinalStrategy() {
        return finalStrategy;
    }

    public void setFinalStrategy(String finalStrategy) {
        this.finalStrategy = finalStrategy;
    }

    public String getExtraCondition() {
        return extraCondition;
    }

    public void setExtraCondition(String extraCondition) {
        this.extraCondition = extraCondition;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
    public Boolean getIsModified() {
        return isModified;
    }

    public void setIsModified(Boolean isModified) {
        this.isModified = isModified;
    }

    public String getClaimedBy() {
        return claimedBy;
    }

    public void setClaimedBy(String claimedBy) {
        this.claimedBy = claimedBy;
    }

    public Date getClaimedAt() {
        return claimedAt;
    }

    public void setClaimedAt(Date claimedAt) {
        this.claimedAt = claimedAt;
    }

    public String getBatchId() {
        return batchId;
    }

    public void setBatchId(String batchId) {
        this.batchId = batchId;
    }

    public String getAnnotator() {
        return annotator;
    }

    public void setAnnotator(String annotator) {
        this.annotator = annotator;
    }

    public Date getAnnotatedAt() {
        return annotatedAt;
    }

    public void setAnnotatedAt(Date annotatedAt) {
        this.annotatedAt = annotatedAt;
    }

    public Date getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Date createdAt) {
        this.createdAt = createdAt;
    }
}

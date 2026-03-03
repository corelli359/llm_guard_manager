/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.entity;

import com.baomidou.mybatisplus.annotation.TableName;

import java.util.Date;

/**
 * 功能描述：暂存全局敏感词实体
 *
 * @date 2024/07/13 16:06
 */
@TableName("staging_global_keywords")
public class StagingGlobalKeywordDO extends BaseDO {

    private String keyword;
    private String predictedTag;
    private String predictedRisk;
    private String finalTag;
    private String finalRisk;
    private String status;
    private Boolean isModified;
    private String claimedBy;
    private Date claimedAt;
    private String batchId;
    private String annotator;
    private Date annotatedAt;

    public String getKeyword() {
        return keyword;
    }

    public void setKeyword(String keyword) {
        this.keyword = keyword;
    }

    public String getPredictedTag() {
        return predictedTag;
    }

    public void setPredictedTag(String predictedTag) {
        this.predictedTag = predictedTag;
    }

    public String getPredictedRisk() {
        return predictedRisk;
    }

    public void setPredictedRisk(String predictedRisk) {
        this.predictedRisk = predictedRisk;
    }

    public String getFinalTag() {
        return finalTag;
    }

    public void setFinalTag(String finalTag) {
        this.finalTag = finalTag;
    }

    public String getFinalRisk() {
        return finalRisk;
    }

    public void setFinalRisk(String finalRisk) {
        this.finalRisk = finalRisk;
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
}

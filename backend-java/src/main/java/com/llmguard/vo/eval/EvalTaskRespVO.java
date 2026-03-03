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
 * 功能描述：测评任务响应 VO
 *
 * @date 2024/07/13 16:06
 */
public class EvalTaskRespVO {

    private String id;
    private String taskName;
    private String appId;
    private String status;
    private Integer totalCases;
    private Integer completedCases;
    private Integer failedCases;
    private Integer concurrency;
    private List<String> filterTagCodes;
    private String filterExpectedResult;
    private Map<String, Object> metrics;
    private Date startedAt;
    private Date completedAt;
    private String createdBy;
    private Date createdAt;
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getTaskName() {
        return taskName;
    }

    public void setTaskName(String taskName) {
        this.taskName = taskName;
    }

    public String getAppId() {
        return appId;
    }

    public void setAppId(String appId) {
        this.appId = appId;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Integer getTotalCases() {
        return totalCases;
    }

    public void setTotalCases(Integer totalCases) {
        this.totalCases = totalCases;
    }

    public Integer getCompletedCases() {
        return completedCases;
    }

    public void setCompletedCases(Integer completedCases) {
        this.completedCases = completedCases;
    }
    public Integer getFailedCases() {
        return failedCases;
    }

    public void setFailedCases(Integer failedCases) {
        this.failedCases = failedCases;
    }

    public Integer getConcurrency() {
        return concurrency;
    }

    public void setConcurrency(Integer concurrency) {
        this.concurrency = concurrency;
    }

    public List<String> getFilterTagCodes() {
        return filterTagCodes;
    }

    public void setFilterTagCodes(List<String> filterTagCodes) {
        this.filterTagCodes = filterTagCodes;
    }

    public String getFilterExpectedResult() {
        return filterExpectedResult;
    }

    public void setFilterExpectedResult(String filterExpectedResult) {
        this.filterExpectedResult = filterExpectedResult;
    }

    public Map<String, Object> getMetrics() {
        return metrics;
    }

    public void setMetrics(Map<String, Object> metrics) {
        this.metrics = metrics;
    }

    public Date getStartedAt() {
        return startedAt;
    }

    public void setStartedAt(Date startedAt) {
        this.startedAt = startedAt;
    }

    public Date getCompletedAt() {
        return completedAt;
    }

    public void setCompletedAt(Date completedAt) {
        this.completedAt = completedAt;
    }

    public String getCreatedBy() {
        return createdBy;
    }

    public void setCreatedBy(String createdBy) {
        this.createdBy = createdBy;
    }

    public Date getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Date createdAt) {
        this.createdAt = createdAt;
    }
}

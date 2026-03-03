/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.eval;

import javax.validation.constraints.Max;
import javax.validation.constraints.Min;
import javax.validation.constraints.NotBlank;
import java.util.List;

/**
 * 功能描述：创建测评任务请求 VO
 *
 * @date 2024/07/13 16:06
 */
public class EvalTaskCreateVO {

    @NotBlank(message = "任务名称不能为空")
    private String taskName;

    @NotBlank(message = "应用ID不能为空")
    private String appId;

    @Min(value = 1, message = "并发数最小为1")
    @Max(value = 20, message = "并发数最大为20")
    private Integer concurrency = 5;

    private List<String> filterTagCodes;

    private String filterExpectedResult;

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
}

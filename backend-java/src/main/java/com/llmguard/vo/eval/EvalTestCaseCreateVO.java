/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.eval;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Pattern;
import java.util.List;

/**
 * 功能描述：创建测评用例请求 VO
 *
 * @date 2024/07/13 16:06
 */
public class EvalTestCaseCreateVO {

    @NotBlank(message = "测试内容不能为空")
    private String content;

    private List<String> tagCodes;

    private String riskPoint;

    @NotBlank(message = "预期结果不能为空")
    @Pattern(regexp = "COMPLIANT|VIOLATION", message = "预期结果只能为 COMPLIANT 或 VIOLATION")
    private String expectedResult;

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

    public String getRiskPoint() {
        return riskPoint;
    }

    public void setRiskPoint(String riskPoint) {
        this.riskPoint = riskPoint;
    }

    public String getExpectedResult() {
        return expectedResult;
    }

    public void setExpectedResult(String expectedResult) {
        this.expectedResult = expectedResult;
    }
}

/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.vo.playground;

import javax.validation.constraints.NotBlank;

/**
 * 功能描述：Playground 输入检测请求 VO
 *
 * @date 2024/07/13 16:06
 */
public class PlaygroundInputVO {

    @NotBlank(message = "应用ID不能为空")
    private String appId;

    @NotBlank(message = "输入内容不能为空")
    private String inputPrompt;

    private boolean useCustomizeWhite = false;
    private boolean useCustomizeWords = false;
    private boolean useCustomizeRule = false;
    private boolean useVipBlack = false;
    private boolean useVipWhite = false;

    public String getAppId() {
        return appId;
    }

    public void setAppId(String appId) {
        this.appId = appId;
    }

    public String getInputPrompt() {
        return inputPrompt;
    }

    public void setInputPrompt(String inputPrompt) {
        this.inputPrompt = inputPrompt;
    }

    public boolean isUseCustomizeWhite() {
        return useCustomizeWhite;
    }

    public void setUseCustomizeWhite(boolean useCustomizeWhite) {
        this.useCustomizeWhite = useCustomizeWhite;
    }

    public boolean isUseCustomizeWords() {
        return useCustomizeWords;
    }

    public void setUseCustomizeWords(boolean useCustomizeWords) {
        this.useCustomizeWords = useCustomizeWords;
    }

    public boolean isUseCustomizeRule() {
        return useCustomizeRule;
    }

    public void setUseCustomizeRule(boolean useCustomizeRule) {
        this.useCustomizeRule = useCustomizeRule;
    }

    public boolean isUseVipBlack() {
        return useVipBlack;
    }

    public void setUseVipBlack(boolean useVipBlack) {
        this.useVipBlack = useVipBlack;
    }

    public boolean isUseVipWhite() {
        return useVipWhite;
    }

    public void setUseVipWhite(boolean useVipWhite) {
        this.useVipWhite = useVipWhite;
    }
}
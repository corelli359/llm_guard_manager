package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PlaygroundInputRequest {
    private String appId;
    private String inputPrompt;
    @Builder.Default
    private Boolean useCustomizeWhite = false;
    @Builder.Default
    private Boolean useCustomizeWords = false;
    @Builder.Default
    private Boolean useCustomizeRule = false;
    @Builder.Default
    private Boolean useVipBlack = false;
    @Builder.Default
    private Boolean useVipWhite = false;
    @Builder.Default
    private String playgroundType = "INPUT";
}

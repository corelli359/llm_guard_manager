package com.llmguard.manager.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GuardrailConfig {

    private String appId;

    private String inputPrompt;

    @Builder.Default
    private boolean useCustomizeWhite = false;

    @Builder.Default
    private boolean useCustomizeWords = false;

    @Builder.Default
    private boolean useCustomizeRule = false;

    @Builder.Default
    private boolean useVipBlack = false;

    @Builder.Default
    private boolean useVipWhite = false;
}

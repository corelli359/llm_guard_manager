/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.common.constant;

/**
 * 功能描述：通用常量定义
 *
 * @date 2024/07/13 16:06
 */
public final class CommonConstant {

    private CommonConstant() {
    }

    // 决策分数
    public static final int SCORE_PASS = 0;
    public static final int SCORE_REWRITE = 50;
    public static final int SCORE_BLOCK = 100;
    public static final int SCORE_MANUAL_REVIEW = 1000;

    // 场景关键词分类
    public static final int CATEGORY_WHITE = 0;
    public static final int CATEGORY_BLACK = 1;

    // 策略类型
    public static final String STRATEGY_BLOCK = "BLOCK";
    public static final String STRATEGY_PASS = "PASS";
    public static final String STRATEGY_REWRITE = "REWRITE";

    // 匹配类型
    public static final String MATCH_TYPE_KEYWORD = "KEYWORD";
    public static final String MATCH_TYPE_TAG = "TAG";

    // 用户角色
    public static final String ROLE_SYSTEM_ADMIN = "SYSTEM_ADMIN";
    public static final String ROLE_SCENARIO_ADMIN = "SCENARIO_ADMIN";
    public static final String ROLE_ANNOTATOR = "ANNOTATOR";
    public static final String ROLE_AUDITOR = "AUDITOR";
}

/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.controller;

import com.llmguard.common.result.R;
import com.llmguard.service.IScenarioKeywordService;
import com.llmguard.vo.keyword.ScenarioKeywordCreateVO;
import com.llmguard.vo.keyword.ScenarioKeywordRespVO;
import com.llmguard.vo.keyword.ScenarioKeywordUpdateVO;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * 功能描述：场景敏感词控制器
 *
 * @date 2024/07/13 16:06
 */
@RestController
@RequestMapping("/api/v1/keywords/scenario")
public class ScenarioKeywordController {

    private final IScenarioKeywordService scenarioKeywordService;

    public ScenarioKeywordController(IScenarioKeywordService scenarioKeywordService) {
        this.scenarioKeywordService = scenarioKeywordService;
    }

    /**
     * 根据场景ID获取敏感词列表
     *
     * @param scenarioId 场景ID
     * @param ruleMode   规则模式（可选）
     * @return 敏感词列表
     */
    @GetMapping("/{scenarioId}")
    public R<List<ScenarioKeywordRespVO>> list(@PathVariable String scenarioId,
                                                @RequestParam(required = false) Integer ruleMode) {
        return R.ok(scenarioKeywordService.listByScenarioId(scenarioId, ruleMode));
    }

    /**
     * 创建场景敏感词
     *
     * @param createVO 创建参数
     * @return 创建后的敏感词
     */
    @PostMapping
    public R<ScenarioKeywordRespVO> create(@Valid @RequestBody ScenarioKeywordCreateVO createVO) {
        return R.ok(scenarioKeywordService.createKeyword(createVO));
    }

    /**
     * 更新场景敏感词
     *
     * @param keywordId 敏感词ID
     * @param updateVO  更新参数
     * @return 更新后的敏感词
     */
    @PutMapping("/{keywordId}")
    public R<ScenarioKeywordRespVO> update(@PathVariable String keywordId,
                                            @RequestBody ScenarioKeywordUpdateVO updateVO) {
        return R.ok(scenarioKeywordService.updateKeyword(keywordId, updateVO));
    }

    /**
     * 删除场景敏感词
     *
     * @param keywordId 敏感词ID
     * @return 被删除的敏感词
     */
    @DeleteMapping("/{keywordId}")
    public R<ScenarioKeywordRespVO> delete(@PathVariable String keywordId) {
        return R.ok(scenarioKeywordService.deleteKeyword(keywordId));
    }
}

/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.controller;

import com.llmguard.common.result.R;
import com.llmguard.service.IGlobalKeywordService;
import com.llmguard.vo.keyword.GlobalKeywordCreateVO;
import com.llmguard.vo.keyword.GlobalKeywordRespVO;
import com.llmguard.vo.keyword.GlobalKeywordUpdateVO;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * 功能描述：全局敏感词控制器
 *
 * @date 2024/07/13 16:06
 */
@RestController
@RequestMapping("/api/v1/keywords/global")
public class GlobalKeywordController {

    private final IGlobalKeywordService globalKeywordService;

    public GlobalKeywordController(IGlobalKeywordService globalKeywordService) {
        this.globalKeywordService = globalKeywordService;
    }

    /**
     * 获取全局敏感词列表
     *
     * @param skip  跳过条数
     * @param limit 限制条数
     * @param q     关键词搜索（模糊匹配）
     * @param tag   标签编码过滤（精确匹配）
     * @return 敏感词列表
     */
    @GetMapping
    public R<List<GlobalKeywordRespVO>> list(
            @RequestParam(defaultValue = "0") int skip,
            @RequestParam(defaultValue = "100") int limit,
            @RequestParam(required = false) String q,
            @RequestParam(required = false) String tag) {
        return R.ok(globalKeywordService.listKeywords(skip, limit, q, tag));
    }

    /**
     * 创建全局敏感词
     *
     * @param createVO 创建参数
     * @return 创建后的敏感词
     */
    @PostMapping
    public R<GlobalKeywordRespVO> create(@Valid @RequestBody GlobalKeywordCreateVO createVO) {
        return R.ok(globalKeywordService.createKeyword(createVO));
    }

    /**
     * 更新全局敏感词
     *
     * @param keywordId 敏感词ID
     * @param updateVO  更新参数
     * @return 更新后的敏感词
     */
    @PutMapping("/{keywordId}")
    public R<GlobalKeywordRespVO> update(@PathVariable String keywordId,
                                          @RequestBody GlobalKeywordUpdateVO updateVO) {
        return R.ok(globalKeywordService.updateKeyword(keywordId, updateVO));
    }

    /**
     * 删除全局敏感词
     *
     * @param keywordId 敏感词ID
     * @return 被删除的敏感词
     */
    @DeleteMapping("/{keywordId}")
    public R<GlobalKeywordRespVO> delete(@PathVariable String keywordId) {
        return R.ok(globalKeywordService.deleteKeyword(keywordId));
    }
}

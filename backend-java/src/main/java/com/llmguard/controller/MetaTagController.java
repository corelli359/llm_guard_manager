/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.controller;

import com.llmguard.common.result.R;
import com.llmguard.service.IMetaTagService;
import com.llmguard.vo.tag.MetaTagCreateVO;
import com.llmguard.vo.tag.MetaTagRespVO;
import com.llmguard.vo.tag.MetaTagUpdateVO;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * 功能描述：元数据标签控制器
 *
 * @date 2024/07/13 16:06
 */
@RestController
@RequestMapping("/api/v1/tags")
public class MetaTagController {

    private final IMetaTagService metaTagService;

    public MetaTagController(IMetaTagService metaTagService) {
        this.metaTagService = metaTagService;
    }

    /**
     * 获取标签列表
     *
     * @param skip  跳过条数
     * @param limit 限制条数
     * @return 标签列表
     */
    @GetMapping
    public R<List<MetaTagRespVO>> list(@RequestParam(defaultValue = "0") int skip,
                                       @RequestParam(defaultValue = "100") int limit) {
        return R.ok(metaTagService.getAllTags(skip, limit));
    }

    /**
     * 创建标签
     *
     * @param createVO 创建参数
     * @return 创建后的标签
     */
    @PostMapping
    public R<MetaTagRespVO> create(@Valid @RequestBody MetaTagCreateVO createVO) {
        return R.ok(metaTagService.createTag(createVO));
    }

    /**
     * 更新标签
     *
     * @param tagId    标签ID
     * @param updateVO 更新参数
     * @return 更新后的标签
     */
    @PutMapping("/{tagId}")
    public R<MetaTagRespVO> update(@PathVariable String tagId,
                                   @RequestBody MetaTagUpdateVO updateVO) {
        return R.ok(metaTagService.updateTag(tagId, updateVO));
    }

    /**
     * 删除标签
     *
     * @param tagId 标签ID
     * @return 被删除的标签
     */
    @DeleteMapping("/{tagId}")
    public R<MetaTagRespVO> delete(@PathVariable String tagId) {
        return R.ok(metaTagService.deleteTag(tagId));
    }
}

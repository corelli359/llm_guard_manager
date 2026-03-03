/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service;

import com.llmguard.vo.tag.MetaTagCreateVO;
import com.llmguard.vo.tag.MetaTagRespVO;
import com.llmguard.vo.tag.MetaTagUpdateVO;

import java.util.List;

/**
 * 功能描述：元数据标签服务接口
 *
 * @date 2024/07/13 16:06
 */
public interface IMetaTagService {

    /**
     * 获取标签列表
     *
     * @param skip  跳过条数
     * @param limit 限制条数
     * @return 标签列表
     */
    List<MetaTagRespVO> getAllTags(int skip, int limit);

    /**
     * 创建标签
     *
     * @param createVO 创建参数
     * @return 创建后的标签
     */
    MetaTagRespVO createTag(MetaTagCreateVO createVO);

    /**
     * 更新标签
     *
     * @param tagId    标签ID
     * @param updateVO 更新参数
     * @return 更新后的标签
     */
    MetaTagRespVO updateTag(String tagId, MetaTagUpdateVO updateVO);

    /**
     * 删除标签
     *
     * @param tagId 标签ID
     * @return 被删除的标签
     */
    MetaTagRespVO deleteTag(String tagId);
}

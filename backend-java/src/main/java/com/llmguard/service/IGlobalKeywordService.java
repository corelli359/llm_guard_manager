/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service;

import com.llmguard.vo.keyword.GlobalKeywordCreateVO;
import com.llmguard.vo.keyword.GlobalKeywordRespVO;
import com.llmguard.vo.keyword.GlobalKeywordUpdateVO;

import java.util.List;

/**
 * 功能描述：全局敏感词服务接口
 *
 * @date 2024/07/13 16:06
 */
public interface IGlobalKeywordService {

    /**
     * 获取全局敏感词列表（支持关键词搜索和标签过滤）
     *
     * @param skip  跳过条数
     * @param limit 限制条数
     * @param q     关键词搜索（模糊匹配）
     * @param tag   标签编码过滤（精确匹配）
     * @return 敏感词列表
     */
    List<GlobalKeywordRespVO> listKeywords(int skip, int limit, String q, String tag);

    /**
     * 创建全局敏感词
     *
     * @param createVO 创建参数
     * @return 创建后的敏感词
     */
    GlobalKeywordRespVO createKeyword(GlobalKeywordCreateVO createVO);

    /**
     * 更新全局敏感词
     *
     * @param keywordId 敏感词ID
     * @param updateVO  更新参数
     * @return 更新后的敏感词
     */
    GlobalKeywordRespVO updateKeyword(String keywordId, GlobalKeywordUpdateVO updateVO);

    /**
     * 删除全局敏感词
     *
     * @param keywordId 敏感词ID
     * @return 被删除的敏感词
     */
    GlobalKeywordRespVO deleteKeyword(String keywordId);
}

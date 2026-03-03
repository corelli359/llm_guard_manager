/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.llmguard.common.exception.BusinessException;
import com.llmguard.entity.GlobalKeywordDO;
import com.llmguard.mapper.GlobalKeywordMapper;
import com.llmguard.service.IGlobalKeywordService;
import com.llmguard.vo.keyword.GlobalKeywordCreateVO;
import com.llmguard.vo.keyword.GlobalKeywordRespVO;
import com.llmguard.vo.keyword.GlobalKeywordUpdateVO;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 功能描述：全局敏感词服务实现
 *
 * @date 2024/07/13 16:06
 */
@Service
public class GlobalKeywordServiceImpl implements IGlobalKeywordService {

    private final GlobalKeywordMapper globalKeywordMapper;

    public GlobalKeywordServiceImpl(GlobalKeywordMapper globalKeywordMapper) {
        this.globalKeywordMapper = globalKeywordMapper;
    }

    @Override
    public List<GlobalKeywordRespVO> listKeywords(int skip, int limit, String q, String tag) {
        LambdaQueryWrapper<GlobalKeywordDO> wrapper = new LambdaQueryWrapper<>();
        if (q != null && !q.isEmpty()) {
            wrapper.like(GlobalKeywordDO::getKeyword, q);
        }
        if (tag != null && !tag.isEmpty()) {
            wrapper.eq(GlobalKeywordDO::getTagCode, tag);
        }
        Page<GlobalKeywordDO> page = new Page<>(skip / Math.max(limit, 1) + 1, limit);
        Page<GlobalKeywordDO> result = globalKeywordMapper.selectPage(page, wrapper);
        return result.getRecords().stream().map(this::toRespVO).collect(Collectors.toList());
    }

    @Override
    public GlobalKeywordRespVO createKeyword(GlobalKeywordCreateVO createVO) {
        // 唯一性校验
        Long count = globalKeywordMapper.selectCount(
                new LambdaQueryWrapper<GlobalKeywordDO>().eq(GlobalKeywordDO::getKeyword, createVO.getKeyword())
        );
        if (count > 0) {
            throw new BusinessException("关键词已存在: " + createVO.getKeyword());
        }

        GlobalKeywordDO entity = new GlobalKeywordDO();
        entity.setKeyword(createVO.getKeyword());
        entity.setTagCode(createVO.getTagCode());
        entity.setRiskLevel(createVO.getRiskLevel());
        entity.setIsActive(createVO.getIsActive());
        globalKeywordMapper.insert(entity);
        return toRespVO(entity);
    }

    @Override
    public GlobalKeywordRespVO updateKeyword(String keywordId, GlobalKeywordUpdateVO updateVO) {
        GlobalKeywordDO entity = globalKeywordMapper.selectById(keywordId);
        if (entity == null) {
            throw new BusinessException(404, "敏感词不存在");
        }
        if (updateVO.getKeyword() != null) {
            // 如果修改了 keyword，需要校验唯一性
            Long count = globalKeywordMapper.selectCount(
                    new LambdaQueryWrapper<GlobalKeywordDO>()
                            .eq(GlobalKeywordDO::getKeyword, updateVO.getKeyword())
                            .ne(GlobalKeywordDO::getId, keywordId)
            );
            if (count > 0) {
                throw new BusinessException("关键词已存在: " + updateVO.getKeyword());
            }
            entity.setKeyword(updateVO.getKeyword());
        }
        if (updateVO.getTagCode() != null) {
            entity.setTagCode(updateVO.getTagCode());
        }
        if (updateVO.getRiskLevel() != null) {
            entity.setRiskLevel(updateVO.getRiskLevel());
        }
        if (updateVO.getIsActive() != null) {
            entity.setIsActive(updateVO.getIsActive());
        }
        globalKeywordMapper.updateById(entity);
        return toRespVO(entity);
    }

    @Override
    public GlobalKeywordRespVO deleteKeyword(String keywordId) {
        GlobalKeywordDO entity = globalKeywordMapper.selectById(keywordId);
        if (entity == null) {
            throw new BusinessException(404, "敏感词不存在");
        }
        globalKeywordMapper.deleteById(keywordId);
        return toRespVO(entity);
    }

    /**
     * DO 转 RespVO
     *
     * @param entity 实体对象
     * @return 响应 VO
     */
    private GlobalKeywordRespVO toRespVO(GlobalKeywordDO entity) {
        GlobalKeywordRespVO vo = new GlobalKeywordRespVO();
        vo.setId(entity.getId());
        vo.setKeyword(entity.getKeyword());
        vo.setTagCode(entity.getTagCode());
        vo.setRiskLevel(entity.getRiskLevel());
        vo.setIsActive(entity.getIsActive());
        return vo;
    }
}

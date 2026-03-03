/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.llmguard.common.exception.BusinessException;
import com.llmguard.entity.MetaTagDO;
import com.llmguard.mapper.MetaTagMapper;
import com.llmguard.service.IMetaTagService;
import com.llmguard.vo.tag.MetaTagCreateVO;
import com.llmguard.vo.tag.MetaTagRespVO;
import com.llmguard.vo.tag.MetaTagUpdateVO;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 功能描述：元数据标签服务实现
 *
 * @date 2024/07/13 16:06
 */
@Service
public class MetaTagServiceImpl implements IMetaTagService {

    private final MetaTagMapper metaTagMapper;

    public MetaTagServiceImpl(MetaTagMapper metaTagMapper) {
        this.metaTagMapper = metaTagMapper;
    }

    @Override
    public List<MetaTagRespVO> getAllTags(int skip, int limit) {
        Page<MetaTagDO> page = new Page<>(skip / Math.max(limit, 1) + 1, limit);
        Page<MetaTagDO> result = metaTagMapper.selectPage(page, null);
        return result.getRecords().stream().map(this::toRespVO).collect(Collectors.toList());
    }

    @Override
    public MetaTagRespVO createTag(MetaTagCreateVO createVO) {
        // 唯一性校验
        Long count = metaTagMapper.selectCount(
                new LambdaQueryWrapper<MetaTagDO>().eq(MetaTagDO::getTagCode, createVO.getTagCode())
        );
        if (count > 0) {
            throw new BusinessException("tag_code 已存在: " + createVO.getTagCode());
        }

        MetaTagDO entity = new MetaTagDO();
        entity.setTagCode(createVO.getTagCode());
        entity.setTagName(createVO.getTagName());
        entity.setParentCode(createVO.getParentCode());
        entity.setLevel(createVO.getLevel());
        entity.setIsActive(createVO.getIsActive());
        metaTagMapper.insert(entity);
        return toRespVO(entity);
    }

    @Override
    public MetaTagRespVO updateTag(String tagId, MetaTagUpdateVO updateVO) {
        MetaTagDO entity = metaTagMapper.selectById(tagId);
        if (entity == null) {
            throw new BusinessException(404, "标签不存在");
        }
        if (updateVO.getTagName() != null) {
            entity.setTagName(updateVO.getTagName());
        }
        if (updateVO.getParentCode() != null) {
            entity.setParentCode(updateVO.getParentCode());
        }
        if (updateVO.getLevel() != null) {
            entity.setLevel(updateVO.getLevel());
        }
        if (updateVO.getIsActive() != null) {
            entity.setIsActive(updateVO.getIsActive());
        }
        metaTagMapper.updateById(entity);
        return toRespVO(entity);
    }

    @Override
    public MetaTagRespVO deleteTag(String tagId) {
        MetaTagDO entity = metaTagMapper.selectById(tagId);
        if (entity == null) {
            throw new BusinessException(404, "标签不存在");
        }
        metaTagMapper.deleteById(tagId);
        return toRespVO(entity);
    }

    /**
     * DO 转 RespVO
     *
     * @param entity 实体对象
     * @return 响应 VO
     */
    private MetaTagRespVO toRespVO(MetaTagDO entity) {
        MetaTagRespVO vo = new MetaTagRespVO();
        vo.setId(entity.getId());
        vo.setTagCode(entity.getTagCode());
        vo.setTagName(entity.getTagName());
        vo.setParentCode(entity.getParentCode());
        vo.setLevel(entity.getLevel());
        vo.setIsActive(entity.getIsActive());
        return vo;
    }
}

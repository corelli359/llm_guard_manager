/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.llmguard.common.exception.BusinessException;
import com.llmguard.entity.ScenarioKeywordDO;
import com.llmguard.mapper.ScenarioKeywordMapper;
import com.llmguard.service.IScenarioKeywordService;
import com.llmguard.vo.keyword.ScenarioKeywordCreateVO;
import com.llmguard.vo.keyword.ScenarioKeywordRespVO;
import com.llmguard.vo.keyword.ScenarioKeywordUpdateVO;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 功能描述：场景敏感词服务实现
 *
 * @date 2024/07/13 16:06
 */
@Service
public class ScenarioKeywordServiceImpl implements IScenarioKeywordService {

    private final ScenarioKeywordMapper scenarioKeywordMapper;

    public ScenarioKeywordServiceImpl(ScenarioKeywordMapper scenarioKeywordMapper) {
        this.scenarioKeywordMapper = scenarioKeywordMapper;
    }

    @Override
    public List<ScenarioKeywordRespVO> listByScenarioId(String scenarioId, Integer ruleMode) {
        LambdaQueryWrapper<ScenarioKeywordDO> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ScenarioKeywordDO::getScenarioId, scenarioId);
        if (ruleMode != null) {
            wrapper.eq(ScenarioKeywordDO::getRuleMode, ruleMode);
        }
        List<ScenarioKeywordDO> list = scenarioKeywordMapper.selectList(wrapper);
        return list.stream().map(this::toRespVO).collect(Collectors.toList());
    }

    @Override
    public ScenarioKeywordRespVO createKeyword(ScenarioKeywordCreateVO createVO) {
        // keyword + scenarioId 唯一性校验
        Long count = scenarioKeywordMapper.selectCount(
                new LambdaQueryWrapper<ScenarioKeywordDO>()
                        .eq(ScenarioKeywordDO::getKeyword, createVO.getKeyword())
                        .eq(ScenarioKeywordDO::getScenarioId, createVO.getScenarioId())
        );
        if (count > 0) {
            throw new BusinessException("该场景下关键词已存在: " + createVO.getKeyword());
        }

        ScenarioKeywordDO entity = new ScenarioKeywordDO();
        entity.setScenarioId(createVO.getScenarioId());
        entity.setKeyword(createVO.getKeyword());
        entity.setTagCode(createVO.getTagCode());
        entity.setRuleMode(createVO.getRuleMode());
        entity.setRiskLevel(createVO.getRiskLevel());
        entity.setIsActive(createVO.getIsActive());
        entity.setCategory(createVO.getCategory());
        entity.setExemptions(createVO.getExemptions());
        scenarioKeywordMapper.insert(entity);
        return toRespVO(entity);
    }

    @Override
    public ScenarioKeywordRespVO updateKeyword(String keywordId, ScenarioKeywordUpdateVO updateVO) {
        ScenarioKeywordDO entity = scenarioKeywordMapper.selectById(keywordId);
        if (entity == null) {
            throw new BusinessException(404, "场景敏感词不存在");
        }
        if (updateVO.getScenarioId() != null) {
            entity.setScenarioId(updateVO.getScenarioId());
        }
        if (updateVO.getKeyword() != null) {
            entity.setKeyword(updateVO.getKeyword());
        }
        if (updateVO.getTagCode() != null) {
            entity.setTagCode(updateVO.getTagCode());
        }
        if (updateVO.getRuleMode() != null) {
            entity.setRuleMode(updateVO.getRuleMode());
        }
        if (updateVO.getRiskLevel() != null) {
            entity.setRiskLevel(updateVO.getRiskLevel());
        }
        if (updateVO.getIsActive() != null) {
            entity.setIsActive(updateVO.getIsActive());
        }
        if (updateVO.getCategory() != null) {
            entity.setCategory(updateVO.getCategory());
        }
        if (updateVO.getExemptions() != null) {
            entity.setExemptions(updateVO.getExemptions());
        }
        scenarioKeywordMapper.updateById(entity);
        return toRespVO(entity);
    }

    @Override
    public ScenarioKeywordRespVO deleteKeyword(String keywordId) {
        ScenarioKeywordDO entity = scenarioKeywordMapper.selectById(keywordId);
        if (entity == null) {
            throw new BusinessException(404, "场景敏感词不存在");
        }
        scenarioKeywordMapper.deleteById(keywordId);
        return toRespVO(entity);
    }

    /**
     * DO 转 RespVO
     *
     * @param entity 实体对象
     * @return 响应 VO
     */
    private ScenarioKeywordRespVO toRespVO(ScenarioKeywordDO entity) {
        ScenarioKeywordRespVO vo = new ScenarioKeywordRespVO();
        vo.setId(entity.getId());
        vo.setScenarioId(entity.getScenarioId());
        vo.setKeyword(entity.getKeyword());
        vo.setTagCode(entity.getTagCode());
        vo.setRuleMode(entity.getRuleMode());
        vo.setRiskLevel(entity.getRiskLevel());
        vo.setIsActive(entity.getIsActive());
        vo.setCategory(entity.getCategory());
        vo.setExemptions(entity.getExemptions());
        return vo;
    }
}

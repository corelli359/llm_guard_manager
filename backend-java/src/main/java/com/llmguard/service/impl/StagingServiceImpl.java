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
import com.llmguard.entity.RuleGlobalDefaultDO;
import com.llmguard.entity.StagingGlobalKeywordDO;
import com.llmguard.entity.StagingGlobalRuleDO;
import com.llmguard.mapper.GlobalKeywordMapper;
import com.llmguard.mapper.RuleGlobalDefaultMapper;
import com.llmguard.mapper.StagingGlobalKeywordMapper;
import com.llmguard.mapper.StagingGlobalRuleMapper;
import com.llmguard.service.IStagingService;
import com.llmguard.vo.staging.StagingKeywordRespVO;
import com.llmguard.vo.staging.StagingRuleRespVO;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 功能描述：暂存区服务实现
 *
 * @date 2024/07/13 16:06
 */
@Service
public class StagingServiceImpl implements IStagingService {

    private final StagingGlobalKeywordMapper stagingKeywordMapper;
    private final StagingGlobalRuleMapper stagingRuleMapper;
    private final GlobalKeywordMapper globalKeywordMapper;
    private final RuleGlobalDefaultMapper ruleGlobalDefaultMapper;

    public StagingServiceImpl(StagingGlobalKeywordMapper stagingKeywordMapper,
                              StagingGlobalRuleMapper stagingRuleMapper,
                              GlobalKeywordMapper globalKeywordMapper,
                              RuleGlobalDefaultMapper ruleGlobalDefaultMapper) {
        this.stagingKeywordMapper = stagingKeywordMapper;
        this.stagingRuleMapper = stagingRuleMapper;
        this.globalKeywordMapper = globalKeywordMapper;
        this.ruleGlobalDefaultMapper = ruleGlobalDefaultMapper;
    }
    @Override
    public List<StagingKeywordRespVO> listStagingKeywords(String status, int skip, int limit) {
        LambdaQueryWrapper<StagingGlobalKeywordDO> wrapper = new LambdaQueryWrapper<>();
        if (status != null && !status.isEmpty()) {
            wrapper.eq(StagingGlobalKeywordDO::getStatus, status);
        }
        Page<StagingGlobalKeywordDO> page = new Page<>(skip / Math.max(limit, 1) + 1, limit);
        Page<StagingGlobalKeywordDO> result = stagingKeywordMapper.selectPage(page, wrapper);
        return result.getRecords().stream().map(this::toKeywordRespVO).collect(Collectors.toList());
    }

    @Override
    public List<StagingRuleRespVO> listStagingRules(String status, int skip, int limit) {
        LambdaQueryWrapper<StagingGlobalRuleDO> wrapper = new LambdaQueryWrapper<>();
        if (status != null && !status.isEmpty()) {
            wrapper.eq(StagingGlobalRuleDO::getStatus, status);
        }
        Page<StagingGlobalRuleDO> page = new Page<>(skip / Math.max(limit, 1) + 1, limit);
        Page<StagingGlobalRuleDO> result = stagingRuleMapper.selectPage(page, wrapper);
        return result.getRecords().stream().map(this::toRuleRespVO).collect(Collectors.toList());
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public List<StagingKeywordRespVO> claimKeywords(String batchId, int count, String claimedBy) {
        LambdaQueryWrapper<StagingGlobalKeywordDO> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(StagingGlobalKeywordDO::getStatus, "PENDING");
        if (batchId != null && !batchId.isEmpty()) {
            wrapper.eq(StagingGlobalKeywordDO::getBatchId, batchId);
        }
        wrapper.last("LIMIT " + count);
        List<StagingGlobalKeywordDO> list = stagingKeywordMapper.selectList(wrapper);
        Date now = new Date();
        for (StagingGlobalKeywordDO item : list) {
            item.setStatus("CLAIMED");
            item.setClaimedBy(claimedBy);
            item.setClaimedAt(now);
            stagingKeywordMapper.updateById(item);
        }
        return list.stream().map(this::toKeywordRespVO).collect(Collectors.toList());
    }
    @Override
    @Transactional(rollbackFor = Exception.class)
    public List<StagingRuleRespVO> claimRules(String batchId, int count, String claimedBy) {
        LambdaQueryWrapper<StagingGlobalRuleDO> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(StagingGlobalRuleDO::getStatus, "PENDING");
        if (batchId != null && !batchId.isEmpty()) {
            wrapper.eq(StagingGlobalRuleDO::getBatchId, batchId);
        }
        wrapper.last("LIMIT " + count);
        List<StagingGlobalRuleDO> list = stagingRuleMapper.selectList(wrapper);
        Date now = new Date();
        for (StagingGlobalRuleDO item : list) {
            item.setStatus("CLAIMED");
            item.setClaimedBy(claimedBy);
            item.setClaimedAt(now);
            stagingRuleMapper.updateById(item);
        }
        return list.stream().map(this::toRuleRespVO).collect(Collectors.toList());
    }

    @Override
    public StagingKeywordRespVO reviewKeyword(String id, String finalTag, String finalRisk) {
        StagingGlobalKeywordDO entity = stagingKeywordMapper.selectById(id);
        if (entity == null) {
            throw new BusinessException(404, "暂存敏感词不存在");
        }
        entity.setFinalTag(finalTag);
        entity.setFinalRisk(finalRisk);
        entity.setStatus("REVIEWED");
        boolean modified = !finalTag.equals(entity.getPredictedTag())
                || !finalRisk.equals(entity.getPredictedRisk());
        entity.setIsModified(modified);
        entity.setAnnotatedAt(new Date());
        stagingKeywordMapper.updateById(entity);
        return toKeywordRespVO(entity);
    }

    @Override
    public StagingRuleRespVO reviewRule(String id, String finalStrategy, String extraCondition) {
        StagingGlobalRuleDO entity = stagingRuleMapper.selectById(id);
        if (entity == null) {
            throw new BusinessException(404, "暂存规则不存在");
        }
        entity.setFinalStrategy(finalStrategy);
        entity.setExtraCondition(extraCondition);
        entity.setStatus("REVIEWED");
        boolean modified = !finalStrategy.equals(entity.getPredictedStrategy());
        entity.setIsModified(modified);
        entity.setAnnotatedAt(new Date());
        stagingRuleMapper.updateById(entity);
        return toRuleRespVO(entity);
    }
    @Override
    @Transactional(rollbackFor = Exception.class)
    public int syncKeywords(List<String> ids) {
        int count = 0;
        for (String id : ids) {
            StagingGlobalKeywordDO staging = stagingKeywordMapper.selectById(id);
            if (staging == null || !"REVIEWED".equals(staging.getStatus())) {
                continue;
            }
            GlobalKeywordDO keyword = new GlobalKeywordDO();
            keyword.setKeyword(staging.getKeyword());
            keyword.setTagCode(staging.getFinalTag());
            keyword.setRiskLevel(staging.getFinalRisk());
            keyword.setIsActive(true);
            globalKeywordMapper.insert(keyword);
            staging.setStatus("SYNCED");
            stagingKeywordMapper.updateById(staging);
            count++;
        }
        return count;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public int syncRules(List<String> ids) {
        int count = 0;
        for (String id : ids) {
            StagingGlobalRuleDO staging = stagingRuleMapper.selectById(id);
            if (staging == null || !"REVIEWED".equals(staging.getStatus())) {
                continue;
            }
            RuleGlobalDefaultDO rule = new RuleGlobalDefaultDO();
            rule.setTagCode(staging.getTagCode());
            rule.setStrategy(staging.getFinalStrategy());
            rule.setExtraCondition(staging.getExtraCondition());
            rule.setIsActive(true);
            ruleGlobalDefaultMapper.insert(rule);
            staging.setStatus("SYNCED");
            stagingRuleMapper.updateById(staging);
            count++;
        }
        return count;
    }
    /**
     * StagingGlobalKeywordDO 转 StagingKeywordRespVO
     *
     * @param entity 实体对象
     * @return 响应 VO
     */
    private StagingKeywordRespVO toKeywordRespVO(StagingGlobalKeywordDO entity) {
        StagingKeywordRespVO vo = new StagingKeywordRespVO();
        vo.setId(entity.getId());
        vo.setKeyword(entity.getKeyword());
        vo.setPredictedTag(entity.getPredictedTag());
        vo.setPredictedRisk(entity.getPredictedRisk());
        vo.setFinalTag(entity.getFinalTag());
        vo.setFinalRisk(entity.getFinalRisk());
        vo.setStatus(entity.getStatus());
        vo.setIsModified(entity.getIsModified());
        vo.setClaimedBy(entity.getClaimedBy());
        vo.setClaimedAt(entity.getClaimedAt());
        vo.setBatchId(entity.getBatchId());
        vo.setAnnotator(entity.getAnnotator());
        vo.setAnnotatedAt(entity.getAnnotatedAt());
        vo.setCreatedAt(entity.getCreatedAt());
        return vo;
    }

    /**
     * StagingGlobalRuleDO 转 StagingRuleRespVO
     *
     * @param entity 实体对象
     * @return 响应 VO
     */
    private StagingRuleRespVO toRuleRespVO(StagingGlobalRuleDO entity) {
        StagingRuleRespVO vo = new StagingRuleRespVO();
        vo.setId(entity.getId());
        vo.setTagCode(entity.getTagCode());
        vo.setPredictedStrategy(entity.getPredictedStrategy());
        vo.setFinalStrategy(entity.getFinalStrategy());
        vo.setExtraCondition(entity.getExtraCondition());
        vo.setStatus(entity.getStatus());
        vo.setIsModified(entity.getIsModified());
        vo.setClaimedBy(entity.getClaimedBy());
        vo.setClaimedAt(entity.getClaimedAt());
        vo.setBatchId(entity.getBatchId());
        vo.setAnnotator(entity.getAnnotator());
        vo.setAnnotatedAt(entity.getAnnotatedAt());
        vo.setCreatedAt(entity.getCreatedAt());
        return vo;
    }
}

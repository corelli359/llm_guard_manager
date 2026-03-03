/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.llmguard.common.exception.BusinessException;
import com.llmguard.entity.RuleGlobalDefaultDO;
import com.llmguard.entity.RuleScenarioPolicyDO;
import com.llmguard.mapper.RuleGlobalDefaultMapper;
import com.llmguard.mapper.RuleScenarioPolicyMapper;
import com.llmguard.service.IRulePolicyService;
import com.llmguard.vo.policy.GlobalDefaultCreateVO;
import com.llmguard.vo.policy.GlobalDefaultRespVO;
import com.llmguard.vo.policy.GlobalDefaultUpdateVO;
import com.llmguard.vo.policy.ScenarioPolicyCreateVO;
import com.llmguard.vo.policy.ScenarioPolicyRespVO;
import com.llmguard.vo.policy.ScenarioPolicyUpdateVO;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 功能描述：规则策略服务实现，包含场景策略和全局默认策略
 *
 * @date 2024/07/13 16:06
 */
@Service
public class RulePolicyServiceImpl implements IRulePolicyService {

    private final RuleScenarioPolicyMapper scenarioPolicyMapper;
    private final RuleGlobalDefaultMapper globalDefaultMapper;

    public RulePolicyServiceImpl(RuleScenarioPolicyMapper scenarioPolicyMapper,
                                 RuleGlobalDefaultMapper globalDefaultMapper) {
        this.scenarioPolicyMapper = scenarioPolicyMapper;
        this.globalDefaultMapper = globalDefaultMapper;
    }

    // ==================== 场景策略 ====================

    @Override
    public List<ScenarioPolicyRespVO> listByScenarioId(String scenarioId) {
        LambdaQueryWrapper<RuleScenarioPolicyDO> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(RuleScenarioPolicyDO::getScenarioId, scenarioId);
        List<RuleScenarioPolicyDO> list = scenarioPolicyMapper.selectList(wrapper);
        return list.stream().map(this::toScenarioPolicyRespVO).collect(Collectors.toList());
    }
    @Override
    public ScenarioPolicyRespVO createScenarioPolicy(ScenarioPolicyCreateVO createVO) {
        RuleScenarioPolicyDO entity = new RuleScenarioPolicyDO();
        entity.setScenarioId(createVO.getScenarioId());
        entity.setMatchType(createVO.getMatchType());
        entity.setMatchValue(createVO.getMatchValue());
        entity.setRuleMode(createVO.getRuleMode());
        entity.setExtraCondition(createVO.getExtraCondition());
        entity.setStrategy(createVO.getStrategy());
        entity.setIsActive(createVO.getIsActive());
        scenarioPolicyMapper.insert(entity);
        return toScenarioPolicyRespVO(entity);
    }

    @Override
    public ScenarioPolicyRespVO updateScenarioPolicy(String policyId, ScenarioPolicyUpdateVO updateVO) {
        RuleScenarioPolicyDO entity = scenarioPolicyMapper.selectById(policyId);
        if (entity == null) {
            throw new BusinessException(404, "场景策略不存在");
        }
        if (updateVO.getScenarioId() != null) {
            entity.setScenarioId(updateVO.getScenarioId());
        }
        if (updateVO.getMatchType() != null) {
            entity.setMatchType(updateVO.getMatchType());
        }
        if (updateVO.getMatchValue() != null) {
            entity.setMatchValue(updateVO.getMatchValue());
        }
        if (updateVO.getRuleMode() != null) {
            entity.setRuleMode(updateVO.getRuleMode());
        }
        if (updateVO.getExtraCondition() != null) {
            entity.setExtraCondition(updateVO.getExtraCondition());
        }
        if (updateVO.getStrategy() != null) {
            entity.setStrategy(updateVO.getStrategy());
        }
        if (updateVO.getIsActive() != null) {
            entity.setIsActive(updateVO.getIsActive());
        }
        scenarioPolicyMapper.updateById(entity);
        return toScenarioPolicyRespVO(entity);
    }

    @Override
    public ScenarioPolicyRespVO deleteScenarioPolicy(String policyId) {
        RuleScenarioPolicyDO entity = scenarioPolicyMapper.selectById(policyId);
        if (entity == null) {
            throw new BusinessException(404, "场景策略不存在");
        }
        scenarioPolicyMapper.deleteById(policyId);
        return toScenarioPolicyRespVO(entity);
    }
    // ==================== 全局默认策略 ====================

    @Override
    public List<GlobalDefaultRespVO> listGlobalDefaults(int skip, int limit) {
        Page<RuleGlobalDefaultDO> page = new Page<>(skip / Math.max(limit, 1) + 1, limit);
        Page<RuleGlobalDefaultDO> result = globalDefaultMapper.selectPage(page, null);
        return result.getRecords().stream().map(this::toGlobalDefaultRespVO).collect(Collectors.toList());
    }

    @Override
    public GlobalDefaultRespVO createGlobalDefault(GlobalDefaultCreateVO createVO) {
        RuleGlobalDefaultDO entity = new RuleGlobalDefaultDO();
        entity.setTagCode(createVO.getTagCode());
        entity.setExtraCondition(createVO.getExtraCondition());
        entity.setStrategy(createVO.getStrategy());
        entity.setIsActive(createVO.getIsActive());
        globalDefaultMapper.insert(entity);
        return toGlobalDefaultRespVO(entity);
    }

    @Override
    public GlobalDefaultRespVO updateGlobalDefault(String defaultId, GlobalDefaultUpdateVO updateVO) {
        RuleGlobalDefaultDO entity = globalDefaultMapper.selectById(defaultId);
        if (entity == null) {
            throw new BusinessException(404, "全局默认策略不存在");
        }
        if (updateVO.getTagCode() != null) {
            entity.setTagCode(updateVO.getTagCode());
        }
        if (updateVO.getExtraCondition() != null) {
            entity.setExtraCondition(updateVO.getExtraCondition());
        }
        if (updateVO.getStrategy() != null) {
            entity.setStrategy(updateVO.getStrategy());
        }
        if (updateVO.getIsActive() != null) {
            entity.setIsActive(updateVO.getIsActive());
        }
        globalDefaultMapper.updateById(entity);
        return toGlobalDefaultRespVO(entity);
    }

    @Override
    public GlobalDefaultRespVO deleteGlobalDefault(String defaultId) {
        RuleGlobalDefaultDO entity = globalDefaultMapper.selectById(defaultId);
        if (entity == null) {
            throw new BusinessException(404, "全局默认策略不存在");
        }
        globalDefaultMapper.deleteById(defaultId);
        return toGlobalDefaultRespVO(entity);
    }
    // ==================== 转换方法 ====================

    /**
     * 场景策略 DO 转 RespVO
     *
     * @param entity 实体对象
     * @return 响应 VO
     */
    private ScenarioPolicyRespVO toScenarioPolicyRespVO(RuleScenarioPolicyDO entity) {
        ScenarioPolicyRespVO vo = new ScenarioPolicyRespVO();
        vo.setId(entity.getId());
        vo.setScenarioId(entity.getScenarioId());
        vo.setMatchType(entity.getMatchType());
        vo.setMatchValue(entity.getMatchValue());
        vo.setRuleMode(entity.getRuleMode());
        vo.setExtraCondition(entity.getExtraCondition());
        vo.setStrategy(entity.getStrategy());
        vo.setIsActive(entity.getIsActive());
        return vo;
    }

    /**
     * 全局默认策略 DO 转 RespVO
     *
     * @param entity 实体对象
     * @return 响应 VO
     */
    private GlobalDefaultRespVO toGlobalDefaultRespVO(RuleGlobalDefaultDO entity) {
        GlobalDefaultRespVO vo = new GlobalDefaultRespVO();
        vo.setId(entity.getId());
        vo.setTagCode(entity.getTagCode());
        vo.setExtraCondition(entity.getExtraCondition());
        vo.setStrategy(entity.getStrategy());
        vo.setIsActive(entity.getIsActive());
        return vo;
    }
}

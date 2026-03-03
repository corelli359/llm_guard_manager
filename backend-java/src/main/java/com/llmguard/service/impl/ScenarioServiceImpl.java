/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.llmguard.common.exception.BusinessException;
import com.llmguard.entity.ScenarioDO;
import com.llmguard.mapper.ScenarioMapper;
import com.llmguard.service.IScenarioService;
import com.llmguard.vo.scenario.ScenarioCreateVO;
import com.llmguard.vo.scenario.ScenarioRespVO;
import com.llmguard.vo.scenario.ScenarioUpdateVO;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 功能描述：场景管理服务实现
 *
 * @date 2024/07/13 16:06
 */
@Service
public class ScenarioServiceImpl implements IScenarioService {

    private final ScenarioMapper scenarioMapper;

    public ScenarioServiceImpl(ScenarioMapper scenarioMapper) {
        this.scenarioMapper = scenarioMapper;
    }

    @Override
    public List<ScenarioRespVO> listScenarios(int skip, int limit) {
        Page<ScenarioDO> page = new Page<>(skip / Math.max(limit, 1) + 1, limit);
        Page<ScenarioDO> result = scenarioMapper.selectPage(page, null);
        return result.getRecords().stream().map(this::toRespVO).collect(Collectors.toList());
    }

    @Override
    public ScenarioRespVO createScenario(ScenarioCreateVO createVO) {
        // appId 唯一性校验
        Long count = scenarioMapper.selectCount(
                new LambdaQueryWrapper<ScenarioDO>().eq(ScenarioDO::getAppId, createVO.getAppId())
        );
        if (count > 0) {
            throw new BusinessException("app_id 已存在: " + createVO.getAppId());
        }

        ScenarioDO entity = new ScenarioDO();
        entity.setAppId(createVO.getAppId());
        entity.setAppName(createVO.getAppName());
        entity.setDescription(createVO.getDescription());
        entity.setIsActive(createVO.getIsActive());
        entity.setEnableWhitelist(createVO.getEnableWhitelist());
        entity.setEnableBlacklist(createVO.getEnableBlacklist());
        entity.setEnableCustomPolicy(createVO.getEnableCustomPolicy());
        scenarioMapper.insert(entity);
        return toRespVO(entity);
    }

    @Override
    public ScenarioRespVO getByAppId(String appId) {
        ScenarioDO entity = scenarioMapper.selectOne(
                new LambdaQueryWrapper<ScenarioDO>().eq(ScenarioDO::getAppId, appId)
        );
        if (entity == null) {
            throw new BusinessException(404, "场景不存在, appId: " + appId);
        }
        return toRespVO(entity);
    }

    @Override
    public ScenarioRespVO updateScenario(String scenarioId, ScenarioUpdateVO updateVO) {
        ScenarioDO entity = scenarioMapper.selectById(scenarioId);
        if (entity == null) {
            throw new BusinessException(404, "场景不存在");
        }
        if (updateVO.getAppName() != null) {
            entity.setAppName(updateVO.getAppName());
        }
        if (updateVO.getDescription() != null) {
            entity.setDescription(updateVO.getDescription());
        }
        if (updateVO.getIsActive() != null) {
            entity.setIsActive(updateVO.getIsActive());
        }
        if (updateVO.getEnableWhitelist() != null) {
            entity.setEnableWhitelist(updateVO.getEnableWhitelist());
        }
        if (updateVO.getEnableBlacklist() != null) {
            entity.setEnableBlacklist(updateVO.getEnableBlacklist());
        }
        if (updateVO.getEnableCustomPolicy() != null) {
            entity.setEnableCustomPolicy(updateVO.getEnableCustomPolicy());
        }
        scenarioMapper.updateById(entity);
        return toRespVO(entity);
    }

    @Override
    public ScenarioRespVO deleteScenario(String scenarioId) {
        ScenarioDO entity = scenarioMapper.selectById(scenarioId);
        if (entity == null) {
            throw new BusinessException(404, "场景不存在");
        }
        scenarioMapper.deleteById(scenarioId);
        return toRespVO(entity);
    }

    /**
     * DO 转 RespVO
     *
     * @param entity 实体对象
     * @return 响应 VO
     */
    private ScenarioRespVO toRespVO(ScenarioDO entity) {
        ScenarioRespVO vo = new ScenarioRespVO();
        vo.setId(entity.getId());
        vo.setAppId(entity.getAppId());
        vo.setAppName(entity.getAppName());
        vo.setDescription(entity.getDescription());
        vo.setIsActive(entity.getIsActive());
        vo.setEnableWhitelist(entity.getEnableWhitelist());
        vo.setEnableBlacklist(entity.getEnableBlacklist());
        vo.setEnableCustomPolicy(entity.getEnableCustomPolicy());
        return vo;
    }
}
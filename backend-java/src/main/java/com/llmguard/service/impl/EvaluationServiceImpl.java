/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.llmguard.common.exception.BusinessException;
import com.llmguard.entity.EvalTaskDO;
import com.llmguard.entity.EvalTaskResultDO;
import com.llmguard.entity.EvalTestCaseDO;
import com.llmguard.mapper.EvalTaskMapper;
import com.llmguard.mapper.EvalTaskResultMapper;
import com.llmguard.mapper.EvalTestCaseMapper;
import com.llmguard.service.IEvaluationService;
import com.llmguard.vo.eval.EvalTaskCreateVO;
import com.llmguard.vo.eval.EvalTaskRespVO;
import com.llmguard.vo.eval.EvalTaskResultRespVO;
import com.llmguard.vo.eval.EvalTestCaseCreateVO;
import com.llmguard.vo.eval.EvalTestCaseRespVO;
import com.llmguard.vo.eval.EvalTestCaseUpdateVO;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 功能描述：测评服务实现
 *
 * @date 2024/07/13 16:06
 */
@Service
public class EvaluationServiceImpl implements IEvaluationService {

    private final EvalTestCaseMapper evalTestCaseMapper;
    private final EvalTaskMapper evalTaskMapper;
    private final EvalTaskResultMapper evalTaskResultMapper;

    public EvaluationServiceImpl(EvalTestCaseMapper evalTestCaseMapper,
                                 EvalTaskMapper evalTaskMapper,
                                 EvalTaskResultMapper evalTaskResultMapper) {
        this.evalTestCaseMapper = evalTestCaseMapper;
        this.evalTaskMapper = evalTaskMapper;
        this.evalTaskResultMapper = evalTaskResultMapper;
    }
    @Override
    public List<EvalTestCaseRespVO> listTestCases(int skip, int limit, String tagCode, String expectedResult) {
        LambdaQueryWrapper<EvalTestCaseDO> wrapper = new LambdaQueryWrapper<>();
        if (tagCode != null && !tagCode.isEmpty()) {
            wrapper.like(EvalTestCaseDO::getTagCodes, tagCode);
        }
        if (expectedResult != null && !expectedResult.isEmpty()) {
            wrapper.eq(EvalTestCaseDO::getExpectedResult, expectedResult);
        }
        Page<EvalTestCaseDO> page = new Page<>(skip / Math.max(limit, 1) + 1, limit);
        Page<EvalTestCaseDO> result = evalTestCaseMapper.selectPage(page, wrapper);
        return result.getRecords().stream().map(this::toTestCaseRespVO).collect(Collectors.toList());
    }

    @Override
    public EvalTestCaseRespVO createTestCase(EvalTestCaseCreateVO createVO) {
        EvalTestCaseDO entity = new EvalTestCaseDO();
        entity.setContent(createVO.getContent());
        entity.setTagCodes(createVO.getTagCodes());
        entity.setRiskPoint(createVO.getRiskPoint());
        entity.setExpectedResult(createVO.getExpectedResult());
        entity.setIsActive(true);
        evalTestCaseMapper.insert(entity);
        return toTestCaseRespVO(entity);
    }

    @Override
    public EvalTestCaseRespVO updateTestCase(String id, EvalTestCaseUpdateVO updateVO) {
        EvalTestCaseDO entity = evalTestCaseMapper.selectById(id);
        if (entity == null) {
            throw new BusinessException(404, "测评用例不存在");
        }
        if (updateVO.getContent() != null) {
            entity.setContent(updateVO.getContent());
        }
        if (updateVO.getTagCodes() != null) {
            entity.setTagCodes(updateVO.getTagCodes());
        }
        if (updateVO.getRiskPoint() != null) {
            entity.setRiskPoint(updateVO.getRiskPoint());
        }
        if (updateVO.getExpectedResult() != null) {
            entity.setExpectedResult(updateVO.getExpectedResult());
        }
        if (updateVO.getIsActive() != null) {
            entity.setIsActive(updateVO.getIsActive());
        }
        evalTestCaseMapper.updateById(entity);
        return toTestCaseRespVO(entity);
    }
    @Override
    public EvalTestCaseRespVO deleteTestCase(String id) {
        EvalTestCaseDO entity = evalTestCaseMapper.selectById(id);
        if (entity == null) {
            throw new BusinessException(404, "测评用例不存在");
        }
        evalTestCaseMapper.deleteById(id);
        return toTestCaseRespVO(entity);
    }

    @Override
    public List<EvalTaskRespVO> listTasks(int skip, int limit, String appId) {
        LambdaQueryWrapper<EvalTaskDO> wrapper = new LambdaQueryWrapper<>();
        if (appId != null && !appId.isEmpty()) {
            wrapper.eq(EvalTaskDO::getAppId, appId);
        }
        wrapper.orderByDesc(EvalTaskDO::getCreatedAt);
        Page<EvalTaskDO> page = new Page<>(skip / Math.max(limit, 1) + 1, limit);
        Page<EvalTaskDO> result = evalTaskMapper.selectPage(page, wrapper);
        return result.getRecords().stream().map(this::toTaskRespVO).collect(Collectors.toList());
    }

    @Override
    public EvalTaskRespVO createTask(EvalTaskCreateVO createVO) {
        EvalTaskDO entity = new EvalTaskDO();
        entity.setTaskName(createVO.getTaskName());
        entity.setAppId(createVO.getAppId());
        entity.setStatus("PENDING");
        entity.setTotalCases(0);
        entity.setCompletedCases(0);
        entity.setFailedCases(0);
        entity.setConcurrency(createVO.getConcurrency());
        entity.setFilterTagCodes(createVO.getFilterTagCodes());
        entity.setFilterExpectedResult(createVO.getFilterExpectedResult());
        evalTaskMapper.insert(entity);
        return toTaskRespVO(entity);
    }
    @Override
    public EvalTaskRespVO getTask(String id) {
        EvalTaskDO entity = evalTaskMapper.selectById(id);
        if (entity == null) {
            throw new BusinessException(404, "测评任务不存在");
        }
        return toTaskRespVO(entity);
    }

    @Override
    public List<EvalTaskResultRespVO> getTaskResults(String taskId, int skip, int limit) {
        LambdaQueryWrapper<EvalTaskResultDO> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(EvalTaskResultDO::getTaskId, taskId);
        Page<EvalTaskResultDO> page = new Page<>(skip / Math.max(limit, 1) + 1, limit);
        Page<EvalTaskResultDO> result = evalTaskResultMapper.selectPage(page, wrapper);
        return result.getRecords().stream().map(this::toTaskResultRespVO).collect(Collectors.toList());
    }

    /**
     * EvalTestCaseDO 转 EvalTestCaseRespVO
     *
     * @param entity 实体对象
     * @return 响应 VO
     */
    private EvalTestCaseRespVO toTestCaseRespVO(EvalTestCaseDO entity) {
        EvalTestCaseRespVO vo = new EvalTestCaseRespVO();
        vo.setId(entity.getId());
        vo.setContent(entity.getContent());
        vo.setTagCodes(entity.getTagCodes());
        vo.setRiskPoint(entity.getRiskPoint());
        vo.setExpectedResult(entity.getExpectedResult());
        vo.setIsActive(entity.getIsActive());
        vo.setCreatedBy(entity.getCreatedBy());
        vo.setCreatedAt(entity.getCreatedAt());
        return vo;
    }
    /**
     * EvalTaskDO 转 EvalTaskRespVO
     *
     * @param entity 实体对象
     * @return 响应 VO
     */
    private EvalTaskRespVO toTaskRespVO(EvalTaskDO entity) {
        EvalTaskRespVO vo = new EvalTaskRespVO();
        vo.setId(entity.getId());
        vo.setTaskName(entity.getTaskName());
        vo.setAppId(entity.getAppId());
        vo.setStatus(entity.getStatus());
        vo.setTotalCases(entity.getTotalCases());
        vo.setCompletedCases(entity.getCompletedCases());
        vo.setFailedCases(entity.getFailedCases());
        vo.setConcurrency(entity.getConcurrency());
        vo.setFilterTagCodes(entity.getFilterTagCodes());
        vo.setFilterExpectedResult(entity.getFilterExpectedResult());
        vo.setMetrics(entity.getMetrics());
        vo.setStartedAt(entity.getStartedAt());
        vo.setCompletedAt(entity.getCompletedAt());
        vo.setCreatedBy(entity.getCreatedBy());
        vo.setCreatedAt(entity.getCreatedAt());
        return vo;
    }

    /**
     * EvalTaskResultDO 转 EvalTaskResultRespVO
     *
     * @param entity 实体对象
     * @return 响应 VO
     */
    private EvalTaskResultRespVO toTaskResultRespVO(EvalTaskResultDO entity) {
        EvalTaskResultRespVO vo = new EvalTaskResultRespVO();
        vo.setId(entity.getId());
        vo.setTaskId(entity.getTaskId());
        vo.setTestCaseId(entity.getTestCaseId());
        vo.setContent(entity.getContent());
        vo.setTagCodes(entity.getTagCodes());
        vo.setExpectedResult(entity.getExpectedResult());
        vo.setGuardrailScore(entity.getGuardrailScore());
        vo.setGuardrailResult(entity.getGuardrailResult());
        vo.setGuardrailRaw(entity.getGuardrailRaw());
        vo.setGuardrailLatency(entity.getGuardrailLatency());
        vo.setLlmJudgment(entity.getLlmJudgment());
        vo.setLlmReason(entity.getLlmReason());
        vo.setLlmConfidence(entity.getLlmConfidence());
        vo.setIsConsistent(entity.getIsConsistent());
        vo.setIsCorrect(entity.getIsCorrect());
        vo.setStatus(entity.getStatus());
        vo.setErrorMessage(entity.getErrorMessage());
        vo.setCreatedAt(entity.getCreatedAt());
        return vo;
    }
}

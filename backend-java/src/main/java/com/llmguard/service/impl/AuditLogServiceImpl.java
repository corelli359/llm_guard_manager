/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.llmguard.entity.AuditLogDO;
import com.llmguard.mapper.AuditLogMapper;
import com.llmguard.service.IAuditLogService;
import com.llmguard.vo.audit.AuditLogRespVO;
import org.springframework.stereotype.Service;

import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 功能描述：审计日志服务实现
 *
 * @date 2024/07/13 16:06
 */
@Service
public class AuditLogServiceImpl implements IAuditLogService {

    private final AuditLogMapper auditLogMapper;

    public AuditLogServiceImpl(AuditLogMapper auditLogMapper) {
        this.auditLogMapper = auditLogMapper;
    }

    @Override
    public List<AuditLogRespVO> queryLogs(String userId, String username, String action,
                                          String resourceType, String scenarioId,
                                          Date startDate, Date endDate,
                                          int skip, int limit) {
        LambdaQueryWrapper<AuditLogDO> wrapper = buildQueryWrapper(
                userId, username, action, resourceType, scenarioId, startDate, endDate);
        wrapper.orderByDesc(AuditLogDO::getCreatedAt);

        Page<AuditLogDO> page = new Page<>(skip / Math.max(limit, 1) + 1, limit);
        Page<AuditLogDO> result = auditLogMapper.selectPage(page, wrapper);
        return result.getRecords().stream().map(this::toRespVO).collect(Collectors.toList());
    }

    @Override
    public long countLogs(String userId, String username, String action,
                          String resourceType, String scenarioId,
                          Date startDate, Date endDate) {
        LambdaQueryWrapper<AuditLogDO> wrapper = buildQueryWrapper(
                userId, username, action, resourceType, scenarioId, startDate, endDate);
        return auditLogMapper.selectCount(wrapper);
    }

    /**
     * 构建查询条件
     *
     * @param userId       用户ID
     * @param username     用户名
     * @param action       操作类型
     * @param resourceType 资源类型
     * @param scenarioId   场景ID
     * @param startDate    开始时间
     * @param endDate      结束时间
     * @return 查询条件包装器
     */
    private LambdaQueryWrapper<AuditLogDO> buildQueryWrapper(String userId, String username,
                                                              String action, String resourceType,
                                                              String scenarioId,
                                                              Date startDate, Date endDate) {
        LambdaQueryWrapper<AuditLogDO> wrapper = new LambdaQueryWrapper<>();
        if (userId != null && !userId.isEmpty()) {
            wrapper.eq(AuditLogDO::getUserId, userId);
        }
        if (username != null && !username.isEmpty()) {
            wrapper.eq(AuditLogDO::getUsername, username);
        }
        if (action != null && !action.isEmpty()) {
            wrapper.eq(AuditLogDO::getAction, action);
        }
        if (resourceType != null && !resourceType.isEmpty()) {
            wrapper.eq(AuditLogDO::getResourceType, resourceType);
        }
        if (scenarioId != null && !scenarioId.isEmpty()) {
            wrapper.eq(AuditLogDO::getScenarioId, scenarioId);
        }
        if (startDate != null) {
            wrapper.ge(AuditLogDO::getCreatedAt, startDate);
        }
        if (endDate != null) {
            wrapper.le(AuditLogDO::getCreatedAt, endDate);
        }
        return wrapper;
    }

    /**
     * DO 转 RespVO
     *
     * @param entity 实体对象
     * @return 响应 VO
     */
    private AuditLogRespVO toRespVO(AuditLogDO entity) {
        AuditLogRespVO vo = new AuditLogRespVO();
        vo.setId(entity.getId());
        vo.setUserId(entity.getUserId());
        vo.setUsername(entity.getUsername());
        vo.setAction(entity.getAction());
        vo.setResourceType(entity.getResourceType());
        vo.setResourceId(entity.getResourceId());
        vo.setScenarioId(entity.getScenarioId());
        vo.setDetails(entity.getDetails());
        vo.setIpAddress(entity.getIpAddress());
        vo.setUserAgent(entity.getUserAgent());
        vo.setCreatedAt(entity.getCreatedAt());
        return vo;
    }
}

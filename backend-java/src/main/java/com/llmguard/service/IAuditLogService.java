/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service;

import com.llmguard.vo.audit.AuditLogRespVO;

import java.util.Date;
import java.util.List;

/**
 * 功能描述：审计日志服务接口
 *
 * @date 2024/07/13 16:06
 */
public interface IAuditLogService {

    /**
     * 查询审计日志列表
     *
     * @param userId       用户ID
     * @param username     用户名
     * @param action       操作类型
     * @param resourceType 资源类型
     * @param scenarioId   场景ID
     * @param startDate    开始时间
     * @param endDate      结束时间
     * @param skip         跳过条数
     * @param limit        限制条数
     * @return 审计日志列表
     */
    List<AuditLogRespVO> queryLogs(String userId, String username, String action,
                                   String resourceType, String scenarioId,
                                   Date startDate, Date endDate,
                                   int skip, int limit);

    /**
     * 统计审计日志数量
     *
     * @param userId       用户ID
     * @param username     用户名
     * @param action       操作类型
     * @param resourceType 资源类型
     * @param scenarioId   场景ID
     * @param startDate    开始时间
     * @param endDate      结束时间
     * @return 日志数量
     */
    long countLogs(String userId, String username, String action,
                   String resourceType, String scenarioId,
                   Date startDate, Date endDate);
}

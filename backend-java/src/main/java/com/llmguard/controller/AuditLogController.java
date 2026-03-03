/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.controller;

import com.llmguard.common.result.R;
import com.llmguard.service.IAuditLogService;
import com.llmguard.vo.audit.AuditLogRespVO;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 功能描述：审计日志控制器
 *
 * @date 2024/07/13 16:06
 */
@RestController
@RequestMapping("/api/v1/audit-logs")
public class AuditLogController {

    private final IAuditLogService auditLogService;

    public AuditLogController(IAuditLogService auditLogService) {
        this.auditLogService = auditLogService;
    }

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
    @GetMapping
    public R<List<AuditLogRespVO>> list(
            @RequestParam(required = false) String userId,
            @RequestParam(required = false) String username,
            @RequestParam(required = false) String action,
            @RequestParam(required = false) String resourceType,
            @RequestParam(required = false) String scenarioId,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") Date startDate,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") Date endDate,
            @RequestParam(defaultValue = "0") int skip,
            @RequestParam(defaultValue = "100") int limit) {
        List<AuditLogRespVO> logs = auditLogService.queryLogs(
                userId, username, action, resourceType, scenarioId,
                startDate, endDate, skip, limit);
        return R.ok(logs);
    }

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
    @GetMapping("/count")
    public R<Map<String, Object>> count(
            @RequestParam(required = false) String userId,
            @RequestParam(required = false) String username,
            @RequestParam(required = false) String action,
            @RequestParam(required = false) String resourceType,
            @RequestParam(required = false) String scenarioId,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") Date startDate,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") Date endDate) {
        long count = auditLogService.countLogs(
                userId, username, action, resourceType, scenarioId,
                startDate, endDate);
        Map<String, Object> result = new HashMap<>();
        result.put("count", count);
        return R.ok(result);
    }
}

/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.llmguard.entity.AuditLogDO;
import org.apache.ibatis.annotations.Mapper;

/**
 * 功能描述：审计日志 Mapper接口
 *
 * @date 2024/07/13 16:06
 */
@Mapper
public interface AuditLogMapper extends BaseMapper<AuditLogDO> {
}

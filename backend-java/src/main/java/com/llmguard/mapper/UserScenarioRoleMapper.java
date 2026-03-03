/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.llmguard.entity.UserScenarioRoleDO;
import org.apache.ibatis.annotations.Mapper;

/**
 * 功能描述：用户-场景-角色关联 Mapper接口
 *
 * @date 2024/07/13 16:06
 */
@Mapper
public interface UserScenarioRoleMapper extends BaseMapper<UserScenarioRoleDO> {
}

/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.llmguard.entity.GlobalKeywordDO;
import org.apache.ibatis.annotations.Mapper;

/**
 * 功能描述：全局敏感词 Mapper接口
 *
 * @date 2024/07/13 16:06
 */
@Mapper
public interface GlobalKeywordMapper extends BaseMapper<GlobalKeywordDO> {
}

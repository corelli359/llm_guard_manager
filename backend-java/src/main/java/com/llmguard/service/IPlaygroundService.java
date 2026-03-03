/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service;

import com.llmguard.vo.playground.PlaygroundHistoryRespVO;
import com.llmguard.vo.playground.PlaygroundInputVO;

import java.util.List;
import java.util.Map;

/**
 * 功能描述：Playground 服务接口
 *
 * @date 2024/07/13 16:06
 */
public interface IPlaygroundService {

    /**
     * 执行输入内容检测
     *
     * @param inputVO 输入检测请求参数
     * @return 检测结果
     */
    Map<String, Object> runInputCheck(PlaygroundInputVO inputVO);

    /**
     * 查询 Playground 历史记录
     *
     * @param page           页码
     * @param size           每页大小
     * @param playgroundType 类型（可选）
     * @param appId          应用ID（可选）
     * @return 历史记录列表
     */
    List<PlaygroundHistoryRespVO> getHistory(int page, int size,
                                             String playgroundType, String appId);
}

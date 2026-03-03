/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.service;

import com.llmguard.vo.eval.EvalTaskCreateVO;
import com.llmguard.vo.eval.EvalTaskRespVO;
import com.llmguard.vo.eval.EvalTaskResultRespVO;
import com.llmguard.vo.eval.EvalTestCaseCreateVO;
import com.llmguard.vo.eval.EvalTestCaseRespVO;
import com.llmguard.vo.eval.EvalTestCaseUpdateVO;

import java.util.List;

/**
 * 功能描述：测评服务接口
 *
 * @date 2024/07/13 16:06
 */
public interface IEvaluationService {

    /**
     * 获取测评用例列表
     *
     * @param skip           跳过条数
     * @param limit          限制条数
     * @param tagCode        标签编码过滤
     * @param expectedResult 预期结果过滤
     * @return 测评用例列表
     */
    List<EvalTestCaseRespVO> listTestCases(int skip, int limit, String tagCode, String expectedResult);

    /**
     * 创建测评用例
     *
     * @param createVO 创建参数
     * @return 创建后的测评用例
     */
    EvalTestCaseRespVO createTestCase(EvalTestCaseCreateVO createVO);

    /**
     * 更新测评用例
     *
     * @param id       用例ID
     * @param updateVO 更新参数
     * @return 更新后的测评用例
     */
    EvalTestCaseRespVO updateTestCase(String id, EvalTestCaseUpdateVO updateVO);

    /**
     * 删除测评用例
     *
     * @param id 用例ID
     * @return 被删除的测评用例
     */
    EvalTestCaseRespVO deleteTestCase(String id);

    /**
     * 获取测评任务列表
     *
     * @param skip  跳过条数
     * @param limit 限制条数
     * @param appId 应用ID过滤
     * @return 测评任务列表
     */
    List<EvalTaskRespVO> listTasks(int skip, int limit, String appId);

    /**
     * 创建测评任务
     *
     * @param createVO 创建参数
     * @return 创建后的测评任务
     */
    EvalTaskRespVO createTask(EvalTaskCreateVO createVO);

    /**
     * 获取测评任务详情
     *
     * @param id 任务ID
     * @return 测评任务详情
     */
    EvalTaskRespVO getTask(String id);

    /**
     * 获取测评任务结果列表
     *
     * @param taskId 任务ID
     * @param skip   跳过条数
     * @param limit  限制条数
     * @return 测评任务结果列表
     */
    List<EvalTaskResultRespVO> getTaskResults(String taskId, int skip, int limit);
}

/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.controller;

import com.llmguard.common.result.R;
import com.llmguard.service.IEvaluationService;
import com.llmguard.vo.eval.EvalTaskCreateVO;
import com.llmguard.vo.eval.EvalTaskRespVO;
import com.llmguard.vo.eval.EvalTaskResultRespVO;
import com.llmguard.vo.eval.EvalTestCaseCreateVO;
import com.llmguard.vo.eval.EvalTestCaseRespVO;
import com.llmguard.vo.eval.EvalTestCaseUpdateVO;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * 功能描述：测评模块控制器
 *
 * @date 2024/07/13 16:06
 */
@RestController
@RequestMapping("/api/v1/evaluation")
public class EvaluationController {

    private final IEvaluationService evaluationService;

    public EvaluationController(IEvaluationService evaluationService) {
        this.evaluationService = evaluationService;
    }

    /**
     * 获取测评用例列表
     *
     * @param skip           跳过条数
     * @param limit          限制条数
     * @param tagCode        标签编码过滤
     * @param expectedResult 预期结果过滤
     * @return 测评用例列表
     */
    @GetMapping("/test-cases")
    public R<List<EvalTestCaseRespVO>> listTestCases(
            @RequestParam(defaultValue = "0") int skip,
            @RequestParam(defaultValue = "100") int limit,
            @RequestParam(required = false) String tagCode,
            @RequestParam(required = false) String expectedResult) {
        return R.ok(evaluationService.listTestCases(skip, limit, tagCode, expectedResult));
    }

    /**
     * 创建测评用例
     *
     * @param createVO 创建参数
     * @return 创建后的测评用例
     */
    @PostMapping("/test-cases")
    public R<EvalTestCaseRespVO> createTestCase(@Valid @RequestBody EvalTestCaseCreateVO createVO) {
        return R.ok(evaluationService.createTestCase(createVO));
    }

    /**
     * 更新测评用例
     *
     * @param id       用例ID
     * @param updateVO 更新参数
     * @return 更新后的测评用例
     */
    @PutMapping("/test-cases/{id}")
    public R<EvalTestCaseRespVO> updateTestCase(@PathVariable String id,
                                                 @RequestBody EvalTestCaseUpdateVO updateVO) {
        return R.ok(evaluationService.updateTestCase(id, updateVO));
    }

    /**
     * 删除测评用例
     *
     * @param id 用例ID
     * @return 被删除的测评用例
     */
    @DeleteMapping("/test-cases/{id}")
    public R<EvalTestCaseRespVO> deleteTestCase(@PathVariable String id) {
        return R.ok(evaluationService.deleteTestCase(id));
    }
    /**
     * 获取测评任务列表
     *
     * @param skip  跳过条数
     * @param limit 限制条数
     * @param appId 应用ID过滤
     * @return 测评任务列表
     */
    @GetMapping("/tasks")
    public R<List<EvalTaskRespVO>> listTasks(
            @RequestParam(defaultValue = "0") int skip,
            @RequestParam(defaultValue = "100") int limit,
            @RequestParam(required = false) String appId) {
        return R.ok(evaluationService.listTasks(skip, limit, appId));
    }

    /**
     * 创建测评任务
     *
     * @param createVO 创建参数
     * @return 创建后的测评任务
     */
    @PostMapping("/tasks")
    public R<EvalTaskRespVO> createTask(@Valid @RequestBody EvalTaskCreateVO createVO) {
        return R.ok(evaluationService.createTask(createVO));
    }

    /**
     * 获取测评任务详情
     *
     * @param taskId 任务ID
     * @return 测评任务详情
     */
    @GetMapping("/tasks/{taskId}")
    public R<EvalTaskRespVO> getTask(@PathVariable String taskId) {
        return R.ok(evaluationService.getTask(taskId));
    }

    /**
     * 获取测评任务结果列表
     *
     * @param taskId 任务ID
     * @param skip   跳过条数
     * @param limit  限制条数
     * @return 测评任务结果列表
     */
    @GetMapping("/tasks/{taskId}/results")
    public R<List<EvalTaskResultRespVO>> getTaskResults(
            @PathVariable String taskId,
            @RequestParam(defaultValue = "0") int skip,
            @RequestParam(defaultValue = "100") int limit) {
        return R.ok(evaluationService.getTaskResults(taskId, skip, limit));
    }
}

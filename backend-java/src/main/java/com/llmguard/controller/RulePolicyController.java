/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.controller;

import com.llmguard.common.result.R;
import com.llmguard.service.IRulePolicyService;
import com.llmguard.vo.policy.GlobalDefaultCreateVO;
import com.llmguard.vo.policy.GlobalDefaultRespVO;
import com.llmguard.vo.policy.GlobalDefaultUpdateVO;
import com.llmguard.vo.policy.ScenarioPolicyCreateVO;
import com.llmguard.vo.policy.ScenarioPolicyRespVO;
import com.llmguard.vo.policy.ScenarioPolicyUpdateVO;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * 功能描述：规则策略控制器，包含场景策略和全局默认策略接口
 *
 * @date 2024/07/13 16:06
 */
@RestController
@RequestMapping("/api/v1/policies")
public class RulePolicyController {

    private final IRulePolicyService rulePolicyService;

    public RulePolicyController(IRulePolicyService rulePolicyService) {
        this.rulePolicyService = rulePolicyService;
    }

    // ==================== 场景策略 ====================

    /**
     * 根据场景ID查询策略列表
     *
     * @param scenarioId 场景ID
     * @return 场景策略列表
     */
    @GetMapping("/scenario/{scenarioId}")
    public R<List<ScenarioPolicyRespVO>> listByScenario(@PathVariable String scenarioId) {
        return R.ok(rulePolicyService.listByScenarioId(scenarioId));
    }

    /**
     * 创建场景策略
     *
     * @param createVO 创建参数
     * @return 创建后的场景策略
     */
    @PostMapping("/scenario/")
    public R<ScenarioPolicyRespVO> createScenarioPolicy(@Valid @RequestBody ScenarioPolicyCreateVO createVO) {
        return R.ok(rulePolicyService.createScenarioPolicy(createVO));
    }

    /**
     * 更新场景策略
     *
     * @param policyId 策略ID
     * @param updateVO 更新参数
     * @return 更新后的场景策略
     */
    @PutMapping("/scenario/{policyId}")
    public R<ScenarioPolicyRespVO> updateScenarioPolicy(@PathVariable String policyId,
                                                         @RequestBody ScenarioPolicyUpdateVO updateVO) {
        return R.ok(rulePolicyService.updateScenarioPolicy(policyId, updateVO));
    }

    /**
     * 删除场景策略
     *
     * @param policyId 策略ID
     * @return 被删除的场景策略
     */
    @DeleteMapping("/scenario/{policyId}")
    public R<ScenarioPolicyRespVO> deleteScenarioPolicy(@PathVariable String policyId) {
        return R.ok(rulePolicyService.deleteScenarioPolicy(policyId));
    }

    // ==================== 全局默认策略 ====================

    /**
     * 查询全局默认策略列表
     *
     * @param skip  跳过条数
     * @param limit 限制条数
     * @return 全局默认策略列表
     */
    @GetMapping("/defaults/")
    public R<List<GlobalDefaultRespVO>> listDefaults(@RequestParam(defaultValue = "0") int skip,
                                                      @RequestParam(defaultValue = "100") int limit) {
        return R.ok(rulePolicyService.listGlobalDefaults(skip, limit));
    }

    /**
     * 创建全局默认策略
     *
     * @param createVO 创建参数
     * @return 创建后的全局默认策略
     */
    @PostMapping("/defaults/")
    public R<GlobalDefaultRespVO> createDefault(@Valid @RequestBody GlobalDefaultCreateVO createVO) {
        return R.ok(rulePolicyService.createGlobalDefault(createVO));
    }

    /**
     * 更新全局默认策略
     *
     * @param defaultId 默认策略ID
     * @param updateVO  更新参数
     * @return 更新后的全局默认策略
     */
    @PutMapping("/defaults/{defaultId}")
    public R<GlobalDefaultRespVO> updateDefault(@PathVariable String defaultId,
                                                 @RequestBody GlobalDefaultUpdateVO updateVO) {
        return R.ok(rulePolicyService.updateGlobalDefault(defaultId, updateVO));
    }

    /**
     * 删除全局默认策略
     *
     * @param defaultId 默认策略ID
     * @return 被删除的全局默认策略
     */
    @DeleteMapping("/defaults/{defaultId}")
    public R<GlobalDefaultRespVO> deleteDefault(@PathVariable String defaultId) {
        return R.ok(rulePolicyService.deleteGlobalDefault(defaultId));
    }
}

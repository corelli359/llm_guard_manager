/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.controller;

import com.llmguard.common.result.R;
import com.llmguard.service.IScenarioService;
import com.llmguard.vo.scenario.ScenarioCreateVO;
import com.llmguard.vo.scenario.ScenarioRespVO;
import com.llmguard.vo.scenario.ScenarioUpdateVO;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * 功能描述：场景/应用管理控制器
 *
 * @date 2024/07/13 16:06
 */
@RestController
@RequestMapping("/api/v1/apps")
public class ScenarioController {

    private final IScenarioService scenarioService;

    public ScenarioController(IScenarioService scenarioService) {
        this.scenarioService = scenarioService;
    }

    /**
     * 获取场景列表
     *
     * @param skip  跳过条数
     * @param limit 限制条数
     * @return 场景列表
     */
    @GetMapping
    public R<List<ScenarioRespVO>> list(@RequestParam(defaultValue = "0") int skip,
                                        @RequestParam(defaultValue = "100") int limit) {
        return R.ok(scenarioService.listScenarios(skip, limit));
    }

    /**
     * 创建场景
     *
     * @param createVO 创建参数
     * @return 创建后的场景
     */
    @PostMapping
    public R<ScenarioRespVO> create(@Valid @RequestBody ScenarioCreateVO createVO) {
        return R.ok(scenarioService.createScenario(createVO));
    }

    /**
     * 根据 appId 获取场景
     *
     * @param appId 应用ID
     * @return 场景信息
     */
    @GetMapping("/{appId}")
    public R<ScenarioRespVO> getByAppId(@PathVariable String appId) {
        return R.ok(scenarioService.getByAppId(appId));
    }

    /**
     * 更新场景
     *
     * @param scenarioId 场景主键ID
     * @param updateVO   更新参数
     * @return 更新后的场景
     */
    @PutMapping("/{scenarioId}")
    public R<ScenarioRespVO> update(@PathVariable String scenarioId,
                                    @RequestBody ScenarioUpdateVO updateVO) {
        return R.ok(scenarioService.updateScenario(scenarioId, updateVO));
    }

    /**
     * 删除场景
     *
     * @param scenarioId 场景主键ID
     * @return 被删除的场景
     */
    @DeleteMapping("/{scenarioId}")
    public R<ScenarioRespVO> delete(@PathVariable String scenarioId) {
        return R.ok(scenarioService.deleteScenario(scenarioId));
    }
}
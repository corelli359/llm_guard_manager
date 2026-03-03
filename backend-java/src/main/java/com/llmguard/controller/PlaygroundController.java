/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.controller;

import com.llmguard.common.result.R;
import com.llmguard.service.IPlaygroundService;
import com.llmguard.vo.playground.PlaygroundHistoryRespVO;
import com.llmguard.vo.playground.PlaygroundInputVO;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import javax.validation.Valid;
import java.util.List;
import java.util.Map;

/**
 * 功能描述：Playground 控制器
 *
 * @date 2024/07/13 16:06
 */
@RestController
@RequestMapping("/api/v1/playground")
public class PlaygroundController {

    private final IPlaygroundService playgroundService;

    public PlaygroundController(IPlaygroundService playgroundService) {
        this.playgroundService = playgroundService;
    }

    /**
     * 执行输入内容检测
     *
     * @param inputVO 输入检测请求参数
     * @return 检测结果
     */
    @PostMapping("/input")
    public R<Map<String, Object>> runInputCheck(@Valid @RequestBody PlaygroundInputVO inputVO) {
        return R.ok(playgroundService.runInputCheck(inputVO));
    }

    /**
     * 查询 Playground 历史记录
     *
     * @param page           页码
     * @param size           每页大小
     * @param playgroundType 类型
     * @param appId          应用ID
     * @return 历史记录列表
     */
    @GetMapping("/history")
    public R<List<PlaygroundHistoryRespVO>> history(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String playgroundType,
            @RequestParam(required = false) String appId) {
        return R.ok(playgroundService.getHistory(page, size, playgroundType, appId));
    }
}

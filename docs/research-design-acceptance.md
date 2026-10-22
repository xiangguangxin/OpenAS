# 调研与设计专用路线验收

2026-10-22，在隔离临时工作区使用 Codex CLI 0.162.0-alpha.17.2 执行 [live 示例任务](../plugins/openas/workflows/examples/research-design-task.json)，输入为 [本地交接工具设计简报](../plugins/openas/workflows/examples/research-design-fixture/brief.md)。运行命令与恢复方式见 [工作流指南](../plugins/openas/workflows/README.md)。

## 实际执行

八次独立真实客户端调用完成六个文档阶段、设计评审和 verifier。市场阶段记录四个原生已完成 web_search 事件；六份输出均非空，仅允许的六个 Markdown 文件发生变化，brief.md 保持不变。基线检查因文档未生成而退出 1，最终检查退出 0；评审 approve/revision_from=none，verifier pass，最终 done=true/status=verified，verification_subject=design-artifacts。

可移植收据保留阶段、评审、验证、文档指纹及退出码，见 [验收 JSON](acceptance/2026-10-22-research-design.json)。完整提示、日志和生成文档留在临时运行目录，没有作为项目知识或用户事实加入仓库。

## 回归与覆盖边界

73 项工作流测试通过，包括 18 项新路线专项测试；仓库级 24 项测试中 21 项通过、3 项因 Node/原生 Claude 环境条件跳过。专项测试覆盖结构化评审回退、所有下游重跑、修订途中中断恢复、预算跨恢复保留、宿主/验证失败、阶段文件限制、缺失文档、原生搜索证据、任务参数校验及图节点接入。

真实试跑结束后，修正了输出路径为 `.` 的输入拒绝边界；修正已包含在完整回归中。真实调用使用默认正常路径，修订回路与恢复故障由模拟客户端测试覆盖，未声称它们也完成了真实故障注入。provided 模式完成自动化回归，未另做真实客户端全链路试跑。

示例宿主检查只验证文档存在且非空，内容一致性由模型评审和 verifier 核对，不能等同于全部人工审查。调研仅确认一个代表性竞品，另一个来源获取失败，文档明确保留调查范围与新鲜度限制；原生搜索事件不证明每条外部事实正确。没有用户访谈、产品实现或性能实测，也没有新增 Claude 原生客户端验收。

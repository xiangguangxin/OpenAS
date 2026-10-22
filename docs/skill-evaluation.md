# 技能行为评测

格式检查证明资源可解析；行为评测检查真实客户端面对任务时如何选择技能和处理边界。

`scripts/evaluate_skills.py` 使用现有 Codex 登录和模型设置，在独立临时工作区运行六种任务：

| 场景 | 宿主检查 |
| --- | --- |
| 普通项目评审 | 选择 requesting-code-review，直接给出发现，不提确认问题，文件不变 |
| 明确要求设计采访 | 选择 grilling，提出问题，文件不变 |
| 指定范围修复 | 选择 bug-fix，只修改指定实现，保留测试，并通过宿主重新运行的测试 |
| 选择最小工作流 | 选择 workflow-routing，不修改文件、不增加确认问题 |
| 当前任务交接 | 选择 context-handoff，保持只读并区分现场与长期记忆 |
| 逐项验收 | 选择 acceptance-tracking，保持只读、说明实际检查证据 |

```bash
python3 scripts/evaluate_skills.py --output /tmp/openas-skill-evaluation
# 只评测一个场景；输出目录仍须为新目录
python3 scripts/evaluate_skills.py --case ordinary-review --output /tmp/openas-review-evaluation
```

每次运行消耗真实客户端额度，每个场景默认超时 180 秒，不自动重试、不更换模型或安装依赖。默认 CI 只测试评测器的失败检测，不调用模型。输出目录必须事先不存在。

报告包含客户端结构化答复、宿主检查结果和文件变更。只有相关门禁全部满足才返回 0；最终仍需人工核对评审问题的语义与证据。`selected_skill` 和文字答复属于客户端声明，文件范围与修复测试由宿主独立核对；有限场景通过不等于所有技能或所有模型均已验证。

真实 Claude 插件加载和热加载属于另一种验收，见 [原生集成测试](hot-reload-testing.md)，不能由本评测替代。

---
name: verification-before-completion
description: "在交付前按改动类型核对验收并提供真实验证证据，明确未运行项，不将文档任务机械升级为完整构建。 / Verify acceptance with real evidence appropriate to the change, distinguishing unexecuted, static, mock, historical, and runtime checks."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 完成前验证

先确认本次验收、修改对象和现有证据。具体报告格式及分类见 [团队协作契约](../../references/team-contract.md)。

- 文档：核对源码、链接、代码围栏和 diff 格式，图表按实际能力预览。
- 行为代码：运行能覆盖变化的测试及必要构建；修复应有原失败场景或可复现证据。
- 应用/服务/数据任务：除退出码，还检查实际输出、状态变化与副作用；涉及协议或时序时再核对对应轨迹。

记录命令、工作目录、退出码、关键输出与覆盖范围。未执行写未执行，缺工具写具体影响；必需验收无法证明不能说通过。mock 结果、历史结果、静态检查和真实运行分别标注。

复用前按共享规则核对实际对象版本和相关依赖；对变化后的对象重新取得受影响范围的证据。逐项结论与证据对应，不用已通过子集证明整体完成。

失败反馈给修改者修复；检查通过后，无新变化或风险不重复无关完整回归。不以角色自称、脚本完成或用户没反馈替代证据。

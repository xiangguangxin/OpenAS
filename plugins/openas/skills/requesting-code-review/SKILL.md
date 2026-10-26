---
name: requesting-code-review
description: "对实际代码、diff 或项目现状进行证据驱动的评审，检查需求、边界、兼容和验证缺口；普通评审直接调查并给出发现。 / Review actual code, diffs, or repository state for evidenced defects in requirements, boundaries, compatibility, and validation; investigate directly rather than interviewing."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

# 代码与项目评审

先确认评审对象与验收，读取实际 diff、相关调用方、测试和项目约束。不只依赖开发者总结，也不把普通评审转成设计采访。可从仓库确认的事实自行查证。

按改动风险检查输入输出、错误路径、状态与资源生命周期、兼容性和测试覆盖。运行最小可区分实验时使用临时目录，不为复现修改产品实现或用户配置；仅静态推断的问题注明未复现。

每条发现包含严重度、文件位置、触发条件、实际与预期、证据、影响和修复建议。P0/P1 为核心正确性或验收阻断，P2 按影响判断，P3 为可选建议；不将措辞或风格偏好升级为缺陷，也不为凑数量制造问题。

区分已确认缺陷、已公开的能力限制与后续增强项。无实质问题可以直接通过，附已检查范围和未覆盖项。复查沿用问题 ID，检查修复与新增影响；仅在用户已授权修复时修改实现。

评审远程 PR 与 CI 时可按 [GitHub MCP 指引](../../integrations/github/README.md) 读取实际对象与提交；缺少工具时沿用本地 diff 或宿主已有能力，标出远程证据缺口。

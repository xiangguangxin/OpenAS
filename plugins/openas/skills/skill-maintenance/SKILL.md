---
name: skill-maintenance
description: "根据可复现的漏触发、误触发或执行失败改进已有 Agent Skill，用新旧版本对照、相似反例和独立验收用例验证修订。 / Improve an existing Agent Skill from reproducible routing or execution failures, comparing versions against realistic and held-out cases."
---

中文 | [English](SKILL.en.md)

遵循[语言约定](../../references/language.md)和[结论与证据共享规则](../../references/evidence-policy.md)。

# 维护已有技能

适用于修订已维护的技能。先明确技能、目标宿主、待修行为和可观察验收条件。用脱敏的会话片段、工具轨迹或实际产物定位问题，记录来源和位置。区分宿主未发现技能、选错入口、加载后步骤有误及外部工具失败。只能从真实证据确认已发生的问题；合成用例标为合成。

1. 固定旧版提交和完整技能包。将问题转为可重跑的正例，加入一个相似但应走其他入口的反例。按风险覆盖用户催促跳过验证、工具缺失或输入不全。提前冻结独立验收样例，修订过程只用复现和开发样例。
2. 先运行旧版，保留实际输出与失败证据。用最小改动修复对应层级。改触发条件时优先修改描述，改执行步骤时同步相关参考资料及双语说明。记录未复现的反馈和证据限制。
3. 用相同的宿主、模型、输入、授权、预算和宿主断言，在新工作区比较旧版和候选版。分别核对入口选择、产物或行为、约束和证据；退出码与自报选择只能支持相应的检查。能取得原生耗时和 token 数据时保留样本及波动。
4. 用冻结样例复验最终候选。任何必需用例退步、关键证据缺失或客户端未运行时，记录对应缺口。若根据验收样例继续调优，换一组未参与调整的样例作最终验收。记录旧版、候选版、逐项差异和回退位置；按项目的评审流程提交修订。

维护 OpenAS 时按需用仓库根目录的 `scripts/evaluate_skills.py --baseline-plugin` 和技能行为评测指南。复盘并生成使用方项目候选技能用 [project-memory](../project-memory/SKILL.md)。[方法来源](FUSION_SOURCES.json)记录了上游版本与落点。

---
name: test-driven-development
description: "测试驱动开发：先写失败测试(RED) → 最小实现(GREEN) → 重构(REFACTOR)，用测试将已确认需求具体化并约束实现。当需要以 TDD 方式开发时使用。 / Use RED → GREEN → REFACTOR to express confirmed behavior as meaningful tests, implement minimally, and verify regression protection."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

# Test Driven Development

## 测试驱动开发

核心循环：

RED

测试失败

GREEN

最小实现

REFACTOR

优化代码

测试将已确认需求具体化，用来约束实现和暴露回归。断言依据需求、接口契约或可信参考，不以当前实现输出自行定义正确性；关键需求有歧义时先澄清或回交，不靠先写测试替用户作决定。

## 选择有意义的测试

新增或修复可执行行为时，先构造能暴露错误的正常/边界场景，确认失败原因来自目标行为，再最小实现并复查相关回归。测试输入输出、状态和错误路径，而不是只断言实现中的字符串存在。

纯文字、格式或低影响可逆调整采用相应检查，不强制制造单元测试。测试环境不可用时说明阻碍，不谎称已完成 RED/GREEN。已有测试通过后，只有新修改或风险才需要扩大验证。

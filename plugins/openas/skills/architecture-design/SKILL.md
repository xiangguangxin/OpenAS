---
name: architecture-design
description: "依据需求和技术决策设计系统边界、模块、接口、数据与部署及失败处理，产出架构说明和需求映射；用于新系统或跨模块设计，不替代选型与实现。 / Design system boundaries, modules, interfaces, data, deployment, and failure behavior from requirements and technical decisions; produce architecture and requirement mappings."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 架构设计

读取需求 ID、技术决定、已有代码和项目约定；新项目允许从需求及约束开始。先明确当前架构、拟议架构和本次变更范围。规模小则采用简单结构，不默认微服务、分布式部署或新基础设施。

## 定义可共同实现的边界

记录会导致独立实现冲突的决定：系统与外部边界、模块职责、依赖方向、数据所有权、状态更新方式、接口及错误语义。接口按需要定义输入输出、单位、幂等、超时、重试及兼容要求。

描述核心流程和关键失败流程，包括数据如何流动、状态如何改变及谁负责恢复。按风险说明存储一致性、并发、权限、资源边界、可观察性和部署拓扑；技术栈列表不是架构。

以具体质量场景驱动设计，例如什么负载/故障下要达到什么结果，并关联机制、验证方式与未决风险。没有容量依据或实验时不声称架构已经达到指标。

## 实施深度

按 [设计粒度与实施就绪](../../references/implementation-readiness.md) 随风险补齐契约、状态、不变量与失败恢复，不按文件数量扩充设计。关键验收需对应现有或拟议模块和验证方法；明确已确定的边界、交给 developer 的局部选择及阻断未知项。

## 图与决策

使用 [technical-diagrams](../technical-diagrams/SKILL.md) 按需要表达系统上下文、组件、时序、数据或部署；图与契约使用一致名称，逻辑关系与物理部署分开。小项目只画能澄清问题的图。

保留稳定架构决策 ID、备选、取舍和适用条件，引用 [technology-selection](../technology-selection/SKILL.md) 的决定，避免重复维护。迁移设计说明兼容、切换、回退及不可逆数据风险；新限制回交选型而非隐瞒。

交付架构说明、必要图、接口/数据契约、需求到设计及验证的映射、风险与待定项。交给 [design-review](../design-review/SKILL.md) 核对，最后由 [project-documentation](../project-documentation/SKILL.md) 整理成设计文档；设计任务不自动继续实现。

已有系统的分阶段改造、兼容窗口与退役安排使用 [architecture-evolution](../architecture-evolution/SKILL.md)；实现后的架构偏差核对使用 [architecture-conformance](../architecture-conformance/SKILL.md)，不与实施前设计评审混同。

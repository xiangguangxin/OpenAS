---
name: code-simplification
description: "用生产者、消费者和兼容证据寻找或实施代码、接口、配置与状态的净简化，减少重复维护和无效抽象；只调查时不修改，不将代码库解释或一般缺陷评审变成删除任务。 / Find or implement evidence-backed simplifications of code, APIs, configuration, and state; preserve compatibility and keep surveys read-only."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

# 代码与系统简化

目标是减少长期维护责任：需要同步的状态、公开接口、分支、配置入口、依赖或生命周期机制，而不是追求删行数。先读 [项目适配约定](../../references/project-context.md)、当前实现、有效设计与本次范围，区分调查建议、方案评估和已授权实施。调查不自动删除文件；明确的实施任务也不需要为每项局部可逆选择重新请示。

## 找到实际可以移除的负担

从重复状态、无人消费的字段、不可达分支、被覆盖的配置透传、推测性扩展和重复基础设施寻找候选。先问是否需要该区别或机制，再问它应该放在哪里；把复杂性搬到公共层或增加同步检查，不等于移除维护负担。少量证据充分的候选优于全仓删除清单。

用 `rg` 搜索符号、字段读写、构造入口、事件名、配置键和导出，再读取命中上下文。沿“生产者 → 转换/覆盖 → 注册或装载 → 消费者 → 可观察效果”追踪。覆盖清单驱动加载、反射、生成代码、CLI / 配置优先级、已发布入口和项目声明的外部扩展契约；测试或声明存在不等于生产消费者存在，仓库内零调用也不等于公开能力无用。

比较缓存或副本与权威数据源时，先确认消费者需要哪个时刻的值：即时读取、历史快照和持久审计可能各有用途。不能因为 UI 不显示某个事件就删除它，也不能用当前值替代原本要求冻结的历史证据。

## 形成可评估的候选

对每项有价值的候选说明源码位置、当前归属、实际调用或数据路径、移除内容、剩余机制、维护收益、兼容影响及最强保留理由。区分不可达行为删除、缩小支持范围的行为变更和证据不足。没有可靠候选时直接报告，不强凑数量。

依赖替换要计算新依赖、适配代码、平台要求、升级和验证成本；只覆盖通用协议却仍需重写同样状态机，不算净简化。已有接口只有一个内置实现也可能承担真实外部扩展契约，不能仅凭实现数量删除。

异步或持久状态改造需明确资源归属、取消、首次终态、清理完成、部分写入和恢复语义。合并状态前证明它们表达同一事实；删除验证前追踪信任边界和下一位拥有者。需评估迁移或兼容分阶段时用 [architecture-evolution](../architecture-evolution/SKILL.md)，需要展开影响时用 [change-impact-analysis](../change-impact-analysis/SKILL.md)。复杂候选按需读 [证据与取舍示例](references/evidence.md)。

## 实施与验证

在已有授权范围内实施选定候选，同步相关消费者、配置、文档和必要测试。发现必须移除用户要求保留的能力时，先完成可独立交付的部分，将该取舍明确交还，不以“简化”为由默认放弃契约。一般缺陷修复用 [bug-fix](../bug-fix/SKILL.md)，普通评审用 [requesting-code-review](../requesting-code-review/SKILL.md)，不强制附带简化审计。

按被保留的行为选择最小验证：正常与错误路径、配置优先级、动态加载，或与本次改造相关的取消、重启和兼容场景。行为保持型重构对照原行为与真实产物；明确的行为变化单独说明新旧差异。测试应证明保留的契约或预期回归，不把复制实现的断言、新增重试、删除失败测试当成简化证据。

交付调查范围、采用及有意义的拒绝/暂缓候选、净收益与能力代价、实际修改和检查结果。静态未找到调用只报告搜索边界，不写成完整运行证明；尚未运行的检查保持未验证。方法改编自 DSH，固定来源和许可见 [来源记录](../../references/dsh-skills-provenance.md)。

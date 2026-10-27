---
name: incident-response
description: "处理正在发生的服务或运行环境故障，确定影响、保留证据、止损恢复并核验服务状态；用于事故响应，深入根因调查与 bug-fix 衔接。 / Contain and recover an active service or environment incident, preserve evidence, and verify recovery; hand deeper causal investigation to debugging."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

# 事故响应

先确认目标环境、症状、开始时间与时区、受影响用户或服务、近期变更及可执行操作范围。已有事故流程和恢复手册时优先沿用。服务恢复是当前目标时，根因调查不能无故阻塞有证据、可回退的恢复操作。

## 判断影响并保留现场

区分已确认影响、观测告警与假设；用最小检查确定故障层次、范围及是否仍在扩大。先保留与问题相关的日志、指标、版本、配置差异和时间线，避免重启或清理先破坏唯一证据，也不为采集全部资料延误必要止损。

记录每次操作的时间、依据、作用对象、预期结果与回退方式。避免多个修改同时进行导致因果不清；确认正在进行的其他操作和共享状态。对外通知只在已明确授权时发送，报告不包含凭据或原始敏感数据。

## 止损与恢复

依据实际证据选择回退、隔离、降级、流量调整或其他现有手册步骤，不预设重启总能解决。执行前检查目标、影响面、数据兼容及恢复条件；已有授权内的常规恢复继续执行，超出授权或无法确认破坏性影响时保留待决策项。

每次操作后核对相关指标与用户路径；无改善时按预设边界停止或回退，避免无依据连续重启。数据迁移或持久化问题不能假定旧版本可直接回滚。无法访问目标环境时只交付具体步骤和未执行状态，不宣称已恢复。

## 核验、根因与交接

恢复后检查代表性请求、错误率、延迟、数据状态和积压等相关指标，并记录观察窗口、残留影响与监控条件；单个健康检查通过不足以证明业务恢复。

输出影响、时间线、证据、操作与结果、当前状态、回退信息、未解决项和后续行动。深入根因使用 [bug-fix](../bug-fix/SKILL.md)，区分触发事件、根因和扩大影响的因素，避免无证据归责。[it](../../agents/it.md) 处理环境，developer 处理代码，verifier 核对恢复和修复验收。

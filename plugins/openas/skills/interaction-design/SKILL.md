---
name: interaction-design
description: "将已确认需求转为用户流程、信息架构、界面状态和可实施的交互规格；用于界面或操作流程设计，不自行扩大产品范围。 / Translate confirmed requirements into user flows, information architecture, interface states, and implementable interaction specifications without expanding product scope."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

# 交互设计

输入是目标用户、核心任务、需求 ID、平台、现有界面与设计系统。先读已有流程、组件和术语；缺少用户证据时标出假设，不能把设计偏好当成用户需求。

## 从任务到流程

明确用户入口、完成目标、必要信息与成功反馈，安排导航与信息层级。优先复用既有操作模式，减少无助于完成目标的步骤。对分支流程描述前置条件、用户动作、系统响应、下一状态和退出/恢复方式。

按适用场景补齐加载、空态、成功、失败、权限不足、重复操作和中断恢复。对提交、删除等关键操作说明校验、进行中反馈、重复触发处理和撤销或确认条件；不对所有普通操作添加确认弹窗。

## 形成实施规格

明确页面或组件的内容层级、交互触发、状态转换、文案、输入约束、焦点与键盘行为，以及必要的窄屏适配。沿用已有设计 token；没有设计系统时只定义当前任务必需的规则，不擅自建设完整组件库。

复杂流程采用文字线框、状态表或宿主支持的原型表达。区分建议、已确认决定和现有实现；工具只能写文档时不宣称已生成可交互原型。产品范围疑问回交 product-manager，接口可行性与技术约束交给 cto。

## 交付与验证

交付流程、页面/组件清单、状态与文案、需求映射和可观察的验收条件。用代表性任务逐步走查入口、正常完成、失败恢复和退出，记录发现及设计调整；走查不能冒充真实用户可用性测试。

需要可访问性检查时使用 [accessibility-review](../accessibility-review/SKILL.md)。交付给 [ux-designer](../../agents/ux-designer.md) 或实现者时保留假设、未决项及当前版本，避免只交付视觉形容词。

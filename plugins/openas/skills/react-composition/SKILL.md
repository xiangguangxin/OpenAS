---
name: react-composition
description: "在 React 项目中设计或重构可组合组件、共享状态与明确的组件接口；用于属性组合失控、重复组件和组件库 API，不触发无关前端迁移。 / Design or refactor React component composition, state ownership, and explicit APIs within the existing React project."
---

中文 | [English](SKILL.en.md)

遵循[语言约定](../../references/language.md)、[证据规则](../../references/evidence-policy.md)和[项目适配](../../references/project-context.md)。先确认实际 React 版本、调用方、组件契约、现有样式与可访问性机制。

# React 组件组合

从具体重复、无效属性组合或状态不同步的问题开始。列出调用方支持的组合和必须保留的行为；小组件可直接使用 props/children，不为复用假设搭建框架。把互斥模式表达为明确变体或类型约束，迁移所有实际消费者后再删除旧接口。

共享状态放在需要同步的组件的最近共同拥有者；区分受控值、默认值、内部瞬态状态和事件通知，避免双重事实源。深层共享确有需要时使用限定范围的 Context，约定缺少 Provider 的行为；以角色清晰的子组件组合布局，保留稳定 key、焦点与语义。只有需要向调用者传递运行值时才使用函数形式的插槽。

保持项目已有 React API 和服务端/客户端边界；不要因组件重构顺带升级 React 或更换状态库。Context 拆分或 memo 需要真实渲染/性能证据，不能仅凭代码形态宣称更快。

授权实施时使用现有测试覆盖受控/非受控状态、事件次数、变体和键盘交互；检查真实调用方及类型构建。只要求评审时给出问题和方案。未运行浏览器时保留视觉与焦点验收缺口。

官方依据：[状态共享](https://react.dev/learn/sharing-state-between-components)、[Context](https://react.dev/learn/passing-data-deeply-with-context)。本技能为独立编写，未复制 Vercel 候选文本或示例，见[来源说明](../../references/skill-methods/NOTICE.md)。

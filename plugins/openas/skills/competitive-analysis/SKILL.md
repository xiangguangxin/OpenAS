---
name: competitive-analysis
description: "围绕目标用户和相同使用场景分析竞品、替代方案及自身差距，形成有来源的对比矩阵和机会判断；用于竞品调研，不以宣传或推测冒充实测。 / Compare competitors and alternatives for the same users and scenarios, with sourced evidence, gaps, and opportunity hypotheses rather than marketing claims."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

# 竞品与替代方案分析

市场调研先明确细分用户、问题和地域/行业边界，再检索当前直接竞品、间接替代与现有工作方式。市场规模、占有率和增长结论必须有可核对的数据口径和时间；公开功能信息不能证明真实需求或付费意愿，没有访谈或使用数据时将机会保持为假设。

先确定分析要支持的决定、目标用户、使用场景和自身项目边界。对代码项目按 [项目适配约定](../../references/project-context.md) 核对当前能力；没有自身实现时明确是在分析产品构想。

## 确定比较对象和口径

选择解决同一问题的直接竞品及有意义的替代方式，包括现有流程或自行实现；说明纳入与排除原因。用户指定对象时保留，不因资料少擅自替换。

按场景定义维度，例如核心任务完成度、集成方式、部署约束、用户体验、价格口径、许可证及维护情况。比较时对齐版本、套餐、地区、计费单位和测试条件；不适用与未知分开，不把没有找到证据写成“不支持”。

## 证据矩阵

每条关键结论关联来源、日期、版本/套餐和证据类型：官方声明、源码确认、实际试用或第三方描述。易变信息需当前查询；来源方法参照 [technical-research](../technical-research/SKILL.md)。无联网工具时可分析用户资料，但不宣称完成了最新市场调查。

体验或性能比较需要相同任务、输入、环境和指标。未实际试用则明确标注；营销案例不当作独立基准，公开 star 数或下载量也不能直接证明质量、市场份额或用户满意度。

## 从差异到机会

解释差异影响哪类用户、发生在什么场景、迁移成本是什么。将可观察事实、原因推断和待验证的用户需求分开。优势也需说明成立条件，避免为了突出自身而选择性比较。

交付对比矩阵、各对象的适用场景、自身有证据的差距、机会假设及验证方式，附来源与未覆盖范围。机会不自动变成开发承诺；需要排序时交给 [roadmap-planning](../roadmap-planning/SKILL.md)，需要技术选型时交给 [solution-design](../solution-design/SKILL.md)。

仅使用任务范围内可访问资料；不自动注册、付费购买、联系厂商或上传项目数据。

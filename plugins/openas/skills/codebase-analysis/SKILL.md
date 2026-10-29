---
name: codebase-analysis
description: "依据实际源码梳理陌生或已有项目的入口、模块、依赖、核心调用链和扩展点，形成有证据的架构现状说明；用于理解代码库，不默认进行缺陷审计、架构改造或二进制逆向。 / Explain repository entry points, modules, dependencies, core call paths, and extension mechanisms from source evidence; do not default to audits or binary reverse engineering."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 代码库分析

明确要回答的问题、目标版本、相关子系统和可用源码，读取 [项目适配约定](../../references/project-context.md)。只读分析默认不修改文件；用户指定输出文档时沿用指定路径。仓库很大时围绕目标选择入口和代表性流程，说明覆盖范围，不为介绍局部模块遍历全部源码。

## 从入口建立结构

先看项目说明、构建清单、运行配置和目录，再从源码确认可执行入口、公开 API、测试入口及模块边界。区分生产实现、测试夹具、示例、生成代码和第三方内容；文档是线索，目录名和文件数量不是职责或重要性的证据。

沿一个与问题相关的真实入口追踪输入、关键调用、状态或数据传递及输出。按需要补充失败路径、初始化与资源释放，记录核心符号和调用方。区分源码依赖、构建依赖和运行时交互；静态引用不等于实际执行顺序，辅助函数存在不等于入口可达。

对插件、反射、代码生成或配置注入，检查注册、发现与绑定位置。不能静态解析的边注明候选和缺失证据，不凭命名补造调用链。仅在任务授权和现有工具允许时运行定向检查，记录环境、输入和观察；源码阅读不能冒充运行验证。

## 形成可追溯的现状

输出与问题有关的系统边界、模块职责、关键路径、数据或资源所有权、外部依赖和扩展入口。每个关键结论附文件及符号位置，区分源码事实、文档宣称、推断与未知。扩展点需说明实际注册或调用机制及已有示例，不把任意可编辑文件称作正式扩展接口。

图确实有助理解时使用 [technical-diagrams](../technical-diagrams/SKILL.md)，图与源码使用一致名称。避免大段抄代码或只列目录；读者应能找到入口，并理解相关模块如何协作、哪里仍待确认。交付目标版本、覆盖范围、现状说明、证据索引和未解析项，不将局部阅读宣称为全面审计。

需要判断某项修改会影响哪里时使用 [change-impact-analysis](../change-impact-analysis/SKILL.md)；检查已实现边界是否符合既定设计使用 [architecture-conformance](../architecture-conformance/SKILL.md)。改造方案交给 architecture-evolution，面向读者整理正式文档使用 [project-documentation](../project-documentation/SKILL.md)，不因发现结构问题自动进入修改。

---
name: ci-cd
description: "依据项目构建与验收配置或排查 CI/CD 流水线，处理触发条件、构建矩阵、缓存、制品、权限和失败证据；用于持续集成与交付工程，不自动部署、发布或修改远程仓库设置。 / Configure or diagnose CI/CD triggers, build matrices, caches, artifacts, permissions, and failure evidence; do not automatically deploy or change remote repository settings."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 持续集成与交付

读取 [项目适配约定](../../references/project-context.md)、现有流水线、本地构建测试入口、运行器约束和任务验收。明确本次是配置、诊断还是执行交付，沿用现有平台和工具；本地配置变更不自动授权触发远程发布、安装依赖或变更仓库保护规则。

## 定义可重复的检查链

把源码检出、环境准备、依赖解析、构建、测试与制品交接对应到具体任务和失败条件。优先复用本地入口，核对工作目录、版本、环境变量和退出码传播，防止管道或错误捕获吞掉失败。明确触发事件、路径过滤、分支与取消策略；取消旧检查可用于无副作用的验证任务，部署或数据变更不能因此被中断到未知状态。

矩阵只覆盖实际支持的平台、运行时和构建组合，区分必需与实验性任务。路径过滤、跳过及允许失败需与必需检查的判定一致，不能让未执行被误认为验收通过。对需要总体验收状态的项目，明确聚合任务如何处理上游失败、取消和跳过。

## 缓存、制品与信任边界

缓存键依据实际工具链、平台和锁文件等兼容输入设计，允许缓存缺失后完整重建；缓存命中不能替代安装完整性或测试。区分可丢失缓存与需要追溯的交付制品，记录制品对应提交、构建环境、校验信息和保留范围。下游验证与交付使用同一已验证制品，避免重新构建后沿用旧验证结论。

识别不可信 PR、第三方执行步骤、自托管运行器与凭据的边界。任务权限按实际需要限定，避免带凭据执行未经信任的代码或提升其产物权限；跨任务和跨运行的制品在消费前核对来源与对象版本。不在日志或制品中保留秘密，沿用平台支持的凭据机制。平台语法、权限默认值或执行组件版本需要确认时，用 [technical-research](../technical-research/SKILL.md) 核对对应版本官方资料，不猜测配置字段。

## 诊断与交付验证

先绑定具体提交、事件、任务和失败步骤，区分配置解析、运行器、网络、依赖、构建与测试失败。比较本地和 CI 的版本、工作目录、权限及环境差异，以最小实验确认原因；重试只用于有证据的暂时失败，保留首次错误，不用无限重试或放宽断言掩盖缺陷。

按环境运行配置检查及相关本地命令；有对应授权和工具时核对远程实际执行结果。本地命令通过不代表远程触发、矩阵、凭据或部署已验证。交付任务需有目标环境、开始条件、同环境并发控制、成功检查与失败恢复安排；无在线操作授权时只交付配置或计划。

由 [it](../../agents/it.md) 处理流水线和环境，业务构建或测试缺陷交给 developer。输出变更范围、触发及任务关系、制品来源、检查证据和未验证项；提交合并用 [finish-development-branch](../finish-development-branch/SKILL.md)，正在发生的服务事故交给 [incident-response](../incident-response/SKILL.md)。配置完成、CI 成功与发布成功分别报告。

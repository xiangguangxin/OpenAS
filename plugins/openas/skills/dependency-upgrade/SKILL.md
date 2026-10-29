---
name: dependency-upgrade
description: "分析并实施指定范围的依赖或工具链升级，核对破坏性变化、传递依赖、锁文件、调用适配和回归证据；用于版本升级及兼容迁移，不默认升级全部依赖或替换既定技术路线。 / Assess or implement scoped dependency and toolchain upgrades, including breaking changes, transitive resolution, lockfiles, call-site adaptation, regression checks, and recovery."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 依赖升级

确认目标依赖、当前与目标版本、升级原因、允许修改范围和支持环境。读取清单、锁文件、实际解析结果、调用方与构建配置，区分声明范围、已锁定版本和当前环境安装版本；无锁文件时沿用项目的版本管理方式，不机械引入新工具。只要求评估时保持只读。

## 比较变化与影响

依据目标版本的官方发布说明、迁移指南和支持矩阵核对 API、行为、默认值、配置、运行时及构建要求；同时检查跨越的中间版本。用 [technical-research](../technical-research/SKILL.md) 核对时效性资料，记录来源、版本和未知项，不把语义版本号当作兼容保证。安全动机需核对官方公告、受影响版本及实际使用路径，必要时交给 [security-review](../security-review/SKILL.md)。

识别直接与传递依赖、插件或 peer 约束、原生 ABI、生成代码和运行时之间的联动，只调查与本次升级相关的边界。检查许可证变化和部署可用性等现有硬约束；推荐路线不满足约束时报告冲突，不擅自扩大为技术栈替换。区分必须同步升级的集合与可独立调整项，保留最小可行升级作为比较基线。

## 控制实施与锁文件差异

记录变更前版本和可信检查基线，按项目既有包管理器及版本更新清单和锁文件，不手改锁文件来伪造解析结果。需要执行安装、下载或生成步骤时核对已有授权和生命周期脚本；评估请求不自动授权执行候选代码。解析失败先调查约束来源，不默认强制安装、忽略 peer 冲突或关闭完整性校验。

检查解析差异是否只包含预期升级及必要联动。无关的大量重锁定需查明工具版本、源配置或解析策略变化，避免混入任务。同步修改实际受影响的调用、配置及生成产物；不因依赖升级顺手重构无关模块。

## 验证兼容与恢复

围绕实际变化验证构建、导入或启动、受影响接口、默认行为、错误路径和相关集成；项目支持多种环境时覆盖受影响的组合，避免只验证当前机器。可复现的兼容缺陷先保留失败场景；纯版本调整无须制造镜像实现的测试。分别记录安装解析成功、构建通过和行为兼容的证据，前一项不能证明后一项。

回退需恢复配套清单、锁文件、调用与配置，不能只退回一个版本号。涉及持久格式、外部协议或不可逆数据变化时使用 [architecture-evolution](../architecture-evolution/SKILL.md) 制定兼容及恢复安排；旧包可重新安装不等于旧程序仍可读新数据。

交付版本及依赖变化摘要、破坏性变化与适配位置、实际验证命令和结果、恢复方法及未验证项。developer 处理调用适配，it 处理环境和流水线；CI 矩阵调整使用 [ci-cd](../ci-cd/SKILL.md)，独立验收由 verifier 核对。不将目标版本安装成功称为升级全部完成。

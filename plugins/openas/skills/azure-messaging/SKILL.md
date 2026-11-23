---
name: azure-messaging
description: "排查实际 Azure Event Hubs 或 Service Bus 的连接、认证、锁续期、重复处理与 checkpoint 问题；用于 Azure 消息 SDK 故障，不把通用消息队列任务绑定到 Azure。 / Diagnose Azure Event Hubs and Service Bus SDK connectivity, authentication, lock, duplication, and checkpoint failures."
---

中文 | [English](SKILL.en.md)

遵循[语言约定](../../references/language.md)、[证据规则](../../references/evidence-policy.md)和[项目适配](../../references/project-context.md)。方法改写来源与 Microsoft MIT 许可见[来源说明](../../references/skill-methods/NOTICE.md)。

# Azure 消息 SDK 排障

读取实际服务、SDK 语言/版本、namespace、queue/topic/consumer group、部署环境、错误码与发生时间。只保留脱敏资源标识、日志和相关配置，不输出连接串、token 或消息正文中的私人数据。已有信息足够时直接诊断。

先查已授权资源的服务健康与观测数据，再对照 SDK 错误、认证方式、网络/AMQP、实体名称和 SDK 配置。使用已连接的 Azure MCP、CLI、日志或等价工具；按当前工具 schema/help 调用，不假定所有宿主都存在某个 MCP 名称。缺少访问时标明缺口，仍可根据代码和官方文档继续分析。

区分 Service Bus 的消息锁、续期、settlement、会话与死信问题，以及 Event Hubs 的分区、consumer group、处理器所有权、offset 与 checkpoint 问题。结合实际投递契约核对幂等和重试，不能通过增加重试掩盖重复副作用。修改 prefetch、批次、超时前明确吞吐、锁时长和处理时延的关系。

优先读取配置和本地可复现证据；发送/接收测试消息、重放死信、移动 checkpoint、重启消费者和修改云资源均有实际副作用，按既有任务授权限定目标。诊断请求不自动许可生产操作。

交付错误→证据→根因或假设→最小修复→回归检查。修复后验证正常处理、重复/失败路径和 offset/锁行为，保留仍需服务端验证的事项。当前依据：[Microsoft 排障入口](https://learn.microsoft.com/en-us/azure/developer/azure-skills/skills/azure-messaging)。

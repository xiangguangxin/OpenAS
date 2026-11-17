---
name: browser-goal-executor
description: "在指定 Web 应用中多轮执行目标，按语义定位、等待动态状态、保存下载并独立验收。 / Execute authorized multi-step web goals with semantic browser actions, observable waits, downloads, and acceptance."
---

中文 | [English](SKILL.en.md)

遵循[语言约定](../../references/language.md)和[结论与证据共享规则](../../references/evidence-policy.md)。

# 浏览器目标执行

1. 明确目标 URL、测试会话、允许的动作和成功条件。已有宿主 Playwright 时读取[接入指南](../../integrations/playwright/README.md)并使用实际工具。需要通过独立 Runtime 运行或恢复时，按[浏览器使用说明](../../integrations/computer-use/RUNTIME.md#浏览器目标)选择 Chromium 入口及下载目录。
2. 读取当前页面语义快照，按可见角色、名称或字段标签唯一定位。每次操作后刷新观察，异步任务等待成功文本或其他可观察状态。输入使用授权测试数据。遇到授权范围外的导航或无法唯一定位的控件时重新确认当前页面。
3. 下载之前建立目标路径和验收规则。使用新文件名保存，随后调用 [artifact-verification](../artifact-verification/SKILL.md) 核对实际下载产物。以目标状态和通过的产物检查为完成依据。
4. 恢复时使用原启动地址、下载目录和 checkpoint，从新的浏览器会话重新观察页面。若中断动作结果未知，走 Runtime reconcile。使用 [gui-goal-executor](../gui-goal-executor/SKILL.md) 处理原生桌面窗口。

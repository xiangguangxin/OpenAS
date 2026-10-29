---
name: accessibility-review
description: "检查界面或交互设计的键盘、焦点、语义、标签、对比度和动态反馈，提供可复现问题；用于可访问性评审，不凭自动扫描宣称全面合规。 / Review keyboard use, focus, semantics, labels, contrast, and dynamic feedback; report reproducible barriers without claiming full compliance from scans."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 可访问性评审

确认评审对象是设计还是可运行界面、目标平台、关键用户任务和要求的标准版本或等级。用户未要求正式合规时围绕操作障碍评审，不自行承诺认证；引用具体标准条款时核对对应版本的官方原文，无法核对则标明限制。

## 按用户任务检查

从关键入口完成实际任务，检查键盘能否到达和操作控件、顺序是否合理、焦点是否可见，弹窗打开和关闭后的焦点是否正确，是否存在键盘陷阱。结合实际语义核对名称、角色、状态、表单标签、错误关联和操作反馈。

按内容检查文本和非文本对比度、缩放或重排、颜色之外的提示、图片替代文本，以及动态状态通知。动画、拖拽、触摸或限时交互只在存在时评估相应替代方式。测量记录工具与条件；不要从截图推断 DOM 语义、键盘行为或读屏结果。

## 工具与证据边界

有浏览器或辅助技术时记录平台、工具、页面版本与复现步骤。自动检查用于发现部分问题，仍需手工检查关键操作；工具通过不等于用户任务可完成。只有源码或设计稿时标明静态覆盖，将运行检查交给有能力的执行者，不编造读屏体验。

## 交付与复查

每个问题记录位置、操作步骤、实际/预期、受影响任务或用户、证据、严重度与修复建议，采用 [协作契约](../../references/team-contract.md) 的问题格式。修改后按原操作复查，并检查相关状态。

交付覆盖任务、实际运行和静态检查范围、发现与未检查项；未验证条目不能写成通过。[ux-designer](../../agents/ux-designer.md) 修订规格，developer 修复实现，test-engineer 补充适合自动化的回归。

需要浏览器结构与操作工具时，可读取 [Playwright MCP 指引](../../integrations/playwright/README.md)，保持快照、键盘实测和辅助技术验证的证据边界。

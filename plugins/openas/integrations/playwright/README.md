# Playwright MCP

用于探索页面、执行用户操作、观察结构与检查交互。适用于 test-engineer、verifier 和 ux-designer 的页面任务；已有稳定 Playwright 测试时优先运行现有测试，交互式 MCP 操作不能替代持久化回归。

## 基础概念

Playwright 是用代码控制浏览器的自动化工具，可以打开网页、点击按钮、填写表单，并检查操作后的结果。端到端测试（E2E）通过浏览器验证完整用户流程，例如“登录 → 进入首页 → 检查用户信息”。

| 名称 | 作用 | 在 OpenAS 中的用途 |
| --- | --- | --- |
| Playwright | 提供浏览器自动化 API | 编写操作页面的程序 |
| Playwright Test | 提供测试执行、断言、隔离、并行与报告等能力 | 将关键流程保存为可重复运行的回归测试，接入 CI |
| Playwright MCP | 通过 MCP 向 AI 客户端提供浏览器工具 | 让角色探索页面、执行交互并记录本次检查证据 |

浏览器自动化的几个核心对象：

- **Browser（浏览器）**：启动或连接的浏览器实例。
- **BrowserContext（独立会话）**：隔离 Cookie、登录状态等浏览器数据；可用不同会话模拟多个用户。服务端数据仍需单独准备与清理。
- **Page（标签页）**：会话中的一个页面，用于导航、读取内容和截图。
- **Locator（元素定位器）**：描述要操作的控件，例如按“按钮”角色和“登录”名称定位。优先使用角色、名称和表单标签等稳定语义。
- **Action / Assertion（操作 / 断言）**：点击、填写是操作；检查跳转地址、提示或数据是否正确是断言。完成点击并不等于业务验证通过。

概念参考：[Playwright Test 入门](https://playwright.dev/docs/intro)、[会话隔离](https://playwright.dev/docs/browser-contexts)。

## 主要功能与适用场景

| 功能 | 解决的问题 | 使用要点 |
| --- | --- | --- |
| 页面操作与端到端测试 | 验证登录、搜索、表单提交等用户流程 | 覆盖正常与失败路径，检查实际业务结果 |
| 自动等待与断言重试 | 处理控件出现、状态变化等异步行为 | 操作会等待相应可操作条件；网页断言可等待预期状态，业务完成条件仍需明确，避免依赖固定睡眠 |
| 多浏览器验证 | 检查 Chromium、Firefox、WebKit 中的兼容性 | 在项目测试配置中声明目标浏览器；MCP 一次会话的结果不代表已覆盖所有浏览器 |
| 独立会话与多用户模拟 | 避免登录状态互相污染，验证用户之间的交互 | 为不同用户创建独立 Context，并准备对应测试账号 |
| 截图与视觉对比 | 留存页面状态，发现意外的布局或样式变化 | 截图可作证据；自动视觉回归还需基准图和稳定的运行环境 |
| Trace、视频与测试报告 | 排查失败发生在哪一步 | 通过项目配置启用所需记录；MCP 中实际可用的工具与记录方式需单独确认 |

功能参考：[自动等待](https://playwright.dev/docs/actionability)、[视觉对比](https://playwright.dev/docs/test-snapshots)、[Trace Viewer](https://playwright.dev/docs/trace-viewer)。

### 最小测试示例

下面是 Playwright Test 示例，需在已安装 `@playwright/test`、浏览器依赖且本地应用运行的目标项目中使用；页面应提供对应标签、按钮及成功提示。它用于说明操作与断言，不是 MCP 配置，也不表示 OpenAS 已执行该测试。

```javascript
import { test, expect } from '@playwright/test';

test('用户能够登录', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByLabel('用户名').fill('alice');
  await page.getByLabel('密码').fill('test-password');
  await page.getByRole('button', { name: '登录' }).click();

  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByText('欢迎，alice')).toBeVisible();
});
```

`await` 等待当前异步步骤完成。示例账号必须使用测试数据；需长期验证的流程应保存到目标项目测试文件中，按该项目的测试命令运行。

在 OpenAS 中，可由 test-engineer 设计流程并维护回归测试，verifier 根据验收条件检查实际结果，ux-designer 检查交互与布局。纯算法、命令行或模拟器内部逻辑应使用对应测试工具；涉及网页界面的部分再使用 Playwright。

## 配置

[Claude Code 示例](claude.mcp.example.json) 固定 `@playwright/mcp@0.0.83`，使用 `npx`、无头与隔离会话。该 npm 包元数据要求 Node >=18；实际运行还需兼容的浏览器及系统依赖。首次启动可能下载 npm 包；缺少浏览器时依据上游版本说明安装，不因验证任务自行修改系统环境。配置合并方法见 [集成入口](../README.md)。

隔离会话关闭后不保留登录状态；它不是网络或操作权限沙箱，也不替代测试数据清理。默认不挂接用户日常浏览器，不加载个人登录资料。

## 操作方法

1. 从原始验收确定目标 URL、账号、前置状态、操作和预期。仅操作授权站点与测试数据。
2. 发现当前浏览器工具，导航后获取页面结构，按当前快照定位控件；页面变化后重新获取结构，不复用过期引用。
3. 执行代表性正常与失败路径，核对页面反馈和必要后端副作用；等待可观察状态且设置截止条件，不用固定睡眠证明完成。
4. 截图或快照写到任务允许位置，记录 URL、环境、步骤、实际与预期；不在报告保留密码、cookie 或敏感表单数据。
5. 关闭会话并按既定方式清理本次测试数据；需长期回归的行为交给测试工程师编写项目原生测试。

可访问性快照只证明部分结构，不能证明对比度、完整键盘体验或读屏结果；按 [accessibility-review](../../skills/accessibility-review/SKILL.md) 标注实际覆盖。

## 最小验收与降级

在已授权的本地测试页面导航、读取标题和一个可见控件，执行无副作用操作并核对状态，关闭浏览器。记录实际工具与结果。无浏览器工具时可运行已有浏览器测试或列出手工步骤，标记交互式检查未执行，不将静态源码检查写成通过。

来源：[官方仓库](https://github.com/microsoft/playwright-mcp)；包元数据：[0.0.83](https://registry.npmjs.org/@playwright/mcp/0.0.83)。上游许可证为 Apache-2.0；本目录为自行编写的指引与配置，不复制服务端源码。

# Praxis 独立 GUI 执行与 OpenAS 接入

[English](RUNTIME.en.md) · [Nova 安装手册](USER-GUIDE.md) · [客户演示与验收](https://github.com/xiangguangxin/OpenAS/blob/main/docs/customer-demo.md)

独立的桌面/浏览器循环、checkpoint、审批、恢复与文件验证由 [Praxis](https://github.com/xiangguangxin/Praxis) 维护。OpenAS 保留编排 Skill、接入指南和兼容脚本，不再携带 Runtime 实现及其测试。

## 安装与启动

```sh
python -m pip install git+https://github.com/xiangguangxin/Praxis.git
praxis create ./goal-state.json --goal "完成授权 GUI 任务" --criterion "结果通过独立检查"
praxis run ./goal-state.json --nova /absolute/path/to/nova --verifier ./rules.json
praxis status ./goal-state.json
praxis resume ./goal-state.json --nova /absolute/path/to/nova --verifier ./rules.json
```

演示应固定实际测试过的提交，安装 URL 可用 `@完整提交SHA` 固定版本。模型 API 和 Nova 需单独配置；Claude/Codex 的订阅、MCP 注册和权限不会自动继承。Nova 要运行在 Windows/macOS 已解锁的原生交互式桌面。运行器不是后台服务，恢复需要重新启动命令。

原 `python goal_runtime.py create/status/...` 和 `python live_goal_agent.py checkpoint --nova ...` 仅为兼容入口，必须先安装 Praxis。新项目优先使用 `praxis` CLI。环境变量、LiteLLM 和完整参数以[当前 Praxis 文档](https://github.com/xiangguangxin/Praxis/blob/main/RUNTIME.md)及本地 `--help` 为准。

## 恢复与独立验收

使用相同 checkpoint、后端配置、下载目录和 verifier 恢复。跨进程锁、未知动作的 reconcile 和审批由 Praxis 实现；不要绕过暂停、盲目重放提交或把重启当作无损事务恢复。

```sh
praxis reconcile ./goal-state.json --outcome executed --note "已核对实际结果"
praxis verify ./goal-state.json --verifier ./rules.json
```

Verifier 将每项条件映射到文件规则，可检查文件、JSON 字段、run ID 和新鲜度。没有 verifier 时不能将模型 completed 当作独立业务验收。规则和边界见 [Praxis artifact verification](https://github.com/xiangguangxin/Praxis/blob/main/RUNTIME.md#artifact-verification)。

## 浏览器目标

```sh
python -m pip install 'praxis-agent-runtime[browser] @ git+https://github.com/xiangguangxin/Praxis.git'
python -m playwright install chromium
praxis run ./goal-state.json --browser-url http://127.0.0.1:8080 --download-dir ./downloads --verifier ./rules.json
```

下载目录事先准备，使用新任务输出；恢复时重新观察页面，不能假定登录和标签页持久化。[客户演示指南](https://github.com/xiangguangxin/OpenAS/blob/main/docs/customer-demo.md)提供可运行的构建/测试/下载 fixture 和真实后端验收脚本。该 fixture 的测试报告不等于生产覆盖率报告。

## 证据范围

OpenAS CI 的本地 HTTP、模拟客户端和 Windows 工作流 smoke 分别验证各自范围；不证明真实浏览器、Windows/macOS Nova 或客户应用已端到端通过。真实验收需在对应环境执行 `scripts/customer_acceptance.py`，保留 checkpoint、独立验证结果和现场业务核对。当前记录见[客户准备度收据](../../workflows/evidence/2026-11-19-customer-readiness/receipt.json)。

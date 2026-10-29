# 共享证据规则评估 / Shared evidence policy evaluation

2026-10-29，针对 [共享规则](../../../references/evidence-policy.md) 的本地评估。完整合成夹具、两次客户端结构化回答、宿主观察和相关源码 SHA-256 见 [receipt.json](receipt.json)。路径已归一化，不包含账号或认证材料。

- `stale-pass`：真实 Codex 客户端读取规则、比较当前与旧源码指纹，运行现有测试得到退出码 1，并明确旧通过报告对当前对象失效。测试失败是夹具预期行为。
- `static-answer`：真实客户端仅静态读取，区分源码推导与运行观察，明确性能与远程 CI 未验证；未运行测试或修改夹具。
- 宿主检查两次路由、实际读取命令和夹具指纹；本次实施会话另行阅读回答内容。不是独立人工审查，也不能证明所有未来会话遵守规则。
- 负对照仅移除 Python 工作流的规则读取和提示注入；两个针对性测试均失败，分别捕获规则正文未传入和缺少规则仍启动客户端。保留规则后的结果见下方回归记录。

对象是基于 `7184386` 的未提交工作区，相关文件版本以回执中的指纹为准。历史合成报告不作为真实测试证据；远程 CI 未检查。JavaScript 回归只覆盖 mock 编排，不能证明真实代理行为。

English: Two real client trials exercised stale evidence rejection and explicitly bounded static analysis. Host observations and implementation-session semantic review support only these fixtures and recorded source versions. The negative control removed policy loading/embedding and caused both targeted tests to fail. No remote CI or universal compliance is claimed.

本地回归：仓库测试 96 项（跳过 12 项），Python 工作流 125 项，JavaScript mock 编排 8 项；两项针对性测试单独复跑通过。执行命令和退出码见回执。以上针对记录版本的 Linux 工作副本，不代表远程 CI。

# OpenAS 移植验收 · 2026-10-21

本次整合了 5 个角色和 14 个 Skills，新增原生插件 manifest、marketplace、使用说明和结构校验器。源目录未修改，源文件指纹与移植边界见 [migration.json](migration.json)；架构见 [architecture.md](architecture.md)。

## 已执行

| 检查 | 结果 | 证明范围 |
|---|---|---|
| 插件移植测试 | 9 项通过 | manifest/catalog 对应、相对资源、损坏包拒绝、搬迁后运行、项目记忆隔离、插件删除后知识保留及插件目录写入保护 |
| 原有 Python 回归 | 25 项通过 | 任务范围与验收门禁、失败处理、记忆生命周期、Codex 适配器模拟调用 |
| JavaScript 模拟宿主 | 8 项通过 | 使用 functions.exec V8 执行同一 runTests(source)，验证编排分支；非 Node CLI/真实 Agent |
| Skill 格式校验 | 14 项通过 | skill-creator quick_validate 的 frontmatter/目录要求 |
| 本地插件结构检查 | 通过 | 5 个角色、14 个技能、包内 Markdown 相对链接、无符号链接、资源内容哈希 |
| REA 上游文件与许可指纹 | 8 份一致 | 保留上游 Skill、六份参考和 MIT 文件 |

机器可读结果、命令及插件内容指纹见 [validation.json](validation.json)。单元测试中的假客户端仅验证适配器行为，不证明独立 Agent 已实际工作。

## 尚未执行的客户端验收

当前 PATH 没有 Claude CLI，因此没有声称已在 Claude Code 会话中验证热加载。具备客户端后：

1. 在仓库运行 `claude plugin validate ./plugins/openas`、`claude plugin validate .`。
2. 在独立使用项目运行 `claude --plugin-dir /absolute/path/OpenAS/plugins/openas`，检查 `/openas:bug-fix` 和角色列表。
3. 临时修改 Skill 中一条可识别说明，运行 `/reload-plugins`，确认后续调用读到新版；恢复说明并再次 reload。不要用正在执行的任务判断热加载。
4. 本地 marketplace 安装后，按 README 的 project-scope 命令禁用/启用/卸载并 reload，检查组件变化及原项目记忆仍在。
5. 使用项目若已有同名独立 Skill，检查命名空间和是否重复加载；不要同时走目录与 marketplace 两条加载路径。

没有为本次移植重新运行六阶段真实模型修复。`plugins/openas/workflows/evidence/` 下的既有报告明确保留为源 gem5 的历史证据，不作为 OpenAS 原生插件加载成功的证据。

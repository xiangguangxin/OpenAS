# 评审修复与验收 · 2026-10-22

本记录逐项对应项目评审中的缺口。代码修复、模拟测试、真实客户端和远端设置分别记录，不相互代替。

| 项目 | 状态 | 实现与证据 |
| --- | --- | --- |
| 文件权限变化漏检 | 已修复 | 快照包含类型、权限和内容哈希；回归覆盖范围外 chmod 与验收命令 chmod |
| 收据缺少原始来源依赖 | 已修复 | evidence.sources 显式记录来源；覆盖内容改变、文件删除、越界和旧格式兼容 |
| grilling 误触发与反复确认 | 已修复并做真实行为验收 | 普通评审、明确采访、授权修复三项任务，宿主检查路由、问题策略、文件变化和修复测试 |
| 强制 CI 合并门禁 | 配置脚本完成，远端未启用 | 当前连接没有设置写入接口，本机没有已认证 gh；`--apply` 明确失败并保持远端不变 |
| 真实客户端验收 | Codex 已通过；Claude 尚缺环境 | 已登录 Codex CLI 完成分页修复六阶段闭环；Claude 原生测试显式启用后因 CLI 不存在退出失败 |
| 技能行为评测 | 已提供并运行有限场景 | scripts/evaluate_skills.py；不是所有技能与模型的普遍正确性证明 |
| 技能操作指导 | 已补齐本次发现的薄弱项 | worktree、计划、执行、评审、分支收尾与 grilling 的适用范围和失败处理 |
| 常规工程产物 | 已支持 | artifacts 只允许声明的新建目录，不覆盖既有源码；验收仍不能修改源码 |
| 跨项目示例 | 已补齐 | 分页、CLI JSON 报告和前端选择状态；CI 验证失败基线及参考修复，不代表浏览器验收 |
| 发布维护 | 已补齐 | 项目级 MIT、CHANGELOG、贡献指南、兼容与升级说明，插件版本 0.3.0 |

## 可重复的检查

```bash
python3 scripts/check_plugin.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/openas/workflows/tests -p 'test_*.py' -v
node plugins/openas/workflows/tests/agent-team.test.mjs
```

独立临时副本中的真实客户端观察见 [验收收据](acceptance/2026-10-22.json)。普通测试和参考修复不调用模型，真实工作流与技能评测使用已有客户端配置和额度，不自动安装依赖、切换模型或放宽沙箱。

## 尚缺的外部条件

1. 在具有仓库 Administration 权限的已认证 gh 环境运行 `python3 scripts/configure_ci_gate.py --apply`。脚本会拒绝覆盖已有保护，应用后读回关键设置；还需确认后续 PR 必须等待 checks。
2. 提供已安装、已登录的 Claude CLI，按 [热加载测试](hot-reload-testing.md) 执行真实插件验证。安装/启停/卸载已有独立的可选原生测试，同样缺少真实运行条件，Codex 结果不能替代这些验收。

没有把这些条件标记为通过，也没有在默认 CI 中引入模型凭据。旧迁移报告与 REA 原始文件保持不变。

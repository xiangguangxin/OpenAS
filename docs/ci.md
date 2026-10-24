# 自动 CI

GitHub Actions 配置位于 [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)。
使用 GitHub 托管的 Ubuntu Runner，在一个 `checks` 任务中依次执行：

1. 插件结构校验。
2. 根目录 Python 单元测试。
3. 工作流 Python 单元测试。
4. JavaScript 工作流的模拟宿主测试。

运行时为 Python 3.10 和 Node.js 22。CI 安装 presentation-creation/requirements.txt 中固定的 Python 依赖，以实际验证可编辑 PPTX 生成；不安装系统 Office，不需要自建 Runner、GitLab、模型凭证或自定义镜像。
真实 Claude 热加载测试显式关闭；CI 通过不能证明真实客户端加载成功。

## 触发与结果

- PR 创建、重新打开或更新时自动检查，包括来自 fork 的 PR（首次贡献可能需要仓库管理员批准运行）。
- 合并或直接 push 到 `main` 后再次检查。
- 在 Actions 页面选择 **CI → Run workflow** 可手动运行。

普通分支 push 不单独触发，避免和 PR 重复。修改文档也会运行全部检查。
同一 PR 或分支的新运行会取消尚未结束的旧运行，单次任务最多运行 10 分钟。
任一检查失败即整个任务失败，日志在 Actions 页面查看。

## 合并门禁

工作流负责自动执行检查；强制“检查通过才能合并”由 GitHub 分支保护设置负责。
在 `main` 的保护规则中启用必需状态检查并选择 `checks`，要求分支更新到最新 `main` 后再合并。
单人维护不需要额外要求其他人审批。状态检查必须成功运行过，才会出现在候选列表中。

仓库提供可审阅的配置脚本：

```bash
python3 scripts/configure_ci_gate.py
# 在已登录且具有目标仓库 Administration 权限的 gh 环境中应用
python3 scripts/configure_ci_gate.py --apply
```

默认只输出计划。应用时要求 PR、必需 `checks`、分支更新到最新基线，并对管理员生效，不额外要求他人审批；随后读回设置核验。若分支已有保护或规则集，脚本拒绝覆盖，需先检查现有规则。当前环境的实际执行状态见 [修复与验收记录](review-remediation.md)，不能将脚本单元测试当作远端门禁已生效。
API 权限依据见 [GitHub 分支保护文档](https://docs.github.com/en/rest/branches/branch-protection#update-branch-protection)。

## 本地复现

在 Linux / WSL，准备 Python 3.10+ 与 Node.js 22 后执行：

```bash
export PYTHONDONTWRITEBYTECODE=1
export OPENAS_RUN_CLAUDE_TESTS=0
python3 scripts/check_plugin.py
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s plugins/openas/workflows/tests -p 'test_*.py' -v
node plugins/openas/workflows/tests/agent-team.test.mjs
```

## 官方参考

- [GitHub Actions](https://docs.github.com/en/actions/get-started/quickstart)
- [分支保护及必需检查](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

# OpenAS — Open Agents & Skills

将工程协作方法打包为可插拔的 Claude Code 插件。包含 5 个工程角色、需求/计划/TDD/评审、四象限 Debug、技术文档绘图、有证据的项目记忆，以及可选 Codex CLI 任务闭环。源自 gem5 项目的 `.claude`，已将资源路径与项目状态解耦。

## 快速加载

在**要工作的项目目录**启动 Claude Code，路径换成你的 OpenAS 位置：

```bash
claude --plugin-dir /mnt/c/Users/xgx/Desktop/github/xgx_gem5/OpenAS/plugins/openas
```

会话中可直接使用：

```text
/openas:bug-fix 排查这个问题，先区分需求、设计、实现、配置/环境四象限，再用日志或 GDB 验证根因
/openas:technical-diagrams 为当前文档画架构图
/openas:project-memory 提炼这次任务中有证据的可复用经验
```

技能和角色使用 `openas:` 命名空间。独立任务不必启动完整团队；Agent 调用、工具和权限依赖真实宿主能力。

## 热加载与插拔

开发模式直接编辑 `plugins/openas` 下的文件，然后在已启动的 Claude Code 会话运行：

```text
/reload-plugins
```

这是同一会话中重新加载插件组件，不需要复制到每个项目的 `.claude`。如客户端提示缓存失效，阅读提示后按需使用 `/reload-plugins --force`；不由脚本强制执行。热加载不意味着替换已在执行的任务或重启外部进程。

`--plugin-dir` 仅本次启动加载。下次启动不传该参数即可不加载。不要同时通过本地目录与 marketplace 重复加载同一插件。

需要持久安装时，先从 shell 添加本地 marketplace，再安装到当前项目：

```bash
claude plugin marketplace add /mnt/c/Users/xgx/Desktop/github/xgx_gem5/OpenAS
claude plugin install openas@openas-marketplace --scope project
```

在会话中运行 `/reload-plugins` 应用；管理持久安装：

```bash
claude plugin disable openas@openas-marketplace --scope project
claude plugin enable openas@openas-marketplace --scope project
claude plugin uninstall openas@openas-marketplace --scope project
```

再次运行 `/reload-plugins` 应用启停/卸载。marketplace 安装可能使用缓存副本；发布更新需增加插件 version，再执行 `claude plugin marketplace update openas-marketplace`、`claude plugin update openas@openas-marketplace --scope project` 和会话内 reload。日常开发优先 `--plugin-dir`，具体命令以本地 CLI help 为准。

## 记忆属于使用插件的项目

可复用规则和脚本位于插件；运行产生的记录写入**使用插件的项目**的 `.openas/memory/`。卸载/更新插件不会删除或覆盖项目记忆，不共享 gem5 的历史知识，也不修改项目 `CLAUDE.md`。

记忆 CLI 必须明确项目根目录，避免写入插件安装/缓存目录：

```bash
python3 /path/to/OpenAS/plugins/openas/skills/project-memory/scripts/project_memory.py \
  --root /path/to/your-project query 'debug gdb 根因'
```

详情见 [记忆说明](plugins/openas/memory/README.md)。目录可按项目政策加入忽略规则；不要直接共享原始日志或 core。

## 可选 Codex 适配器

Claude 插件与 Codex CLI 是两个入口；Codex 不会因 plugin.json 自动加载 Claude 插件。使用已登录的 Codex CLI 可显式运行 [工作流适配器](plugins/openas/workflows/README.md)，无需自动安装 SDK，也不修改全局客户端配置。

## 开发与验证

GitHub Actions 会在 PR 更新和合并到 `main` 后运行检查，配置见 [CI 工作流](.github/workflows/ci.yml)，使用及合并检查设置见 [CI 说明](docs/ci.md)。

Python 3.10+；项目记忆使用 POSIX 文件锁，当前支持 Linux/WSL。校验器只读，不安装依赖、不启动模型：

```bash
python3 scripts/check_plugin.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/openas/workflows/tests -p 'test_*.py' -v
node plugins/openas/workflows/tests/agent-team.test.mjs
```

有 Claude CLI 时补做原生验证和会话内加载验收：

```bash
claude plugin validate ./plugins/openas
claude plugin validate .
```

真实客户端热加载已固定为可选 unittest 集成测试，运行方式、额度上限与断言见 [热加载测试](docs/hot-reload-testing.md)。默认跳过，显式启用后缺少客户端会失败。

当前移植的验证范围见 [验收记录](docs/validation.md)。结构校验与模拟客户端测试不能证明 Claude 已在会话中真实加载；本项目没有用后台进程伪造热加载结果。

## 目录与来源

```text
.claude-plugin/marketplace.json   本地/仓库分发入口
plugins/openas/
  .claude-plugin/plugin.json     插件清单
  agents/                       五角色
  skills/                       可按需调用的技能及资源
  references/                   协作契约
  workflows/                    可选执行适配器、测试和历史样例
  integrations/rea/              REA 来源、MIT 许可及可选环境检查
  memory/README.md              状态存储约定（不附带知识库）
scripts/check_plugin.py         本地只读校验
```

[迁移记录](docs/migration.json) 保存源提交和源文件指纹。REA 上游 Skill 及参考原样保留并附 [MIT 许可](plugins/openas/integrations/rea/LICENSE)；其工具/MCP 仍为可选依赖，加载本插件不自动安装或连接它们。gem5 专属内容保留为有标注的例子，不作为其他项目的必选技术栈。

官方依据：[插件格式](https://code.claude.com/docs/en/plugins-reference)、[创建与迁移](https://code.claude.com/docs/en/plugins/create)、[热加载和管理命令](https://code.claude.com/docs/en/plugins/cli-reference)。

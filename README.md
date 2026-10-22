# OpenAS — Open Agents & Skills

**可插拔的角色协作、证据驱动的调试、可复用的项目记忆。**

OpenAS 将需求分析、方案设计、开发调试、评审与验证整理为可按需组合的工作方法，以 Claude Code 插件形式提供 **5 个协作角色、14 个技能**，并配备可选的 Codex CLI 工作流适配器。

适用于 Web 应用、后端服务、库、命令行工具、原生程序、数据处理和文档项目。接入后沿用目标仓库的技术栈、规则和验收命令。

## 功能特性

### 按需组合的角色与技能

架构师、开发者、对抗评审、技术文档工程师和独立验证者各有明确职责，共用任务范围、交接和证据约定。简单任务直接调用单个技能；复杂任务按需要组合设计、实现、评审与验证，评审问题通过稳定 ID 跟踪和逐项回应。

14 个技能覆盖需求探索、实施计划、TDD、系统化调试、代码评审、技术绘图、项目记忆和分支收尾等环节，可独立使用，也可用于团队协作。

### 证据驱动的故障定位

从**需求、设计、实现、配置与环境**四个角度调查候选原因，再用日志、适合当前运行时的调试工具和可区分实验建立因果链。修复验证保留命令、退出码与关键输出，区分已确认结论、待验证假设和未覆盖范围。

### 可审查、可追溯的项目记忆

将项目事实、设计决定和可复用经验保存到目标项目的 `.openas/memory/`，供后续任务检索与交接。记录先进入候选状态，经过审查后才参与复用；直接证据或显式关联的原始来源变化后，检索会排除对应的旧记录。各项目独立存储，插件更新或卸载后记忆仍然保留。

### 可插拔与会话内热加载

通过 `--plugin-dir` 临时加载，或通过 marketplace 持久安装到项目。修改插件资源后，可在当前 Claude Code 会话中用 `/reload-plugins` 更新后续调用使用的组件，便于迭代角色与技能，无需逐项目复制文件。

### 沿用现有项目工具链

从目标仓库读取技术栈、目录、依赖、领域约束和验证方式。服务端使用现有 API 测试，前端检查交互与页面状态，文档任务核对来源和链接；接入时无需额外创建 OpenAS 专用配置文件。

### 技术图表与可追溯的任务编排

- **技术绘图**：按表达需求选择 Mermaid、SVG 或 D2，绘制架构、数据流、状态机和交互时序，并核对图与源码、文档的一致性。
- **可选 Codex CLI 工作流**：顺序执行设计、评审、文档、实现与验证，保留阶段输出、文件指纹和验收记录；评审或验证未通过时，在限定轮数内回交修订，仍未通过则停止并保留现场。

Agent 调用、热加载和工具执行以实际客户端能力及会话授权为准；具体使用方式与验证边界见下文。

## 快速开始

在**目标项目目录**中启动 Claude Code，将路径替换为你的 OpenAS 所在位置：

```bash
claude --plugin-dir /path/to/OpenAS/plugins/openas
```

随后可在会话中调用技能：

```text
/openas:bug-fix 排查这个问题，先分析可能的原因，再用当前项目的日志和测试验证根因
/openas:technical-diagrams 为当前文档绘制架构图
/openas:project-memory 提炼本次任务中有证据、可复用的项目经验
```

技能和角色统一使用 `openas:` 命名空间。`--plugin-dir` 只对本次启动生效，下次启动时省略该参数即可不加载。

### 适配现有项目

OpenAS 从目标仓库的规则文件、文档、源码和 CI 配置中确认工作方式，沿用已有目录、依赖管理和验证命令。接入时无需额外创建 OpenAS 专用配置文件。

例如，服务端变更使用现有 API 测试，前端交互修复检查用户操作与页面状态，文档调整核对来源、链接和图表。领域相关的单位、协议、设备和数据约束以目标项目为准。具体约定见 [项目适配说明](plugins/openas/references/project-context.md)。

## 安装与更新

### 本地开发与热加载

开发插件时，建议使用 `--plugin-dir` 直接加载本地目录。修改 `plugins/openas` 下的文件后，在已启动的 Claude Code 会话中运行：

```text
/reload-plugins
```

热加载会重新读取插件组件，供后续调用使用，无需将文件复制到各个项目的 `.claude` 目录。如客户端提示缓存问题，按提示决定是否使用 `/reload-plugins --force`。正在执行的任务和外部进程不保证同步切换到新版本。

### 持久安装到项目

在目标项目目录的终端中添加本地 marketplace，并安装插件：

```bash
claude plugin marketplace add /path/to/OpenAS
claude plugin install openas@openas-marketplace --scope project
```

安装后，在会话中运行 `/reload-plugins` 应用。后续可按需启用、禁用或卸载：

```bash
claude plugin disable openas@openas-marketplace --scope project
claude plugin enable openas@openas-marketplace --scope project
claude plugin uninstall openas@openas-marketplace --scope project
```

操作后再次运行 `/reload-plugins`。同一插件请选择本地目录或 marketplace 中的一种加载方式，避免重复加载。

### 更新已安装版本

marketplace 安装可能使用缓存副本。维护者发布更新时需递增插件版本号；使用者随后在终端执行：

```bash
claude plugin marketplace update openas-marketplace
claude plugin update openas@openas-marketplace --scope project
```

最后在会话中运行 `/reload-plugins`。具体命令及可用参数以本地 Claude CLI 的帮助信息为准。

## 项目记忆

技能、角色和脚本随插件分发，任务产生的记忆则保存在**目标项目**的 `.openas/memory/` 中。插件更新或卸载后，项目记忆仍然保留。各项目的记录独立管理，记忆功能不会改写项目的 `CLAUDE.md`。

使用记忆 CLI 时，必须显式指定目标项目根目录：

```bash
python3 /path/to/OpenAS/plugins/openas/skills/project-memory/scripts/project_memory.py \
  --root /path/to/your-project query '输入校验 根因'
```

可复用结论先进入候选状态，经审查后才能用于后续任务；直接证据或显式关联的原始来源发生变化时，旧记录会被检索排除。存储格式、检索与维护方式见 [项目记忆说明](plugins/openas/memory/README.md)。是否纳入版本管理应遵循项目约定，原始日志、core dump 和敏感信息不应直接共享。

## Codex CLI 工作流

除 Claude Code 插件外，OpenAS 还提供基于 Python 标准库的 [Codex CLI 工作流适配器](plugins/openas/workflows/README.md)。它使用已安装、已登录的 Codex CLI，顺序调用角色并执行验收命令，记录阶段结果、文件变化和验证证据。

这两个入口分别使用：Claude Code 通过插件发现角色与技能；Codex 适配器显式读取相关资源并调用 CLI，`plugin.json` 本身不会让 Codex 自动加载插件。适配器不自动安装 SDK，也不修改客户端全局配置。

## 开发与验证

以下命令在 OpenAS 仓库根目录运行。Python 工具要求 Python 3.10+，JavaScript 工作流测试使用 Node.js 22；项目记忆依赖 POSIX 文件锁，当前支持 Linux / WSL。

### 本地检查

```bash
python3 scripts/check_plugin.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/openas/workflows/tests -p 'test_*.py' -v
node plugins/openas/workflows/tests/agent-team.test.mjs
```

这些检查覆盖插件结构、资源链接和工作流回归，不安装依赖、不调用模型。

已有 Claude CLI 时，可进一步验证插件清单：

```bash
claude plugin validate ./plugins/openas
claude plugin validate .
```

真实客户端的热加载验收由可选集成测试完成，默认跳过。运行条件、额度上限和断言见 [热加载测试说明](docs/hot-reload-testing.md)。结构检查和模拟客户端测试的结果应与真实客户端验收分别看待。

### 持续集成

GitHub Actions 在 PR 创建或更新，以及代码推送或合并到 `main` 后执行检查。配置见 [CI 工作流](.github/workflows/ci.yml)，运行方式与合并检查设置见 [CI 说明](docs/ci.md)。初始移植的验收范围保存在 [验收记录](docs/validation.md) 中，最新回归结果以 GitHub Actions 为准。

## 目录结构

```text
.claude-plugin/marketplace.json   本地 marketplace 入口
plugins/openas/
  .claude-plugin/plugin.json     插件清单与版本
  agents/                       5 个协作角色
  skills/                       14 个技能及配套资源
  references/                   协作契约与项目适配约定
  workflows/                    可选适配器、示例、测试与历史证据
  integrations/rea/             REA 集成说明、许可与环境检查
  memory/README.md              项目记忆存储约定
scripts/check_plugin.py         只读结构校验器
```

## 来源与参考

OpenAS 最初从 gem5 项目的协作配置中提取，现已将角色、技能与具体工程解耦。[迁移记录](docs/migration.json) 保留原始提交和文件指纹，供来源追溯；历史工作流报告与旧示例不作为新项目的默认上下文或验收证据。

REA 上游 Skill 及参考文件保留原文，并附 [MIT 许可](plugins/openas/integrations/rea/LICENSE)。相关 MCP 服务和分析工具为可选依赖，加载 OpenAS 不会自动安装或连接它们，详见 [REA 集成说明](plugins/openas/integrations/rea/README.md)。

Claude Code 官方文档：[插件格式](https://code.claude.com/docs/en/plugins-reference)、[插件创建与迁移](https://code.claude.com/docs/en/plugins/create)、[热加载与管理命令](https://code.claude.com/docs/en/plugins/cli-reference)。

## 维护与验收

项目自有内容采用 [MIT License](LICENSE)，第三方内容保留各自许可。版本变化见 [CHANGELOG](CHANGELOG.md)，开发与发布流程见 [贡献指南](CONTRIBUTING.md)，运行环境和记录格式见 [兼容说明](docs/compatibility.md)。

真实技能行为评测、修复验证及尚缺外部条件的项目分别记录在 [行为评测说明](docs/skill-evaluation.md) 和 [本次修复验收](docs/review-remediation.md) 中。

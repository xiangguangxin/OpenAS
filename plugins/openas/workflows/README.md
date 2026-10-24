# 可执行的 Codex 客户端闭环

`codex-team.py` 是本仓库的第一个真实客户端适配器，使用 Python 标准库调用已经安装并登录的 Codex CLI，不需要 Node 或另配 API SDK。

本页命令默认在插件根目录运行：先 `cd /path/to/OpenAS/plugins/openas`。资源由脚本自身位置解析，与使用项目的目录无关；记忆归属用 `--project-root /path/to/consumer-project` 显式指定。

## 默认开发链路

```text
任务 JSON → 主进程采集基线与初始指纹 → cto → red-team 设计评审 → tech-writer
    → developer → red-team 实现评审
    → 主进程执行验收命令 → verifier
    → 主进程再次验收与文件范围检查 → verified
```

各角色是独立、顺序启动的 `codex exec --ephemeral` 会话，沿用当前客户端模型配置；不硬编码模型。角色提示读取 `agents/*.md` 和协作契约，不意味着 Codex 原生解析 Claude 的角色工具白名单。评审角色使用 read-only，文档、产品、IT 配置和开发角色使用 workspace-write；没有使用跳过审批和沙箱的参数。

评审、输出格式、退出码或超时异常会停止；架构或实现需要修订时在最多三轮内回交，仍失败则停止并保留现场。不会自动安装依赖、提交、推送或合并，也不自动启动嵌套 Agent。

## 准备条件

```bash
codex --version
codex login status
python3 --version
```

需支持 exec、--ephemeral、--output-schema、-o 和相应 sandbox 的 Codex CLI。实际参数以当前安装版本 help 为准。首次客户端使用的登录与安装需要独立完成，本运行器不修改客户端全局配置。

## 先用独立 fixture 验收

仓库中的示例函数故意写错，**不要在示例源目录直接修复**。复制到临时工作区后运行：

```bash
harness_example=$(mktemp -d /tmp/openas-harness-example-XXXXXX)
cp -R workflows/examples/pagination-fixture "$harness_example/workspace"
python3 workflows/codex-team.py \
  --task workflows/examples/pagination-task.json \
  --workspace "$harness_example/workspace" \
  --output "$harness_example/run" \
  --timeout 240 --rounds 3 --no-memory
```

预期 developer 修复分页索引、边界和参数校验，tech-writer 写 DESIGN.md，原始测试保持不变。这个例子只使用 Python 标准库，不依赖任何业务工程。最终进程退出 0、state.json 的 done=true/status=verified，且 final_checks 中所有退出码为 0，才算本次闭环成功。

每次执行会消耗真实客户端额度；不要把这个命令放进普通单元测试或无条件 CI。已有项目应先在可丢弃工作树中试用。

## 自定义任务

任务包含 requirement、scope、acceptance、checks：

- scope：允许修改的明确相对文件名，不支持目录通配；含新文档时也列出其名称。
- acceptance：用户认可的验收要求，逐角色保留。
- checks：可信任务提供的命令 argv 数组，例如 `["python3", "-m", "unittest", "-v", "test_example.py"]`，主进程不通过 shell 执行。
- constraints：可选字符串列表，记录目标项目的平台、兼容性和依赖限制；完整任务会交给每个角色。
- workflow：`development`（默认）、`repair`、`direct`、`review`、`security-review`、`operations`、`documentation` 或 `research-design`，由任务显式选择，不通过关键词推断授权。`security-review` 由 security-reviewer 只读评审；`operations` 由 it 修改声明的工作区配置文件，再经 red-team 评审、检查和 verifier 验证，不负责登录或操作在线系统。
- acceptance_checks：可选，与 acceptance 等长的检查索引列表，例如 `[[0], []]`；空列表表示该项没有机器检查映射。
- artifacts：可选的新建产物目录列表，例如 `["build", ".pytest_cache"]`。可在这些目录生成编译输出、缓存或报告；默认不允许额外产物。
- 验收命令不能修改源码，只能向明确声明的 artifacts 输出；不能自动安装依赖或访问生产系统。

artifacts 目录在任务开始时必须不存在，不能包含或覆盖 scope 文件、既有源码或根目录 Git 元数据，不接受目录通配。校验失败不会自动删除目录。产物不参与源码快照，所有其他文件继续比较内容与权限；任务工作区仍拒绝符号链接。存在构建产物时应为下一次运行使用新的干净工作区。

**checks 会以主进程权限执行，必须来自可信任务定义；argv 不使用 shell 不等于命令安全。** scope 是执行后检测，不是逐文件写入访问控制，范围外变更会停止但不自动撤销；不要在有价值的共享目录中把它当成完整隔离。沙箱、用户级配置、hooks 和 MCP 以客户端实际环境为准。

输出目录必须在工作区之外且事先不存在，防止覆盖记录。目录不能含符号链接；当前实现面向小型独立工作区，会扫描全部工作区文件（包括 Git 元数据），大型仓库应先选取独立的任务工作区，而不是对整个源码树逐阶段快照。

角色使用 [项目适配约定](../references/project-context.md) 选择当前仓库的命令；上面的 Python 示例不是其他项目的强制测试框架。原有 cache-address 示例仅用于复查历史报告，不是默认任务或预加载知识。

## 产物与失败定位

输出目录保留：

| 文件 | 含义 |
|---|---|
| state.json | 版本化状态、初始/检查点快照、阶段缓存、失败类别与最终验收 |
| task.json | 本次完整任务快照，图节点包含实际上游结果 |
| handoff.json | 当前现场、已完成阶段、失败、下一阶段和证据位置 |
| acceptance.json | 每项原始验收的检查映射、宿主结果、模型验证与人工核对提示 |
| NN-phase.prompt.txt | 该角色收到的任务包及交接 |
| NN-phase.result.json | 客户端最终结构化响应 |
| NN-phase.stdout/stderr.log | 客户端运行日志 |
| baseline-checks.json / round-N-checks.json / final-checks.json | 每类检查的最新摘要；带尝试编号的日志和 JSON 保留旧记录 |

日志可能含源码或环境相关信息，发布前人工审查。客户端错误或超时时不会当作通过；超时/中断会终止本次进程组，保留工作区供检查。0.4.0 的版本化 state 支持显式 `--resume`，见下方恢复说明；不带该参数不能覆盖已有 output，旧版本状态仅用于审计。

0.3.0 起快照为每个文件保存 `sha256`、`type` 和 POSIX `mode`，因此 chmod 变化也会触发范围或验收修改检查；旧记录格式及迁移见 OpenAS 仓库的 docs/compatibility.md。

## 更多独立任务示例

| 任务 | 文件 | 复现命令 | 覆盖范围 |
| --- | --- | --- | --- |
| 分页工具 | examples/pagination-task.json / pagination-fixture | `python3 -B -m unittest -v test_pagination.py` | 纯 Python 函数与输入校验 |
| 命令行报告 | examples/cli-task.json / cli-fixture | `python3 -B -m unittest -v test_report.py` | stdin/stdout、JSON、错误码和诊断 |
| 前端选择状态 | examples/selection-task.json / selection-fixture | `node test-selection.mjs` | 不可变状态更新，不代表浏览器或 UI 验收 |

均为故意失败的训练样例。沿用上面的临时复制流程，替换 task 和 fixture 路径后运行，不能直接改随包示例。普通 CI 在临时副本中验证失败基线和参考修复，不调用模型。真实技能选择与行为检查可在 OpenAS 仓库运行 scripts/evaluate_skills.py，说明位于 docs/skill-evaluation.md。

## 有证据的项目记忆

命令行默认以 `--project-root`（省略时为当前工作目录）作为记忆所属项目；面向实际项目执行时应显式指定该参数，避免写入插件根目录。任务开始检索相关已审查记录，在运行中保存短期检查点，并在 verified 后采集有限的验收事实。经验结论先成为候选，经语义评审才能用于后续任务；来源文件改变后自动排除旧记录。使用 `--no-memory` 关闭本次记忆读写。

存储格式、命令、冲突处理及适用边界见 [项目记忆说明](../memory/README.md)，提炼流程见 [project-memory Skill](../skills/project-memory/SKILL.md)。不改写角色或权限规则。

### 自动复盘与项目技能演进

启用记忆后，任务结束还会自动保存成功/失败的有限观察。增加 `--learn` 可开启模型提炼 → 独立评审 → 生成候选技能，额外消耗客户端额度。output 需位于整个 project-root 之外，记忆需位于任务 workspace 之外；启动前校验重叠路径。超时、中断、客户端/环境错误、格式错误或范围越界时只采集观察，不额外调用模型。

技能草稿先保存在客户项目，经过可信正反试用、独立技能评审和启用后，下次任务才作为指导传给角色。运行器记录送入上下文的具体版本及关联任务结果，连续三次失败/负反馈自动暂停，支持回滚仍有效的旧版本。学习失败通过 learning_warning 报告，不改写任务验收结论。

详细命令、字段、试用 fixture 与限制见 [四阶段接入指南](../memory/learning.md)。本接入仅适用于 Python 单任务适配器；JS 模板、图运行和普通客户端会话不会因此自动执行学习。

## 运行器回归测试

不调用模型的自动测试：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s workflows/tests -p 'test_*.py' -v
```

覆盖输入和输出校验、越界修改、日志位置、失败验收阻断、客户端错误、验收修改工作区和超时。包含基线失败→修复后成功→独立验证交接的证据链回归。这些测试与真实客户端验收分开报告。

记忆测试覆盖候选隔离、证据失效、重复提议、冲突与退役、损坏文件保护，以及运行器检索和采集接入。

原有 `agent-team.js` 仍是 JavaScript 宿主模板，没有自动套用 Python 适配器。两者使用相同团队原则，但不是共享实现；修改后各自运行回归，不能用一个的结果证明另一个正确。

## 官方依据

- [Codex 非交互执行](https://developers.openai.com/codex/noninteractive)
- [使用 Codex 构建修复循环](https://developers.openai.com/cookbook/examples/codex/build_iterative_repair_loops_with_codex)

下列真实验收是源 gem5 工程的历史记录，不代表本移植版本重新完成过六阶段模型运行： [2026-10-21 Codex 闭环报告](evidence/2026-10-21-codex/README.md)。

## 选择路线

| workflow | 执行方式 | 成功状态 |
| --- | --- | --- |
| development / repair | 默认六阶段闭环；repair 明确要求故障假设和失败基线 | verified |
| direct | developer → 宿主检查 → verifier → 最终检查 | verified |
| operations | it 修改任务范围内配置 → red-team → 宿主检查 → verifier → 最终检查 | verified（工作区配置） |
| documentation | tech-writer → red-team → 文档检查 → verifier → 最终检查 | verified |
| research-design | product-manager 调研与需求 → tech-writer 后续设计 → 独立评审/回交 → 检查与验证 | verified（设计文档） |
| review | 当前宿主检查 → 只读 red-team，不修复实现 | reviewed |
| security-review | 当前宿主检查 → 只读 security-reviewer，不修复实现 | reviewed |

`reviewed` 表示评审任务已交付，允许含 needs_fix，不能据此认定目标实现正确；图中的通过依赖只接受 approve。所有路线都保留原始目标和范围；direct 不能替代用户明确要求的设计评审。JS 宿主模板仍使用原固定流程，没有自动获得 Python 运行器的新能力。

## 检查点恢复

恢复沿用原任务、工作区、客户端路径、轮数、记忆选项和 project-root。使用运行目录的 task.json 可保留图节点注入的上游结果：

```bash
python3 workflows/codex-team.py \
  --task /path/to/run/task.json --workspace /path/to/task-workspace \
  --output /path/to/run --resume --no-memory --rounds 3
```

新运行记录 `state_version=2`。恢复前核对任务、源码内容与权限、角色/技能/运行器指纹和检索到的记忆；同一运行目录不能并发恢复。完成阶段按输入摘要和实际结果文件指纹复用，缺失或失效阶段及其后继重新执行；宿主检查和 verifier 重新运行。原始失败基线与已有尝试日志保留，不重置原有修订轮数。

源文件、规则或记忆变化时默认拒绝。确认变化仍属于原始授权后，可附加 `--restart-stages` 使旧角色结果全部失效，再按本路线重新验证。此选项不允许任务变更、范围外变化或无输入变化时重置轮数。旧版本记录、已完成运行或任务定义变化应使用新的 output。

恢复读取的是可信本地记录，不是签名证明；不对不可信任务或 state 自动执行命令。进程异常退出时可从最后成功检查点检查；部分写入未形成检查点时需要人工核对。未声明的外部服务状态不在源码快照内，当前不提供跨服务事务恢复或自动回滚。

## 顺序任务图

`graph-runner.py` 支持 version=1 的 nodes，每个节点包含唯一 id、depends_on、workspace 和 task（完整对象或相对 JSON 路径）。路径相对于图文件；节点工作区事先准备，运行产物必须在所有工作区之外。

```bash
graph_example=$(mktemp -d /tmp/openas-graph-example-XXXXXX)
cp workflows/examples/workflow-graph.json workflows/examples/pagination-task.json "$graph_example/"
cp -R workflows/examples/pagination-fixture "$graph_example/workspace"
python3 workflows/graph-runner.py --graph "$graph_example/workflow-graph.json" --plan
# 以下命令才会启动真实客户端并消耗额度
python3 workflows/graph-runner.py --graph "$graph_example/workflow-graph.json" \
  --run --output "$graph_example/run"
```

先验证依赖缺失、环、工作区与共享写入范围，再按拓扑顺序执行。共享写入需要显式依赖或独立工作区；失败节点阻断下游，独立节点可继续，用户中断则不再启动后续节点。下游完整任务通过 upstream_results 收到上游状态、验收和可用交接文件位置，这些数据不增加写入权限。

图运行保存 graph.json 及逐节点目录。当前只顺序执行，不自动并行、不自动重试或恢复整个图、不启用项目记忆；单节点可使用上面的恢复流程，但恢复节点不会自动重写原图摘要或推进已阻断下游。后续执行应核对实际节点证据后准备新的图任务。技能 parallel-integration 仅指导已授权并行成果的整合。

## 验收与失败交接

acceptance.json 对显式映射且宿主检查成功、verifier 通过的条目标为 passed；没有映射的条目最多为 reviewed，仍需人工核对。review 路线为 reported。退出码不替代语义验收，不能为填满映射而引用无关检查。

state.failure 包含 kind、message 和 phase。类型区分 environment、timeout、interrupted、client_failure、invalid_result、scope_violation、review_limit、acceptance_limit 与输入 validation。没有后台自动重试，失败后先检查日志、部分产物和是否存在外部副作用，再选择恢复、修复或交回所缺条件。

## 专用调研与设计路线

在任务 JSON 设置 `workflow: research-design`，可自动执行：

```text
市场/竞品调研 → 产品需求 → 方案设计 → 技术选型 → 架构设计 → 设计文档
    → 独立设计评审 → 宿主检查 → 独立 verifier → 最终宿主检查
```

市场调研与产品需求阶段由 product-manager 承担，后续四个设计写作阶段由 tech-writer 承担；各阶段提示嵌入对应技能。red-team 评审、verifier 验证只读。不会调用 developer，不修改产品代码。每阶段只能修改自己的一个 Markdown 文件；图用内联 Mermaid。阶段产物缺失或为空时不能进入下游。

- `research_mode` 必填：`live` 使用当前公开信息，`provided` 只分析已有本地材料，保留新鲜度与需求证据限制。
- live 向客户端传入 `-c web_search="live" --json`，市场阶段必须有原生 `item.completed`/`web_search` 事件才可交付；仅“声称搜索过”无效。搜索失败停止，不能静默降为已有资料模式。搜索事件证明调用发生，不自动证明每个结论正确，引用与证据强弱仍由评审核对。
- provided 设置 `web_search="disabled"` 并提示禁止联网；这不构成对宿主其他网络工具的安全隔离。不要以已有材料模式声称完成最新市场调研。搜索配置依据 [Codex 官方配置说明](https://developers.openai.com/codex/config-reference)，使用本机已支持的参数，不修改全局配置。
- 默认六个输出为 `design/01-market.md`、`02-requirements.md`、`03-solution.md`、`04-technology.md`、`05-architecture.md` 和 `DESIGN.md`（均在 design/ 下）。可用 `design_outputs` 以阶段名映射六个不同的 `.md` 路径，scope 必须恰好包含它们；此路线不允许 artifacts。
- 基线检查在文档尚未生成时允许失败，最终 checks 必须全部通过。用目标项目可信的、不会修改工作区的检查命令，示例仅做文档存在/非空检查，语义验收由评审与 verifier 核对。

完整示例在 [live 任务](examples/research-design-task.json)、[已有资料任务](examples/research-design-provided-task.json) 和 [设计输入](examples/research-design-fixture/brief.md)。先复制到独立目录：

```bash
design_trial=$(mktemp -d /tmp/openas-design-XXXXXX)
cp -R workflows/examples/research-design-fixture "$design_trial/workspace"
python3 workflows/codex-team.py \
  --task workflows/examples/research-design-task.json \
  --workspace "$design_trial/workspace" --output "$design_trial/run" \
  --timeout 300 --rounds 3 --no-memory
```

这会调用真实客户端并使用模型额度。只验证本地材料流程时换用 provided 任务。中断后用相同参数及 `--resume`；源码/规则变化需先检查，再按既有恢复规则使用 `--resume --restart-stages`，不会重置每阶段预算。

设计评审额外返回 `revision_from`：approve 时为 `none`；needs_fix 时为六个写作阶段之一，表示最早受影响阶段。运行器重做该阶段及全部下游，保留不受影响上游的结果与评审反馈。宿主检查或 verifier 失败时保守重做六阶段，最多 rounds 轮，仍未通过则停止。每阶段独立计费修订预算并跨 resume 保留；补跑丢失证据也会消耗预算。

输出目录额外包含 `design-artifacts.json`（阶段、文件及结果）与 `design-review.json`（最新结构化评审）。真实完整日志与每次评审保留在普通阶段记录。done=true/status=verified 且 `verification_subject=design-artifacts` 只表示本次设计文档交付成功；不表示产品已经实现、市场需求得到真实用户验证或性能目标已经达到。无机器检查映射的验收仍显示 reviewed。

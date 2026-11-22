# 软件重建：吸收 Craft Anything 的方法，原生接入 OpenAS

OpenAS 新增 `software-reconstruction`，用于从已获授权的软件观测中建立独立规格，构建自己的实现，并按真实差异迭代。没有加入上游子模块、Rust crate、整仓副本或运行时依赖。

| 上游精华 | OpenAS 的原生落点 |
| --- | --- |
| Study → Build → Check → Refine | 本地准备规格 → 标准开发/独立评审 → 宿主观察器逐项比较 → 最多三轮差异反馈 |
| Clean room / Deep 分离 | 导入类型白名单与任务级显式模式，未知类型拒绝；deep 仍需目标授权 |
| Evidence confidence / limitations | 固定 observation ID、摘要、observed/derived/inferred、来源边界和限制；内容指纹校验 |
| 摘要优先、按需读取 | show 摘要与 browse 分页，避免把工具大输出当作全部目标知识 |
| Residual unknowns | 分级问题、证据引用、revision 校验；高/关键未知阻断开工 |
| 视觉和行为分别验收 | JSON 行为严格匹配；截图按相同视口与状态测量 RGB 误差，缺项/错误不可通过 |
| 无进展停止与跨恢复预算 | 连续两次无源码变化停止；沿用 OpenAS 的阶段恢复、scope、修订预算和独立 verifier |

没有导入它的反汇编/反编译引擎、320 工具全集、品牌资产、第三方字体、AI 供应商配置或依赖自动安装。许可证选择上游提供的 MIT，保留版权与[来源记录](../plugins/openas/skills/software-reconstruction/FUSION_SOURCES.json)。

## 使用

Claude Code 可直接调用：

```text
/openas:software-reconstruction 根据我授权的界面和行为观测，做一个独立实现。先明确未知与验收，再构建并逐项比较。
```

Codex 项目安装器会包含新技能入口 `openas-software-reconstruction`；更新后用 `codex_skills.py update`、`check --native` 检查，具体命令见[客户接入](customer-demo.md)。

```sh
# prepare 只整理本地证据，不调用模型
python plugins/openas/workflows/reconstruct.py prepare --brief plugins/openas/workflows/examples/reconstruction/brief.json --project /path/to/new-project
python plugins/openas/workflows/reconstruct.py show --project /path/to/new-project
python plugins/openas/workflows/reconstruct.py browse --project /path/to/new-project --limit 2
# run 才调用已安装、已登录的 Codex
python plugins/openas/workflows/reconstruct.py run --project /path/to/new-project --rounds 3
```

示例是 OpenAS 自有的数值列表应用契约。可信观察器实际调用新实现，检查空输入、数值求和、布尔值和文本拒绝，便于离线复现。它不是某个商业软件或真实浏览器重建成功的证据。Windows 请将 brief 中的 `python3` 换成本机可用的 Python 命令。完整数据契约、截图配置、未知项和恢复命令见[使用说明](../plugins/openas/skills/software-reconstruction/references/usage.md)。

## 验收边界

clean-room/deep 是本方法及本地导入入口的策略，不能封锁外部 Agent 自带的所有工具，也不是操作系统沙箱。已提供的观测标记为 provided-artifact；“observed”是材料声明，不代表宿主已访问原软件。指纹检测文件变化，不证明来源真实性。

候选结果由受信任、事先固定且位于构建工作区之外的观察器生成，不采用模型手写通过 JSON。观察器作为可信本地主机程序运行；先审阅代码和命令，不从目标材料自动执行命令。检查通过只覆盖声明的输入、视口与状态；未知和未采样行为仍须报告。视觉分数不能证明业务功能等价。

普通 CI 使用合成参考、真实本地 Python 观察器和模拟模型阶段，覆盖模式拒绝、证据损坏、类型差异、缺项、停滞与恢复。实际网站采集、真实模型、客户桌面程序需要单独验收。可选真实客户端技能评测：`python scripts/evaluate_skills.py --case software-reconstruction --output /path/to/new-evaluation`。

## English

OpenAS natively adapts Craft Anything's observation-led reconstruction method, not its Rust engine. The bilingual skill and `reconstruct.py` prepare pinned reference studies, execute trusted candidate observers, compare declared behavior/viewport cases, preserve unknowns and refine through standard OpenAS reviews/checks. No upstream install, submodule or vendored repository is required. Captures remain untrusted data; modes are ingestion/guidance rules rather than OS isolation. Local synthetic tests and mock model phases do not certify live website/desktop reconstruction. See the [English skill](../plugins/openas/skills/software-reconstruction/SKILL.en.md) and [provenance](../plugins/openas/skills/software-reconstruction/NOTICE.md).

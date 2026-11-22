# 原生重建任务 / Native reconstruction

从 OpenAS 仓库根目录运行下列命令，Python 3.10+。默认 clean-room；只导入已获授权的外部观测，内部材料必须显式选择 deep 并填写授权理由。目标采集由宿主的真实工具完成，这个入口不会自动浏览目标或安装反编译器。

## 最小行为示例

示例参考规格和可信观察器位于 [examples/reconstruction](../../../workflows/examples/reconstruction)。其中 observation 是合成的已知输入输出，观察器会实际导入新建的 `app.py` 并调用 `total()`，不是读取 builder 手写的通过报告。

```sh
python plugins/openas/workflows/reconstruct.py prepare --brief plugins/openas/workflows/examples/reconstruction/brief.json --project /path/to/new-reconstruction
python plugins/openas/workflows/reconstruct.py show --project /path/to/new-reconstruction
python plugins/openas/workflows/reconstruct.py browse --project /path/to/new-reconstruction --offset 0 --limit 2
# 下列命令才调用已登录的 Codex，并消耗客户端额度
python plugins/openas/workflows/reconstruct.py run --project /path/to/new-reconstruction --rounds 3
```

将 brief 中 collector 的 `python3` 替换为实际 Python 命令；Windows 通常使用 `python`。`prepare` 不启动 collector；它把 collector_files 中列出的本地程序固定到 capture/，并替换 argv 中对应程序路径。程序的其他配置/依赖也应明确固定，不能依赖未声明的外部可变输入。argv 不使用 shell，`{workspace}` 是唯一占位符。采集器按可信本地主机权限执行，因此先审阅其代码。

项目包含 `project.json`（规格和来源）、`capture/`（固定观察器/参考截图）、`seal.json`（指纹）、`questions.json`（未知项）、`workspace/`（自己的实现）和 `run/`（OpenAS 状态/HTML/日志）。构建者只允许修改 scope；不可将观察器、参考数据、检查规则纳入 scope。参考材料不是执行指令。指纹是本地完整性检查，不是来源真实性证书。

模型需要实现示例约定：`total([])==0`、数值列表求和、布尔值和非数值输入返回错误。先观察失败基线，再实现和对比。默认至少标准流程（大范围任务按现有 rigor 门禁升级）包含设计、评审、实现、宿主比较和独立 verifier。两次开发回合没有源码变化就停止，恢复不重置修订预算。

```sh
python plugins/openas/workflows/reconstruct.py run --project /path/to/new-reconstruction --resume
# 仅在已核对、仍属于授权范围的输入变化后使用
python plugins/openas/workflows/reconstruct.py run --project /path/to/new-reconstruction --resume --restart-stages
```

`check` 可独立运行可信观察器，并创建工作区的 `reconstruction-results/`。首次 `run` 会将属于同一研究的已有检查结果保留到 `check-history/`，为运行器准备干净产物目录；不删除旧证据。完整执行中会自动检查。完成运行后可重新 check 查看当前差异，或用新的研究目录做新任务。收据保留在 `workspace/reconstruction-results/comparison.json`，总体交付报告为 `run/report.html`。

## 数据契约

Brief `version=1` 包含 goal、target、authorization、mode、scope、collector argv、collector_files、observations、cases 与可选 unknowns。每条观测包括 id、kind、confidence、summary、limitations；`value` 可提供有界 JSON 数据。所有观测都标注为 provided-artifact，不将用户提供的 observed 标签当成宿主已经访问过原软件。

类型：clean-room 允许 `visible-ui/screenshot/behavior-run/user-brief`，deep 额外允许 `source/binary/network`。deep 不自动扩大宿主权限或允许复制资源。每个 case 必须引用至少一个非 inferred 观测。

行为 case 的 `kind=behavior`，以 expected 指定完整 JSON 值。Collector stdout 必须是 `{"cases":{"case-id":{"value":123,"context":{}}}}`；布尔值不会等同于数字 1，列表顺序和对象字段都会核对。无对应 case、上下文不一致或 collector 退出非零均失败。

截图 case 使用 `kind=screenshot`、reference（brief 旁的相对文件路径）、viewport `[width,height]`、context（如 `{"state":"menu-open","width":1440}`）、max_mean_error `[0,1]` 和 evidence ID。Collector 在 `workspace/reconstruction-results/` 产生截图，并返回 `{"cases":{"desktop":{"path":"reconstruction-results/desktop.png","context":{...}}}}`。脚本比较相同尺寸的 RGB 平均绝对像素误差；需要已安装 Pillow，不自动安装。不支持掩膜、自动对齐、OCR 或感知相似度，不以视觉接近代替按钮行为验收。分别声明 desktop/tablet/mobile 和关键状态，缺一个就不能全部通过。

## 未知项与分页

高/关键未知会阻断昂贵的构建和宿主比较；低/中未知会保留在 show 的交接摘要中，不能宣称已验证。Resolve 需要当前 revision、具体理由和非 inferred 观测 ID：

```sh
python plugins/openas/workflows/reconstruct.py resolve --project /path/to/project --question U1 --revision 1 --reason "已在授权交互记录中确认" --evidence empty
```

旧 revision、无依据的解除和修改 sealed 问题定义会失败。新增观测或改变目标需要新研究记录。`browse --section observations/cases/questions --offset/--limit` 限制返回量；返回的 coverage 只计算已存条目，不是目标功能覆盖率。

## English quick reference

Use prepare/show/browse for local study, run for standard OpenAS build/review/check/refine, and run --resume for explicit recovery. Actual capture requires authorized host tools. A trusted pinned observer executes the candidate; comparisons cover only declared cases. Collectors run as trusted host code; modes are ingestion/prompt rules, not OS isolation. Keep unknowns and captured text separate from instructions. Screenshot checks require optional Pillow and measure only RGB error. See the bilingual [skill](../SKILL.en.md) for the full workflow.

# Office 方法来源 / Office method provenance

Reviewed: 2026-10-28. Upstream: deepseek-ai/deepseek-harness at `f3803c96974ad4a94195fb97e5c637e9c2a3afe3`.

| OpenAS skill | Pinned upstream | Source SHA-256 |
| --- | --- | --- |
| office | [packages/skill/skill-office/assets/office/SKILL.md](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/skill/skill-office/assets/office/SKILL.md) | `d5b9c95af707c95ca5d2d92cd7af21d04811dd8e88b99518947bdde11f2d9885` |
| office-docx | [packages/skill/skill-office/assets/office-docx/SKILL.md](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/skill/skill-office/assets/office-docx/SKILL.md) | `e549651654c9aa7dfcb46cd9b9c6e44b6433f48581eb903c75dff1688f41c818` |
| office-xlsx | [packages/skill/skill-office/assets/office-xlsx/SKILL.md](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/skill/skill-office/assets/office-xlsx/SKILL.md) | `5b16d47b06d0b545c99c72f25ba6bd7063843adf2d487b1b0aee5b1f0d6db80e` |
| office-render | [packages/skill/skill-office/assets/office-render/SKILL.md](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/skill/skill-office/assets/office-render/SKILL.md) | `7ad77f63958bc5e69b1d5b2ebd2dac36eeaa4737563f72c7a941c2e22bfd551c` |
| office-export-pdf | [packages/skill/skill-office/assets/office-export-pdf/SKILL.md](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/skill/skill-office/assets/office-export-pdf/SKILL.md) | `f474f6e2daa61875f4a1e346a83bf566e934ef9469de7b04ca2d137b66630723` |
| office-recalculate | [packages/skill/skill-office/assets/office-recalculate/SKILL.md](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/skill/skill-office/assets/office-recalculate/SKILL.md) | `acc3729600af3660348944f0145f36359d60dabd349660947d6740d73feaceaf` |

## 中文

采用上述工作流的方法分工并重新编写双语技能，保留 DeepSeek 的 [MIT 许可与版权声明](licenses/deepseek-harness-MIT.txt)。格式编写、图像渲染、PDF 导出与公式缓存刷新分开；PPTX 继续复用 OpenAS 已有 presentation-creation。

采用的方法包括：DOCX 定点 runs 编辑、XLSX 公式和缓存区分、DataFrame 与完整工作簿区分、格式修改后的实际重开核对、按请求选择视觉检查，以及保留源文件。未复制上游脚本、sidecar、依赖包、字体或图片，也不移植其专属工具、安装规则、固定状态句或一旦空白便禁止所有后续检查的项目政策。

共用 office_ops.py 为 OpenAS 独立实现，使用现有本地 LibreOffice/Poppler 和可选 Python 库。输出新目录、临时输入副本、独立 profile、进程组超时清理、有限操作报告及保守的公式缓存检查适配本仓库。其 PDF 页渲染不提供 DSH sidecar 的 worksheet/range 等能力；不宣称原生 Office 保真或安全处理任意不可信文档。

Python 库和系统工具通过用户环境使用，不随本插件再分发，依赖按各自许可使用。该来源记录不替代实际验证，尤其不代表存在可用渲染/重算引擎。

## English

The workflows were adapted into bilingual skills with DeepSeek's [MIT copyright/license notice](licenses/deepseek-harness-MIT.txt) retained. Format authoring, image rendering, PDF export, and formula-cache refresh are separate; PPTX reuses OpenAS presentation-creation.

Adopted methods include targeted DOCX run editing, XLSX formulas versus caches, DataFrames versus workbooks, reopening saved artifacts, request-driven visual review, and source preservation. No upstream scripts, sidecars, dependency packages, fonts, or images were copied. DSH-specific tools, installation policies, fixed status sentences, and its blanket post-blank-preview inspection ban were not ported.

OpenAS independently implements office_ops.py using installed local LibreOffice/Poppler and optional Python libraries: fresh outputs, staged source copies, isolated profiles, process-group timeout cleanup, scoped reports, and conservative cache checks. PDF-page rendering does not implement sidecar worksheet/range features or establish native Office fidelity or safe handling of arbitrary untrusted documents.

Dependencies are used from the user's environment under their own terms, not redistributed in this plugin. Provenance does not replace actual validation or establish an available rendering/recalculation engine.

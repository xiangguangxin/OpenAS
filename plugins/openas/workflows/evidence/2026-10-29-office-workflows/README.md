# Office 工作流验证 / Office workflow validation

真实客户端样例执行于 2026-10-28，记录整理于 2026-10-29。使用 Codex CLI 0.160.0、现有登录与模型配置，在独立合成工作区提供完整 55 项技能目录，要求读取相关 SKILL.md。可选 Python 库仅安装在临时 venv，未安装系统 Office 工具。[receipt.json](receipt.json) 保存请求、返回、宿主检查及原生命令观察。

| Case | Primary skill | Observed outcome |
| --- | --- | --- |
| DOCX + XLSX 创建 | office → office-docx / office-xlsx | 实际文件生成、重开与公式/数值核对通过 |
| 定点 DOCX 编辑，不要渲染 | office-docx | 原稿不变，bold 与相邻 italic 保留 |
| PDF-only 导出，缺少引擎 | office-export-pdf | 正确报告缺失，未造假 PDF 或图片 |
| 重算，缺少引擎 | office-recalculate | 正确报告未刷新，保留公式，未以常量替代 |
| PDF 页面渲染 | office-render | 客户端在执行前遇到 provider 429，不计通过 |
| 普通 Markdown 文字草稿 | project-documentation | 未创建 Office 产物 |

调用沿用 evaluate_skills.py 的 schema 和完整技能路径/frontmatter 目录，通过 stdin 传入任务。命令形态为 `codex exec --ephemeral --skip-git-repo-check --color never --json --sandbox workspace-write -C <fixture> --output-schema <schema> -o <result> -`。每例宿主超时 180 秒，不覆盖模型或审批配置，编排器未重试。模型客户端内部的 provider 重试最终收到 429，相关案例保留为阻断。

宿主核对真实 DOCX/XLSX 结构、指定公式和值、相邻 run 格式、原文件指纹，以及仅在 outputs/ 范围创建请求产物。其余案例检查没有伪造或未请求的文件。原生命令事件确认已执行案例实际读取相关技能，返回内容另经实现会话审阅。没有声称独立人工验收。

新增 test_office_workflows.py 的实际库测试覆盖可运行编写示例、公式和缓存区分、公式变常量拒绝、缓存错误和空字符串、源文件保护，以及清空旧缓存后“不计算只复制”不能通过。转换/图像/引擎管线测试使用模拟进程结果，只验证调度和检查边界；超时测试终止并等待真实子进程。它们不证明 LibreOffice 或 Poppler 在本环境已成功运行。

本环境缺少 LibreOffice/Poppler，实际 PDF 导出、页面图像、公式引擎重算及视觉检查仍未执行；样例中的“缺工具处理通过”不是转换成功。源文件和产物均为合成数据。原始客户端日志和临时环境不随插件发布，路径用占位符归一化。

## English

Five real-client single-run synthetic cases completed; the PDF rendering case was blocked before execution by provider 429. The cases used Codex CLI 0.160.0, existing authentication/model configuration, the full 55-skill catalog, isolated workspaces and a temporary Python environment. No system Office tools were installed. The receipt preserves requests/results, host artifact/scope checks and observed skill reads.

Actual DOCX/XLSX creation and targeted DOCX edits were reopened and verified. Missing-engine cases preserved inputs and produced no fake PDF, images or formula caches. Ordinary Markdown stayed outside Office tooling. Unit tests cover artifact semantics, stale-cache invalidation, failure handling and owned-process timeout cleanup; simulated converter/renderer results are not real engine acceptance.

LibreOffice/Poppler were unavailable. Actual PDF conversion, page rendering, engine recalculation, visual review, native Office fidelity and native Claude discovery remain unverified. Raw logs and environments are not distributed; published paths are normalized placeholders.

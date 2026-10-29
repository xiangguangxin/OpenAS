# PDF 提取技能验证 / PDF extraction validation

2026-10-29，Codex CLI 0.160.0，沿用既有认证和模型配置，完整 56 项技能目录；每例为独立合成工作区和 ephemeral workspace-write 会话，宿主超时 180 秒。依赖复用临时 Office Python 环境，没有安装系统工具或 OCR。[receipt.json](receipt.json) 记录原始试验、修订与最终观察。

| Final case | Expected / observed | Host checks |
| --- | --- | --- |
| 第 3、2、1 页提取 TXT/JSON | pdf-extraction | 真实执行脚本，页序/文字/源指纹正确，图像页 no_text，统一报告存在，无 OCR 或源修改 |
| 只渲染 PDF 页，缺少引擎 | office-render | 未误用提取技能，未创建文字文件或伪造图像，源文件不变 |

合成 PDF 由 tests/test_pdf_extraction.py 的 make_pdf 构造，含 Alpha report 文字页、只有图像的页、Gamma result 文字页和真正空白页。选页不是印刷页码。宿主独立解析实际输出并核对内容，原生命令事件确认客户端读取技能并调用 [提取脚本](../../../skills/pdf-extraction/scripts/extract_pdf.py)。返回内容另经实现会话核对，不称为独立人工验收。

首轮客户端自行重写循环：请求的 TXT/JSON 内容正确，但漏掉统一 extraction-report.json，原评测器因缺文件未完成回执。保留该结果后，补充“能力已覆盖时直接复用脚本”的窄范围说明，并在新工作区进行同一请求的前向验证；最终实际调用脚本且全部宿主检查通过。没有把首轮改写成通过或把这一例推广为整体准确率提高。

15 项 PDF 单测使用真实 PDF，覆盖页码/范围、源保护、TXT/JSON、layout、图像和空白、既有隐藏文字层、损坏流的部分失败、加密与密码文件、CLI 状态及中断报告。没有依赖 LibreOffice/Poppler。真实 OCR、表格还原、复杂字形/阅读顺序、原生 Claude 发现和图片渲染未验收。

原始客户端日志、临时环境和密码文件不随插件发布，发布记录路径已归一化。客户端出现的模型目录刷新诊断没有阻止最终任务完成。

## English

Two final single-run synthetic cases completed under Codex CLI 0.160.0 with existing authentication/model settings, the full 56-skill catalog, isolated ephemeral workspaces and a 180-second host timeout. Actual extraction retained requested page order/text/hash provenance, marked image-only text as absent without OCR, and invoked the helper. A rendering-only negative case stayed with office-render and produced no fake text/images when no renderer was available.

The initial trial produced correct requested text but rebuilt the extraction loop and omitted the common report, so its evaluator did not complete. That observation remains in the receipt. A narrow instruction correction clarified helper reuse, followed by a new-workspace forward trial that invoked the script and passed host checks. This is not general accuracy or performance proof.

Fifteen PDF tests cover real text/blank/image/hidden-layer PDFs, partial parser failures, selection, encryption, output protection, CLI behavior and interruption. No real OCR, table reconstruction, complex reading-order/glyph guarantee, native Claude discovery or successful image rendering was established. Raw logs/environments/password files are not distributed; paths are normalized.

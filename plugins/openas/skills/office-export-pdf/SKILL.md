---
name: office-export-pdf
description: "将已保存的 DOCX、XLSX 或 PPTX 导出为新的 PDF，保留源文件；PDF 导出不自动要求页面图片或视觉审查。 / Export saved DOCX, XLSX, or PPTX to a new PDF while preserving sources; PDF-only export does not require image rendering."
---

中文 | [English](SKILL.en.md)

语言 / Language: 用户指定语言优先，否则跟随任务语言；保留已有文档语言和机器字段。Honor explicit language preferences; preserve existing document language and machine-readable fields. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# Office 导出 PDF

确认用户需要 PDF 而非可编辑源稿、页面图片或公式缓存刷新。使用最终保存的文档，保留源文件；默认写入新文件或新输出目录。沿用项目/宿主已配置的导出工具，或用 [共用操作脚本](../office/references/operations.md) 的 export-pdf；本地路径不在 PATH 时可显式指定 soffice。

脚本使用临时输入副本和独立 LibreOffice profile，避免覆盖原稿或接入用户已有 Office 会话。默认不改页边距、打印区域、横竖方向或缩放；电子表格 PDF 遵循已有打印设置。缺少引擎或转换失败时保留可用源稿与已生成诊断，不用改扩展名、空文件或另画图片冒充导出。

核对命令退出状态、预期非空 PDF 和 %PDF- 标识。脚本只承诺这些检查；需要文本/页数核对时用已有 PDF 解析工具，说明实际范围。单纯导出 PDF 不要求生成预览图片、安装额外渲染器或加载所有 Office 技能。用户还要求图片或视觉检查时另用 [office-render](../office-render/SKILL.md)。

交付实际 PDF；只有用户同时需要时才附源稿或临时记录。说明当前导出器可能与 Word/Excel/PowerPoint 的字体和分页不同，不把导出成功称为视觉通过、原生 Office 保真或公式重算完成。[来源与许可](../../references/dsh-office-provenance.md)。

---
name: office-docx
description: "创建、读取或定点编辑 Word DOCX，保留相关文字格式并核对保存结果；不将普通替换冒充修订跟踪。 / Create, read, or edit Word DOCX files while preserving relevant formatting and validating saved content; ordinary edits are not tracked changes."
---

中文 | [English](SKILL.en.md)

语言 / Language: 用户指定语言优先，否则跟随任务语言；保留已有文档语言和机器字段。Honor explicit language preferences; preserve existing document language and machine-readable fields. See [语言约定 / language policy](../../references/language.md).

# Word DOCX

先确认新建、读取、定点修改还是模板改版，检查实际文档中相关段落、表格、样式与用户要求保留的内容。优先沿用项目工具；常规任务可用 python-docx，环境要求见 [Office 操作指南](../office/references/operations.md)。只需读取或提供大纲时不创建未请求的文件。

默认保存新文件。文字替换先定位实际文本及 runs；给整个 paragraph.text 赋值会重建 runs，不能以此保留局部字体、链接或强调。跨 runs 的目标需在相关 runs 范围内处理并复核格式，不重建整份文档来替换一句话。标题可能是普通段落，不只根据 Heading 样式或属性查找。

新文档使用段落样式组织标题和正文，表格宽度考虑当前节、合并单元格及页边距。中日韩字体可能需要 eastAsia 字体设置；字体名存在不代表已安装或实际渲染正确。常见创建示例按需读 [编写示例](references/authoring.md)。

普通编辑不默认解包 ZIP 或扫描无关元数据；只有目标不明确、功能不受库支持或具体失败时再检查相关 OOXML。涉及真实修订、批注、域、复杂嵌入对象或保真模板时明确工具支持，保留原稿和相关包部件，不把彩色文字或普通替换称为修订跟踪。

保存后用 python-docx 重开，核对目标文字、段落/表格及应保持的内容和格式。内容修改附带基础样式不自动触发额外渲染；布局、颜色、字号、间距、对齐是主任务或要求视觉检查时，使用 [office-render](../office-render/SKILL.md)，除非用户跳过。python-docx 不分页或渲染，结构检查不能证明没有换行溢出。要 PDF 时另用 [office-export-pdf](../office-export-pdf/SKILL.md)。

交付实际 DOCX 和已检查范围；缺少渲染器或原生 Word 验收时明确未验证，不因此伪造预览或覆盖原稿。[来源与许可](../../references/dsh-office-provenance.md)。

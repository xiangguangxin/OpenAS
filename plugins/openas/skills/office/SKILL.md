---
name: office
description: "按产物和操作选择 DOCX、XLSX、现有 PPTX 制作、图像渲染、PDF 导出或公式重算；用于多格式 Office 任务分流，不把普通项目 Markdown 当作 Office 文档。 / Route Office tasks by format and operation: DOCX, XLSX, PPTX authoring, image rendering, PDF export, or formula recalculation."
---

中文 | [English](SKILL.en.md)

语言 / Language: 用户指定语言优先，否则跟随任务语言；保留已有文档语言和机器字段。Honor explicit language preferences; preserve existing document language and machine-readable fields. See [语言约定 / language policy](../../references/language.md).

# Office 任务路由

先区分用户要创建/编辑什么，以及是否另需图像、PDF 或刷新计算结果。沿用已有授权与工具，不为清晰请求重复采访，也不因能导出就增加未请求的产物。

| 目标 | 使用的技能 |
| --- | --- |
| 创建、读取或修改 Word .docx | [office-docx](../office-docx/SKILL.md) |
| 创建、读取或修改 Excel .xlsx | [office-xlsx](../office-xlsx/SKILL.md) |
| PPTX 内容组织、创建或编辑 | 复用 [presentation-creation](../presentation-creation/SKILL.md)，不另造 PPT 入口 |
| 导出页面图片或检查视觉布局 | [office-render](../office-render/SKILL.md) |
| 将已保存的 Office 文件导出 PDF | [office-export-pdf](../office-export-pdf/SKILL.md) |
| 用真实引擎刷新 XLSX 公式缓存 | [office-recalculate](../office-recalculate/SKILL.md) |

独立导出、渲染或重算只需加载对应操作技能，不必先加载所有格式技能。已加载的说明直接复用；宿主没有 skill 工具时读取实际文件，不虚构注册能力。纯 Markdown 项目文档用 project-documentation，不加载 Office 工具链。

格式技能负责可编辑内容和结构，操作技能负责指定的转换。普通文字或数值修改、附带加粗表头不自动要求渲染；主任务是布局、颜色、对齐或视觉检查时使用 office-render，用户明确跳过则尊重。现有 presentation-creation 对新演示稿的渲染验收要求继续适用。

使用项目指定或已有 Python/Office 环境，不依赖 DSH 的专属 load_workspace_dependencies、present 或 sidecar。可选 Python 依赖记录在 [requirements.txt](requirements.txt)，共用脚本与实际能力见 [操作指南](references/operations.md)。缺少工具时完成可交付部分，明确阻断的操作，不默认安装系统软件、上传文件或切换付费服务。

写入任务工作区，默认生成新文件并保留原稿；输出、缓存和检查记录不进入技能目录。交付用户请求的实际文件及简短验证说明，不默认交付临时预览。能创建/重开文件、成功转换和已目视检查是不同结论。[来源与许可](../../references/dsh-office-provenance.md)。

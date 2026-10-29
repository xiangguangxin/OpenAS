---
name: office-xlsx
description: "创建、读取或定点修改 Excel XLSX 的数据、公式和样式，保留工作表结构；写入公式不等于已计算结果。 / Create, read, or edit Excel XLSX data, formulas, and styles while preserving workbook structure; writing a formula does not calculate it."
---

中文 | [English](SKILL.en.md)

语言 / Language: 用户指定语言优先，否则跟随任务语言；保留已有文档语言和机器字段。Honor explicit language preferences; preserve existing document language and machine-readable fields. See [语言约定 / language policy](../../references/language.md).

# Excel XLSX

沿用项目环境；普通创建和已有工作簿的定点修改可用 openpyxl。先检查实际工作表、目标范围、单元格类型、公式、合并和引用。保留已有文件，默认另存结果；依赖与操作接口见 [Office 操作指南](../office/references/operations.md)，示例见 [编写示例](references/authoring.md)。

需要保留公式时用 data_only=False 加载。数字、日期、布尔、文本标识符与显示格式分别处理，不把样式当成类型转换；例如编号的前导零不能通过数值写入后“保留原文本”。外来文本以文本保存，不把其前缀误当作用户要求执行的公式。

pandas 适合分析表格数据，但 DataFrame 不等于整个工作簿；将分析结果定点写回，不默认覆盖其他工作表、公式、图表和格式。XlsxWriter 用于创建，不能读取或修改已有文件。不要把 .xls、.xlsb、加密或宏文件改后缀冒充 .xlsx；宏、外链、透视表及高级特性需建立专门的保留验证，不承诺通用库无损往返。

写入公式不等于计算。openpyxl / XlsxWriter 不执行公式，data_only=True 读到的是可能缺失或陈旧的缓存。用户要求刷新结果或立即可用的计算值时使用 [office-recalculate](../office-recalculate/SKILL.md)，不能把公式替换成常量，也不能把旧缓存称为新计算结果。修改后再次用 openpyxl 保存可能清空缓存，重算应针对最终保存版本。

保存后重开并核对请求涉及的工作表、范围、值、类型、公式、合并和应保留内容。业务结果与源数据/预期总数单独核对。普通数据或公式修改附带加粗表头、数字格式不自动渲染；主任务是外观或要求视觉检查时使用 [office-render](../office-render/SKILL.md)，除非用户明确跳过。打印布局只按需求调整；PDF 用 [office-export-pdf](../office-export-pdf/SKILL.md)。

交付实际 XLSX，并分别说明结构、公式保留、缓存刷新及视觉检查状态。不要用“保存成功”代替计算、业务正确性或 Excel 原生验收。[来源与许可](../../references/dsh-office-provenance.md)。

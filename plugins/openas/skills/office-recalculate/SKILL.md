---
name: office-recalculate
description: "使用真实表格引擎刷新 XLSX 公式缓存，核对公式保留与计算结果；不以手填常量、旧缓存或 PDF 转换代替重算。 / Refresh XLSX formula caches with a real spreadsheet engine and verify formulas and results; constants, stale caches, and PDF export are not recalculation."
---

中文 | [English](SKILL.en.md)

语言 / Language: 用户指定语言优先，否则跟随任务语言；保留已有文档语言和机器字段。Honor explicit language preferences; preserve existing document language and machine-readable fields. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# XLSX 公式重算

用于需要刷新缓存或立即读取计算值的请求，不要求普通数据/公式编辑一律重算。先保存最终公式与输入，保留原始工作簿。使用实际支持目标函数的 Excel/LibreOffice 或宿主引擎；没有引擎时说明缓存未刷新，不用 Python eval、自写部分公式计算器或手填常量代替。

[共用操作脚本](../office/references/operations.md) 的 recalculate 用隔离 LibreOffice profile 将临时副本重新保存为新的 XLSX。引擎执行前以 openpyxl 清空副本旧缓存并设自动完整计算，防止仅复制旧值冒充刷新；该暂存往返也不承诺高级特性保真。支持本地普通工作簿，拒绝宏、外部数据连接/链接及已识别的外部数据公式；不支持数组/数据表公式的保留验收。复杂函数、动态数组、插件、实时数据或特定 Excel 兼容要求交给合适的真实引擎，不默认刷新外部来源。

对结果分别用 openpyxl data_only=False 和 data_only=True 重开：前者核对原公式和位置，后者检查缓存、错误值及用户指定的结果/总数。脚本检查公式映射未改变、缓存非缺失、没有公式错误；计算为空字符串的缓存与缺失缓存区分。公式错误或丢失、缺缓存会保留产物和失败报告，不称重算通过。

缓存存在不等于业务正确。核对用户要求的结果、相关输入、工作表、样式及其他需保持的特性；LibreOffice 往返可能改变高级特性或原生表现。重算后不要再用会丢弃缓存的保存步骤覆盖结果；若修改，针对最终版本重新计算。

交付保留公式的新工作簿、引擎与检查范围。需要图像或 PDF 时分别使用 [office-render](../office-render/SKILL.md) / [office-export-pdf](../office-export-pdf/SKILL.md)。源文件未被写入、公式仍存在、缓存已更新和业务结果正确分别报告。[来源与许可](../../references/dsh-office-provenance.md)。

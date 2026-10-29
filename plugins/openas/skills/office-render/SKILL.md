---
name: office-render
description: "将已保存的 DOCX、XLSX、PPTX 或 PDF 渲染为页面图片，支持指定 PDF 页并检查视觉布局；不把成功导出视为视觉验收。 / Render saved DOCX, XLSX, PPTX, or PDF to page images and inspect layout; conversion success is not visual acceptance."
---

中文 | [English](SKILL.en.md)

语言 / Language: 用户指定语言优先，否则跟随任务语言；保留已有文档语言和机器字段。Honor explicit language preferences; preserve existing document language and machine-readable fields. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 页面图像与视觉检查

使用最终保存的文档和实际渲染器生成图像，不按源数据另画“预览”。优先复用项目或宿主已有工具；共用 [操作脚本](../office/references/operations.md) 支持本地 LibreOffice → PDF → Poppler PNG，已有 PDF 可直接渲染，不需要 LibreOffice。它不依赖 DSH sidecar，也不自动安装替代工具或上传文件。

区分用户请求的图像导出和检查用临时图像。给当前版本创建独立新输出目录；文档未变时复用已有渲染，不重复转换排障。DOCX/PPTX/PDF 的 pages 是一基 PDF 页号；XLSX 按现有打印布局导出，PDF 页号不是工作表编号，脚本不提供单元格范围渲染。精确工作表范围需要实际支持的宿主工具；不要悄悄修改打印区域或缩放以伪造该能力。

主任务是外观时检查实际受影响的页面、区域、图表和标签；要求整份文档评审时覆盖全部所需页面。检查中文/字体、换行和裁切、对齐、表格宽度、图表刻度和数字格式。成功命令、PNG 文件存在或读取图片本身不等于视觉通过，脚本的 visual_review 默认 not_run。

用当前会话真实图像读取能力查看图片。没有该能力仍可交付用户请求的图像，视觉检查保持未完成；不切换模型、猜测文字几何或重复读取同一空白图。对本应有内容的页面若出现空白/损坏结果，保留源稿与诊断，停止盲目重试，说明本次检查未完成。真实缺陷修复后才重新生成对应版本并检查。

交付请求的图片和检查摘要；仅供检查的临时输出不默认交付，删除后不链接。现有 PPT 生成器的逐页渲染验收仍适用。渲染不刷新源 XLSX 缓存，不证明媒体/动画、原生 Office 排版或无障碍验收。[来源与许可](../../references/dsh-office-provenance.md)。

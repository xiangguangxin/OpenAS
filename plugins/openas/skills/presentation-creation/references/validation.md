# 验证与交付

本文件由 OpenAS 于 2026-10-24 根据来源工作流重新组织；具体改动和许可见 [NOTICE](../NOTICE.md)。

## 1. 内容与对象检查

对照 JSON 和实际 PPTX 检查：页面顺序、标题、数据、单位、来源、备注与时间预算。图表的每组数值与源数据一致，表格无缺行缺列，图片为原始可信资产；演示性数据不作为业务结论。

```bash
python3 /path/to/skill/scripts/inspect_deck.py /path/to/deck.pptx \
  --output /path/to/new-structure-report.json
```

检查工具只使用标准库，解析实际 slide 关系、文字、原生图表/表格和顶层几何，检测越界与内容框重叠；decor: 前缀表示本生成器有意放在文字下的装饰形状，不参与内容重叠判定。不要通过改名字规避真实问题。

输出 passed 仅表示所检查的结构/几何未发现错误。占位文本提示为 warning，需要结合语境核对；分组、旋转对象、文字真实溢出、字体替换、母版和阅读顺序等仍需额外检查。不能将无结构错误写成全部视觉或客户端验收通过。

## 2. 通过真实应用渲染

需要本地 LibreOffice（soffice 或 libreoffice）与 Poppler 的 pdftoppm，Python 环境需含 Pillow。脚本不会安装这些系统工具，也不上传客户文件。工具不可用时提供源稿和实际 PPTX，并标记渲染与视觉检查未执行。

```bash
/path/to/venv/bin/python /path/to/skill/scripts/render_deck.py /path/to/deck.pptx \
  --output-dir /path/to/new-preview-directory
```

不在 PATH 的已安装工具可通过 `--soffice /path/to/soffice --pdftoppm /path/to/pdftoppm` 指定。输出目录必须不存在。渲染使用独立临时 LibreOffice profile，超时会终止本次进程；失败保留日志，不循环重装或换用收费网络转换。

输出含实际导出的 PDF、pages/slide-N.png、montage.png 和 render-report.json。渲染报告初始 human_visual_review 为 not_run，完成导出不代表 AI 已查看页面。不能将按源稿另画的预览伪装成原 PPTX 的渲染结果。

## 3. 逐页检查并留证据

先查看 montage，再查看每张实际 PNG，检查中文与标点、字体、标题换行、正文边界、图表轴标签、表格密度、图片比例、对齐与对比度。发现问题要改 JSON/实现、重新生成并渲染对应版本，不能只改预览图。

报告至少包含：源稿/PPTX 指纹、结构结果、实际渲染器及版本、检查的页码、发现和修复、最终限制。对未实际看过的页面不写已通过；没有发现缺陷时如实记录。确认内容和视觉后，仍需区分 PowerPoint 原生编辑/放映、投影设备、字体替换和无障碍检查是否执行。

## 4. 交付范围

交付 .pptx、JSON/源代码、重建所需资产、预览/可选备份 PDF 和检查摘要。既有项目遵循本次允许的文件范围；不要带入虚拟环境、工具下载包、完整聊天、凭据或无关日志。引用和个人信息仅使用实际提供或核实的内容。

本技能附带的示例只能证明其对应布局与数据，不证明任意品牌模板或所有 Office 版本兼容。退出码：生成器 0 表示生成且几何检查通过，1 表示结构检查发现问题，2 表示输入/环境/输出错误；inspect 为 0/1/2；render 为 0 表示渲染完成、2 表示失败，均不能代替内容与人工视觉结论。

# 来源、改动与许可

Copyright 2026 OpenAS contributors.

本技能是根据已审查公开方法独立组织的新工作流，不是将多个 SKILL.md 原样拼接。2026-10-24 对来源方法进行了中文重述、合并、删减与目标环境适配。SKILL.md、references 和本目录独立编写的 Python 代码按 [Apache-2.0](LICENSE) 提供；来源的适用版权和许可随包保留，仓库根目录的 MIT 不替代这些条款。

| 来源 | 固定提交 | 保留的方法 | 保留的许可 |
| --- | --- | --- | --- |
| MiniMax-AI/skills，pptx-generator | `60aaae52bb2af8162732751a4332f62a5fef518b` | 共享主题、页面用途、布局变化与内容检查 | Copyright (c) 2026 MiniMax；[MIT](licenses/MiniMax-MIT.txt) |
| K-Dense-AI/scientific-agent-skills，scientific-slides | `593377bb048752abb0152deab9fbb1083a6087df` | 受众和时长、叙事、定量来源、备注与逐页复核 | Copyright (c) 2025 K-Dense Inc.；[MIT](licenses/K-Dense-MIT.txt) |
| openai/skills，历史 slides | `e6afb0d74cc75d220df2faf3dd6c635c2dc6a108` | 原生可编辑对象、可重建源文件、几何检查和真实渲染 | [上游 Apache-2.0 原文](licenses/OpenAI-slides-Apache-2.0.txt)，保留其中 Microsoft Corporation 版权声明 |

源文件链接、规范化 UTF-8 内容指纹、选用与不选用的方法见 [FUSION_SOURCES.json](FUSION_SOURCES.json)。指纹记录将 CRLF 换行规范化为 LF；法律文本仅规范化换行和末尾换行，未修改授权条款。

选用 OpenAI 的已核实历史提交，不声称其路径在当前 main 中仍可用。该提交的 slides 目录未列出独立 NOTICE 文件；本包保留随目录提供的 LICENSE.txt。未复制其 helpers、脚本、资产或特定运行路径，也未保留“只能用 PptxGenJS”的工具约束。

MiniMax 中强制固定页码坐标、全局 npm 安装、自动分派及强制修复循环未被继承。K-Dense 中依赖收费图像 API、整页图片为默认输出、固定论文数量和额外技能的要求未被继承；本包不调用其网络脚本。生成器仅依赖公开 python-pptx API 与少量本地 OOXML 字体设置，代码为 OpenAS 独立实现。

Anthropic 的 pptx 目录在核对提交中具有专有条款，不参与融合，未复制其技能内容、脚本或资产。搜索结果中已失效的路径也未用作来源。

本包不含第三方字体或图片。客户材料及图像仍遵循其各自授权；使用本技能不改变材料或生成器依赖的许可证。外部依赖通过 requirements.txt 单独安装，不在插件中分发其运行时。

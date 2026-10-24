# 源稿、环境与生成

本文件是 OpenAS 于 2026-10-24 编写的融合适配，来源和条款见 [NOTICE](../NOTICE.md)。

## 环境

生成需要 Python 3.10+ 和 [requirements.txt](../requirements.txt) 中的 python-pptx、Pillow 及其固定依赖。安装前按目标项目的环境约定执行；以下命令在本次任务工作目录和隔离虚拟环境中运行，路径替换为实际位置：

```bash
python3 /path/to/skill/scripts/build_deck.py --check-environment
python3 -m venv /path/to/task-workspace/.venv-slides
/path/to/task-workspace/.venv-slides/bin/python -m pip install -r /path/to/skill/requirements.txt
```

Windows 原生环境使用对应虚拟环境 `Scripts/python.exe`；WSL 与 Windows 的依赖和路径不同。检查不安装依赖、不请求凭据、不访问网络；报告字体需要在目标环境核对。生成器不调用 LLM API，文案提炼由当前宿主完成；这不表示宿主模型能够离线运行。

字体按客户环境配置。默认 Latin 为 Arial、CJK 为 Microsoft YaHei，不表示这些字体已安装；Linux 可按实际环境改为合适的开源字体。字体缺失可能发生替换，只有实际渲染与目标客户端才能确认效果。不得将本机字体文件直接打包分发。

## JSON 源稿

参考完整的 [8 页示例](../assets/example-deck.json)。顶层字段：

| 字段 | 含义 |
| --- | --- |
| version | 固定为整数 1 |
| title、audience | 演示名称、可选的受众/页眉标签；不知道作者时不编造姓名 |
| duration_minutes | 可选，总讲述预算上限；每页 seconds 合计不能超过它，真实节奏仍需排练 |
| size | wide（默认 16:9）或 standard（4:3） |
| theme | background、foreground、accent、surface、muted 为六位十六进制；font、cjk_font 为已选字体 |
| slides | 1–100 页，按最终讲述顺序排列 |

每页都有 type、title、notes、seconds，可选 sources。seconds 为 1–600 的整数，notes 写实际讲稿而不是逐字重复页面。sources 为短注/来源字符串列表，最多 12 项；第一页短注显示于页脚，完整列表进入备注，较长链接可作为后续来源项。

| type | 额外字段 | 生成结果 |
| --- | --- | --- |
| cover / section | 可选 subtitle | 原生标题与副标题，深色主题页 |
| bullets / closing | bullets：1–6 项 | 原生正文与视觉标记 |
| two-column | left、right 各含 heading 和 1–5 项 bullets | 双栏对比 |
| process | steps：2–4 项，每项 label、detail | 原生流程卡片 |
| chart | categories：1–10 类；series：1–4 组 name / values；unit；sources；可选 chart_type（column / line） | 原生图表与嵌入工作簿 |
| table | columns：1–5 列；rows：1–6 行；sources | 原生可编辑表格 |
| image | image、alt | 插入原始本地图片，保持比例并记录说明 |

非 cover / section 页面可加 caption。未支持的字段会报错，不能通过填入 template、animation 等字段暗示生成器已支持它们。图表 values 必须是有限数，数量匹配 categories，单位和来源必填；示例数值必须在可见 caption 中说明。

图像路径相对于 assets-root（默认 JSON 所在目录），不得指向其外部；支持 Pillow 能读取且适合插入 PPTX 的 PNG/JPEG 等图像。SVG、EMF、PDF 先使用项目已有工具转换并确认内容，不能仅修改扩展名。图像保留为图像对象，不宣称其中的数据或文字可编辑。

## 生成与内容密度

```bash
/path/to/venv/bin/python /path/to/skill/scripts/build_deck.py \
  --spec /path/to/task-workspace/deck.json \
  --assets-root /path/to/task-workspace/assets \
  --output /path/to/task-workspace/deck.pptx
```

未使用图像时可省略 assets-root。输出必须是新的 .pptx 文件；存在时停止并保留原文件，修订请使用新的任务内文件名。脚本只解析 JSON，不把源稿当代码执行。

当前布局针对简洁汇报：标题约 32pt、正文约 22–25pt、表格约 19pt，页脚更小。文本预算以中英文字符宽度和行数做保守估计，过密时要求缩短或拆页，不自动缩成小字。该估计不能取代真实字体度量或逐页视觉检查。复杂学术图、大型表格和特殊品牌模板应另选合适的布局实现，不强塞进有限布局。

生成的图表包含嵌入工作簿，表格包含原生单元格；这些结构可解析不等于目标 PowerPoint 已完成编辑验收。演讲备注含讲稿、预算和完整来源。保留 JSON、必要图片及使用的生成器版本以重新生成；不承诺 ZIP 二进制逐字节相同。

## 与已有文稿和模板协作

读取已有文稿时先提取文字、对象和备注并实际渲染；保留原文件。已有模板或复杂对象优先在支持它们的原生应用/工具中编辑；本生成器没有 template 导入或任意版式复制接口。使用其他库编辑时核对原有格式与功能是否保留，不把丢失动画、母版或嵌入对象的结果称为无损。

公开 API 参考：[python-pptx 入门](https://python-pptx.readthedocs.io/en/latest/user/quickstart.html)、[原生图表](https://python-pptx.readthedocs.io/en/latest/user/charts.html)。这些是实现资料，不能代替当前环境的实际验证。

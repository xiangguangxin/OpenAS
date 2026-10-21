# 工具选择与本地执行

## 推荐组合

| 需求 | 首选 | 可维护源 | 独立产物 |
|---|---|---|---|
| API 调用、任务交接 | Mermaid sequenceDiagram | .md 代码块或 .mmd | 按需 SVG |
| 状态转移 | Mermaid stateDiagram-v2 | .md 或 .mmd | 按需 SVG |
| 指针、记录或报文字段 | 原生 SVG | .svg | SVG 本身 |
| 系统架构、多节点关系 | Mermaid；有 D2 时可选 D2 | .mmd/.d2 | SVG |
| 手动拖动布局 | tldraw / FigJam 等画布 | 工具的原生文件 | 依据实际工具能力导出 |

## 先检查依赖

```bash
command -v mmdc
command -v d2
command -v rsvg-convert
command -v inkscape
```

工具不存在时可直接生成 SVG，不自动安装全局 npm 包或修改系统环境。用户要求搭建渲染环境时，选择项目本地、可记录版本的安装方式；在线插件需要实际确认连接和导出能力。

## 可用工具的命令示例

下面只在对应程序存在时使用；文件路径带空格需加引号。

```bash
mmdc -i diagram.mmd -o diagram.svg
d2 diagram.d2 diagram.svg
rsvg-convert -o /tmp/diagram-preview.png diagram.svg
inkscape diagram.svg --export-type=png --export-filename=/tmp/diagram-preview.png
```

Mermaid CLI 可能还需要浏览器运行环境；导出失败就报告实际错误，不凭空声称生成成功。先渲染到临时目录检查，再将确认后的文件放进文档目录。

## 方案来源与边界

- Mermaid 官方：[使用与 SVG 渲染](https://mermaid.js.org/config/usage)、[CLI](https://github.com/mermaid-js/mermaid-cli)。
- D2 官方：[导出格式](https://d2lang.com/tour/exports/)、[命令行](https://d2lang.com/tour/man/)。
- SVG 可直接用 XML 文本维护，不需要额外插件。
- tldraw/FigJam 是外部画布选项，不是本技能依赖；本仓库放置 skill 不等于自动安装插件，也不表示 Codex 已自动发现 .claude 的技能。

## 不同 Agent 的使用

本技能属于 OpenAS 插件，Claude Code 通过 `/openas:technical-diagrams` 发现和调用；工具与模板相对此技能目录定位。其他客户端可显式读取 SKILL.md，不能宣称 Claude 插件清单会自动启用 Codex 技能。

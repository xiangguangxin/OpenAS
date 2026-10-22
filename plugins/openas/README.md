# OpenAS 插件资源

入口清单位于 [.claude-plugin/plugin.json](.claude-plugin/plugin.json)。从任意项目用 `claude --plugin-dir /absolute/path/to/this-directory` 加载本目录；开发时保存后在会话内 `/reload-plugins`。安装、卸载和验证命令见仓库 README。

资源以本目录为根，与使用项目的 `.claude` 无关：

- [agents](agents)：cto、red-team、tech-writer、developer、it、verifier；Claude 原生角色使用 `openas:` 命名空间。
- [skills](skills)：31 个可按需使用的技能，含技术调研、方案选型、文档、竞品、路线图、四象限 Debug、绘图和项目记忆。
- [团队契约](references/team-contract.md)：需求、范围、角色交接、证据和失败回环。
- [项目适配](references/project-context.md)：按目标仓库选择技术栈、运行命令、领域约束和验收。
- [工作流](workflows/README.md)：可选 Codex 执行入口；JS 模板需要宿主。
- [记忆](memory/README.md)：运行数据位于使用项目的 `.openas/memory/`。

不附带自动执行的 hooks、MCP 服务或后台监听进程。读取技能不等于安装工具或授予执行目标的权限。不预设项目语言、框架、业务或目录；新项目沿用自己的构建、复现与验收命令。默认工作流示例为独立分页工具，历史报告不作为新项目知识。

# 插件架构与加载边界

OpenAS 仓库目前只分发一个原生插件 `openas`。顶层 marketplace 描述去哪找它，插件目录中的 manifest 描述它的身份；宿主负责发现 Skills、注册 Agents、启停及热加载。没有另造一个与客户端竞争的插件注册中心或常驻进程。

```text
OpenAS/.claude-plugin/marketplace.json
                 │ source: ./plugins/openas
                 ▼
     plugins/openas/.claude-plugin/plugin.json
                 │
        ┌────────┼───────────┐
        ▼        ▼           ▼
      skills/  agents/    workflows/（可选 Codex 适配器）
        │        │           │
        └─── references/ ────┘
                 │ 明确指定 consumer project
                 ▼
       使用项目/.openas/memory/
```

## 资源与状态

插件包含可版本化的提示、技能、参考资料、资源模板和可选脚本。资源间引用用插件内相对路径；Python 适配器从自身文件位置寻找角色、项目适配约定及记忆模块，不依赖使用项目的目录布局。

项目状态只属于使用项目。记忆 CLI 要求 `--root`，Codex 适配器提供 `--project-root`；插件目录以及其中的子目录不能成为记忆目标。插件删除后用户知识仍保留；不会把其他项目的 records.json 注入新项目。跨项目共享知识需明确审查和迁移，不通过全局单例隐式实现。

角色共用 [项目适配约定](../plugins/openas/references/project-context.md)，从目标仓库发现技术栈与验收，不增加固定项目配置格式。Codex 适配器将约定全文和完整任务传给每个角色；Claude 角色通过团队契约读取它，JS 宿主模板同时携带适配指引。Python、Node 是 OpenAS 脚本各自的运行依赖，不是使用项目必须采用的开发语言。

## 生命周期

- 本地开发：`--plugin-dir` 加载指定插件目录，修改后会话内 `/reload-plugins` 应用。是否自动发现保存变化、缓存提示及可热加载的组件，以实际客户端为准。
- 持久使用：marketplace → install → enable/disable/uninstall → reload。客户端缓存的插件应走版本更新流程，不能假设改了仓库就已替换缓存。
- 正在执行的调用不保证切换到新代码；热加载适用于后续调用。没有后台服务，因此没有自建进程需要在卸载时终止。
- 本地快照应先运行结构/链接检查再 reload。失败时检查客户端插件错误面板，修复磁盘版本后重新 reload，或通过 Git 恢复已知版本；没有实现客户端版本回滚控制器。

## 客户端差异

Claude Code 原生消费 plugin.json 和 `openas:` 名称。Codex 不消费该 manifest；其可选 Python 适配器显式读取同一组资源，再调用已安装的 Codex CLI。JS 编排脚本仍需要能注入 agent/args/log 的宿主。

同一团队原则不等于相同执行器：结构测试、模拟宿主测试、真实模型调用及原生 Claude 加载结果分开报告。REA 所需 MCP/分析工具为可选接入，不作为本插件的自动安装步骤。

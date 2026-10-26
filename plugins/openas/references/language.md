# 中英文输出约定 / Chinese and English output policy

## 中文

OpenAS 的中文和英文共用同一套技能 ID、角色、命令和执行路线，无需安装两份插件。

- 用户明确指定的回复或交付语言优先；也可以分别指定“用中文解释、产出英文文档”。
- 未指定时，面向用户的说明跟随当前任务请求的语言，不由技能说明、日志、源码或引用材料的语言决定。混合请求优先遵循明确偏好；没有偏好时沿用会话已确认语言，否则采用请求主体的语言。
- 编辑已有文档、注释或界面文案时，保留目标文件及项目原有语言，除非用户要求翻译。新文件遵循用户指定语言或项目约定；没有约定时跟随任务语言。翻译不改变技术含义、授权范围、验收或证据状态。
- 技能 ID、角色 ID、命令、路径、API 名称、JSON 字段、枚举值和原始日志保持原样。结构化输出中的自然语言说明可翻译，但 schema、`verdict` 等机器读取值不得翻译。
- 交接保留用户的语言偏好和每个交付物的语言。英文任务可以读取中文资料，中文任务也可以读取英文资料；资料语言不改变回复语言。

中文技能入口为 `skills/<id>/SKILL.md`，配套英文说明为同目录 `SKILL.en.md`；英文角色说明位于 `references/en/agents/`。配套文件不注册新的角色或技能。按需要读取语言版本，不必同时加载两份。

第三方 REA 的入口原本为英文，保留上游文件及许可；中文使用说明见 [REA 集成](../integrations/rea/README.md)。详细技术参考、历史验收和第三方资料保留原文，不承诺所有归档材料都有译本。

## English

Chinese and English share the same skill IDs, roles, commands, and routes. Install the plugin once.

- An explicit user choice of response or artifact language takes priority. Users may request Chinese explanations with English deliverables, or the reverse.
- Otherwise, use the language of the current task for user-facing explanations, not the language of skill instructions, code, logs, or quoted material. For mixed-language requests, honor an explicit preference, then an established conversation preference, otherwise the main request language.
- Preserve the language of existing documents, comments, and UI copy unless translation is requested. New artifacts follow the requested language or project convention, falling back to the task language. Translation must preserve technical meaning, scope, acceptance, and evidence status.
- Keep skill/role IDs, commands, paths, API names, JSON keys, enum values, and raw logs unchanged. Translate natural-language explanations inside structured output, while preserving its schema and machine-readable values such as `verdict`.
- Carry response and artifact language preferences through handoffs. Reading Chinese sources for an English task, or English sources for a Chinese task, does not change the requested output language.

Chinese skill entry points remain `skills/<id>/SKILL.md`; English companions are `SKILL.en.md` in the same directory. English role instructions live in `references/en/agents/`. These companions do not register additional skills or roles. Read the appropriate edition as needed, rather than loading both.

REA already has an upstream English entry point, retained with its licensing; a Chinese integration guide remains available. Detailed technical references, historical evidence, and third-party material retain their original languages; not every archived document has a translation.

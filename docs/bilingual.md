# 中英文支持 / Chinese and English support

[English entry](../README.md#english) | [中文入口](../README.md#chinese)

## 中文

仓库根目录使用单一 README，英文在前，通过 English / 简体中文链接跳转到对应章节。GitHub Markdown 不隐藏另一语言的内容；同一页面保留两种语言。子目录插件与工作流指南继续保留配套译本。

同一份插件提供 47 个技能和 12 个角色，不按语言重复注册。明确指定的输出语言优先，否则跟随任务语言；已有文件保留原语言，除非要求翻译。结构化字段、枚举、命令和标识符不翻译。完整规则见 [语言约定](../plugins/openas/references/language.md)。

| 内容 | 中文 | 英文 |
| --- | --- | --- |
| 仓库入口（同一文件，英文优先） | README.md#chinese | README.md#english |
| 技能 | 原 SKILL.md | 同目录 SKILL.en.md（46 份）及上游英文 REA |
| 角色 | agents 下的原定义 | references/en/agents 下的 12 份说明 |
| 协作、项目适配、设计就绪 | references 下的原文件 | 同目录 .en.md |
| 插件与工作流指南 | README.md | README.en.md |
| 完整英文技能索引 | 中文技能地图见 README | docs/skills.en.md |
| 详细技术参考、历史验收、第三方材料 | 保留原文 | 不保证全部提供译本 |

英文技能配套文件和英文角色说明不作为额外组件发现。REA 是上游英文资源，保留其原文、许可和来源；中文用户可以使用现有集成指引。英文说明应保留原有约束和证据要求，不因翻译简化授权、将未验证改成已验证或增加独立执行流程。

### 维护翻译

修改技能或角色时同步检查两种语言的触发范围、步骤、交付、授权和失败行为。版本与来源变化、支持范围、未验证项也要一致。双方说明可以使用不同自然表达，但不能改变行为语义。对应文件保留切换链接。

`plugins/openas/references/translations.json` 记录 63 对插件内文件及双方 SHA-256。`scripts/check_plugin.py` 会检查配套覆盖、路径、技能 ID 和指纹。新增或删除自有技能时必须同时更新配套说明、英文索引和注册表。不能通过只刷新指纹掩盖未审查翻译。

完成语义核对后，已有配对可用以下命令更新指纹（不会新增缺失译本）：

```bash
python3 - <<'PY'
import hashlib
import json
from pathlib import Path
root = Path('plugins/openas')
p = root / 'references/translations.json'
data = json.loads(p.read_text())
for entry in data['entries']:
    for key in ('source', 'target'):
        entry[key + '_sha256'] = hashlib.sha256((root / entry[key]).read_bytes()).hexdigest()
p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
PY
python3 scripts/check_plugin.py
```

结构和指纹检查只能证明文件配对完整且经过记录，不能证明翻译正确、模型遵循语言要求或客户端实际加载成功。

### 可选语言行为评测

新增四个场景：`english-analysis`、`chinese-analysis`、`explicit-english`、`explicit-chinese`，分别验证英文/中文任务及反向显式语言覆盖。它们共用只读源码分析 fixture，检查 skill 路由、文件不变、无额外确认、证据和摘要语言信号。

```bash
python3 scripts/evaluate_skills.py --case english-analysis --output /tmp/openas-lang-en
python3 scripts/evaluate_skills.py --case chinese-analysis --output /tmp/openas-lang-zh
python3 scripts/evaluate_skills.py --case explicit-english --output /tmp/openas-lang-override-en
python3 scripts/evaluate_skills.py --case explicit-chinese --output /tmp/openas-lang-override-zh
```

命令需要已登录客户端，消耗真实模型额度；输出目录必须不存在。普通 CI 只模拟评测器，不运行模型。语言门禁只检查 summary 的中英文字符信号，不证明整份报告的语言、语义和证据质量；仍须人工核对原任务、输出与未修改文件。实际 Claude 加载、热加载和特定客户端行为另行验证。

## English

One installation provides the same 47 skills and 12 roles in both languages. Explicit language preferences override the task language; existing files retain their language unless translation is requested. Keep schemas, enum values, commands and identifiers stable. See the [language policy](../plugins/openas/references/language.md).

The repository uses one README with English first and clickable English/Chinese section links. The English edition covers the repository README, complete skill catalog, all skill entry instructions (46 new companions plus upstream English REA), 12 role descriptions, team/project/readiness references, plugin guide and workflow guide. Detailed references, historical evidence and third-party documents retain original languages and are not all translated. Companion files do not register duplicate components; vendored REA and its licensing remain unchanged.

When editing shared behavior, compare triggers, procedures, deliverables, authorization, failure handling, versions, applicability and evidence limits in both editions. Different wording is acceptable; changed behavior is not. Preserve language-switch links. The 63 plugin-local pairs in `references/translations.json` record source and target hashes. Structural validation checks coverage, paths, skill IDs and drift. Review meaning before updating hashes using the command above; it does not create missing translations. New/removed skills also require companion/catalog/registry updates.

Fingerprint checks establish recorded file consistency, not translation quality or real-client execution. The four optional evaluation commands above test implicit Chinese/English output and explicit opposite-language overrides on a read-only source-analysis fixture. They inspect routing, unchanged files, question policy, evidence and a basic summary-language signal. The detector is not a semantic language validator and may reject legitimate mixed-language quotations. Review actual prose and source grounding manually.

Real-client evaluations require existing authentication, consume quota and use new output directories; ordinary CI only tests the evaluator with mocks. Native Claude discovery/reload and target-client behavior require separate validation. No successful real-client bilingual run is implied by adding fixtures or passing unit tests.

# 任务复盘、经验审查与项目技能演进

本功能分四阶段实现：自动采集复盘 → 提炼与独立审查 → 生成和验证候选技能 → 记录效果、停用和回滚。它复用项目记忆的证据校验，不训练模型参数，也不修改插件自带技能、角色、CLAUDE.md 或权限。

需要 Python 3.10+、Linux/WSL。模型提炼、评审和试用还需要已登录且支持现有工作流参数的 Codex CLI，并消耗客户端额度。当前自动接入的是 Python 单任务运行器；JS 模板、图运行器和普通聊天没有后台学习进程。

## 第一阶段：自动复盘采集

单任务运行器启用记忆时，任务结束自动生成成功或失败的观察记录，包括状态、失败类别、检查退出码、恢复次数及输入/输出快照摘要。不会将原始日志、完整聊天、任务正文或失败消息直接存入观察记录。相同观察重复采集不重复入库。

```bash
# 从 OpenAS 仓库根目录运行；所有路径替换为实际路径。
python3 plugins/openas/workflows/codex-team.py \
  --task /path/to/task.json \
  --workspace /path/to/task-worktree \
  --output /path/to/private-run-output \
  --project-root /path/to/consumer-project \
  --learn
```

`--learn` 在任务完成后额外执行只读的模型提炼与独立评审，并为通过的经验生成技能草稿。省略该参数只采集机器观察，不额外调用模型。`--no-memory` 关闭记忆、复盘采集及项目技能复用，不能与 `--learn` 同时使用。

项目记忆必须位于任务 workspace 之外，模型学习的 output 必须位于整个 consumer-project 之外；建议使用独立任务工作树和单独的私有运行目录。两者重叠时，现有范围保护会禁用记忆；显式要求 `--learn` 则在运行前报错。

超时、中断、范围越界、客户端/环境错误或无效输出只采集观察，不继续调用模型。其他业务失败可复盘，但失败退出码只证明执行失败，不能直接证明原因。学习过程出错记录 `learning_warning`，保留任务本身的验收状态；不会把学习失败改写为任务通过，也不会撤销已完成的候选。

运行器将本次任务和最近阶段结果作为临时模型上下文，私有 prompt/result/log 留在 output；长期记忆只接收筛选后的候选。观察和人工提供的 JSON 不是不可伪造的证明，必须来自可信任务。

已有可信任务记录也可单独采集：

```bash
python3 plugins/openas/skills/project-memory/scripts/learning.py \
  --root /path/to/consumer-project capture /path/to/private-run-output/state.json
```

输出的 `id` 是观察标识，可在已有登录的客户端中单独触发提炼：

```bash
python3 plugins/openas/workflows/learning_cycle.py \
  --root /path/to/consumer-project --output /path/to/new-private-reflection \
  reflect OBSERVATION_ID
```

## 第二阶段：经验提炼与独立审查

候选经验具有明确的 `key`、`scope`、`statement`、`trigger`、`cause`、`procedure`、`validation`、`limitations`、`tags`、`author`、`observation_ids` 和 `evidence`。原因未确认时明确标为假设，不将“重试后成功”泛化为修复方法。

- 程序校验必需字段、长度、项目内证据和来源指纹，并拒绝明显的 token、私钥等凭据模式。模式检查不能保证发现所有敏感信息，语义评审仍需检查。
- 完全相同的候选幂等；关键词集合相似度达到阈值的同 scope 候选标记 `similar`，供评审判断，不宣称语义去重。
- 同 key/scope 存在已接受经验时标记 `conflict`，不覆盖；需核对并退役旧项后才能接受新项。
- 作者和评审者标识必须不同。自动模式使用两个独立、短期、只读客户端会话；评审必须核对原始来源，而不是只接受作者总结。
- 通过评审的经验写入现有 records.json；完整步骤和适用边界放入关联证据收据。证据或显式关联来源改变时，后续检索排除旧记录。

自动评审检查：`supported`（有证据）、`scoped`（边界明确）、`reusable`（值得复用）、`no_secrets`（无敏感内容）、`conflicts_resolved`（冲突已处理）。全部为 true 才能批准。不同标识和模型会话不等于已认证的人员身份，记录仍需信任调用方。

人工或其他宿主也可以提供候选 JSON 和评审 JSON：

```bash
python3 plugins/openas/skills/project-memory/scripts/learning.py --root /path/to/consumer-project propose /path/to/proposal.json
python3 plugins/openas/skills/project-memory/scripts/learning.py --root /path/to/consumer-project review LESSON_ID /path/to/review.json
python3 plugins/openas/skills/project-memory/scripts/learning.py --root /path/to/consumer-project retire OLD_LESSON_ID --reason '来源变更，已核对替代经验'
```

`evidence` 通过现有 `Memory.evidence()` 从实际项目文件生成，格式见 [项目记忆说明](README.md)。评审 JSON 示例：

```json
{
  "verdict": "approve",
  "reviewer": "actual-independent-reviewer",
  "reason": "已核对原始来源及复现结果，结论仅适用于声明范围",
  "checks": {
    "supported": true,
    "scoped": true,
    "reusable": true,
    "no_secrets": true,
    "conflicts_resolved": true
  }
}
```

这是字段示例，不能直接用作实际审查证明；未满足时使用 reject 并写明原因。

## 第三阶段：生成候选技能、试用与启用

自动学习会从通过评审的经验生成项目内的版本化 `SKILL.md`，包含触发条件、前提、步骤、验证及适用边界。至少一条已接受经验即可生成草稿；是否足够成熟由后续试用和语义评审判断，不按次数自动认定正确。

也可将多个同 scope 的已接受经验合成一个技能：

```bash
python3 plugins/openas/skills/project-memory/scripts/learning.py \
  --root /path/to/consumer-project draft diagnose-average-input \
  --lessons LESSON_ID_1 LESSON_ID_2 --author actual-author
```

草稿保存在 `.openas/memory/learning/skills/名称/版本ID/SKILL.md`。生成时不注册为客户端原生技能；步骤是已审查经验的 Markdown 组合，不自动生成或执行任意脚本。

每个候选必须先试用，再独立审查。试用定义由可信项目维护者提供，不能从未经审查的技能内容中自动提取执行命令：

```json
{
  "cases": [
    {
      "fixture": "learning-fixture",
      "task": "Diagnose the average empty-input behavior from the local contract. Explain the expected result.",
      "expected_applicable": true,
      "checks": [["python3", "-B", "validate_response.py", "yes"]]
    },
    {
      "fixture": "learning-fixture",
      "task": "Assess an unrelated CSS color change. Do not apply average-input guidance.",
      "expected_applicable": false,
      "checks": [["python3", "-B", "validate_response.py", "no"]]
    }
  ]
}
```

可复制随包的 [试用 fixture](../workflows/examples/learning-fixture) 到客户项目的 `learning-fixture/`，参考 [试用定义](../workflows/examples/learning-trial.json)。示例针对 average 输入诊断技能，其他技能需编写匹配自身行为的测试，不能用这套示例证明任意技能有效。

```bash
python3 plugins/openas/workflows/learning_cycle.py \
  --root /path/to/consumer-project --output /path/to/new-private-trial \
  trial SKILL_VERSION_ID /path/to/trial-spec.json

python3 plugins/openas/workflows/learning_cycle.py \
  --root /path/to/consumer-project --output /path/to/new-private-skill-review \
  review-skill SKILL_VERSION_ID --activate
```

试用在临时 fixture 副本中调用真实只读客户端，检查适用性、文件保持不变，并执行可信 argv 检查。检查脚本通过 `OPENAS_TRIAL_RESULT` 读取实际响应、通过 `OPENAS_SKILL_FILE` 读取候选原文。`checks` 以宿主权限执行，必须来自可信定义；临时副本不是操作系统隔离。

试用至少覆盖一个正例和一个不应触发的反例，结果绑定技能内容指纹、原始 fixture、定义与响应。随后独立评审核对 `supported`、`scoped`、`no_secrets`、`positive_case`、`negative_case`、`behavior_checked`。只通过简单退出码而没有有意义的行为断言应拒绝。当前试用面向只读诊断和流程指导，不能证明写代码、部署或其他副作用正确；此类技能还需对应项目的行为评测。

`--activate` 表示评审通过后写入项目激活注册表。省略时保持已批准但未启用。也可通过 learning.py 的 `evaluate ID 项目相对报告路径`、`review-skill ID 评审JSON`、`activate ID --reason 原因` 接入可信外部评测；外部报告必须含 exact skill_sha256、正反 cases、检查退出码和来源列表，不可自称已运行真实客户端。

## 第四阶段：使用评估、停用和回滚

下一次单任务运行开始时，运行器按关键词检索最多三个有效的已启用技能，将其作为可适用的指导放入角色上下文，并保存实际版本。未启用、已退役、证据过期、技能被改写或试用收据变化的版本不会复用。普通 Claude 插件会话可由 project-memory 技能运行 `context 查询词` 读取；不会自动创建 `.claude/skills` 或修改客户端配置。

任务结束后自动关联送入上下文的技能版本与任务结果。`inspect` 显示任务成功数、未分类任务数、正负使用反馈和审计历史；reviewed 等非实现验收状态不计作失败。送入上下文不证明模型实际采用，任务成功也不证明技能产生收益；需要具体反馈和对照评测才能判断因果。

```bash
python3 plugins/openas/skills/project-memory/scripts/learning.py --root /path/to/consumer-project inspect
python3 plugins/openas/skills/project-memory/scripts/learning.py --root /path/to/consumer-project context 'average empty input'
python3 plugins/openas/skills/project-memory/scripts/learning.py --root /path/to/consumer-project outcome SKILL_VERSION_ID OBSERVATION_ID --useful no
python3 plugins/openas/skills/project-memory/scripts/learning.py --root /path/to/consumer-project disable SKILL_VERSION_ID --reason '实际任务出现回归，先停用排查'
python3 plugins/openas/skills/project-memory/scripts/learning.py --root /path/to/consumer-project rollback OLD_SKILL_VERSION_ID --reason '回到已验证版本'
```

同一版本/观察重复登记不增加样本数，后来补充的 useful 反馈可更新并留审计。最近连续三次观察为任务失败或负反馈时自动暂停该版本，停止后续复用；这是保守的止损条件，不把任务失败直接归因于技能。重新启用暂停版本需要新的试用证据和独立审查。

新版本启用时保留旧版本和历史。rollback 仅允许回到曾启用且当前仍满足证据、试用与审查条件的版本；不会恢复已经过期的旧经验，不自动回滚业务代码。

## 存储、退出码与验证范围

原有 records.json 保持 version=1；演进状态单独保存在 `.openas/memory/learning/state.json`，也为 version=1，包含 observations、lessons、skills、active、outcomes 和 audit。证据收据、技能版本、试用定义和响应位于同目录的子目录。长期记录是否入 Git 由客户决定；输出日志、锁和检查点不应直接分发。

状态写入使用 POSIX 锁和原子替换；经验库与演进状态是两个文件，异常后应检查两边记录，候选/证据/注册表不一致时不会启用技能。来源指纹证明内容一致，不能证明语义正确或评审者身份。

learning.py 操作成功退出 0，输入或证据错误退出 2。learning_cycle.py 试用失败或技能审查拒绝退出 1，环境/格式错误退出 2；reflect 成功处理候选时退出 0，即使候选全部被拒绝，具体状态见输出报告。

自动测试覆盖状态机、隔离、证据失效、冲突、去重、真实检查子进程、模型输出校验、运行器接入和回滚；测试中模型调用使用模拟响应，不等于真实账号、模型质量或客户端原生技能加载验收。真实模型试用应按上面的命令在目标环境执行。

已有一次独立临时项目的 [真实客户端验收记录](../workflows/evidence/2026-10-24-learning/README.md)，覆盖提炼、独立审查、候选生成、正反试用和启用；其范围限于该最小案例。

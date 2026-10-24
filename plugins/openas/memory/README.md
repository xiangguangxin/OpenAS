# 项目记忆：插件资源与项目状态分离

## 路径约定

本目录只提供使用说明，不随插件分发 records.json。每个使用项目独立保存：

| 项目中的文件 | 用途 |
|---|---|
| `.openas/memory/records.json` | 事实、设计决定、经验及审计历史 |
| `.openas/memory/evidence/*.json` | 精简运行收据或语义评审回执 |
| `.openas/memory/current-task.json` | 最新任务状态、文件范围和需求哈希；不自动恢复 |
| `.openas/memory/.lock` | POSIX 并发写入锁，不应提交 |

卸载或更新插件不操作上述目录；各项目自行决定知识记录是否入 Git。建议忽略锁文件和检查点，不默认删除已有知识。不要把插件目录作为使用项目；插件可处于只读安装缓存。

Python 记忆脚本必须传 `--root`，不会从脚本安装路径推断项目：

```bash
python3 /path/to/OpenAS/plugins/openas/skills/project-memory/scripts/project_memory.py \
  --root /path/to/consumer-project query 'harness verifier 证据'
python3 /path/to/OpenAS/plugins/openas/skills/project-memory/scripts/project_memory.py \
  --root /path/to/consumer-project inspect
```

## 有证据的生命周期

- fact：观测到的项目事实；decision：已发生且有依据的设计选择；lesson：有适用边界的经验。
- 每项含 key、scope、kind、statement、tags、evidence。通过 propose 创建 candidate，语义审查后 review approve 才成为 accepted。
- 相同内容及证据复用 ID；同 key/scope 的已接受项存在时，新项成为 conflict，不覆盖。核对后 retire 旧项，再评审新项；reject/retire 都保留原因。
- query 只检索 accepted 且证据有效的记录，最多 5 项、约 5000 字符。关键词检索不保证召回全部相关知识，不是向量数据库。
- evidence 包括项目内文件相对路径、SHA-256、JSON pointer 及对应值。路径不允许越出项目。源文件整体改变或缺失，旧记录自动排除；不静默更新指纹。

证据示例（指纹和 value 必须从实际文件生成）：

```json
{
  "path": "debug-proof.json",
  "sha256": "实际文件的 SHA-256",
  "pointer": "/result",
  "value": "实际 JSON 值"
}
```

非 JSON 来源应先核对并保存证据收据，然后显式关联原始文件：

```python
evidence = memory.evidence('debug-proof.json', '/result', sources=['src/example.py', 'README.md'])
```

该方法会在 evidence 中增加 `sources`，每项包含项目内相对路径和真实 SHA-256。提议、审查和查询时同时核对收据及所有原始文件；任一内容改变、文件缺失或路径越界都会拒绝或排除记录。
旧证据没有 `sources` 时只校验直接 JSON 文件，不能自动追踪收据正文中任意命名的来源字段。需要此能力的旧经验应重新构造证据、提议和审查。
指纹只能证明文件内容一致，不能证明经验正确或评审者身份。

## 提议、审查与采集

`propose proposal.json` 接受上述字段，可用 Python API `Memory.evidence(path,pointer)` 构造 evidence。下面的命令均需加脚本路径与 `--root`：

```text
review RECORD_ID --verdict approve --reviewer 实际评审标识 --reason 有限结论为何成立
review RECORD_ID --verdict reject --reviewer 实际评审标识 --reason 拒绝原因
retire RECORD_ID --reason 退役原因
harvest /path/to/trusted-run/state.json
```

review 存储调用方声明的评审标识，不验证身份；没有实际语义核对时不能填 approve。harvest 只接受 done=true、status=verified 且 final_checks 全部退出 0 的记录，自动接受的仅是“这份记录记载通过”的有限事实。输入 JSON 必须来自可信任务记录，不能作为不可伪造的运行证明；重复采集不重复入库。

## Harness 接入与边界

Codex 适配器用 `--project-root /path/to/consumer-project` 指定记忆所属项目，`--no-memory` 关闭。默认 CLI project-root 为当前工作目录，执行时显式传入可避免混淆；直接 Python Runner 默认不启用记忆。为防污染插件自身，记忆目标不得位于插件目录中。

任务开始检索相关项并明确不是指令；每次状态写入同步短期检查点；verified 后自动采集有限机器事实。写入失败记录 memory_warning，不改写任务验收结论。若记忆目录在任务 workspace 内，为保持 scope 检查，当前实现跳过记忆读写；可用独立任务工作树和其外部的 project-root。

经验提炼可由 project-memory Skill 按任务执行，也可在单任务运行器中使用 `--learn`，自动执行提炼、独立评审并生成项目内候选技能。候选经过试用与技能评审后才能启用；运行结果、停用和回滚形成后续评估闭环。完整命令和四阶段边界见 [项目学习与技能演进](learning.md)。

没有后台观察器，不修改角色、模型参数或权限。文件写入采用 POSIX 锁和原子替换；短期检查点只保留最后写入者，尚无多任务看板。运行日志、core、认证信息与完整聊天不直接写长期记忆。

# 可验收任务切片 / Verifiable task slices

## 中文

优先按一条完整的用户行为切片。例如“导入预览不写入数据库，并展示无效行”，可跨 UI/API/数据校验/测试；单独“做前端”“做数据库”通常无法证明用户目标。每片覆盖实际需要的层，不为命名完整强加无关架构层。

为任务分配稳定 ID、需求/规格引用、目标与非目标、依赖、输入/产物、实际模块/允许修改路径及证明检查。文件路径服务于当前执行与所有权，Issue 标题与验收使用稳定领域词；路径变化时更新任务，不能因可能过时删掉执行范围。

阻塞只表示真正的开始条件。一个任务的状态标记为 done 之前核对交付物和证据；依赖失败时阻断消费者。跨会话恢复检查规格与代码版本，不重复执行已产生副作用的节点。Issue 发布、分配、评论和关闭仍按既有授权；仅规划时先交付本地草稿。

大范围机械重构用 expand–migrate–contract：先添加兼容形式，再按影响范围分批迁移消费者，最后在全部消费者迁移并通过检查后删除旧形式。每批保留可工作状态；确实不能独立集成时显式使用集成分支与最终组合验收，不能把中间失败叫作全程通过。

## English

Prefer a complete user-visible slice, such as import preview that leaves storage unchanged and displays invalid rows, spanning only the UI/API/validation/tests it actually needs. Layer-only tasks rarely demonstrate the user outcome; do not invent layers for completeness.

Give each task stable IDs, requirement/spec references, scope/exclusions, prerequisites, inputs/artifacts, actual modules/allowed paths, and proving checks. Current paths establish execution scope and ownership; titles/acceptance use stable domain vocabulary. Update paths when they change rather than omitting execution boundaries.

Block only on real start conditions. Inspect artifacts/evidence before accepting done. Failed prerequisites block consumers. Recheck code/spec versions on resume and reconcile existing effects before retrying. Remote issue publishing, assignment, comments, and closure require existing authorization; planning alone returns local drafts.

For broad mechanical refactors, expand with a compatible form, migrate consumers in bounded batches, then contract only after all consumers and checks pass. Keep batches operational. If independent integration is impossible, explicitly use an integration branch and final combined acceptance; do not claim green intermediate states.

## Task template / 任务模板

```text
ID / title:
Requirement/spec reference and version:
Behavior delivered / exclusions:
Blocked by / required upstream artifacts:
Modules and allowed paths / owner:
Outputs / compatibility and failure behavior:
Checks and expected outcomes:
Evidence / status / unresolved blockers:
```

Methods adapted from Matt Pocock's to-tickets; [attribution](../../../references/skill-methods/NOTICE.md).

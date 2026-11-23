# 深度安全审计 / Deep security audit

## 中文

仅在用户要求系统审计或范围确有需要时加载。普通局部评审沿用主技能。先记录对象版本（脏工作树需指纹）、授权路径、环境、预算和输出位置；只读对象保持只读，报告写入获准位置。使用[示例记录](audit-example.json)的结构，不导入上游执行器或扫描器。

1. **覆盖计划**：为相关入口×信任边界×攻击类别建立稳定 unit ID，记录范围、证据、状态。候选问题必须来自实际可达路径；通用最佳实践缺失不等于漏洞。未知、未检查、阻断与有证据检查分开。
2. **调查**：静态追踪低信任方控制的输入、跨越边界与可观察影响。根据任务限定预算和停止条件，不要求无限轮次。只有已授权且可隔离、可限定资源的本地实验才执行目标代码；使用合成数据，不因审计访问外部目标或真实用户数据。
3. **候选去重与复核**：用稳定 fingerprint 标识根因和边界；每项关联 coverage unit、源码位置、前提、证据、影响及最小修复。需要独立确认时由有独立上下文的评审者核对；未具备独立复核不能标记 confirmed。单人自检保留 needs_validation，不伪造身份或验证。
4. **确定性与严重度分开**：confirmed 需要当前证据、明确边界影响和独立复核；needs_validation 记录阻断与安全验证计划，不赋严重度；rejected 保存拒绝原因。严重度沿用团队契约，只赋给确认问题。来源中的 severity 不是任务运行器 verdict。
5. **报告与结束**：从统一记录生成说明，列出确认问题、待验证项、拒绝项和覆盖缺口。所有 coverage unit 为 checked 或明确 out_of_scope 才能标记覆盖完成；checked 仅代表记录的有限检查，不是系统安全证明。仍有 planned/blocked 单元时 run_status 为 incomplete 并说明原因。发现待验证项不妨碍完成一次明确限定的覆盖，但报告必须保留验证缺口。

复用旧记录时重新核对相关代码、配置和证据；相同 SHA 或旧拒绝不能替代当前检查。变更过的根因重新调查；保留历史。

运行只读结构检查：

```bash
python /path/to/OpenAS/plugins/openas/skills/security-review/scripts/check_audit.py audit.json
```

检查器验证记录关系、状态与必需字段，不执行审计、不证明证据真实，也不生成报告或提供 OS 隔离能力。不能把它的通过当作安全验收通过。

## English

Load only for an explicitly requested systemic audit or a scope that warrants it; local reviews retain the main skill. Record source identity (including dirty-worktree hashes), authorized paths, environment, budget, and allowed report location. Keep the target read-only. Use the [example record](audit-example.json); no upstream runtime/scanner is imported.

1. **Coverage:** assign stable unit IDs to relevant entry/boundary/attack-class combinations, with scope, evidence, and status. Candidates require reachable paths, not generic best-practice deviations. Distinguish unknown, unexamined, blocked, and evidenced checks.
2. **Investigation:** trace lower-trust control, boundary crossing, and observable impact. Bound work and stopping by the task budget. Execute target code only in authorized, isolated, resource-bounded local experiments with synthetic data; audit scope does not authorize external targets or real user data.
3. **Deduplication/validation:** fingerprint root cause and boundary; link each record to coverage, source, prerequisites, evidence, impact, and minimal fixes. Independent confirmation requires a reviewer with independent context. Without it, use needs_validation; self-review does not create independence.
4. **Certainty/severity:** confirmed requires current evidence, concrete boundary impact, and independent verification. needs_validation carries a blocker and safe validation plan, without severity. rejected retains its reason. Confirmed severity follows the team contract and is separate from runtime verdicts.
5. **Reporting/termination:** derive reports from the canonical records, retaining confirmed, unresolved, rejected, and coverage gaps. Complete coverage requires each unit checked or explicitly out_of_scope. Checked means only the bounded recorded examination, not system safety. Planned/blocked units require incomplete status and a reason. A bounded coverage pass may finish with unresolved candidates, but must disclose their validation gaps.

Recheck current code/configuration/evidence before carrying prior records; matching SHAs or old rejection are insufficient. Investigate changed roots again and retain history.

Run the read-only checker using the command above. It checks field/relationship consistency, not evidence authenticity, audit execution, report generation, or OS isolation. A structurally valid record is not security acceptance.

Adapted methodology: [Cloudflare attribution](../../../references/skill-methods/NOTICE.md).

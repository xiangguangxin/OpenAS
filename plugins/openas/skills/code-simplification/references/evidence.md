# 简化的证据与取舍 / Simplification evidence and tradeoffs

## 中文

这些是判断示例，不是待删除清单；使用目标项目中的真实位置和契约。

| 候选 | 应追踪的证据 | 决定边界 |
| --- | --- | --- |
| “没有调用”的扩展接口 | 包导出、插件清单、动态装载、外部扩展文档与实际消费者 | 内部零引用不等于废弃；保留契约，或把兼容变化单独提出 |
| 复制的状态与缓存 | 唯一写入方、读取方、时序与失效路径 | 当前值可以派生时可能删除副本；历史快照不能由当前值替代 |
| 层层透传的配置 | CLI、默认值、覆盖顺序、提供者实际读取点 | 最终被覆盖需分辨设计意图与缺陷；不要只删除表面无效参数掩盖错误优先级 |
| 同一进程里的重复校验 | 输入来源、解析边界、后续拥有者、可变性 | 可移除已建立不变量后的重复检查；保留不可信输入边界的验证 |
| “重复”的开始/结束事件 | 恢复、审计、指标与其他持久消费者 | 不删除能区分未开始、运行中和中断的事实 |
| 新依赖替换自写代码 | 实际删除代码、适配层、平台/版本和传递依赖 | 比较完整维护成本，并验证截断、取消、边界输入等适配差异 |

一次候选记录可以是：位置与归属；生产到消费的证据路径；删除内容和剩余实现；保留行为与能力损失；最强反对理由；能区分成败的验证。不强制为局部清理新增设计文档。

实施场景按实际风险选择：正常和无效输入；manifest 动态加载；配置覆盖；取消与重复清理；旧数据或旧消费者兼容。只读调查可报告建议检查，不能把未执行的建议写成通过。

## English

These are decision examples, not a deletion inventory. Use actual project locations and contracts.

| Candidate | Evidence to trace | Decision boundary |
| --- | --- | --- |
| Extension interface with “no callers” | Exports, plugin manifests, dynamic loading, external extension docs, actual consumers | Zero internal references do not establish obsolescence; preserve the contract or propose compatibility changes separately |
| Copied state or cache | Authoritative writer, readers, observation timing, invalidation | A current value may be derived; historical snapshots cannot be replaced by today's state |
| Forwarded configuration | CLI, defaults, override ordering, actual provider reads | Distinguish intentional overrides from defects; deleting an apparently ineffective parameter must not hide wrong precedence |
| Repeated same-process validation | Input origin, parsing boundary, next owner, mutability | Remove checks after invariants are established where appropriate; retain validation at untrusted boundaries |
| “Duplicate” start/end events | Recovery, audit, metrics, other durable consumers | Preserve facts distinguishing not-started, running, and interrupted work |
| Dependency replacing handwritten code | Deleted implementation, adapter, platforms/versions, transitive dependencies | Compare full maintenance cost and exercise truncation, cancellation, and boundary mismatches |

A candidate record can name location/owner, producer-to-consumer evidence, removed and remaining machinery, retained behavior/capability loss, strongest objection, and discriminating validation. Local cleanup does not require a new design document.

Choose implementation checks by actual risk: normal/invalid inputs, manifest loading, configuration overrides, cancellation/repeated cleanup, or old data/consumer compatibility. A read-only survey may propose checks but cannot report unexecuted checks as passed.

# Agent experience：验证场景 / Evaluation scenarios

## 中文

按实际修改选择场景，不要求每次运行全部案例。

| 场景 | 要观察的结果 |
| --- | --- |
| 用户要求改工具描述或技能发现入口 | 找到相关定义和消费者，提出或实施限定范围的改动，保留参数、权限与失败语义 |
| 用户只要改普通产品按钮文案 | 使用产品交互或文案方法，不因出现“体验”就加载 Agent 接口设计流程 |
| 摘要只返回前几项并给出详情路径 | 明确截断；用实际读取入口取回遗漏的必要信息，不猜测全文 |
| 指令放到延迟参考资料 | 行动前仍能看见关键权限与验收；参考资料存在且能访问 |
| 首轮文本缩短，但后续反复搜索 | 报告调用和总上下文的代价，不把静态缩短宣称为整体优化 |

可用的最小 fixture：一个分页查询工具，schema 中的 `limit` 已有范围和默认值，工具描述却重复这些字段；结果只返回前两项和可读取的完整结果文件。比较改动前后是否仍能正确分页、识别截断、取回详情；用不存在的路径检查可见错误。不为文字调整扩大到工具实现。

比较时固定任务、工具集合、模型、宿主配置与输入数据。分别记录目录/系统提示、按需加载和后续请求；保留 usage 的实际口径、工具次数、重复读取、完成情况和违规情况。无 usage 时可比较 UTF-8 字节数，但必须标为文本体积，不换算成精确 token。没有前后对照就只报告当前观察。

## English

Select scenarios relevant to the change rather than running the entire table every time.

| Scenario | Observable outcome |
| --- | --- |
| Request changes a tool description or skill discovery entry | Locate definitions and consumers; propose or implement scoped changes preserving parameters, permissions, and failures |
| Request only changes an ordinary product button label | Use product interaction/copy methods without routing the word “experience” to Agent interface design |
| Summary returns only the first items plus a detail path | Identify truncation and retrieve necessary missing information through a real read operation instead of guessing |
| Instructions move into a deferred reference | Critical permissions and acceptance remain visible before action; the resource exists and is reachable |
| Shorter first-turn text causes repeated searches later | Report call and total-context costs rather than claiming an overall gain from static shortening |

A minimal fixture can use a paginated query tool whose schema already defines a `limit` range/default while its description repeats them. Results include two items and a readable full-result file. Compare pagination, truncation recognition, and detail retrieval before/after; check a visible failure with an unavailable path. Do not broaden prose edits into tool implementation changes.

Keep tasks, tool sets, models, host configuration, and input data fixed. Record catalog/system text, deferred loads, subsequent requests, actual usage accounting, tool calls, repeated reads, completion, and constraint violations. Without usage, UTF-8 byte counts describe text size, not precise tokens. Without a before/after comparison, report current observations only.

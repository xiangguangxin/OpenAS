# 测试、架构与调试方法

中文 | [English](engineering-methods.en.md)

按本次风险选方法，注明运行环境、预期行为、直接证据和仍不能判断的问题。

## 测试

| 方法 | 实施与验收 |
| --- | --- |
| 故障注入 | 在测试后端分别注入模型超时和动作已发出后回执丢失。断言前一种没有调用工具，后一种保留待核对状态并阻止自动重放。固定注入点，断言业务副作用与恢复状态。 |
| 变形测试 | 为原始输入和变换后的输入定义应保持的关系。例：有序轨迹中插入一次只读观察时，产物结论和下载次数应一致。交换必要动作顺序或额外导出时应发现违规。 |
| 变异测试 | 在临时副本里只削弱一条验收断言对应的实现保护，再运行同一回归。原始实现应通过。变异版本应因预期断言失败而被发现。导入错误和执行环境错误单列。 |
| 状态机属性 | 确定合法转移和每一步都要满足的不变量。用状态序列覆盖执行、暂停、阻塞、人工核对与恢复。记录失败序列和可复现的种子。 |

方法来源：[FoundationDB 确定性模拟](https://apple.github.io/foundationdb/client-testing.html) · [变形测试综述](https://arxiv.org/abs/2605.13898) · [PIT 变异测试概念](https://pitest.org/quickstart/basic_concepts/) · [Hypothesis 状态机测试](https://hypothesis.readthedocs.io/en/latest/stateful.html)。

## 架构

- **质量属性场景**明确触发来源、刺激、环境、受影响组件、期望响应和可测量结果。示例中，测试环境里的浏览器动作可能已执行，回执却丢失。Runtime 保留未知动作，核对前重复提交次数为零。
- **轻量 ATAM 评审**让每个备选方案覆盖风险最高的质量场景。比较延迟、可替换性和恢复语义。记录敏感点、取舍、风险及应验证的假设，再由选型流程沉淀 ADR。
- **ADR**保留决策背景、备选方案、采用理由、代价、状态和复审触发条件。已被替代的决定链接到新记录。
- **架构适应度函数**把已接受的约束写成自动检查。示例中，核心的状态、轨迹和产物验收模块保持与具体模型网关及 GUI 后端的单向依赖。

方法来源：[SEI ATAM](https://www.sei.cmu.edu/library/the-architecture-tradeoff-analysis-method/) · [Architecture Decision Records](https://adr.github.io/) · [Thoughtworks 架构适应度函数](https://www.thoughtworks.com/insights/articles/fitness-function-driven-development)。

## 调试

1. 固定版本、输入、网关模型、应用状态和失败判据。准备一个可通过的基准运行和一个失败运行。
2. 对齐两次运行的可比证据。优先找第一处有意义的差异，按工具名和动作结果看分歧，再核对产物、任务终态和可用的网关错误。忽略会自然变化的时间戳，缺失或未核对的轨迹标为证据不足。
3. **Delta debugging** 用稳定判据逐块删减复现数据。每次保留同一种故障，并反复验证缩减结果。对允许最小化的 JSON 数组可使用 OpenAS 的 `scripts/minimize_repro.py`，为不同故障设置不同退出码或输出标记。
4. 最早差异是缩小排查范围的证据。用单独实验验证因果假设，再把最小复现保留为回归。

方法来源：[Cleve 与 Zeller 的 Delta Debugging](https://www.st.cs.uni-saarland.de/publications/details/cleve-aadebug-2000/)。

---
name: coverage-analysis
description: "分析代码覆盖率报告或异常，定位未覆盖的语句、分支、条件或 MC/DC 判定，区分测试缺口、插桩采集问题和源码映射问题。 / Diagnose code coverage reports and gaps in statement, branch, condition, or MC/DC coverage, including instrumentation, collection, and source mapping."
---

中文 | [English](SKILL.en.md)

遵循[语言约定](../../references/language.md)和[结论与证据共享规则](../../references/evidence-policy.md)。

# 代码覆盖率分析

先确认验收指标、统计范围、排除规则和工具所支持的粒度。绑定源码提交、实际执行的二进制或模块、构建与插桩选项、测试场景、原始数据及报告生成工具版本。使用匹配的对象和数据生成报告，记录多进程、动态库或多个场景合并方式。报告缺失或数据版本不匹配时，先定位插桩、运行数据写出、合并或源码映射阶段；只有证据能定位到语句、分支或判定时才下覆盖结论。

## 定位缺口并验证

- 按文件、函数、源码位置和工具可提供的判定或分支 ID 列出缺口。区分确实未执行、未插桩、数据未收集、映射有误、已按规则排除及证据不足。核对生成代码、宏和多构建配置的统计口径。
- 按可观察行为设计能区分缺失路径的最小用例，写出输入、前置状态、预期结果和目标位置。MC/DC 使用项目和工具采用的判定口径，给出能证明目标条件独立改变判定结果的用例对，并核对短路或耦合条件对该证据的影响。单纯的条件真假计数只支持相应的计数结论。
- 已授权时运行选定用例，使用一致的指标、范围和构建配置比较前后报告。除覆盖计数外，核对业务断言和相关回归。对不可达路径和排除项记录依据；证据不足时标为待核对。

交付来源与命令、工具及指标口径、逐项缺口及证据、建议或已验证用例、剩余限制。总体测试规划用 [test-strategy](../test-strategy/SKILL.md)，交付验收用 [verification-before-completion](../verification-before-completion/SKILL.md)。

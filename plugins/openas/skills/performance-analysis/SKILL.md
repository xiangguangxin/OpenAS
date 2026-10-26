---
name: performance-analysis
description: "建立可复现基准、采集剖析数据并用对照实验验证性能瓶颈和收益；用于性能调查与优化验证，不从单次耗时推导结论。 / Establish reproducible benchmarks, profile execution, and test bottleneck and optimization hypotheses with controlled comparisons rather than single-run timings."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

# 性能分析

输入包括性能问题、目标指标、代表性负载、实现版本、运行环境和资源预算。先明确测量的是用户体验、服务吞吐、资源使用还是模拟指标，保持单位、统计窗口和成功标准一致。

## 建立可信基线

记录提交、构建模式与选项、硬件、系统、依赖、输入规模、并发和缓存状态。复用已有基准；把预热、测量和清理分开，根据运行成本与波动选择重复次数。区分冷启动与稳定态、单请求与总体吞吐，不把不同口径混作一个结果。

保留原始样本，报告适合问题的分布、离散程度或区间，不仅报告最好一次。核对负载发生器是否成为瓶颈、输出是否正确以及采集工具的开销。环境变化或样本不足时降低结论强度，而不是只挑有利数据。

## 从剖析到实验

先用与运行时相符的 CPU、内存、I/O 或其他剖析方式定位热点及调用路径；区分等待和执行、累计与自身开销，不能把相关性直接当因果。提出能被实验否定的瓶颈假设，一次尽量改变一个关键因素，比较相同负载、配置和指标。

基准及采集脚本写入授权目录。优化产品实现需要对应修改授权；不擅自压测线上系统或开通收费资源。实验设置时限和资源上限，触及限制、出现错误或环境失稳时停止并保留证据。

## 交付与验收

输出基线与对照配置、复现命令、原始数据位置、热点证据、改动因素、收益计算和波动。核对正确性、尾延迟、内存及其他相关代价，区分实际测得的收益与推测的扩展效果。

没有稳定差异时报告未能证明改善；目标硬件或真实负载缺失时标明适用范围。[performance-engineer](../../agents/performance-engineer.md) 负责分析，it 协助环境，developer 处理范围外优化，verifier 核对验收证据。

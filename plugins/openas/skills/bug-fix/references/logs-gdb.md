# 日志与 GDB 定位

## 日志：重建一条事务，不盲目扩大输出

先保留原始错误和退出码，再用 `rg -n 'panic|fatal|assert|error' run.log` 找线索并读前后文。没有匹配不能证明无错。每次实验使用独立输出位置，记录命令、代码版本、配置和种子。新增日志优先放在边界和不变量附近，记录输入/输出、对象或事务标识、队列、状态前后值；不要解引用可能失效的指针来打印。

按当前系统的请求 ID、任务 ID、对象、线程或进程关联日志；同一对象可能处理多次操作，地址也可能复用。查首次偏离而非只查最后一条错误。服务可结合请求链路，UI 可结合用户操作与网络响应，数据任务可结合输入批次与记录键。

```bash
# 示例：替换为实际复现命令和输入；输出目录每次独立。
debug_run=$(mktemp -d)
/path/to/program /path/to/input >"$debug_run/stdout.log" 2>"$debug_run/stderr.log"
debug_status=$?
printf 'exit_code=%s\n' "$debug_status"
```

日志级别、过滤条件和输出位置沿用目标程序的配置，不猜测通用命令行参数。大日志先缩小时间范围、任务或组件；异步问题核对开始/完成、重试与状态转换，保留失败样本。

## GDB：先保留现场，再追上游

用匹配当前源码、带调试信息的二进制。优化可能使变量显示 `<optimized out>`，不能据此推断未初始化。需要时按项目构建流程生成 debug 版本，保留原始触发条件。

本节适用于可由 GDB 调试的原生程序；其他运行时按项目已有工具取得异常栈或执行轨迹，不为使用本指南而更换技术栈。

```bash
gdb --args /path/to/debug-binary /path/to/input
```

进入 GDB 后：

```gdb
set pagination off
run
# 信号或断点停止后先采集：
bt full
info threads
thread apply all bt full
frame 0
info args
info locals
list
up
```

`bt` 从当前最内层栈帧向调用方展示；`frame N` 切换观察位置。找到第一个相关业务栈帧，核对参数及调用方如何生成它们。SIGABRT 顶层常是 abort/断言处理；真正违反不变量的位置在调用链中。栈损坏时回溯可能不完整；一份栈只是某个时刻的快照，不是完整事件历史。

针对一个假设逐步选用（替换示例名称与行号，不能整段盲贴）：

```gdb
break file.cc:123
break 'Namespace::Class::method'
info breakpoints
# N 替换为真实断点编号；条件变量须在该断点作用域内。
condition N count < 0
continue
next
step
finish
print count
# 地址有效、对象寿命明确后，监视何处改变值：
watch -location obj->count
# C++ 异常需要定位抛出点时：
catch throw
```

`print` 优先读字段；表达式中的函数调用可能改变目标状态。watchpoint 有数量/大小/作用域和平台限制，软件 watchpoint 较慢；重跑或对象销毁后应重新确认地址与监视点，不监视已释放对象。不能把新增日志或断点后不再出现的竞态当修复。

卡死时先 Ctrl-C 暂停，再查看所有线程栈；检查锁、条件变量、事件循环、队列和未完成请求。线程仍在运行不等于业务有进展，结合任务完成数、状态变化或超时记录定位等待环。Attach 仅用于获授权目标；通常直接启动自己的复现进程即可。

已有 core 时：

```bash
gdb /path/to/exact-matching-binary /path/to/core
```

再运行 `thread apply all bt full`。core 必须与二进制/库匹配；系统不一定生成 core，先核对现有收集设置。core 可含完整进程数据，不自动纳入 Git 或长期记忆。

GDB 若因 ptrace/容器限制失败，记录具体错误和缺失证据，不擅自放宽系统权限。可用受支持环境重现，或先做日志与静态分析。

## 权威参考

- [GDB Backtrace](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Backtrace.html)
- [GDB 官方手册：Breakpoints / Watchpoints / Catchpoints](https://sourceware.org/gdb/current/onlinedocs/gdb/)

命令以本地 `help` 为准，本文不要求安装最新 GDB。

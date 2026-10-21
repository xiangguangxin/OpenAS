---
name: git-worktrees
description: 使用 Git worktree 让多个任务并行、每个任务独立环境。当需要并行开发多个特性时使用。
---

# Git Worktrees

## 多工作区开发

用于支持多个任务并行。

例如：

project/

feature-import/

fix-validation/

docs-api/

每个任务拥有独立文件工作区；数据库、端口、外部服务和构建缓存仍可能共享，按项目实际情况隔离。

适合AI Agent并行开发。

---
name: git-worktrees
description: 为需要独立文件工作区的 Git 任务创建、检查和清理 worktree；用于并行特性或隔离试验，不为简单改动强制新建工作区。
---

# Git worktree

先运行 `git status --short`、`git worktree list`，确认当前修改、已有工作区及任务分支。沿用仓库指定的位置；没有约定时选择仓库外的明确目录，避免构建或递归扫描把其他工作区纳入当前工程。

## 创建与使用

以下名称只是例子，应替换为实际任务，并先确认分支和目标目录未被占用：

```bash
git worktree add -b feature/import ../project-import HEAD
git -C ../project-import status --short
```

已有分支可使用 `git worktree add ../project-import existing-branch`。同一分支已在其他 worktree 检出时，优先复用或选择新的任务分支，不使用 `--force` 绕过保护。

新工作区只共享 Git 对象与引用，不会自动复制未提交改动、依赖或项目记忆。按目标项目说明准备依赖和测试；数据库、端口、外部服务和缓存仍可能共享，涉及这些资源时单独指定位置。任务交接写明工作区、分支、修改归属和验收命令。

## 清理与失败处理

结束前检查该工作区的 diff、未跟踪文件和提交是否已经按任务要求保存。只有已获授权且无需保留的干净工作区才执行：

```bash
git worktree remove ../project-import
git worktree list
```

删除被拒绝时先检查未保存内容，不使用强制删除或手工清空目录。目录被意外移动或删除时，先看 `git worktree list --porcelain`；修复路径或确认失效记录后再按 Git 提示处理，不盲目 prune 仍在使用的工作区。不自动删除任务分支。

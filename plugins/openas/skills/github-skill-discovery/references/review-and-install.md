# 外部技能审查与可追溯引入

## 证据与候选比较

每个候选记录仓库 URL、技能路径、完整 commit、查阅日期和结论。保留支持判断的 `SKILL.md`、依赖清单、相关脚本、许可证/NOTICE 的提交固定链接；分支名与标签可以帮助查找，但不作为最终版本标识。

内容检查应能回答：触发条件是否匹配本次需求，步骤是否有实际支持，是否隐含任意代码执行、外部数据上传、破坏性操作或权限扩大。依赖逐项记录名称、版本约束、平台、是否在目标环境存在、安装与认证方式；本机有工具不表示客户环境也有。来源与验证记录保留必要的凭据变量名，不保存实际凭据。

许可证核对要覆盖被复制的技能、脚本、字体、图片和模板。仓库根许可证可能被子目录或单项资源的条款补充或替代；双重授权按实际选用分支记录。保留适用条款、归属和修改声明，不能把外部资源统一标为 OpenAS 的 MIT。条款缺失、用途不明或条件与交付冲突时，先交付调查结果，不以未知代表允许。

决定直接使用、做最小适配或不采用；对保留候选说明关键差异及验证成本。只搜索的任务到此交付即可。

## 固定版本与暂存

从经过核对的 GitHub 地址克隆到临时目录，解析目标版本为完整 SHA，不运行仓库代码或初始化子模块。脚本只调用 git 读取本地对象，不联网、启动远程脚本、安装依赖或加载技能。Python 3.10+、git 即可运行。

以下命令从 OpenAS 仓库根目录执行，owner、repo、路径和 SHA 都替换为本次实际对象：

```bash
python3 plugins/openas/skills/github-skill-discovery/scripts/import_skill.py stage \
  --checkout /path/to/local-clone --repository owner/repo \
  --commit FULL_COMMIT_SHA --skill-path skills/desired-skill \
  --legal LICENSE NOTICE --output /path/to/new-staging-directory
```

`--legal` 只列出该提交中实际存在、已核对适用的文件；没有 NOTICE 时不传。技能自身包含的文件全部保留，目录外法律文件附带到 `_openas_origin/legal/`，并在来源记录中保留原路径和指纹。源技能目录可为 `.`；脚本拒绝符号链接、子模块、路径越界和过大包（最多 1000 文件、合计 50 MiB）。有此类特殊结构时先评估完整依赖，再人工适配，不绕过检查假装已安装。

`stage` 要求 origin 对应声明的 GitHub.com 仓库，直接读取完整提交的 Git 对象，不受工作区未提交修改影响。origin 与 SHA 是可复现线索，不是来源真实性的数字签名；检索时仍需核对实际 GitHub 仓库。GitHub Enterprise、自定义授权及超大包使用人工流程并记录等价来源证据。

Git LFS 资源以提交中的指针为准，不自动下载真实大文件；审查时检查资源是否完整，指针不能当作可用模板或图片。

脚本在暂存目录写入 `OPENAS_SOURCE.json`；来源记录保留上游提交、原始文件清单和法律文件。它占用该文件名与 `_openas_origin` 目录，源技能已有同名内容时拒绝暂存，避免覆盖。

## 适配与审查记录

在暂存区完成需要的改动，不删改附带法律文件。再次运行 inspect 获取当前包指纹及相对上游的变化：

```bash
python3 plugins/openas/skills/github-skill-discovery/scripts/import_skill.py inspect /path/to/staged-skill
```

审查 JSON 绑定 inspect 输出的 `package_sha256` 与相同上游提交。字段示例（身份、版本、结论和验证必须来自实际工作）：

```json
{
  "repository": "owner/repo",
  "commit": "实际完整提交 SHA",
  "skill_path": "skills/desired-skill",
  "package_sha256": "inspect 输出的当前包 SHA-256",
  "reviewer": "实际评审标识",
  "decision": "accept",
  "mode": "adapted",
  "changes": ["将宿主专属命令替换为目标项目可用的等价工具"],
  "checks": {
    "content": true,
    "dependencies": true,
    "license": true,
    "fit": true
  },
  "license": {
    "expression": "从适用条款确认的许可证或组合",
    "usage": "客户实际使用或分发方式",
    "notes": "已核对的归属、通知和修改条件"
  },
  "dependencies": [
    {"name": "实际依赖名称", "version": "实际版本约束", "status": "available"}
  ],
  "validation": [
    {"kind": "structure", "status": "passed", "evidence": ["实际命令和结果或记录路径"]},
    {"kind": "behavior", "status": "passed", "evidence": ["代表性任务与不应触发场景的实际结果"]}
  ]
}
```

无运行依赖时 `dependencies` 为 `[]`，原样复制时 mode 为 `copy`、changes 为 `[]`。有改动时必须写 `adapted` 和变更说明。暂存阶段通过结构与行为测试才安装；缺依赖、失败或未运行时保留暂存候选，报告缺口。脚本验证字段和指纹，评审者标识、文字证据和许可证表达式仍由调用方负责，不能当作经过身份认证或法律判定。

## 安装、客户端核验与来源检查

```bash
python3 plugins/openas/skills/github-skill-discovery/scripts/import_skill.py install \
  --candidate /path/to/staged-skill --review /path/to/review.json \
  --destination /path/to/client-skills/desired-skill
```

明确目标客户端的实际技能目录后再设置 destination。脚本要求末级目录名等于 SKILL.md 的 name，目标必须不存在；不会选择用户全局目录、覆盖旧版本或改客户端配置。安装后原生宿主是否发现技能，需要按该宿主实际机制重连/刷新并调用验证。

安装记录初始为 `installed_unverified`。验证报告使用相同 validation 数组格式，至少含实际完成的 `host-discovery` 和 `host-invocation` 两项。每项 status 为 passed / failed / not_run，evidence 为非空说明列表；未调用客户端时写 not_run 及原因。

```bash
python3 plugins/openas/skills/github-skill-discovery/scripts/import_skill.py record-validation \
  /path/to/client-skills/desired-skill --report /path/to/host-validation.json
python3 plugins/openas/skills/github-skill-discovery/scripts/import_skill.py verify \
  /path/to/client-skills/desired-skill
```

报告形如 `{"validation": [{"kind": "host-discovery", "status": "passed", "evidence": ["实际发现记录"]}, {"kind": "host-invocation", "status": "not_run", "evidence": ["缺少目标客户端，未执行调用"]}]}`。两项均通过才记录 `validated`，否则保持 `installed_unverified`。该状态是调用方报告，不是脚本自行调用客户端的证明。

verify 检查已安装包的文件和模式是否仍与安装清单相符、法律文件是否保持完整；失败不更新指纹、不自动修复。退出码 0 只表示文件一致，不代表客户端或业务验收通过。inspect 只读输出，不注册技能；所有错误退出码为 2，verify 发现变化退出 1。

来源记录包含原始清单、安装清单、评审、验证历史及时间；再次修改技能后应重新适配和验证。撤销只处理本次新建目标目录，不移除其他技能、不删除来源仓库、不自动卸载依赖。

## 上游参考

- [GitHub Code Search 语法](https://docs.github.com/en/search-github/github-code-search/understanding-github-code-search-syntax)：用于网页搜索；API/CLI 以各自参数为准。
- [GitHub 仓库许可说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)：核对实际授权，公开可见不等于可自由复制分发。
- [Agent Skills 格式规范](https://agentskills.io/specification)：核对 SKILL.md 和资源布局，最终兼容性由目标宿主验证。

本技能不附带第三方技能、不提供外部候选的预先背书；检索和审查针对本次需求及实际提交执行。

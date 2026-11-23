---
name: remotion-render
description: "在已有 Remotion 项目中导出指定 composition 的视频或静帧，并核对媒体产物；用于客户演示与视频交付，不将普通界面动画或屏幕录制路由到视频渲染。 / Render and verify video or still artifacts from an existing Remotion composition without implying recording or animation-authoring capability."
---

中文 | [English](SKILL.en.md)

遵循[语言约定](../../references/language.md)、[证据规则](../../references/evidence-policy.md)与[项目适配](../../references/project-context.md)。先检查项目锁定版本、入口、依赖、素材及脚本，不自动初始化工程或下载缺失依赖。

# Remotion 媒体导出

明确 composition ID、输入 props、分辨率、帧率、输出类型和目标路径。使用项目已有命令或已安装 CLI 的 help 核对参数，再列 composition。优先使用本地二进制；若依赖未安装，说明阻断并按既有授权处理，不让 `npx` 隐式获取未知版本。

以下为项目已安装相应 CLI 时的命令形状，入口和 ID 必须替换为实际值：

```text
remotion compositions <entry-point> --props=<props.json>
remotion render <entry-point> <composition-id> <output.mp4> --props=<props.json>
remotion still <entry-point> <composition-id> <output.png> --props=<props.json>
```

用同一 props 确认有效 composition 的尺寸、fps 和帧数符合请求；不符时先在授权范围内解决，不能盲加版本不支持的覆盖参数。props 文件不包含凭据；记录其指纹及实际使用值的非敏感摘要。保留现有渲染浏览器配置；遇到浏览器或字体缺失时说明实际错误。云渲染、收费资源和媒体上传只在任务明确涵盖时执行；核对当前 Remotion 和素材使用条款，不假设本技能赋予商业许可。

导出前检查已有目标，使用新路径或按已授权范围替换。完成后记录命令、版本、退出码、产物指纹；用已有媒体工具核对可解码、尺寸、帧率、时长及预期音轨，并抽查首、中、尾帧。静帧要实际打开核对。文件存在或 CLI 返回 0 不能单独证明媒体正确；无解码工具或无法预览时明确未验证项。

来源：[官方 render 文档](https://www.remotion.dev/docs/cli/render)、[compositions](https://www.remotion.dev/docs/cli/compositions)。这是独立编写的官方 CLI 操作指引，不分发上游 Skill 文本，见[来源说明](../../references/skill-methods/NOTICE.md)。

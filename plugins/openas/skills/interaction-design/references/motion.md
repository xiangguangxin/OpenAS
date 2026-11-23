# 动效设计与实现 / Motion design and implementation

## 中文

先确认动画是否帮助反馈、空间关系、状态理解或讲解。高频操作优先即时响应；装饰动画不得遮挡读数、抢占焦点或延迟关键操作。遵守用户明确需求与既有设计 token，不移植来源的固定频次阈值、统一曲线或绝对审美规则。

按需求选择足够简单的机制：现有 CSS transition/animation、原生动画 API 或已安装的库；简单淡入不需要新依赖。优先验证 transform/opacity，避免无意布局抖动，精确声明过渡属性。保留触发位置和空间方向，定义连续触发、反向、中断、退出及卸载清理，不能重播已结束的业务副作用。

同时实现 `prefers-reduced-motion` 的减少或关闭动态效果版本，以及键盘、触屏与悬停设备差异。减少动态效果不得隐藏业务反馈或阻止操作；不强制用户保留淡入。动效不能承载唯一的状态信息。

设计任务交付状态/动效规格；已授权实现时写代码并用可用工具检验。覆盖连续触发、打断、退出、低动态效果、键盘和触屏，按需要测量渲染开销。静态 CSS 检查不能证明流畅或视觉正确；无法实际预览时列出待检查的状态与设备。

## English

Establish a purpose: feedback, spatial relation, state comprehension, or explanation. Prefer instant responses for frequent actions. Decorative motion must not obscure readings, steal focus, or delay critical operations. Preserve explicit user requirements and existing tokens rather than importing fixed frequency thresholds, universal curves, or absolute style rules.

Choose the simplest sufficient existing CSS transition/animation, native API, or installed library; a fade does not require a dependency. Prefer checking transform/opacity, prevent unintended layout shifts, and name transitioned properties. Preserve spatial origin/direction and define repeated triggers, reversals, interruption, exit, and unmount cleanup without replaying business effects.

Ship reduced or disabled motion for `prefers-reduced-motion`, plus keyboard, touch, and hover-device behavior. Reduced motion must preserve business feedback and operability; a fade is not mandatory. Never encode state solely through movement.

Design-only work delivers state/motion specifications; authorized implementation writes code and checks it with available tools. Cover rapid retriggers, interruptions, exit, reduced motion, keyboard, and touch; measure render costs when relevant. Static CSS does not prove smoothness or visual correctness. Disclose states/devices needing preview.

Adapted from Emil Kowalski's animate workflow; [attribution and changes](../../../references/skill-methods/NOTICE.md).

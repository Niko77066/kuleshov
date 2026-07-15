# Compose 参考笔记 · 借自 hyperframes-launches/vfx-heygen-combined

来源:https://github.com/heygen-com/hyperframes-launches/tree/main/vfx-heygen-combined(用户 2026-07-14 指定作画面参考)

> **纪律:借技术,不借长相。** 该参考是 HeyGen 产品发布会 VFX(悬浮 iPhone、lime-green CTA、光泽广告感),与本片「工程解剖/事故调查纪录片」气质相反。凡涉及配色/版式/情绪一律以 engineering-anatomy playbook 为准;只提取下面三类**可复现的合成技术**。

## 1. HyperFrames 能承载真 WebGL —— 剖面图升级为真 3D

参考里 `index.html` 同时跑三套 WebGL:Three.js 3D 模型渲染(`iphone.glb`)、chromatic RGB split、portal reveal shader。且 `hyperframes lint/validate` 仍过。

**迁移到本片**:
- 「剖面标注卡 / 电池包爆炸图」候选做成 **Three.js 真 3D 电芯/模组模型**(`.glb`),配相机推拉,而非平面 SVG 卡——观众能真正"绕着剖面看"。
- **热色 shader**:温度场用 fragment shader 上色(琥珀→橙红→白炽单色梯,禁彩虹),比逐帧 PNG 更可控、确定性更好。
- **已定(d10):程序化 Three.js 真 3D**,不下载 glb。实搜 Poly Pizza 无合适 CC0(全是 AA/铅酸/低模卡通);方形电芯是规则几何,`RoundedBoxGeometry` 阵列 + emissive 热色 + UnrealBloom 建模比货不对板的下载模型更准更可控。概念验证:`compose/proto/battery-module-3d.html`(已渲通过,6×3 模组 + 单芯白炽 + 邻芯梯度)。
- ⚠️ DEBT:proto 用 CDN Three.js;compose 正式版须 vendored 到本地(HyperFrames 禁 CDN)。

## 2. 运动接管转场(cut-the-curve)—— 升级"剖面擦除"与"链路进度条"

参考的转场核心原则(COMBINED_VIDEO_HANDOFF.md):
- 两个画面当作**同一段向上运动的两半**:出场层加速+模糊甩出,入场层从下方沿同一路径减速入位;
- **opacity 与 position/blur 分离**——绝不靠 opacity 做转场,否则会"pop"(硬闪);
- **禁 crossfade**,让运动本身承接转场。

**迁移到本片**:
- engineering-anatomy 的转场词汇「剖面擦除(MG 图解 ↔ Seedance 实景)」由"擦除"升级为**匹配运动 + 模糊接力**:如从整包实景"钻入"剖面时,实景加速+模糊后退,剖面沿同一轴线迎上——切换即"镜头钻进电池内部"的叙事动作。
- 「链路进度条」节点推进也用位移承接,不用 opacity 点亮。
- 不与风格包冲突:转场总数仍 ≤ 4 种,只是把其中"剖面擦除"的实现方式定义清楚。

## 3. 工程流程

- 校验链:`hyperframes lint && hyperframes validate && hyperframes inspect`(本片 compose 的 G1 硬门,叠加我方 `--docker` 复现规则);
- 迭代用 **HyperFrames Studio 预览/scrub**,不在编辑期反复 render;
- 大 composition 拆子文件(参考踩过 `composition_file_too_large` 警告)——本片若剖面 3D 较重,`compositions/` 下按镜头组拆块。
- DESIGN.md 的四段式(Style Prompt / Colors / Typography / What Not To Do)已被 engineering-anatomy playbook 覆盖,无需另写。

## 待办(带入 storyboard/compose)

- [ ] storyboard 标注哪些 MG 镜头走"伪 3D 分层剖面",哪些争取真 glb;
- [ ] 定义热色 shader 的三档色标锚点(对齐 playbook 的 --heat-0/1/2);
- [ ] compose 阶段把"剖面擦除"落成匹配运动+模糊的具体 GSAP/shader 参数,回填 translation-table 新行。

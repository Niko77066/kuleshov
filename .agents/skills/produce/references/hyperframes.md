# 引擎知识包 · HyperFrames（HTML 确定性合成）

> 何时读我：storyboard 有镜头路由到 `hyperframes` 时；compose 阶段全程。

## 定位

HeyGen 开源（Apache 2.0）的 agent-native 合成框架："写 HTML/CSS/GSAP，渲染视频"。**不产生像素，只做确定性合成**。它是 **MG 动画（motion graphics）/信息图形语言**的主引擎，也是全片叠加层（字幕/角标/数据卡）的宿主——按表达选它，不是按成本选它。

**类型纪律**：全部产出属"幻灯片语法"，**不计入运动占比**——片型承诺只能写 `typography_led` / `data_explainer`，冒充 `motion_led` 是承诺违约。

## 安装与文档

```bash
npx skills add heygen-com/hyperframes   # 8 核心 + 10 工作流技能
```

- 文档索引：hyperframes.heygen.com/llms.txt （细节问题先查这里，别猜 API）
- Playground：hyperframes.dev

## 硬规则（violate = lint 不过 = 禁 render）

1. timeline 必须 `{ paused: true }` 创建并注册到 `window.__timelines[compositionId]`；
2. `<video>` 元素必须 `muted`（声音走独立 audio 轨，混音归 compose 契约管）；
3. 禁 `Math.random` / `Date.now` / `requestAnimationFrame` / 渲染期网络请求——一切必须由帧时钟驱动、可复现；
4. 计时元素必须 `class="clip"` + `data-start` / `data-duration` / `data-track-index`；
5. 资产全部本地文件，禁 CDN。

`npx hyperframes lint` 是现成 G1 硬门：**lint → 过了才 render**。

## 渲染纪律

- 渲染一律 `--docker`：同一 composition 逐字节复现——未来 golden-set 回归可做帧级 diff，基线从 M0 第一片就用 Docker 建；
- 逐帧寻位（整数帧时钟），动画时长换算成帧数思考（30fps：0.3s = 9 帧）。

## 感受词 → 参数（与 styles/translation-table.md 联动，拉片后往总表补行）

| 感受词 | GSAP 参数 |
|---|---|
| 干脆 / snappy | `power4.out`，0.2–0.4s |
| 能量感 | 入场 0.2s 级；元素错峰 stagger 0.05–0.08s |
| 沉稳 | `power2.inOut`，0.5–0.8s，位移小 |
| 数字强调 | count-up ≤ 0.6s，`tabular-nums` 防抖动 |

## 典型用途（声部：信息主轨）

榜单卡 / 数据卡 / 大数字卡 / 标题与章节卡 / 引言卡 / 全片字幕层 / 图片动效容器（见 image-motion.md——Ken Burns 在这里做，不预烘焙 mp4，可调且确定性）。

## 反模式

- 每个条目换一种版式（模板味 + 认知负担）；
- 用 HTML 做"要真运动"的镜头（路由纪律：task_fit 归零）；
- 动画堆砌：同屏 > 2 个并发动画即审视必要性。

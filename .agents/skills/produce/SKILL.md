---
name: produce
description: Kuleshov 十阶段视频生产管线（M0 手工作坊版）——从 brief 到成片：音频先行、锚点先行、逐镜头来源路由，状态机活在 film.json。当用户说"开拍"、"出一条片"、"跑管线"、"继续做某片"、"重做第 N 镜"时使用。
---

# Kuleshov 生产管线 · M0 手工作坊版

你是这条链路的执行制片人（EP）兼各阶段导演。M0 是人在环模式：**用户就是评委门**。

## 0. 工作方式（先读这五条）

1. **人在环**：每个阶段的关键产物落盘后**停下来**，用一小段话 + 产物路径向用户汇报，拿到认可再进下一阶段。标记了 ⏸ 的停点绝不跳过。
2. **状态从文件读**：开工先查 `projects/` 下有无该片目录。有 `film.json` 就读它续跑（`meta.status` 记录当前阶段），没有才从 brief 开始。
3. **知识按需加载**：本文件只有骨架。镜头路由到哪个来源，才读对应的 `references/` 知识包；没路由到的不读。
4. **风格包先行**：没选风格包不开拍。风格包在 `styles/` 下，含开拍提问模板的要执行它的提问。
5. **铁律见根目录 AGENTS.md**：先写 IR 再花钱、留痕、音频先行、禁静默降级。

## 1. 开拍提问（elicitation）

基础五问（一次问完，用后续对话补细节）：

1. **选题**是什么？有没有已有素材（文档 / 链接 / 图片 / 录屏）？
2. **片型**：M0 优先 `faceless_news_recap`（资讯速览）或 `faceless_explainer`（知识讲解）；其他片型提醒用户属超纲试验。
3. **风格包**：列出 `styles/` 下可用包让用户选；选定后执行该包的开拍提问模板。
4. **时长承诺**：如 60s ± 5%。
5. **预算上限**（可选）：仅用于记账与熔断，**不影响选源**——五种来源全量可用，按镜头意图自由调配（铁律 7）。用户不设即默认不限。

回答齐了就建 `projects/<片名>/`，从 `projects/_template/film.json` 复制初始化，写入 `meta`。

## 2. film.json 契约（简化版 Film IR）

全片唯一真相源。三条设计规则：**① 一切引用靠 ID**（镜头引用锚点、叠加层引用镜头，禁止路径散落）；**② 生成参数全记录**（模型/seed/prompt/参考，任何资产可复现）；**③ IR 引擎无关**（compose 阶段才翻译成 HyperFrames composition / FFmpeg 命令）。

```
film.json
├── meta          # 片名、片型、风格包、交付承诺、宽高比、预算、pipeline_version、status
├── audio         # voiceover / music / timeline（逐词时间戳 + 分节区间）
├── anchors[]     # 锚点：id、类型、文件、生成参数、一致性备注
├── shot_groups[] # Seedance 通路才用：生成调度单元（≤15s、≤5 镜）+ 接缝契约
├── shots[]       # 镜头（见下方示例）
├── overlays[]    # 字幕/角标/logo 等全片叠加层（引擎无关声明，引用 shot id 区间）
├── edit          # 转场词汇(≤4)、LUT、颗粒、响度目标、闪避规则
└── ledger        # decisions[]（决策日志）、costs[]（成本台账）、gates[]（自查记录）
```

镜头条目示例（ID 用语义命名 `s03_top1_card` 式）：

```json
{
  "id": "s03_top1_card",
  "t": [12.48, 17.92],
  "voice_ref": "sec02",
  "intent": "榜单第 1 条：标题 + 关键数据强调",
  "framing": "全屏版式卡",
  "source": { "provider": "hyperframes", "template": "list-item-card" },
  "anchor_refs": [],
  "status": "planned",
  "gen": null,
  "qc": null
}
```

烘焙型镜头生成后回填 `gen`：`{ "model": "...", "prompt": "<完整 prompt>", "seed": 1234, "refs": ["anchor:style01"], "cost_usd": 0.4, "wallclock_s": 95, "duration_actual_s": 5.3, "file": "shots/s05.mp4" }`。
`status` 取值：`planned → generated → qc_pass / qc_fail / redo`。

## 3. 十阶段

阶段目录约定：`projects/<片名>/` 下 `brief.md`、`research.md`、`script.md`、`audio/`、`anchors/`、`shots/`（烘焙 clip）、`compose/`（composition 源码）、`out/`（成片）、`review.md`。每阶段完成即更新 `meta.status`。

### ① brief
写 `brief.md` + `film.json.meta`：选题、受众、片型承诺、时长、风格包、预算上限、素材清单。

### ② research（M0-lite）
WebSearch / 用户素材整理出 5–10 条核心事实，**每条带出处 URL 与获取日期**，写 `research.md` 并编号（`F01…`）。news_recap 加时效戳（数据抓取时间）。解说片的事实底座——script 里的每个事实主张必须回链编号。

### ③ blueprint + script（M0 合并回合）⏸
写 `script.md`：
- **结构**：But/Therefore 叙事链（禁 And then 流水账）；开头 3 秒必须有钩子。
- **字数预算硬校验**（写完先自己数，超了砍内容不掺水）：中文常速 60s ≈ 220–260 字，快报体 ≈ 280–320 字；英文 60s ≈ 130–150 词，news 密度 165–180 wpm。
- **分节**：每节 = 旁白文本 + TTS 表演指令（语速/停顿/重音）+ 视觉提示（这节画面大意）+ 事实回链（`F01`）。
- 每 8–10 秒的内容要能支撑一次视觉变化。

⏸ **停：把剧本给用户看**，认可后才做音频。

### ④ audio ⏸
读 `references/tts-audio.md`（接入方式、对齐工具、混音契约都在里面）。
1. TTS 生成 `audio/voiceover.wav`（分节生成便于重做单节）。
2. 强制对齐产出 `audio/timeline.json`（逐词时间戳 + 分节区间），回填 `film.json.audio.timeline`。
3. **自查（G1 级，不过必须重做）**：回转写与剧本比对准确率 ≥ 95%；总时长在承诺 ± 5% 内。
4. 有音乐需求的选曲并记 BPM / 段落结构。

⏸ **停：给用户听旁白**。此后一切视觉时长以 timeline 为准。

### ⑤ storyboard ⏸
填 `film.json.shots[]`，每镜头：绑定 timeline 的真实音频区间、intent、景别/版式、来源路由（见 §4 路由表）、锚点需求。走 Seedance 的镜头同时划 `shot_groups[]` 并声明组间接缝契约（A 尾帧接力 / B 硬切 / C 转场，详见 `references/seedance.md`）。

**自查八项**（逐项过，结果记 `ledger.gates`）：
1. 镜头区间无缝隙、无重叠，首尾对齐音频总长；
2. 每 8–10s 至少一次视觉变化；
3. 连续同版式 / 同景别 ≤ 2 镜；
4. 幻灯片风险：静态类（图片动效/纯版式）连续 ≤ 2 镜，且总占比符合片型承诺；
5. 声部匹配：每镜 intent 与来源的叙事角色一致（风格包声部表）；
6. 运动承诺可达性：承诺 motion_led 时真运动镜头占比够不够；
7. （Seedance）组划分算术：每镜恰好属于一组、组时长 ≤ 15s、各组之和 = 承诺时长 ± 公差；
8. 每镜一个主动作 + 明确运镜词，无"静态场景描述"式镜头。

⏸ **停：把分镜表（含路由与理由）给用户看**——这是花钱前最后一道门。

### ⑥ anchors（按需）⏸
纯版式/MG 片：风格包的 CSS tokens / 版式模板即锚点，可跳过本阶段。
用到图片或生成视频的：读 `references/image-motion.md`，产角色表 / 产品图 / 风格帧 / 关键帧，参数全记录，回填 `anchors[]`。
⏸ **停：锚点给用户 N 选 1**——图便宜，在这里多轮迭代，别到视频阶段返工（廉价品味注入点）。

### ⑦ motion
只做**烘焙型**镜头（Seedance / 数字人 / 实拍素材），声明型（HTML / 图片动效）直接进 compose 不烘焙。
按 `references/seedance.md` 的契约逐组生成；每段落地即做**镜头级 QC**：技术检查（实际时长、黑帧、分辨率）+ 语义自查（是否兑现 intent、有无畸变、角色是否对得上锚点），结果写 `shots[].qc`。不合格重试 ≤ 2 次（锁 seed 改 prompt），仍败**停下来和用户商量**，禁止静默降级换路。

### ⑧ compose
读 `references/hyperframes.md`。IR → HyperFrames composition（`compose/`）：
- 声明型镜头与叠加层直接写成组件；烘焙 clip 按 `t` 挂入；
- **时长调和**（烘焙 clip 超长时按序）：尾部裁切（保动作完成点）→ 变速 ± 5% → 均不可则该镜 fail 重做；**禁止冻结帧补时长**；
- 混排缝合：统一 LUT（以 style frame 为基准）+ 共享颗粒；剪辑点落句读/节拍，默认 J-cut/L-cut；转场 ≤ 4 种；
- `npx hyperframes lint` 不过禁 render；render 用 `--docker` 保帧级复现，出 `out/final.mp4`。
- 服务器渲染 API 就位后用 `tools/render-remote.sh projects/<片名>` 跑 final；它要求 `KULESHOV_RENDER_URL`、`KULESHOV_RENDER_TOKEN`、`HYPERFRAMES_VERSION`，缺配置或远端失败即停止，禁止静默回落本地。首次切换必须用同一 composition 与本地 `--docker` 双跑一次帧级一致性对比，通过才切，切换记 `ledger.decisions`。

### ⑨ review ⏸
1. **L0 手动仪器**（结果与证据写 `review.md`）：`ffprobe` 查时长/分辨率/帧率；blackdetect / freezedetect 查黑帧冻结；响度是否 -14 LUFS；成片音轨回转写 vs 剧本；承诺复验（时长、运动占比、转场数）。出示证据，"我检查过了"不算数。
2. ⏸ **用户亲自看片**（M0 的评委团就是用户）。
3. 引导用户跑 `/video-score` 登记 7 维分；有问题跑 `/video-triage` 归因到环节。

### ⑩ deliver
`out/` 里放齐：成片 + `film.json` + `review.md` + 成本小结（`ledger.costs` 汇总）。git commit（一片一提交）。向用户汇报：总成本、总墙钟、各阶段耗时、留下的 DEBT 标记。

## 4. 来源路由表（五源平权，全量可用）

| Provider | 状态 | 这门语言擅长表达什么 | 关键约束 | 知识包 |
|---|---|---|---|---|
| MG 动画（HyperFrames） | ✅ | 信息与图形语言：数据卡、榜单、动态排版、字幕层 | 产出属"幻灯片语法"，不计运动占比 | `references/hyperframes.md` |
| AI 生成视频（Seedance 2.0） | ✅ | 真运动、氛围、场景再现、hook/hero 镜头 | 单次 4–15s；角色/产品镜头必须挂锚点 | `references/seedance.md` |
| 数字人（HeyGen Avatar 4） | ✅ | 口播、主持、结论、人设 IP | 时长=音频时长；aspect_ratio 必填；形象锚点按目标画幅构图 | `references/avatar.md` |
| 图片 + 动效（GPT-Image-2） | ✅ | 风格化静帧、插画、概念示意、"准运动" | 连续 ≤ 2 镜（防幻灯片化） | `references/image-motion.md` |
| TTS 音频（seed-audio-1.0） | ✅ | 一切旁白（+可单独生成 BGM/音效轨） | 旁白轨纪律见知识包 | `references/tts-audio.md` |
| 实拍 / 检索剪辑 | ⛔ 素材语料库未建（M3） | 纪实感、证据声部、B-roll | provenance/license 硬门 | — |

路由纪律：
1. **平权 + 意图优先**（铁律 7）：逐镜头问"哪种来源最能表达这个 intent"，成本不进权重；混排是常态不是例外，声部语法（风格包）负责让切换成为叙事信号；
2. 要真运动的镜头**禁止**路由到 HTML/图片动效（task_fit 归零）——这是工艺诚实，不是成本规则；
3. 每个路由决策把理由和备选项记入 `ledger.decisions`（归因时能回答"这个镜头为什么长这样"）。

## 5. 定点重做（单镜手术）

用户说"第 N 镜不行"时：
1. 读 `film.json` 定位镜头，确认问题归属（prompt？锚点？路由？剪辑?）；
2. 置 `status: "redo"`，决策与理由记 `ledger.decisions`；
3. 只重跑该镜（生成类：锁 seed 改 prompt，或换锚点；声明型：改 composition 参数）；Seedance 通路最小重做单元是**镜头组**；
4. compose 增量重渲受影响区间，重过该镜 QC。

**禁止**因单镜问题重跑整片——拒掉一个镜头很便宜，拒掉一条片很贵。

## 6. 止损规则(M0 版制片人)

- 每阶段修订 ≤ 3 轮；同一对阶段间打回 ≤ 1 次——到限即停，和用户重新对齐；
- 单镜重试 ≤ 2 次，仍败必须请示（降级要用户点头）；
- 成本熔断**仅当 brief 显式设了预算上限**才生效（`meta.budget.cap_usd` 非空）；未设则只记账不设限——质量优先是默认；
- 任何工具/引擎缺失：如实报告 + 记 DEBT，不造假产物糊弄下一阶段。

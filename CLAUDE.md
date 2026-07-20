# Kuleshov · M0 手工作坊

全自动多源视频 agent 生产链路 **Kuleshov** 的第一形态：人 + Claude Code + ~10 份文件。
设计蓝图（v3.4）：https://claude.ai/code/artifact/06e62b33-6e82-4ffc-b893-94a15ccd69a1

M0 的交付物不是视频，是：**验证过的品味资产 + 带人工分的片库（未来评委的校准语料）+ 稳定下来的 prompt 模式（未来编译器的输入）**。

## 当前目标（M1 · 2026-07-16 会后拍板版）

场景定位：**社媒账号内容创作与运营**（覆盖 KOL 选题验证 → KOC 起号变现），产出发布**小红书 + 抖音**。选题、创意、信息密度是拿流量的生命线（评分卡已补 D8 创意 / D9 网感）。M1 两条生产链路，**首片均已交付**（2026-07-20 状态），当前重心是把两条链路固化为**可端到端复跑的生产模式**（工程项见 `docs/m1-plan.md` 7/18–22 段）：

1. **知识科普类 3 分钟视频**——风格包 `styles/pixel-chronicle/`，首片 `projects/uk-argentina-feud/`（已出厂合 main）；
2. **荆华密算 AI 隐私平台社媒视频**——内容引擎：**搜集全球 AI 隐私与泄露热点新闻 → 专业解读 + 安全提醒 → 凸显六场景（法律/医疗/心理/职场/金融/科研）中的产品价值**。风格包 `styles/case-file/`，首片 `projects/openai-78m-logs/`（已出厂合 main）。企业号红线见 `.claude/skills/rednote-mentor/references/compliance.md`。

M0 实验项目（800v-thermal-runaway / estee-lauder-night / samsung-health-ai-consent / _smoke）与弃用风格包（daily-brief / tech-newsroom / engineering-anatomy / night-luxe）已于 2026-07-20 精简出库：git 历史可查，本地全量归档在 `~/kuleshov-archive/m0-projects/`，film.json 校准语料在 `film-ir/tests/fixtures/` 有只读副本。

两个外部依赖由用户提供 API（契约到手即接入，todo 见 `docs/m1-plan.md`）：**检索/实拍素材 API**（补齐五源里最后一源）、**服务器渲染 API**（替代本地渲染，切换前须帧级一致性对比）。

账号运营层用 `/rednote-mentor`：选题从搜索词反推进 brief，出厂随片交付双平台发布包，冷启动数据按 L5 回流归因。M1 工程化设计（Film IR API、导演—子导演上下文、风格包注入机制）见 `docs/film-ir-context-architecture.md`，排期与 todo 见 `docs/m1-plan.md`。

## 目录

- `.claude/skills/produce/` — 十阶段生产管线 SOP（入口：`/produce`），引擎知识包在其 `references/` 下，按镜头路由按需加载
- `styles/` — 风格包（现存两包：`pixel-chronicle` 知识科普横屏 / `case-file` 官号竖屏）+ 反主观翻译总表（`translation-table.md`）+ 进化规程（`_iteration.md`）
- `projects/<片名>/` — 每片一个目录：`film.json`（全片唯一真相源）+ 阶段 artifact + 产物
- `film-ir/` — Film IR API（Python 库 + CLI `kuleshov-ir`：read / patch / validate / execute 四动词 + G1 门套件 + migrate 收编器）；测试 `film-ir/.venv/bin/python -m pytest film-ir/tests/`
- `tools/oss-upload.sh` — 本地资产传 grain S3 → 返回 `storage.neodrop.ai` 公网 URL（Seedance @ref 引用用）

## 运行铁律（M0 版 Rule Zero）

1. **先写 IR，再花钱。** 一切生成动作（图 / 音频 / 视频）必须对应 `film.json` 里已存在的镜头或资产条目；生成完立刻回填结果与参数。查不到条目就不许调 API。
2. **留痕不可事后补。** 每次生成记录：模型、完整 prompt、seed、参考文件、成本、耗时、实际时长；每个关键决策（选源、重做、降级、砍内容）记入 `ledger.decisions`，带理由。
3. **音频先行。** `audio.timeline` 定稿后，一切视觉时长以真实音频时间戳为准，禁止按剧本字数估时。
4. **状态从文件读。** 续跑、重做、回答"做到哪了"之前，先读 `film.json`——状态机活在文件里，不在对话记忆里，也不在提示词里。
5. **禁止静默降级。** 引擎不可用、参数被迫改变（如超时重试想丢掉首帧锚定）时，**停下来问用户**，不许自动换路——LibTV 的两次静默降级是活的反面教材。
6. **每片出厂过 `/video-score` 登记**，人工分进片库；发现问题用 `/video-triage` 归因。这是未来机器评委的校准语料，漏一片少一片。
7. **来源平权，质量唯一。** MG 动画（HyperFrames）、AI 生成视频（Seedance）、数字人、图片动效、实拍/检索素材是五种平权的表达语言——选源只问一个问题：**哪种来源最能表达这个镜头的意图**。成本只记账、不进路由权重；禁止"能用便宜的就先用便宜的"。最终目的是把用户期望主题的视频做到最好，不惜成本。

## 品味宪法（初稿 — 每一条都等作者亲手裁决）

> **状态：草案。** 以下从蓝图与既有拉片记录中提炼，不是定稿。请逐条批注：保留 / 改写 / 删除，并补上只属于你的硬观点。定稿前按"强倾向"执行，与用户意见冲突时停下来问。

### 爱

- **意义产生于并置**（库里肖夫）。剪辑点是第一表达手段：先想"这两个镜头相邻说明了什么"，再想单个镜头有多美。
- **真实音频的呼吸感。** 剪辑点落在句读与节拍上；J-cut / L-cut 是默认动作，不是炫技。
- **克制的版式。** 一屏只讲一个主张；字是排出来的，不是堆出来的。
- **有出处的事实。** 每个事实主张能回链 research；宁可少说一件事，不说一件没根据的事。
- **每 8–10 秒一次视觉变化。** 观众的注意力是租来的，租金按秒计。

### 恨

- **幻灯片化。** 静帧 + 慢速 Ken Burns 冒充运动；用冻结帧补时长（直接判废，反模式零容忍）。
- **转场遮丑。** "来源切换必加转场"是心虚；全片转场词汇 ≤ 4 种。
- **模板味。** 出厂前自问"换个选题/产品名还成立吗？"——成立，就是没做够。
- **AI 光泽的塑料感**不做质感缝合（统一 LUT + 共享颗粒）就出厂。
- **无意图的运镜。** 动了，但说不出为什么动。

### 宁可牺牲什么，保什么

- 宁可**短**，不可**水**：60 秒讲不完就砍内容，不掺水。
- 宁可信息密度降一档，保**节奏的呼吸**。
- 宁可重做一个镜头，不放过一处**角色变脸 / 文字碎裂**。
- 宁可 TTS 平实克制，不要过火的**表演腔**。

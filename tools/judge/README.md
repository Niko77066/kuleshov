# G2 评委 harness（Kimi K3 · API 直调）

独立评委席位的工具链（2026-07-21 升级计划 P1-6）。设计出处：`docs/film-ir-context-architecture.md` §2.2——评委物理隔离、只读证据包、评分必须引用镜头 ID/时间码否则判无效、只产报告不改状态。评委与导演**不同模型家族**是特性不是妥协：同族自评共享盲区。

## 三件套

| 脚本 | 干什么 |
|---|---|
| `build_evidence_pack.py <project> [--golden <golden项目>]` | 出证据包：contact sheet 两轮（整数点 + 半步错位）+ 逐镜中点帧 + Golden 并排 sheet + L0 报告 + 隔离 manifest（只含镜头事实，**零创作理由**） |
| `judge.py <pack> --node {hero_frames\|final} [--dry-run]` | 调 Kimi 盲评。hero_frames = ③b 品味门（3 张 hero frame vs Golden，fail 禁止铺开生产）；final = ⑨ 成片门（D1–D9 + 反模式逐条核）。报告落 `<pack>/judge-report-<node>.json` |
| `calibrate.py <scores.csv>` | 人工分 vs 评委分的 Spearman 秩相关（CSV: `film,human_overall,judge_overall`） |

## 凭据

`.env`（worktree 缺失自动回退 git 主仓）：`KIMI_API_KEY`（必需）、`KIMI_BASE_URL`（缺省 `https://new-api.neodrop.ai/v1`）、`KIMI_MODEL`（缺省 `kimi-k3`）。

工程注意（2026-07-21 都踩过）：网关 Cloudflare 拦 python-urllib 的 UA → 全部走 curl + 文件负载；kimi-k3 是推理模型，思考 token 计费且 `max_tokens` 太小时 `content` 为空 → 给足额度、只解析 `message.content`。

## 模型链（2026-07-21 拍板）：kimi-k3 → Gemini 原生视频 fallback

`judge.py` 按链尝试：`kimi-k3`（图片证据）→ `google/gemini-3.1-pro-preview` → `gemini-3.5-flash`（后两者**原生视频理解**：整条 final.mp4 直接入参，含音轨，**禁抽帧**；D5 音画同步因此可全维评审）。可用 `JUDGE_FALLBACK_MODELS` 覆写、`--model` 强制。

Gemini 通路实测（2026-07-21）：
- **凭据分组是坑**：KIMI_API_KEY 的分组（Kimi-MIX-LowCost）没有 Gemini 渠道 → gemini 用 `GEMINI_API_KEY`（缺省回退 `MINIMAX_MUSIC_API_KEY`，其 default 分组实测可达 3.5-flash）；3.1-pro-preview 两个分组当前都无渠道，链条会自动落到 flash；
- **视频入参格式是坑**：OpenAI 兼容层的 `video_url` 部件被网关**静默丢弃**（prompt_tokens 骤降到纯文本量即被丢）；`image_url` 部件携带 `data:video/mp4;base64` 可透传（15MB 实测过，prompt_tokens 7486 证明视频真进去了）；原生 `/v1beta/models/<m>:generateContent` 协议也可用；
- **首个 live 数据点**：hf-ai-agent-breach 成片门，19s 出全 9 维报告，均分 4.78（人工 EP 分 4.67），引用镜头 ID 精准、逐字听写了钩子文案、模板味测试判断正确——校准起点良好；
- 超 30MB 的成片自动转低码率 proxy（完整视频转码，不是抽帧）。

## kimi-k3 leg 状态：被网关稳定性阻塞（2026-07-21）

kimi 腿单独看：证据包与 dry-run 通过，**live 被网关拦（评委因此靠 Gemini fallback 上岗）**。排查留档（下次别重踩）：

- 文本、单图（600KB）、三大图（2.2MB）、12 张小图：全部 ✅；
- 评委完整负载（2 张 sheet + 9 帧 ≈2.2MB，与能过的三图同量级）：稳定 ❌ `get_channel_failed`；逐项剥离 system/response_format/temperature/长文本/图文交错均不解；
- 去掉采样参数后错误变成 **Cloudflare 524（上游超时）**——"渠道不存在（retry）"实为网关把慢的多图推理请求判成渠道失败；`stream:true` 也被同样拦截；
- 结论：kimi-k3 多图 + 长推理输出的组合在该网关的超时窗口内跑不完，属网关侧渠道/超时配置问题，非本 harness 缺陷。**复活路径**：网关调大 vision 渠道超时或直连 Moonshot 官方端点重试 `judge.py`（代码无需改动）。

## 校准协议（先校准后放权，m1-plan 既定纪律）

1. 拿**带人工分的片库**盲评：M0 校准语料 + 2026-07-20 五片对照实验（同 brief、质量分布已知、人工排序已知——天然考卷）；
2. `calibrate.py` 出 Spearman ρ 与逐片偏差；
3. **ρ ≥ 0.7 且评委无系统性放水（均分偏高 ≤ +0.3）之前，评委分只并行记录、不拿否决权**；hero-frame 门在校准期出 fail 时降级为"警示 + 记 ledger"，由 EP 拍板并留痕；
4. 达标后放权：hero_frames fail = 禁止铺开生产；final fail = 禁止 delivered。放权决定由作者拍板，记入本 README。

## 纪律红线

- 评委报告里无镜头 ID/时间码引用的判断会被 `citations_valid=false` 标记——**这样的报告不作数，重评**；
- 评委只写报告文件；往 `ledger.gates` 登记由 EP 执行（附报告路径为证据）；
- 禁止把评委降级成纯文本评委（无图片 = 无效评审）；禁止拿创作过程解释去说服评委。

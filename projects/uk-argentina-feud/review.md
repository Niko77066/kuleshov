# Review / 交接文档 · 英国和阿根廷：什么仇什么怨

> **状态**：compose v3 draft 已出，用户看片仍有问题（未细化）。session 上下文满，交接新 session。
> **新 session 第一步**：读 `film.json` 的 `meta.next_action` + 本文件；然后**请用户逐条列出 draft_v3 的具体问题**（用户只说"还是有很多问题"，需细化才能定点改）。

## 当前产物
- **draft_v3**：`out/draft_v3.mp4`（222.78s，冻结仅 3 段，lint+check 双过）← 最新
- 历史：`out/draft.mp4`(v1) · `out/draft_v2.mp4`

## 三版迭代史 + 用户反馈（重要）
- **v1（文字卡为主）**：13 个 MG 文字卡 + 9 collage + 1 空镜，冻结 20+。用户打回：①布局穿字 ②音色 6 节拼接有跳变 ③音画不同步、画面提前 ④文字画面占比高、转换慢、没耐心。
- **v2（引入真实空镜）**：Pexels 7 真实空镜代文字卡 + MiniMax 整条音轨，冻结 5。用户打回：①音色还在变 ②**音画还不同步（最重要痛点）** ③空镜时间久/反复重复/相关性差。
- **v3（≤3s 快切 + 精确音画 + 最稳音色）← 当前**：音色换 shaonv（测 5 女声最稳 0.907）；音画字幕+画面全钉 whisper 逐词真实戳；空镜 ≤3s 大量快切（28 素材轮换），冻结 3。用户：**"还是有很多问题"（未细化）**。

## 关键决策 / 踩坑（避免重踩）
- **音色**：火山 seed-audio 分节漂移，`reference_audio`/`speaker`/`voice_type` 字段被接口"接受但忽略"（声纹坐实无效）；改 MiniMax `speech-2.8-hd`，**单次可出整条**（无 120s 限）、固定 voice 零拼接。但 MiniMax 所有女声整条声纹仍 **0.84–0.91**（生成式起伏天花板），shaonv 最稳（0.907）。要 >0.95 只能让**用户提供真人音源走 MiniMax 克隆**（`ndclone-` 前缀，代码源 grain `minimax-voice-client.ts`）。详见 memory `tts-longform-minimax`。
- **音画同步（最重要，v3 仍被指有问题）**：根因是 v1/v2 字幕用"字数比例估算"（不准）+ 画面时间自估。v3 已改：字幕(`gen_captions_v2.py`)+ 画面(`find_cues.py` 的 cue)全钉 mlx-whisper 逐词真实戳。**若 v3 仍不同步，下一步试**：① whisperx forced alignment（比 mlx 转写更精确的逐词对齐）② 核查 HyperFrames render 的音/视频轨对齐 ③ 字幕显隐延迟（当前 0.1s）。
- **空镜**：用户要单素材 ≤3s + 大量相关素材快切 + 找不到降文本。v3 已做（`build_compose_v3.py` 的 POOLS 按节相关素材 ≤3s 轮换）。**相关性可再提**：部分是通用素材（如欧洲老城代殖民、现代集装箱船代 1900s 货运），可换更贴的关键词重检索。
- **素材下载**：Pexels 检索(urllib)必须加 `User-Agent`（否则 403）；下载(curl)必须 `-A UA -e https://www.pexels.com/`（Referer）。
- **Seedance collage**：首帧空色场 + 尾帧成品 → assemble-from-empty；实产 ~5.04s/条；死尾查 YDIF；compose 挂载 ≤5s。
- **HyperFrames**：collage/broll 挂入前重编码 `-g 12 -keyint_min 12 -sc_threshold 0` 防 seek 冻帧；`<video>` 必须 muted；`render --strict` 含 lint gate；`--docker` 帧级复现。

## 资产
- 音频：`audio/voiceover.mp3`（shaonv 整条 223s）+ `audio/timeline.json`（逐词 976 戳）
- 像素事件 9：`shots/{s01_banner,s01_1806,s03_invade,s04_belgrano,s04_sheffield,s05_rattin,s05_hand,s05_goal}.mp4`（源静帧 `anchors/*.png`）
- 真实空镜：`compose/assets/broll/`（7，`_g` 后缀）+ `compose/assets/broll2/`（21，`_g` 后缀重编码 720p/做旧）
- 档案照：`anchors/s06_photo.png`（拉廷致敬，做旧黑白，非真人肖像）
- 字幕：`compose/assets/captions_data.js`（108 句 whisper 戳）
- composition：`compose/index.html`（v3）+ `compose/_css_v3.txt`（CSS）

## 脚本（`scripts/`，从 session scratchpad 移入）
- `build_compose_v3.py` — **compose 生成器**（改 PIX 事件 / POOLS 空镜池 / BADGE 角标 → 重跑生成 index.html）
- `gen_captions_v2.py` — 字幕 whisper 逐词精确戳
- `find_cues.py` — 内容词 cue 戳（音画同步锚点）
- `align_full.py` — 整条音轨 → 48k + mlx 逐词 → timeline.json
- `pexels_bulk.py` / `pexels_fetch.py` — Pexels 素材检索下载
- `mm_payload.py` — MiniMax TTS payload（voice/speed/emotion）
- `gen_seedance.py` — Seedance 首尾帧组装 payload
- `gen_image.py` — GPT-Image 像素静帧
- `test_voices.py` / `diag_voice.py` — 音色稳定性声纹

## 未做（v3 问题解决后 → 交付）
1. **解决用户 v3 具体问题**（待细化）
2. BGM 垫乐（pixel-chronicle 要"BGM 垫底"；seed-audio/MiniMax 可生成）
3. 响度归一 -14 LUFS（当前 ~-23）
4. `docker high` final render → `out/final.mp4`
5. ⑩ deliver：成片 + film.json + 成本小结 + git 提交合 main（worktree 合并纪律）
6. `/video-score` 登记 + 成本单价回填（GPT-Image / Seedance / TTS 单价 DEBT）

## 凭据（`.env` 仓库根，gitignored）
`MINIMAX_MUSIC_API_KEY`/`_BASE_URL`(TTS) · `ARK_VIDEO_API_KEY`/`_BASE_URL`(Seedance+GPT-Image) · `PEXELS_API_KEY`/`PIXABAY_API_KEY`(素材) · `AWS_S3_*`(oss-upload.sh) · `VOLC_TTS_API_KEY`(旧 seed-audio，已废)

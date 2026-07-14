# 引擎知识包 · TTS 与音频先行

> 何时读我：audio 阶段开工前；storyboard 需要节拍网格时；compose 混音时。

## 为什么音频先行

文字估时是 OpenMontage 时长反馈环（TTS 超时 → 打回重写）的病根。顺序倒过来：**旁白先定稿，视觉对齐真实音频**。`audio/timeline.json` 定稿后就是全片的时钟，任何视觉时长争议以它为准。

## 接入：火山引擎 seed-audio-1.0（已定，2026-07-14）

- 端点：`POST https://openspeech.bytedance.com/api/v3/tts/create`（**同步**，非流式）
- 鉴权：单 header `X-Api-Key: $VOLC_TTS_API_KEY`，key 在仓库根 `.env`（gitignored，禁入库）；控制台管理页 console.volcengine.com/speech/new/setting/apikeys
- 硬限制：单次输出 ≤ **120s**；`text_prompt` ≤ **3000 字符**；按 `original_duration` 秒计费
- 返回：`url`（**有效期 2 小时，拿到立即下载**）或 `audio`（Base64）；`duration` / `original_duration`
- ⚠️ 曾踩坑：curl 传 JSON 文件要用 `--data-binary @file`，`--data-raw` 不解析 `@`

请求模板（每次调用的完整 payload 与响应都留痕到 `film.json.ledger`）：

```bash
source .env && curl -sS -X POST 'https://openspeech.bytedance.com/api/v3/tts/create' \
  --max-time 300 -H 'Content-Type: application/json' -H "X-Api-Key: $VOLC_TTS_API_KEY" \
  --data-binary @payload.json
```

```json
{
  "model": "seed-audio-1.0",
  "text_prompt": "<声音档描述>朗读：“<旁白文本>”",
  "audio_config": { "format": "mp3", "sample_rate": 48000, "pitch_rate": 0,
                    "speech_rate": 0, "loudness_rate": 0, "enable_subtitle": true },
  "watermark": {}
}
```

### text_prompt 纪律（Kuleshov 专用约束，比 API 能力更严）

seed-audio-1.0 是生成式音频模型：能在一条音频里混环境音、BGM、多角色。**我们禁用这些能力于旁白轨**——旁白轨必须干净（混音契约：音乐/音效独立轨、独立闪避），所以：

- 旁白 `text_prompt` 只写两样：**声音档描述 +「朗读：」+ 文本**；禁止写音效/音乐/多角色标注；
- 声音档描述模板固定在风格包里（如 daily-brief：`一位专业的中文新闻播报员（中年女性，普通话，冷静克制，语速中快）`），跨期逐字复用；
- BGM / 音效**可以**用同一接口单独生成（独立调用、独立轨、独立留痕）——这是白捡的能力，音乐选型时优先考虑。

### 声音一致性（跨节、跨片）

纯文本描述模式下**分节生成音色会漂移**。规则：
- 60s 片 ≤ 120s 上限 → **整片旁白一次生成**（默认）；
- 必须分节时（长片/单节重做），用 `references` 锚定：`speaker`（豆包 2.0 音色 ID）或 `audio_url`/`audio_data`（≤30s 参考音频，可用本栏目首期成品旁白截段——人设声音资产化）；三者互斥只填一个；
- 单节重做后**必须回听接缝两侧**确认音色无跳变。

### 时间戳

`enable_subtitle: true` → 响应带 `subtitle.sentences`（句级时间戳）——audio_timeline 的骨架直接从响应拿（结构首次成功调用后核实并回填本节）。逐词精度与回转写校验仍走 WhisperX。

## 字数预算表（script 阶段硬校验）

| 语言 / 密度 | 60s 预算 | 说明 |
|---|---|---|
| 中文 · 常速叙事 | 220–260 字 | explainer 默认 |
| 中文 · 快报体 | 280–320 字 | news_recap，语速指令调快 |
| 英文 · 常速 | 130–150 词 | |
| 英文 · news 密度 | 165–180 词 | |

超预算砍内容，不掺水、不指望 TTS 加速救场。

## TTS 表演指令写法

每节剧本附带：语速（常速 / 快 / 慢）、停顿点（用 `……` 或 SSML break 标注）、重音词（**加粗**）、语气（陈述 / 设问 / 收束）。忌"表演腔"——宪法条款：宁可平实克制。

## 强制对齐（audio_timeline 的来源）

首选 WhisperX：

```bash
pip install whisperx   # 首次
whisperx audio/voiceover.wav --language zh --output_format json --output_dir audio/
```

把输出整理成：

```json
{ "duration_s": 61.2,
  "sections": [{ "id": "sec01", "t": [0.0, 8.4] }],
  "words": [{ "w": "今天", "t": [0.12, 0.44] }] }
```

**G1 自查（不过必须重做，禁放行）**：
- 回转写文本 vs 剧本，词准确率 ≥ 95%（低于线 = TTS 吐词有问题或音频损坏）；
- 总时长在承诺 ± 5% 内（超了回 script 砍字，走正式修订，不许偷偷变速）。

无法安装对齐工具时的降级：按节用 `ffprobe -show_entries format=duration` 取节级时长 + 句级均分估算，**标记 DEBT**（分镜只能绑到节级精度），出厂前补齐。

## 音乐（有 BGM 需求才读）

- 选曲后记录：BPM、段落结构（intro/verse/chorus）、能量曲线（低/中/高分段）；
- 卡点片：storyboard 的剪辑点布在节拍网格上，chorus 对应视觉能量峰值；
- 授权来源记入 `ledger`（provenance 习惯从 M0 养成）。

## 混音契约（compose 阶段执行，全部机器可验）

- 旁白是主轨；音乐自动闪避（旁白在场时 -12 dB，闪避攻击/释放 ≈ 0.3s/0.8s，风格包可覆写）；
- 生成视频的原生音频只保留环境声层，≤ **-18 dB**；
- 成片响度归一 **-14 LUFS**（`ffmpeg loudnorm`），真峰 ≤ -1 dBTP；
- review 阶段用 ffmpeg `loudnorm print_format=json` 出示证据。

# 引擎知识包 · TTS 与音频先行

> 何时读我：audio 阶段开工前；storyboard 需要节拍网格时；compose 混音时。

## 为什么音频先行

文字估时是 OpenMontage 时长反馈环（TTS 超时 → 打回重写）的病根。顺序倒过来：**旁白先定稿，视觉对齐真实音频**。`audio/timeline.json` 定稿后就是全片的时钟，任何视觉时长争议以它为准。

## 接入位（首次运行时与用户确认，确认后把答案写进本节）

```
TTS provider:        [待定] —— 候选:new-api 网关挂 TTS(蓝图开放点④,未定)/ 其他 API
调用方式:            [待定] —— 命令或 curl 模板写在这里
声音档:              [待定] —— 每个栏目/人设固定一个声音档,跨片一致
```

- 调试链路可用 macOS `say -o` 占位，但 **`say` 的产物禁止出厂**，用了必须记 DEBT。
- 分节生成（每节一个 wav 再拼接），单节重做才便宜。

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

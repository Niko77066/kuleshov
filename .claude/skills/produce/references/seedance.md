# 引擎知识包 · Seedance 2.0（生成视频，烘焙型）

> 何时读我：通路预算选了"完整通路"，且 storyboard 有镜头路由到 `seedance` 时。零成本通路不读。

## 接入（已定并冒烟，2026-07-14；契约源自 grain `ark-video-client.ts` / `fal.ts` + 实测）

- 网关：`$ARK_VIDEO_API_BASE_URL`（https://new-api.neodrop.ai），鉴权 `Authorization: Bearer $ARK_VIDEO_API_KEY`，均在仓库根 `.env`；
- 模型名：**`doubao-seedance-2-0-260128`**（标准款）。备选：`-fast-260128`（快、低质）/ `-mini-260615`。**禁用不带日期的别名**（如 `doubao-seedance-2-0-pro`）——default 分组未挂渠道，直接 503 `model_not_found`；
- 计费：响应头 `x-oneapi-request-id` 是成本反查凭据，**每次调用连同 payload 一起留痕进 `ledger.costs`**；参考：满价一条约 $2.7。

### 请求契约（字段全挂 `metadata` 下，与顶层混用会被忽略或拒绝）

```
POST {base}/v1/videos
{ "model": "doubao-seedance-2-0-260128",
  "prompt": "<英文提示词,@Image1..@ImageN/@Audio1 按 content 顺序 1 起编号>",
  "metadata": {
    "content": [
      { "type": "image_url", "image_url": { "url": "<公网URL>" }, "role": "reference_image" },
      { "type": "audio_url", "audio_url": { "url": "<公网URL>" }, "role": "reference_audio" }
    ],
    "resolution": "480p|720p|1080p",     // 默认 720p
    "ratio": "16:9|4:3|1:1|3:4|9:16|21:9", // 要默认就整个省略,不接受 "auto" 字面量
    "generate_audio": false               // 默认 true;我们默认 false(旁白走 TTS 轨)
  },
  "duration": 4 }                         // 整数 4–15;省略=auto。范围外的值在排队后才被拒且已计费,提交前必须本地校验
```

- submit 返回 `{ id/task_id, status: "queued" }`；轮询 `GET {base}/v1/videos/{id}`（10–20s 间隔），中间态实测为 `in_progress`（判定逻辑写"非 completed/failed 即继续等"，别枚举中间态）；
- 成片 URL 在 **`metadata.url`**（火山 TOS 带签名 URL，**拿到立即下载**）；`metadata.duration` 实测可能缺失，ffprobe 兜底是必须动作；
- 生成耗时：4s/480p 文生视频实测 **~2.5 分钟**；带参考、720p、15s 镜头组按 5–30 分钟预期；
- 纯文生视频（不带 content）也受理（2026-07-14 实测）。

### 实测记录（冒烟 2026-07-14，task_1L7Zk…）

- 请求 4s → **实际产出 5.04s**：实际时长 ≠ 请求时长是常态，**compose 时长调和规则（尾裁→±5%变速→fail）不是防御性设计，是必经路径**；每条 clip 落地必 ffprobe 实测时长回填 `gen.duration_actual_s`；
- "480p" 实际输出 864×496 / 24fps / h264——compose 归一（1080p/30fps）时超分与帧率转换都会发生，质感缝合按此预设；
- 样本：`projects/_smoke/seedance-smoke.mp4`。

## 硬约束

- 单次生成 **4–15s**（整数秒）；
- 参考位：**≤ 9 图**（JPEG/PNG/WebP，单张 ≤30MB，约定 index 0 = 首帧）+ **≤ 3 音频**（MP3/WAV，累计 ≤15s；给音频必须同时至少给一张图）；提示词内用 `@Image1` / `@Audio1` 引用——IR 的 `anchor_refs` 翻译成这套语法；
- **参考文件必须是公网可访问 URL**——本地锚点图要先传图床/OSS（M0 开放项：定一个上传通道再开参考图链路）；
- **极端长宽比的参考图会在受理后才失败且满价计费**——提交前本地 ffprobe 校验长宽比；
- 音频参考会驱动**口型同步人声**（数字人式能力）；但旁白纪律不变：旁白走我们的 TTS 轨，`generate_audio` 默认 false，需要环境声时才开；
- 首尾帧：网关 content 角色支持 `first_frame`/`last_frame`（grain 未暴露、我们待实测），keyframe 锚点走这个角色；
- **必须挂锚点**：无锚点的角色/产品镜头不许生成（一致性问题要在便宜的图像阶段解决，不在贵的视频阶段重摇）。

## 生成单元是镜头组，不是镜头

同场景连续镜头合并为 shot group（**≤ 15s、≤ 5 镜**），用多镜头语法一次生成：

```
Shot 1: [主体@Image1] does [单一主动作], [运镜术语]. Shot 2: ...
```

组内剪辑交给模型；组间才走 IR 级拼接。定点重做的最小颗粒度随之是"组"。

**分组算术是确定性校验，不赌模型细心**（storyboard 自查第 7 项）：每镜恰好属于一组；组时长 ≤ 15s；各组之和 = 承诺时长 ± 公差。

## 组间接缝契约（storyboard 阶段声明，写进 shot_groups[]）

| 类型 | 机制 | 何时用 |
|---|---|---|
| A · 连续动作 | 提取上组**尾帧**作下组首帧，动作续接（LibTV 实测可行） | 同场景动作跨组 |
| B · 硬切 | 无需帧接力 | 场景/时空跳变 |
| C · 转场 | compose 层处理 | 章节边界 |

A 型接缝在 motion 阶段的标准动作：尾帧提取 → 人眼（M0）判断"适合作续接起点吗" → 作为下组 first frame。

## 提示词纪律

- 用摄影术语：dolly / tracking / rack focus / whip pan / POV / snap zoom；
- 写"**什么在动、镜头怎么动、何时换拍**"，禁静态场景描述式提示词；
- 每镜**一个主动作 + 一个运镜**，贪多必糊；
- 首尾帧：高价值镜头（hook / hero）用 keyframe 锚点锁 first/last frame，构图和落点确定，运动交给模型；
- 声音：原生音频只留环境声/效果音（compose 压到 -18dB 以下）；**旁白永远走 TTS 轨**，提示词里不许要人声念白；
- 外观描述禁与锚点冲突（锚点说了算，提示词不重复描述长相）。

## seed 与重做

- 每次生成记 seed（`shots[].gen.seed`）；
- 微调 = **锁 seed 改 prompt**，减少无关漂移；
- 重试 ≤ 2 次，仍败停下来请示；**超时重试时禁止自动丢弃首帧锚定/改参考方式**（LibTV 静默降级反例），改契约必须用户点头。

## 镜头级 QC（每组落地即查，写 shots[].qc）

技术：实际时长 vs 计划（超长走 compose 时长调和：尾裁 → ±5% 变速 → fail）、黑帧、分辨率。
语义（M0 人眼 + 自查）：兑现 shot intent 了吗；肢体/文字畸变；角色 vs 锚点一致；组内镜头数对不对。

## 高风险镜头双候选

hook / hero / 角色首次出场镜头：一次并发 2 候选选优——成本 +1 次生成，重做墙钟归零。M0 手动模式按需使用，花钱前报备用户。

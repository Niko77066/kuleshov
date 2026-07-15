# Review · 800V 热失控

成片:[out/final.mp4](out/final.mp4) · 90.46s · 1920×1080 · 24fps · h264 + aac 48k stereo

## L0 手动仪器复验(证据,非"我检查过了")

| 项 | 目标 | 实测 | 结论 |
|---|---|---|---|
| 时长 | 90s ± 5%（85.5–94.5s） | 90.46s | ✅ PASS |
| 分辨率 / 帧率 | 1920×1080 / 24fps | 1920×1080 / 24fps | ✅ |
| 黑帧（blackdetect d=0.3） | 无 | 无黑帧段 | ✅ |
| 冻结帧（freezedetect d=0.6） | 无 | 无冻结段 | ✅ |
| 响度（ebur128） | -14 LUFS / TP ≤ -1 | **-15.3 LUFS** / LRA 3.5 | ⚠️ 偏低 1.3 LU（容差内、不削波；如需可两遍 loudnorm 精调到 -14） |
| 音轨 | 旁白 + SFX 床已 mux | aac 立体声 90.46s | ✅ |
| 转场词汇 | ≤ 4 种 | hard_cut / white_flash×2(s04,s11) / 剖面切换 / black 0.3s = 4 | ✅ |
| 真运动占比（motion_led） | > 50% | 48.74s / 90.43s = **53.9%** | ✅ |

命令见 [compose/review_l0.sh](compose/review_l0.sh);全片留痕见 [film.json](film.json) `ledger`。

## 待用户裁决（⏸ 评委门 = 你）

请看 **out/final.mp4**,重点看:
1. 叙事链是否顺(新国标钩子 → 膜分解 → 高压锅 → 蔓延 → 800V 电弧 → 拆多米诺 → 国标底线);
2. 混排缝合:Seedance 实景 ↔ MG 图解切换是否自然、LUT 是否统一;
3. SFX 床是否"克制"(会不会盖旁白 / 太吵);
4. 数据卡/时间锚信息是否准、看得清。

## 已知项 / 可选精修(等你点头)

- **s02 / s13 剖面** 当前为 2D SVG。你先前要的真 3D 模组(Three.js proto 已验证,`compose/proto/battery-module-3d.html`)可按需**单镜换入**(定点重做,不重渲整片)。
- 响度可两遍 loudnorm 精确到 -14 LUFS。
- 若某镜不满意,单镜重做(Seedance 锁 seed 改 prompt / MG 改 composition)。

## /video-score 与 /video-triage

出厂前请跑 `/video-score` 登记 7 维分(进片库校准语料);发现问题跑 `/video-triage` 归因到环节。

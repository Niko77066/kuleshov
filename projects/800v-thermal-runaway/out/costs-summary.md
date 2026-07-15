# 成本小结 · 800V 热失控(v1+v2)

预算上限:未设(质量优先,只记账)。request-id 全量留痕见 `film.json ledger.costs`,可逐条反查网关账单。

## 生成调用台账

| 类别 | 次数 | 规格 | 备注 |
|---|---|---|---|
| TTS 旁白(seed-audio-1.0) | 1 | 90.4s 整片一次 | 计费时长 90.4s |
| GPT-Image-2 图 | 5 | medium/1536×864 | 锚点候选×3 + s03 微观层×1 +(a01 首张)|
| Seedance 2.0 视频 | **19** | 1080p/16:9 | v1 hero 候选×4(5.04s,duration顶层bug)+ 时长探针×1(480p)+ v2 正片×7 + v3 重生成×7 |
| HyperFrames docker render | 2 | 90.43s/2171帧 | 31min + 41min |
| 3D 烘焙(headless Chrome) | 149 帧 | 本地,零 API 成本 | s02 |

Seedance 满价参考 ~$2.7/条 → 视频生成成本量级 **~$45-50**(4 条 5s 候选与探针按比例更低;精确金额以 request-id 反查为准)。

## 墙钟(粗计)

brief→script ~1h · audio ~0.5h · storyboard/anchors ~1h · motion v1+v2 ~1.5h · compose+render ~2h · v3 返工+3D ~2h ≈ **8h**(跨 2 天,大量时间为并行等待生成/渲染)

## DEBT 清单

- s02 真 3D 材质偏"图解感"(3 轮 timebox),用户裁决"先这样"——后续可换 PBR 贴图/bloom 后处理或改 Seedance 镜
- 响度 -15.3 LUFS(目标 -14,容差内)可两遍 loudnorm 精调
- TTS 成本反查凭据未存响应头(下片修)
- engineering-anatomy 风格包仍为候选,待 `/benchmark-breakdown` 拉片验证
- v2 评分为自评,待用户看片校准(防漂移)

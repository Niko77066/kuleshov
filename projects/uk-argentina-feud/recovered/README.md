# recovered/ — 2026-07-20 worktree 误删事故抢救区

**事故**：M0 精简清理 worktree 时，英阿片的未入库媒体（gitignored mp4/mp3）只存在于
`claude/uk-argentina-v5-v6-delivery` 的 worktree 工作区，随 `git worktree remove --force` 一起被删。
openai 片当时把媒体复制回了主仓库，英阿片没做这一步。

**本目录来源**：该 worktree 对应 session 的 scratchpad（`/private/tmp/claude-501/...` 不随 worktree 删除），
2026-07-20 抢救回仓库。**mp4/mp3 仍被 gitignore，本目录只在本机存在——处理完前不要再跑任何清理。**

## 存活清单（≈1.1G）

- `stage/` `stage2/` — broll 素材池重编码前的staging（Pexels/Pixabay/公域，v4–v5 全量候选）
- `ia/` — archive.org 档案素材原件（taskforce1 / surrender / 1928 阿根廷纪录片等）
- `news/` — APIhub 新闻素材（Sky/AP 横幅 webm + 审查 contact sheet，broadcast-risk）
- `bgm_raw.mp3` / `bgm_loop.mp3` — MiniMax BGM 原始件与循环件（v5 拼接脚本在 git，可复现 bgm_v5）
- `b2r/ grade/ qc3/ sheets/` — 编码/调色/QC 中间物

## 仍缺失（截至 2026-07-20）

| 缺失物 | 恢复路径 |
|---|---|
| `out/final.mp4`（255.7s 成片） | **首选：用户本地/传输记录里找副本**；否则走全链路重渲 |
| `audio/voiceover_v6.mp3`（MiniMax Gentle_Senior 256.68s） | 只能重生成（同参数≠同 take，需重跑 forced-align→captions→cues） |
| 13 条像素片段 `s0*_s.mp4` | Seedance 重查已试：网关返回原始过期签名 URL（403）。重生成：prompt/seed/首尾帧 refs 全在 film.json + anchors/（tracked），成本约首次的像素部分 |

## 教训（已进 memory + 直写拦截 hook 已上线）

worktree 清理前必须 `git status --porcelain` 检查**未跟踪文件**，尤其 `projects/**/out|audio|shots` 下的
gitignored 媒体；出厂 SOP 增补：deliver 必含"媒体复制回主仓库工作区"一步（openai 片做了，英阿片漏了）。

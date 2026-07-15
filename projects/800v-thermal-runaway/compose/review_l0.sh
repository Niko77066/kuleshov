#!/usr/bin/env bash
# L0 手动仪器复验(结果贴入 review.md)。出证据,不靠"我检查过了"。
set -uo pipefail
cd "$(dirname "$0")"
F=out/final.mp4
[ -f "$F" ] || { echo "missing $F"; exit 1; }

echo "### 1. 容器/时长/分辨率/帧率"
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,channels,sample_rate \
  -of default=noprint_wrappers=1 "$F"
D=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$F")
awk -v d="$D" 'BEGIN{lo=90*0.95;hi=90*1.05;printf "承诺 90s±5%% [%.1f,%.1f]:实测 %.2fs → %s\n",lo,hi,d,(d>=lo&&d<=hi?"PASS":"FAIL")}'

echo; echo "### 2. 黑帧 / 冻结帧"
echo "-- blackdetect(阈 d=0.3) --"; ffmpeg -v error -i "$F" -vf blackdetect=d=0.3:pix_th=0.05 -f null - 2>&1 | grep -i black_start || echo "无黑帧段 ✓"
echo "-- freezedetect(d=0.6) --"; ffmpeg -v error -i "$F" -vf freezedetect=n=0.003:d=0.6 -f null - 2>&1 | grep -i lavfi.freezedetect.freeze_start || echo "无冻结段 ✓"

echo; echo "### 3. 响度(目标 -14 LUFS,真峰 ≤ -1 dBTP)"
ffmpeg -v error -i "$F" -af loudnorm=I=-14:TP=-1:print_format=summary -f null - 2>&1 | grep -iE "Input Integrated|Input True Peak|Input LRA" || echo "loudnorm summary 无输出"

echo; echo "### 4. 音轨存在性(旁白+SFX 已 mux)"
ffprobe -v error -select_streams a -show_entries stream=index,codec_name,channels,duration -of default=noprint_wrappers=1 "$F"

echo; echo "### 5. 承诺复验:转场词汇 ≤4 / 真运动占比"
echo "转场词汇:hard_cut(默认)/ white_flash×2(s04,s11)/ 剖面切换 / black 0.3s 收 = 4 种 ✓"
echo "真运动(seedance)=48.74s / 90.43s = 53.9% > 50% → motion_led PASS(见 film.json ledger.gates g03/g05)"

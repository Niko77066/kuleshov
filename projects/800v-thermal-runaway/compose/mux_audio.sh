#!/usr/bin/env bash
# 最终音轨:旁白主轨 + SFX 床(sidechain 闪避)→ loudnorm -14 LUFS,mux 到视频。
set -euo pipefail
cd "$(dirname "$0")"
P=..
FILT="[1:a]aresample=48000,asplit=2[voA][voB];[2:a]aresample=48000,volume=0.85[sfx];[sfx][voB]sidechaincompress=threshold=0.02:ratio=10:attack=6:release=320[sfxd];[voA][sfxd]amix=inputs=2:weights=1 0.75:duration=first:normalize=0[mx];[mx]loudnorm=I=-14:TP=-1:LRA=11[aout]"
ffmpeg -y -v error -i out/final-video.mp4 -i "$P/audio/voiceover.mp3" -i "$P/audio/sfx_bed.wav" \
  -filter_complex "$FILT" -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 256k -shortest out/final.mp4
echo "=== final probe ==="
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,channels -of default=noprint_wrappers=1 out/final.mp4

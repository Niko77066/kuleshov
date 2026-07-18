#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
用法：
  KULESHOV_RENDER_URL=http://render-host:7300 \
  KULESHOV_RENDER_TOKEN=... \
  HYPERFRAMES_VERSION=0.7.58 \
    tools/render-remote.sh projects/<片名> [输出 MP4]

可选环境变量：
  HYPERFRAMES_COMPOSITION  相对项目根目录的 composition，默认 compose/index.html
  HYPERFRAMES_QUALITY      draft / standard / high，默认 high
EOF
}

project_root=${1:-}
output_path=${2:-}
composition=${HYPERFRAMES_COMPOSITION:-compose/index.html}
quality=${HYPERFRAMES_QUALITY:-high}

if [[ -z "$project_root" ]]; then
  usage >&2
  exit 2
fi
if [[ ! -d "$project_root" ]]; then
  echo "项目目录不存在：$project_root" >&2
  exit 2
fi
if [[ ! -f "$project_root/$composition" ]]; then
  echo "composition 不存在：$project_root/$composition" >&2
  exit 2
fi

: "${KULESHOV_RENDER_URL:?缺少 KULESHOV_RENDER_URL}"
: "${KULESHOV_RENDER_TOKEN:?缺少 KULESHOV_RENDER_TOKEN}"
: "${HYPERFRAMES_VERSION:?缺少 HYPERFRAMES_VERSION}"

case "$quality" in
  draft | standard | high) ;;
  *)
    echo "HYPERFRAMES_QUALITY 只能是 draft / standard / high" >&2
    exit 2
    ;;
esac

if [[ -z "$output_path" ]]; then
  output_path="$project_root/out/final.mp4"
fi
mkdir -p "$(dirname "$output_path")"

archive=$(mktemp --suffix=.tar.gz)
response=$(mktemp)
header_file=$(mktemp)
chmod 600 "$header_file"
printf 'Authorization: Bearer %s\n' "$KULESHOV_RENDER_TOKEN" >"$header_file"
trap 'rm -f "$archive" "$response" "$header_file"' EXIT

# 以项目根为 tar 根，保留 compose 对 ../shots、../audio 等兄弟目录的相对引用。
tar -czf "$archive" \
  --exclude='./out' \
  --exclude='./node_modules' \
  --exclude='./.git' \
  -C "$project_root" .

query=$(python3 - "$HYPERFRAMES_VERSION" "$quality" "$composition" <<'PY'
import sys
from urllib.parse import urlencode

print(urlencode({
    "hyperframesVersion": sys.argv[1],
    "quality": sys.argv[2],
    "composition": sys.argv[3],
}))
PY
)
endpoint="${KULESHOV_RENDER_URL%/}/render/hyperframes?$query"

echo "远程渲染：$project_root/$composition → $output_path"
if ! http_code=$(curl \
  --silent \
  --show-error \
  --connect-timeout 15 \
  --request POST \
  --header "@$header_file" \
  --header 'Content-Type: application/gzip' \
  --data-binary "@$archive" \
  --output "$response" \
  --write-out '%{http_code}' \
  "$endpoint"); then
  [[ ! -s "$response" ]] || cat "$response" >&2
  echo "远程渲染请求失败" >&2
  exit 1
fi

if [[ ! "$http_code" =~ ^2 ]]; then
  cat "$response" >&2
  echo >&2
  echo "远程渲染失败（HTTP $http_code）" >&2
  exit 1
fi
if [[ ! -s "$response" ]]; then
  echo "远程渲染返回空文件" >&2
  exit 1
fi

mv "$response" "$output_path"
echo "远程渲染完成：$output_path"

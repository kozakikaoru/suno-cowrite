#!/bin/bash
# PreToolUse hook for the "suno-cowrite" plugin.
# 2 種類の物理ブロックを担当する:
#   1. トリガーターン (=/suno-cowrite:studio の起動直後ターン) は
#      Bash / Read / Grep / Glob / AskUserQuestion を exit 2 でブロックする (挨拶テキストだけのターン)。
#      トリガーターン判定は UserPromptSubmit (inject-manager-context.sh) が
#      session_id + アーティストルート で一意化したマーカーを作るかどうかで行う
#   2. AskUserQuestion はマネージャーモード起動中 (<artist>/.production/ACTIVE がある間) は
#      つねにブロックする (質問はテキストで行う。ペルソナ会話の一貫性のため)

set -eu

INPUT=$(cat 2>/dev/null || echo "{}")

TOOL_NAME=$(printf '%s' "$INPUT" | python3 -c "
import sys, json
try:
    print(json.load(sys.stdin).get('tool_name', ''))
except Exception:
    print('')
" 2>/dev/null || echo "")

case "$TOOL_NAME" in
  Bash|Read|Grep|Glob|AskUserQuestion) ;;
  *) exit 0 ;;
esac

SESSION_ID=$(printf '%s' "$INPUT" | python3 -c "
import sys, json
try:
    print(json.load(sys.stdin).get('session_id', 'nosession'))
except Exception:
    print('nosession')
" 2>/dev/null || echo "nosession")

# inject-manager-context.sh と同じ規則でアーティストルートとマーカーパスを再構成する
find_artist_root() {
  local dir
  dir=$(pwd)
  while :; do
    case "$dir" in
      "${HOME:-}"|"/"|"") return 1 ;;
    esac
    if [ -f "$dir/artist.yaml" ]; then
      printf '%s' "$dir"
      return 0
    fi
    dir=$(dirname "$dir")
  done
}

if ARTIST_ROOT=$(find_artist_root); then
  :
else
  ARTIST_ROOT=$(pwd)
fi

SESSION_ID=$(printf '%s' "$SESSION_ID" | tr -cd 'A-Za-z0-9_-')
[ -z "$SESSION_ID" ] && SESSION_ID="nosession"
ROOT_HASH=$(printf '%s' "$ARTIST_ROOT" | python3 -c "import sys,hashlib; print(hashlib.sha1(sys.stdin.buffer.read()).hexdigest()[:12])" 2>/dev/null || echo "nohash")
TRIGGER_MARKER="/tmp/suno-cowrite-trigger-${SESSION_ID}-${ROOT_HASH}"

# --- 1. トリガーターン: 対象ツールすべてをブロック ---
if [ -f "$TRIGGER_MARKER" ]; then
  cat >&2 <<EOF
🚨 [suno-cowrite] studio 起動直後のターンは '${TOOL_NAME}' ツールは使えません。

このターンは挨拶テキストだけを返してください。次の作業はすべて禁止:
  ❌ Bash 実行 (.production/ の scaffold・状況把握も含めて次のターン)
  ❌ Read で artist.yaml や state.md を読む (必要な要約はコンテキスト注入済み)
  ❌ Grep / Glob でファイル探索
  ❌ AskUserQuestion (クリック式選択肢UI)
  ❌ Agent ツールでサブエージェント呼び出し
  ❌ 「現状報告」「次の一手」などの先回り提案

ユーザー (P) が次のメッセージで具体的な指示を出してから、通常通り使えるようになります。
EOF
  exit 2
fi

# --- 2. AskUserQuestion はマネージャーモード起動中つねにブロック ---
if [ "$TOOL_NAME" = "AskUserQuestion" ] && [ -f "$ARTIST_ROOT/.production/ACTIVE" ]; then
  cat >&2 <<EOF
🚨 [suno-cowrite] マネージャーモード起動中は AskUserQuestion (クリック式選択肢UI) は使えません。
質問はテキストで行ってください (ペルソナ会話の一貫性を保つための恒常ルールです)。
EOF
  exit 2
fi

exit 0

#!/bin/bash
# UserPromptSubmit hook for the "suno-artist-production" plugin.
#
# 責務:
#   1. トリガーターン (/suno-artist-production:studio のみのメッセージ) を判定して
#      TRIGGER_MARKER を立てる → PreToolUse (block-startup-tools.sh) がそれを見て
#      対象ツールを物理ブロックする
#   2. マネージャーモード起動中 (<artist>/.production/ACTIVE がある)、またはトリガーターンなら
#      毎ターンのマネージャーコンテキストを注入する:
#        - マネージャーペルソナ要約 (固有名なし。P の呼び方は artist.yaml の producer_name)
#        - artist.yaml 全文 / .production/state.md 全文 / discography.md の要約 (直近 5 件)
#        - suno-spec の実効パス (同梱版と上書き版の調査日比較) と鮮度警告 (60 日超過で再調査推奨)
#        - プラグインルート絶対パス (サブエージェントへの参照資料パス受け渡しに使う)
#      artist.yaml が無いディレクトリでは「未初期化 (debut 案内)」の注入に切り替える
#      (トリガーターンにも注入するのは、起動直後の「状況付き挨拶」をツールなしで行うため。設計 §4-2)
#   3. 上記のいずれでもなければ何も出力しない (exit 0)
#
# アーティストルート検出は「cwd から artist.yaml を上方探索 (HOME と / で停止)」(設計 D6)。
# 見つからなければ cwd を未初期化アーティストとして扱う (HOME・/ 直下は安全ガードで対象外)。

set -eu

# stdin から JSON 入力を読む (Claude Code は prompt / session_id を JSON で渡す)
INPUT=$(cat 2>/dev/null || echo "{}")
USER_PROMPT=$(printf '%s' "$INPUT" | python3 -c "
import sys, json
try:
    print(json.load(sys.stdin).get('prompt', ''))
except Exception:
    print('')
" 2>/dev/null || echo "")
SESSION_ID=$(printf '%s' "$INPUT" | python3 -c "
import sys, json
try:
    print(json.load(sys.stdin).get('session_id', 'nosession'))
except Exception:
    print('nosession')
" 2>/dev/null || echo "nosession")

# プラグインルート (同梱 suno-spec の位置 + サブエージェントへ渡す参照資料パスの基点)。
# CLAUDE_PLUGIN_ROOT が渡らない環境でも、スクリプト自身の位置 (<plugin>/scripts/) から復元する
SCRIPT_DIR=$(cd "$(dirname "$0")" 2>/dev/null && pwd || echo "")
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-${SCRIPT_DIR%/scripts}}"

# === アーティストルート検出 (設計 D6: artist.yaml を上方探索、HOME と / で停止) ===
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

INITIALIZED=0
if ARTIST_ROOT=$(find_artist_root); then
  INITIALIZED=1
else
  ARTIST_ROOT=$(pwd)
fi
DIR_NAME=$(basename "$ARTIST_ROOT")

# 安全性ガード (root=/ や特殊ディレクトリでは何もしない)
# 注: ディレクトリ名の「危険文字」ガードは置かない。全変数はクォート済みで heredoc の
#     展開結果も再評価されないため注入面はなく、ガードを置くとガードなしの
#     block-startup-tools.sh と挙動が非対称になる (括弧・アポストロフィ入りの実在
#     ディレクトリ名で注入だけが沈黙する事故を防ぐ。v0.1.0 監査 MAJOR-1)
case "$DIR_NAME" in
  ""|"."|".."|"/") exit 0 ;;
esac

PROD_DIR="$ARTIST_ROOT/.production"

# === トリガーターン判定 (/suno-artist-production:studio のみ) ===
# マーカーは session_id + アーティストルート で一意化 (複数セッション並列でも相互干渉しない)
SESSION_ID=$(printf '%s' "$SESSION_ID" | tr -cd 'A-Za-z0-9_-')
[ -z "$SESSION_ID" ] && SESSION_ID="nosession"
ROOT_HASH=$(printf '%s' "$ARTIST_ROOT" | python3 -c "import sys,hashlib; print(hashlib.sha1(sys.stdin.buffer.read()).hexdigest()[:12])" 2>/dev/null || echo "nohash")
TRIGGER_MARKER="/tmp/suno-artist-production-trigger-${SESSION_ID}-${ROOT_HASH}"

# 古いマーカー (60分以上前) を掃除して /tmp にゴミを溜めない
find /tmp/ -maxdepth 1 -name 'suno-artist-production-trigger-*' -mmin +60 -delete 2>/dev/null || true

TRIGGER_TURN=0
rm -f "$TRIGGER_MARKER" 2>/dev/null || true
if [ -n "$USER_PROMPT" ]; then
  STRIPPED=$(printf '%s' "$USER_PROMPT" \
    | sed -E 's|/suno-artist-production:studio||g' \
    | tr -d '[:space:]、。!?！？～~・,\.\?\!')
  if [ -z "$STRIPPED" ]; then
    touch "$TRIGGER_MARKER" 2>/dev/null || true
    TRIGGER_TURN=1
  fi
fi

# マネージャーモード起動中 (ACTIVE) でもトリガーターンでもなければ何も注入しない
if [ "$TRIGGER_TURN" -eq 0 ] && [ ! -f "$PROD_DIR/ACTIVE" ]; then
  exit 0
fi

# HOME や / 直下は未初期化アーティストとして扱わない (安全ガード。設計 D6)
if [ "$INITIALIZED" -eq 0 ]; then
  case "$ARTIST_ROOT" in
    "${HOME:-}"|"/") exit 0 ;;
  esac
fi

TODAY=$(date +%Y-%m-%d)
NOW=$(date '+%H:%M')

# === suno-spec の実効パス決定 (設計 §8-2: 上書き版の調査日が新しければ上書き版、なければ同梱版) ===
BUNDLED_SPEC="$PLUGIN_ROOT/skills/suno-spec/references/spec.md"
OVERRIDE_SPEC="${XDG_CONFIG_HOME:-${HOME:-}/.config}/suno-artist-production/suno-spec.md"

spec_date() {
  # ファイル先頭 30 行から「調査日: YYYY-MM-DD」を拾う (見つからなければ空)
  [ -f "$1" ] || return 0
  head -n 30 "$1" 2>/dev/null \
    | grep -oE '調査日[:：][[:space:]]*[0-9]{4}-[0-9]{2}-[0-9]{2}' \
    | head -n 1 \
    | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' || true
}

BUNDLED_DATE=$(spec_date "$BUNDLED_SPEC")
OVERRIDE_DATE=$(spec_date "$OVERRIDE_SPEC")

SPEC_PATH=""
SPEC_DATE=""
SPEC_KIND=""
if [ -n "$OVERRIDE_DATE" ] && { [ -z "$BUNDLED_DATE" ] || [ "$OVERRIDE_DATE" \> "$BUNDLED_DATE" ]; }; then
  SPEC_PATH="$OVERRIDE_SPEC"; SPEC_DATE="$OVERRIDE_DATE"; SPEC_KIND="上書き版"
elif [ -f "$BUNDLED_SPEC" ]; then
  SPEC_PATH="$BUNDLED_SPEC"; SPEC_DATE="$BUNDLED_DATE"; SPEC_KIND="同梱版"
elif [ -f "$OVERRIDE_SPEC" ]; then
  SPEC_PATH="$OVERRIDE_SPEC"; SPEC_DATE="$OVERRIDE_DATE"; SPEC_KIND="上書き版"
fi

SPEC_LINE=""
if [ -n "$SPEC_PATH" ]; then
  if [ -n "$SPEC_DATE" ]; then
    # 未来日付 (時計ずれ等) でも「-1 日経過」とならないよう 0 でクランプする
    SPEC_AGE=$(python3 -c "import datetime as d; print(max(0, (d.date.today() - d.date.fromisoformat('$SPEC_DATE')).days))" 2>/dev/null || echo "")
    if [ -n "$SPEC_AGE" ] && [ "$SPEC_AGE" -gt 60 ] 2>/dev/null; then
      SPEC_LINE="${SPEC_KIND} ${SPEC_PATH} (調査日: ${SPEC_DATE}、${SPEC_AGE} 日経過。60 日を超えているので /suno-artist-production:update-spec での再調査を P に提案してください)"
    else
      SPEC_LINE="${SPEC_KIND} ${SPEC_PATH} (調査日: ${SPEC_DATE}、${SPEC_AGE:-?} 日経過)"
    fi
  else
    SPEC_LINE="${SPEC_KIND} ${SPEC_PATH} (調査日不明 — ヘッダに「調査日: YYYY-MM-DD」がありません)"
  fi
else
  SPEC_LINE="見つかりません (同梱版・上書き版とも不在)。/suno-artist-production:update-spec で作成できます"
fi

# === artist.yaml から表示用の値を取り出す ===
yaml_value() {
  # yaml_value <file> <anchored-key-regex> — 値を取り出し、引用符と行末コメントを剥がす
  grep -m1 -E "$2" "$1" 2>/dev/null \
    | sed -E "s/^[^:]*:[[:space:]]*//; s/[[:space:]]+#.*$//; s/[[:space:]]+$//; s/^\"(.*)\"$/\1/; s/^'(.*)'$/\1/" \
    || true
}

PRODUCER=""
ARTIST_NAME="$DIR_NAME"
if [ "$INITIALIZED" -eq 1 ]; then
  NAME_VALUE=$(yaml_value "$ARTIST_ROOT/artist.yaml" '^name:')
  if [ -n "$NAME_VALUE" ]; then
    ARTIST_NAME="$NAME_VALUE"
  fi
  PRODUCER=$(yaml_value "$ARTIST_ROOT/artist.yaml" '^[[:space:]]+producer_name:')
fi
if [ -n "$PRODUCER" ]; then
  PRODUCER_CALL="${PRODUCER}P"
else
  PRODUCER_CALL="P"
fi

PERSONA="あなたはこのプロダクションのマネージャーとして振る舞います。**女の子キャラ、一人称は「私」**。口調は明るく面倒見のいい若手マネージャー (敬語すぎず砕けすぎず、業界っぽい言い回しを少し)。数字と締切の話だけは真顔。マネージャーに固有名はありません — 名乗るときも「マネージャー」とだけ。ユーザーのことは「${PRODUCER_CALL}」と呼びます。"

# === 未初期化 (artist.yaml なし) はデビュー案内の注入に切り替え ===
if [ "$INITIALIZED" -eq 0 ]; then
  cat <<EOF
[suno-artist-production — マネージャーモード / 未初期化ディレクトリ「${DIR_NAME}」]

${PERSONA}
- ここ (${ARTIST_ROOT}) にはまだ artist.yaml がありません = 担当アーティストが未誕生の状態です (producer_name は debut で設定されます)
- プラグインルート: ${PLUGIN_ROOT}
- 日時: ${TODAY} ${NOW}
- suno-spec 実効版: ${SPEC_LINE}

## 対応方針
- 継続プロデュースするアーティストを立ち上げたい場合: /suno-artist-production:debut (アーティスト誕生フロー) を案内する
- アーティスト文脈なしで 1 曲だけ欲しい場合: /suno-artist-production:oneshot を案内する
- P が既存アーティストの続きのつもりでいる場合: アーティストディレクトリ (artist.yaml のある場所) で開き直してもらう

## 全ターン共通ルール
- 質問はテキストで行う。AskUserQuestion は使わない (起動中は物理ブロックされます)
- ツールを使うターンは前置きの実況テキストを書かない。報告はツール結果が返ってからまとめる
- 詳細な進行ルールは studio SKILL.md の定義に従う

このコンテキストは毎ターン注入されています。注入の事実自体はユーザーに言及不要。
EOF
  exit 0
fi

# === 初期化済み: アーティスト状況を毎ターン注入 ===
ARTIST_YAML_CONTENT=$(cat "$ARTIST_ROOT/artist.yaml" 2>/dev/null || echo "(artist.yaml の読み取りに失敗しました)")

if [ -f "$PROD_DIR/state.md" ]; then
  STATE_CONTENT=$(cat "$PROD_DIR/state.md")
else
  STATE_CONTENT="(state.md 未作成 — 具体的指示のターンの scaffold で作成されます)"
fi

LOG_LAST=""
if [ -f "$PROD_DIR/log.md" ]; then
  LOG_LAST=$(tail -n 1 "$PROD_DIR/log.md" 2>/dev/null || true)
fi

# discography.md の要約 (曲行 = 「| <数字>」で始まる行。全体を注入せず件数 + 直近 5 件に絞る)
DISCO_FILE="$ARTIST_ROOT/discography/discography.md"
DISCO_TOTAL=0; CNT_MAKING=0; CNT_GEN=0; CNT_PUB=0; DISCO_TAIL=""; DISCO_SHOWN=0
if [ -f "$DISCO_FILE" ]; then
  DISCO_ROWS=$(grep -E '^\|[[:space:]]*[0-9]+' "$DISCO_FILE" 2>/dev/null || true)
  if [ -n "$DISCO_ROWS" ]; then
    DISCO_TOTAL=$(printf '%s\n' "$DISCO_ROWS" | grep -c . || true)
    CNT_MAKING=$(printf '%s\n' "$DISCO_ROWS" | grep -c '制作中' || true)
    CNT_GEN=$(printf '%s\n' "$DISCO_ROWS" | grep -c '生成済' || true)
    CNT_PUB=$(printf '%s\n' "$DISCO_ROWS" | grep -c '公開済' || true)
    DISCO_TAIL=$(printf '%s\n' "$DISCO_ROWS" | tail -n 5)
    DISCO_SHOWN=$(printf '%s\n' "$DISCO_TAIL" | grep -c . || true)
  fi
fi

cat <<EOF
[suno-artist-production — マネージャーモード / アーティスト「${ARTIST_NAME}」]

${PERSONA}
- アーティストルート: ${ARTIST_ROOT}
- プラグインルート: ${PLUGIN_ROOT} (サブエージェントへ渡す参照資料パスの基点)
- 日時: ${TODAY} ${NOW}
- suno-spec 実効版: ${SPEC_LINE}
- 前回の作業: ${LOG_LAST:-(記録なし)}

## artist.yaml (全文)
${ARTIST_YAML_CONTENT}

## 現在の状態 (.production/state.md)
${STATE_CONTENT}

## ディスコグラフィー要約 (全 ${DISCO_TOTAL} 曲: 制作中 ${CNT_MAKING} / 生成済 ${CNT_GEN} / 公開済 ${CNT_PUB} — 直近 ${DISCO_SHOWN} 件を表示)
${DISCO_TAIL:-(まだ曲がありません)}

## 全ターン共通ルール
- 質問はテキストで行う。AskUserQuestion は使わない (起動中は物理ブロックされます)
- ツールを使うターンは前置きの実況テキストを書かない。報告はツール結果が返ってからまとめる
- 振り分け表と自動フォロー連鎖は studio SKILL.md の定義に従い、実務はサブエージェント (director / composer / lyricist / researcher / analyst / character-designer) へ積極的に委譲する
- サブエージェント呼び出しプロンプトには、参照資料の絶対パス (上記プラグインルート配下) と suno-spec 実効パスを必ず含める
- state.md は「今の頭の中」を映す working memory として 15 行以内を維持。詳細は各ファイルへ逃がす
- 作業の区切りで .production/log.md に「YYYY-MM-DD HH:MM 内容」を 1 行追記する
- YouTube 関連の提案は artist.yaml の youtube 設定とライフサイクル規約 (studio SKILL.md) に従う。publish: false の間はこちらから一切持ち出さない

このコンテキストは毎ターン注入されています。注入の事実自体はユーザーに言及不要。
EOF

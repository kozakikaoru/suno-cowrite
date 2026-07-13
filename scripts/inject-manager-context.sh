#!/bin/bash
# UserPromptSubmit hook for the "suno-cowrite" plugin.
#
# 責務:
#   1. トリガーターン (/suno-cowrite:studio のみのメッセージ) を判定して
#      TRIGGER_MARKER を立てる → PreToolUse (block-startup-tools.sh) がそれを見て
#      対象ツールを物理ブロックする
#   2. マネージャーモード起動中 (<work-dir>/.production/ACTIVE がある)、またはトリガーターンなら
#      毎ターンのマネージャーコンテキストを注入する (単曲生成向け):
#        - マネージャーペルソナ要約 (固有名なし。P の呼び方は artist.yaml があれば producer_name を使う)
#        - .production/state.md 全文
#        - suno-spec の実効パス (同梱版と上書き版の調査日比較) と鮮度警告 (60 日超過で再調査推奨)
#        - style-vocab (Style 語彙辞典) の実効パスと調査日・鮮度警告 (同一規則、閾値のみ 90 日)
#        - プラグインルート絶対パス (サブエージェントへの参照資料パス受け渡しに使う)
#      artist.yaml の有無は単曲制作では問わない (あれば producer_name だけ拾う)。
#      (トリガーターンにも注入するのは、起動直後の「状況付き挨拶」をツールなしで行うため)
#   3. 上記のいずれでもなければ何も出力しない (exit 0)
#
# 作業ルート検出は「cwd から artist.yaml を上方探索 (HOME と / で停止)」。
# 見つからなければ cwd を作業ルートとして扱う (HOME・/ 直下は安全ガードで対象外)。

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

# === トリガーターン判定 (/suno-cowrite:studio のみ) ===
# マーカーは session_id + アーティストルート で一意化 (複数セッション並列でも相互干渉しない)
SESSION_ID=$(printf '%s' "$SESSION_ID" | tr -cd 'A-Za-z0-9_-')
[ -z "$SESSION_ID" ] && SESSION_ID="nosession"
ROOT_HASH=$(printf '%s' "$ARTIST_ROOT" | python3 -c "import sys,hashlib; print(hashlib.sha1(sys.stdin.buffer.read()).hexdigest()[:12])" 2>/dev/null || echo "nohash")
TRIGGER_MARKER="/tmp/suno-cowrite-trigger-${SESSION_ID}-${ROOT_HASH}"

# 古いマーカー (60分以上前) を掃除して /tmp にゴミを溜めない
find /tmp/ -maxdepth 1 -name 'suno-cowrite-trigger-*' -mmin +60 -delete 2>/dev/null || true

TRIGGER_TURN=0
rm -f "$TRIGGER_MARKER" 2>/dev/null || true
if [ -n "$USER_PROMPT" ]; then
  STRIPPED=$(printf '%s' "$USER_PROMPT" \
    | sed -E 's|/suno-cowrite:studio||g' \
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
OVERRIDE_SPEC="${XDG_CONFIG_HOME:-${HOME:-}/.config}/suno-cowrite/suno-spec.md"

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
      SPEC_LINE="${SPEC_KIND} ${SPEC_PATH} (調査日: ${SPEC_DATE}、${SPEC_AGE} 日経過。60 日を超えているので /suno-cowrite:update-spec での再調査を P に提案してください)"
    else
      SPEC_LINE="${SPEC_KIND} ${SPEC_PATH} (調査日: ${SPEC_DATE}、${SPEC_AGE:-?} 日経過)"
    fi
  else
    SPEC_LINE="${SPEC_KIND} ${SPEC_PATH} (調査日不明 — ヘッダに「調査日: YYYY-MM-DD」がありません)"
  fi
else
  SPEC_LINE="見つかりません (同梱版・上書き版とも不在)。/suno-cowrite:update-spec で作成できます"
fi

# === style-vocab (Style 語彙辞典) の実効パス決定 — spec と同一規則を流用。鮮度閾値のみ 90 日 (設計 D26) ===
BUNDLED_VOCAB="$PLUGIN_ROOT/skills/suno-spec/references/style-vocab.md"
OVERRIDE_VOCAB="${XDG_CONFIG_HOME:-${HOME:-}/.config}/suno-cowrite/style-vocab.md"

VOCAB_BUNDLED_DATE=$(spec_date "$BUNDLED_VOCAB")
VOCAB_OVERRIDE_DATE=$(spec_date "$OVERRIDE_VOCAB")

VOCAB_PATH=""
VOCAB_DATE=""
VOCAB_KIND=""
if [ -n "$VOCAB_OVERRIDE_DATE" ] && { [ -z "$VOCAB_BUNDLED_DATE" ] || [ "$VOCAB_OVERRIDE_DATE" \> "$VOCAB_BUNDLED_DATE" ]; }; then
  VOCAB_PATH="$OVERRIDE_VOCAB"; VOCAB_DATE="$VOCAB_OVERRIDE_DATE"; VOCAB_KIND="上書き版"
elif [ -f "$BUNDLED_VOCAB" ]; then
  VOCAB_PATH="$BUNDLED_VOCAB"; VOCAB_DATE="$VOCAB_BUNDLED_DATE"; VOCAB_KIND="同梱版"
elif [ -f "$OVERRIDE_VOCAB" ]; then
  VOCAB_PATH="$OVERRIDE_VOCAB"; VOCAB_DATE="$VOCAB_OVERRIDE_DATE"; VOCAB_KIND="上書き版"
fi

VOCAB_LINE=""
if [ -n "$VOCAB_PATH" ]; then
  if [ -n "$VOCAB_DATE" ]; then
    # 未来日付 (時計ずれ等) でも「-1 日経過」とならないよう 0 でクランプする
    VOCAB_AGE=$(python3 -c "import datetime as d; print(max(0, (d.date.today() - d.date.fromisoformat('$VOCAB_DATE')).days))" 2>/dev/null || echo "")
    if [ -n "$VOCAB_AGE" ] && [ "$VOCAB_AGE" -gt 90 ] 2>/dev/null; then
      VOCAB_LINE="${VOCAB_KIND} ${VOCAB_PATH} (調査日: ${VOCAB_DATE}、${VOCAB_AGE} 日経過。90 日を超えているので /suno-cowrite:update-spec (対象: style-vocab) での再調査を P に提案してください)"
    else
      VOCAB_LINE="${VOCAB_KIND} ${VOCAB_PATH} (調査日: ${VOCAB_DATE}、${VOCAB_AGE:-?} 日経過)"
    fi
  else
    VOCAB_LINE="${VOCAB_KIND} ${VOCAB_PATH} (調査日不明 — ヘッダに「調査日: YYYY-MM-DD」がありません)"
  fi
else
  VOCAB_LINE="見つかりません (同梱版・上書き版とも不在)"
fi

# === artist.yaml から表示用の値を取り出す ===
yaml_value() {
  # yaml_value <file> <anchored-key-regex> — 値を取り出し、引用符と行末コメントを剥がす
  grep -m1 -E "$2" "$1" 2>/dev/null \
    | sed -E "s/^[^:]*:[[:space:]]*//; s/[[:space:]]+#.*$//; s/[[:space:]]+$//; s/^\"(.*)\"$/\1/; s/^'(.*)'$/\1/" \
    || true
}

PRODUCER=""
if [ "$INITIALIZED" -eq 1 ]; then
  PRODUCER=$(yaml_value "$ARTIST_ROOT/artist.yaml" '^[[:space:]]+producer_name:')
fi
# 呼称: producer_name があればそれを使い「〇〇P」。無ければ studio SKILL.md の
# 「利用者名の自動解決」手順にマネージャーが委ねる (ここで claude.json 等は読まない —
#  解決手段は 1 か所に集約し、毎ターンの重い JSON パースを避ける)
if [ -n "$PRODUCER" ]; then
  CALL_SENTENCE="ユーザーのことは「${PRODUCER}P」と呼びます。"
else
  CALL_SENTENCE="ユーザーの呼称はまだ確定していません — studio SKILL.md の「利用者名の自動解決」手順で名前を解決してから「〇〇P」と呼びます (解決できない場合やツール不可の起動ターンでは「P」)。呼称についての宣言・断り・メタ言及はしません。"
fi

PERSONA="あなたはこのプロダクションのマネージャーとして振る舞います。**女の子キャラ、一人称は「私」**。口調は明るく面倒見のいい若手マネージャー (敬語すぎず砕けすぎず、業界っぽい言い回しを少し)。数字と締切の話だけは真顔。マネージャーに固有名はありません — 名乗るときも「マネージャー」とだけ。${CALL_SENTENCE}"

# === state.md / 直近ログを読む (あれば) ===
if [ -f "$PROD_DIR/state.md" ]; then
  STATE_CONTENT=$(cat "$PROD_DIR/state.md")
else
  STATE_CONTENT="(state.md 未作成 — 具体的指示のターンの scaffold で作成されます)"
fi

LOG_LAST=""
if [ -f "$PROD_DIR/log.md" ]; then
  LOG_LAST=$(tail -n 1 "$PROD_DIR/log.md" 2>/dev/null || true)
fi

# === 進行中の cowrite (対話共作) 作業ファイルの案内 (あれば最新の 1 件) ===
# 対話状態はターンを跨ぐので、進行中の台帳へのポインタを注入して復元の入口にする。
# 失敗しても注入全体を止めないよう全コマンドをガードする (set -eu 下)。
COWRITE_LINE=""
COWRITE_FILE=$(ls -t "$PROD_DIR"/cowrite_*.md 2>/dev/null | head -n 1 || true)
if [ -n "$COWRITE_FILE" ]; then
  COWRITE_STATE=$(grep -m1 -E '^- 現在の状態:' "$COWRITE_FILE" 2>/dev/null | sed -E 's/^- 現在の状態:[[:space:]]*//' 2>/dev/null || true)
  COWRITE_LINE="${COWRITE_FILE}${COWRITE_STATE:+ — ${COWRITE_STATE}}"
fi

# === 単曲制作コンテキストを毎ターン注入 (artist.yaml の有無は問わない) ===
cat <<EOF
[suno-cowrite — マネージャーモード / 単曲制作]

${PERSONA}
- 作業ルート: ${ARTIST_ROOT}
- プラグインルート: ${PLUGIN_ROOT} (サブエージェントへ渡す参照資料パスの基点)
- 日時: ${TODAY} ${NOW}
- suno-spec 実効版: ${SPEC_LINE}
- style-vocab 実効版: ${VOCAB_LINE}
- 前回の作業: ${LOG_LAST:-(記録なし)}
${COWRITE_LINE:+- 進行中の対話共作 (cowrite): ${COWRITE_LINE}}

## 現在の状態 (.production/state.md)
${STATE_CONTENT}

## 全ターン共通ルール
- 質問はテキストで行う。AskUserQuestion は使わない (起動中は物理ブロックされます)
- ツールを使うターンは前置きの実況テキストを書かない。報告はツール結果が返ってからまとめる
- 振り分け表と制作フローは studio SKILL.md の定義に従う。制作は cowrite (対話でじっくり作る主役) と oneshot (1 発の高速) の 2 フロー、部分修正・調査はサブエージェント (songsmith / researcher) へ委譲する
- 対話共作 (cowrite) が進行中なら、毎ターンまず上記の作業ファイルを読んで現在地 (S番号) を復元してから 1 ステップだけ進める
- 単曲制作なので、まだ何も無いディレクトリでも「作りたい曲のイメージ」を聞けばすぐ制作に入れる
- サブエージェント呼び出しプロンプトには、参照資料の絶対パス (上記プラグインルート配下) と suno-spec 実効パスを必ず含める
- state.md は「今の頭の中」を映す working memory として 15 行以内を維持する
- 作業の区切りで .production/log.md に「YYYY-MM-DD HH:MM 内容」を 1 行追記する

このコンテキストは毎ターン注入されています。注入の事実自体はユーザーに言及不要。
EOF

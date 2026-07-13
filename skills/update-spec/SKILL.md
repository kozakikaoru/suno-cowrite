---
name: update-spec
description: Suno 仕様の再調査・更新。「Suno の仕様変わった?」「新モデル出た?」「spec が古いみたい」「Suno の最新情報に更新して」などの発言、spec 鮮度警告 (調査日から 60 日超過) への対応、または /suno-artist-production-x:update-spec で起動。Style 語彙辞典 (style-vocab) の更新も同フローで扱う — 「Style に効く言葉を調べて」「語彙辞典を更新して」などの発言、または style-vocab 鮮度警告 (調査日から 90 日超過) で対象に加える。リサーチャーが現行版を差分調査し、更新版をユーザー設定ディレクトリの上書き版に保存、update-log.md に履歴を残して P に差分を報告する。同梱版は書き換えない。
---

# Suno 仕様更新 — /suno-artist-production-x:update-spec

suno-spec (モデル一覧・文字数上限・メタタグ語彙などの参照仕様) をリサーチャーに再調査させ、更新版を保存するフロー。マネージャー (メイン会話のペルソナ) として進行する。スラッシュ起動でも、鮮度警告からの自発起動 (Skill ツール) でも同じフローに従う。

**書き込み先はユーザー設定ディレクトリの上書き版 (`${XDG_CONFIG_HOME:-~/.config}/suno-artist-production-x/` 配下の `suno-spec.md`、style-vocab 対象時は `style-vocab.md`) のみ。同梱版 (`<プラグインルート>/skills/suno-spec/references/` 配下) は絶対に書き換えない。** 2 層構造と実効版の判定規則は `<プラグインルート>/skills/suno-spec/SKILL.md` に定義されている。

## このスキル実行中の共通ルール

- ユーザーは「〇〇P」と呼ぶ (producer_name 未設定時は「P」)
- 質問はテキストで行う。AskUserQuestion は使わない
- ツールを使うターンでは前置きの実況テキストを書かず、報告はツール結果が返ってからまとめる
- サブエージェント起動プロンプトには、参照させるファイルの**絶対パス**を必ず書く。プラグインルートは hook が注入する絶対パスを使う (未注入なら、この SKILL.md の読み込み元 `<プラグインルート>/skills/update-spec/SKILL.md` から 2 階層上をプラグインルートとする)
- Suno の仕様は全アーティスト共通の外部事実。**このスキルは artist.yaml 不要**で、どのディレクトリからでも実行できる
- 作業の区切りで `.production/log.md` に 1 行追記し、`.production/state.md` を最新化する (scaffold できたディレクトリの場合のみ)

## 対象の決定 (spec / style-vocab)

更新対象は既定で **spec のみ**。次のどちらかに該当するときは **style-vocab (Style 語彙辞典)** を対象に加える (spec 側に更新の必要がなければ style-vocab 単独でもよい):

- (a) **P の明示** — 「Style に効く言葉を調べて」「語彙辞典を更新して」など、辞典側への言及
- (b) **hook 注入の style-vocab 鮮度警告** — 調査日から **90 日超過** (spec の 60 日とは別閾値)

style-vocab を対象にするときの差分 (書いていないことは spec と同じ手順に従う):

- **Step 1**: 実効版の判定規則は同一。同梱版 `<プラグインルート>/skills/suno-spec/references/style-vocab.md` / 上書き版 `${XDG_CONFIG_HOME:-~/.config}/suno-artist-production-x/style-vocab.md`
- **Step 2**: **researcher は対象ごとに別実行する** (調査規約が異なるため 1 つのプロンプトに混ぜない)。style-vocab 用の調査規約: 公式一次情報がほぼ無い領域のため、コミュニティの複数ソース突き合わせと実験報告 (A/B・統制実験) の収集を主軸に確度を判定する (確度基準は style-vocab §1 の High / Med / Low / 未検証)。維持契約は「先頭付近の `調査日: YYYY-MM-DD` 行 + §1〜§9 構成 + 表スキーマ (`日本語の意図 / 英語記述子 (推奨) / 日本語表記の挙動 / 確度 / 相性ジャンル / 備考`)」。現行の上書き版に P の実測追記 (style-vocab §8) があれば全文を渡し、再調査結果と**マージして保持させる** (実測を捨てない)
- **Step 3**: 保存先は `$CONF_DIR/style-vocab.md` のみ。update-log.md は spec と共用で、行内に `(style-vocab)` を含める — 例: `- YYYY-MM-DD 再調査 (style-vocab) — 情景語 2 語を Med に昇格`
- **Step 5**: 対象外 (validate_song.py は語彙辞典を参照しない)

## Step 0 — 前提チェック (scaffold)

```bash
DIR="$PWD"; ARTIST_ROOT=""
while :; do
  if [ -f "$DIR/artist.yaml" ]; then ARTIST_ROOT="$DIR"; break; fi
  if [ "$DIR" = "$HOME" ] || [ "$DIR" = "/" ]; then break; fi
  DIR=$(dirname "$DIR")
done
[ -n "$ARTIST_ROOT" ] || ARTIST_ROOT="$PWD"
if [ "$ARTIST_ROOT" = "$HOME" ] || [ "$ARTIST_ROOT" = "/" ]; then
  echo "UNSAFE_DIR"
else
  mkdir -p "$ARTIST_ROOT/.production"
  touch "$ARTIST_ROOT/.production/ACTIVE"
  [ -f "$ARTIST_ROOT/.production/state.md" ] || printf '# state\n\n- 現在フォーカス: (未設定)\n- 進行中の曲: (なし)\n- 未解決事項: (なし)\n- 次のアクション: (なし)\n' > "$ARTIST_ROOT/.production/state.md"
  [ -f "$ARTIST_ROOT/.production/log.md" ] || : > "$ARTIST_ROOT/.production/log.md"
  echo "ARTIST_ROOT=$ARTIST_ROOT"
  if [ -f "$ARTIST_ROOT/artist.yaml" ]; then echo "artist=yes"; else echo "artist=no"; fi
fi
```

- 以降の `$ARTIST_ROOT` は、ここで判明した絶対パスに置き換えて使う
- artist.yaml が無くても実行できる (spec はユーザー単位の共有物)。`UNSAFE_DIR` でも更新フロー自体は進められる (log.md / state.md の記録なしで動く)

## Step 1 — 現行 spec (実効版) の特定

hook 注入コンテキストの「suno-spec 実効版」の絶対パスをそのまま使う。未注入の文脈では次で判定する (調査日は ISO 形式のため文字列比較がそのまま新旧比較になる。新しい方が実効版、上書き版が無ければ同梱版):

```bash
PLUGIN_ROOT="<プラグインルートの絶対パス>"
CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/suno-artist-production-x"
for f in "$PLUGIN_ROOT/skills/suno-spec/references/spec.md" "$CONF_DIR/suno-spec.md"; do
  if [ -f "$f" ]; then
    D=$(head -n 30 "$f" | grep -oE '調査日[:：][[:space:]]*[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -n 1 | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}')
    echo "${D:-不明} $f"
  fi
done
```

- 実効版を Read して全文を手元に置く (Step 2 でリサーチャーに渡す)
- 同梱版・上書き版とも見つからない (異常時) → 実効版なしとして進め、Step 2 では差分調査ではなく **spec の新規作成**を依頼する (下記のセクション構成契約を守らせる)

## Step 2 — リサーチャー起動

subagent_type `suno-artist-production-x:researcher` を起動する。プロンプトに含めるもの:

1. **現行 spec の全文** (実効版の内容をそのまま貼る) と、その調査日・実効版の絶対パス
2. **調査規約**:
   - 公式一次情報 (Suno の release notes / help / blog) を最優先し、非公式情報は複数ソースの突き合わせで確度を判断する
   - すべての事実に出典 (URL + 取得日) を付す
   - 各項目に確度 (High / Med / Low) を付し、事実と推測を分ける
   - 無料の手段のみ (WebSearch / WebFetch / curl)
3. **維持すべき契約** (更新版が壊してはいけない形式):
   - セクション構成 §1〜§9 (モデル一覧 / Custom Mode 上限 / Advanced Options / メタタグ語彙 / Style 記法 / Persona・Voices・Custom Models / 日本語入稿対策 / プラン・商用権 / API 状況) を維持する
   - 先頭付近に、行頭から装飾なしで `調査日: YYYY-MM-DD` (今日の日付) の行を必ず置く (hook が新旧比較のため機械抽出する。位置と形式を変えない)
4. 返してもらうもの: **差分サマリ** (変わった点 / 変わっていないことを確認した点、それぞれ出典付き) + **更新版 spec.md の全文**

保存先はリサーチャーに渡さない (保存は Step 3 でマネージャーが行う。設計 §8-3)。

## Step 3 — 上書き版の保存と更新履歴

```bash
CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/suno-artist-production-x"
mkdir -p "$CONF_DIR"
```

1. 受領した更新版全文を `$CONF_DIR/suno-spec.md` に保存する。**保存前に必ず確認**: `調査日: <今日>` の行が契約どおりあるか / §1〜§9 が揃っているか / 出典と確度が残っているか。欠けていたら researcher に差し戻す (欠けたまま保存しない)
2. 更新履歴 `$CONF_DIR/update-log.md` に 1 行追記する。ファイルが無ければ、同梱版 `<プラグインルート>/skills/suno-spec/references/update-log.md` を複製して作成してから追記する。形式は追記専用・1 件 1 行:
   - 差分あり: `- YYYY-MM-DD 再調査 — <差分の要約 1 行>`
   - 差分なし: `- YYYY-MM-DD 再調査 — 変更なし (調査日のみ更新)`
3. 同梱版 (`<プラグインルート>/skills/suno-spec/references/` 配下) には何も書き込まない

## Step 4 — P への差分報告

- 差分サマリを報告する (新モデル / 文字数上限 / Advanced Options / メタタグ語彙 / Persona 系 / プラン・商用権 / API 状況の順で、**変化があった項目だけ**を出典付きで)
- **変更が無かった場合も「変更なし」を結果として報告する** (仕様が安定していると確認できたこと自体が成果。鮮度がリセットされ、60 日警告も消える)
- 以後のターンからは hook が新しい上書き版を実効版として注入する

## Step 5 — 定数・既定モデルの見直し提案 (自動書き換えしない)

差分が次に触れる場合だけ行う。**どちらもマネージャーが勝手に書き換えない** (プラグイン本体の変更とアーティストの質感統一は P の判断事項):

- **文字数上限・スライダー閾値・メタタグ語彙が変わった** → `<プラグインルート>/scripts/validate_song.py` 冒頭の定数ブロック (`SPEC_SNAPSHOT_DATE` / `TITLE_MAX_CHARS` / `STYLE_MAX_CHARS` / `LYRICS_MAX_CHARS` / `META_TAG_VOCAB` など) を読んで突き合わせ、不一致を**警告として P に報告する**。例: 「spec では Style 上限が変わりましたが、検証スクリプトは 1,000 字のままです。スクリプトを更新するまで、検証は古い上限で判定します」
- **推奨既定モデルが変わった** → artist.yaml の `suno.preferred_model` の見直しを提案する。P が「変える」と明言したときだけ artist.yaml を更新する (`artist=yes` のディレクトリで実行している場合。既定モデルの変更は曲の質感に直結するため、メリットと注意点を添えて提案する)

## 後処理

- `artist=yes` のディレクトリで実行した場合のみ: `.production/log.md` に 1 行追記し (例: `2026-07-10 19:00 update-spec: spec 更新 — 変更なし`)、`.production/state.md` を最新化する

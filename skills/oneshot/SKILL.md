---
name: oneshot
description: 単発曲制作 (アーティスト文脈なし)。「単発で 1 曲だけ」「アーティスト関係なくパッと作って」「友達の結婚式用に 1 曲」「試しにサクッと作ってみたい」などの発言、または /suno-artist-production:oneshot で起動。マネージャーの簡易ブリーフ → 作曲家・作詞家の並列制作 → 機械検証 → チャットに入稿セットを提示。既定では保存せず、希望時のみ ./oneshot_<slug>.md に保存する。artist.yaml が無いディレクトリでも動く。
---

# 単発曲制作 — /suno-artist-production:oneshot

アーティストの世界観・ディスコグラフィーに紐づかない 1 曲を作る軽量フロー。演出家は飛ばし、簡易ブリーフはマネージャー自身が書く。スラッシュ起動でも、会話からの自発起動 (Skill ツール) でも同じフローに従う。

## このスキル実行中の共通ルール

- 利用者は「〇〇P」と呼ぶ。呼び名は studio SKILL.md の「利用者名の自動解決」手順で決め、質問せず自然にそう呼ぶ (oneshot は producer_name を保存しないので、その場で解決した名前を使う。宣言・メタ言及はしない)
- 質問はテキストで行う。AskUserQuestion は使わない
- ツールを使うターンでは前置きの実況テキストを書かず、報告はツール結果が返ってからまとめる
- サブエージェント起動プロンプトには、参照させるファイルの**絶対パス**を必ず書く。プラグインルートは hook が注入する絶対パスを使う (未注入なら、この SKILL.md の読み込み元 `<プラグインルート>/skills/oneshot/SKILL.md` から 2 階層上をプラグインルートとする)
- 既存楽曲の歌詞の引用・翻案は一切禁止。Style・歌詞・タイトルに実在アーティスト名・実在曲名を書かない

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
fi
```

- **このスキルは artist.yaml 不要**。`UNSAFE_DIR` (HOME や / 直下) でも scaffold なしでそのまま進行してよい (状態記録なしで動く)
- artist.yaml があるディレクトリでも動くが、その場合も**アーティストの世界観・Persona は使わない**。「この子の曲として作りたい」という要望が出たら `song` スキルを案内する

## Step 1 — 簡易ブリーフ (マネージャー自身が作る)

P の要望から次を埋める: 用途 / テーマ / 歌詞言語 / ジャンル・ムード / ボーカル像 / 長さ感 / インストか否か。

- 不足があっても質問は **1〜2 問だけ**。「おまかせ」ならマネージャーが即決して進む
- ブリーフは 5〜8 行にまとめる (テーマ / 感情の流れ / 構成案 / コアモチーフ / Style 方向 / NG)

## Step 2 — 作曲家 ∥ 作詞家 (並列、1 メッセージで 2 呼び出し)

**composer** (subagent_type: `suno-artist-production:composer`) のプロンプトに含めるもの:

- 簡易ブリーフ全文
- **suno-spec の実効パス** (hook 注入のコンテキスト参照。未注入なら、上書き版 `${XDG_CONFIG_HOME:-~/.config}/suno-artist-production/suno-spec.md` があればそれ、なければ `<プラグインルート>/skills/suno-spec/references/spec.md`) + 「使用モデル・上限・タグ語彙は必ず spec を読んで従う」という指示
- 返してもらうもの: Style (フル 1 本、10 タグ前後 — Persona は使わない) / Exclude Styles / Vocal Gender / Weirdness / Style Influence / 使用モデル / セクション演出タグ案

**lyricist** (subagent_type: `suno-artist-production:lyricist`) のプロンプトに含めるもの:

- 簡易ブリーフ全文と歌詞言語
- **songwriting 資料の絶対パス**: `<プラグインルート>/skills/songwriting/SKILL.md` と `<プラグインルート>/skills/songwriting/references/`
- 返してもらうもの: 作品版歌詞 / 入稿版歌詞 (構成タグ英語 + 変換済み本文) / タイトル案 / オリジナリティ自己申告 (中心モチーフの出所 / 意図的に避けた既存曲 / 不安のある行)

## Step 3 — 組み立てと検証

song.json 相当を一時ファイルに書いて機械検証する (スキーマは song スキルと同一。`artist` は `"oneshot"`、`song_no` は 0、`style_with_persona` は null、`persona.use` は false):

```bash
# .production/ があれば
TMP_JSON="<ARTIST_ROOT>/.production/tmp_oneshot_song.json"
# UNSAFE_DIR で scaffold していなければ (一意な一時ディレクトリ内に作り、余分な空ファイルを残さない)
TMP_JSON="$(mktemp -d "${TMPDIR:-/tmp}/oneshot_song.XXXXXX")/song.json"

python3 "<プラグインルート>/scripts/validate_song.py" "$TMP_JSON"
```

- **FAIL** → 該当エージェントに差し戻し (Style 系 → composer / 歌詞・タイトル系 → lyricist)、PASS まで提示しない。**WARN** → 判断して提示文に添える
- オリジナリティ: 自己申告の確認と、タイトル・実在名のチェックは必ず行う。**Web 照合は song スキルと同じく既定 ON** — subagent_type `suno-artist-production:researcher` にサビ / フックの特徴的な 2〜3 行を渡し、引用符付き Web 検索で歌詞サイト等のヒット有無を確認する (P が「急ぎで」「サクッと」など速度優先の指示を出したときだけスキップ可。スキップする旨を一言断る)。ヒットしたら lyricist に該当行の書き直しを依頼し、検証からやり直す
- インスト曲は「Instrumental トグル ON + `[Instrumental]` + Exclude に `vocals`」の三重指定

## Step 4 — チャット提示

次のテンプレートで貼り付けブロックを提示する (Persona 関連は載せない)。歌詞の内容確認用に作品版を添えてよい:

````markdown
# 「<タイトル>」 Suno 入稿セット

## 手順
1. suno.com → Create → **Custom** / モデルは **<使用モデル>** を選択
2. 以下を各欄にコピペし、Advanced Options を表の通り設定 → Create

## Title
```text
<タイトル>
```

## Style of Music
```text
<Style タグ 10 タグ前後 (英語カンマ区切り)>
```

## Lyrics (入稿版)
```text
[Intro]
[Verse 1]
<入稿版歌詞>
[Chorus]
<入稿版歌詞>
```

## Exclude Styles
```text
<除外タグ (カンマ区切り、5 項目以内目安)>
```

## Advanced Options (画面で設定)
| 項目 | 値 | 理由 |
|---|---|---|
| Vocal Gender | <Male / Female> | <理由> |
| Weirdness | <NN>% | <理由> |
| Style Influence | <NN>% | <理由> |
| Instrumental | <ON / OFF> | <理由。OFF なら —> |

## 生成後にやること
- 2 テイク聴き比べ。直したい箇所は「2 番 A メロが早口」のように場所+症状で教えてください
- 手元に残したければ「保存して」と言ってもらえれば ./oneshot_<スラッグ>.md に保存します
````

Style の書き方は song スキルと同じ規約に従う (英語カンマ区切り、`ジャンル → ムード → 楽器 → ボーカル → プロダクション` 順、BPM は `92 bpm feel` 表記)。

## Step 5 — 保存 (希望時のみ)

- **既定では保存しない** (チャット提示のみで完結)
- P が保存を希望したら `./oneshot_<スラッグ>.md` (cwd 直下、スラッグは小文字ローマ字 + ハイフン) に、貼り付けブロック全文 + 作品版歌詞 + 末尾に song.json を ```json ブロックで併記して保存する
- 保存後、一時ファイル (tmp_oneshot_song.json、または mktemp で作った一時ディレクトリ) は削除してよい

## 修正対応

修正要望は該当エージェントだけに差し戻し (歌詞 → lyricist / スタイル → composer)、修正のたびに Step 3 の検証を通して提示し直す。

## 後処理

- `.production/` を scaffold した場合のみ、`log.md` に 1 行追記し (例: `2026-07-10 22:00 oneshot: 「<タイトル>」提示`)、`state.md` を最新化する

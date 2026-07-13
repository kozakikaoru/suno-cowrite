---
name: oneshot
description: 単発曲制作 (アーティスト文脈なし)。「単発で 1 曲だけ」「アーティスト関係なくパッと作って」「友達の結婚式用に 1 曲」「試しにサクッと作ってみたい」などの発言、または /suno-cowrite:oneshot で起動。マネージャーの簡易ブリーフ → 制作 (songsmith) が Style + 歌詞 + タイトルを一括制作 → build_submission_lyrics.py で入稿版を機械変換 → 機械検証 → チャットに入稿セットを提示。既定では保存せず、希望時のみ ./oneshot_<slug>.md に保存する。artist.yaml が無いディレクトリでも動く。
---

# 単発曲制作 — /suno-cowrite:oneshot

1 曲を単発で作る軽量フロー。簡易ブリーフはマネージャー自身が書く。スラッシュ起動でも、会話からの自発起動 (Skill ツール) でも同じフローに従う。

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
- artist.yaml があるディレクトリでも動くが、その場合も**アーティストの世界観・Persona は使わない** (常に単発曲として作る)

## Step 1 — 簡易ブリーフ (マネージャー自身が作る)

P の要望から次を埋める: 用途 / テーマ / 歌詞言語 / ジャンル・ムード / ボーカル像 / 長さ感 / インストか否か。

- 不足があっても質問は **1〜2 問だけ**。「おまかせ」ならマネージャーが即決して進む
- ブリーフは 5〜8 行にまとめる (テーマ / 感情の流れ / 構成案 / コアモチーフ / Style 方向 / NG / 韻プロファイル)
- **韻プロファイル**は standard / heavy の 1 行。P が「韻重視」「ラップ曲」「ヒップホップ」等と明示したとき、またはラップ/ヒップホップ系ジャンルで [Rap] が主役級のときだけ heavy にする (heavy 時は主戦場セクションと軸の方向を添える)。それ以外は standard

## Step 2 — 制作 (songsmith) 一括制作

**songsmith** (subagent_type: `suno-cowrite:songsmith`) を 1 回だけ起動する。1 起動で Style + 作品版歌詞 + タイトル (+ 韻プロファイル heavy の日本語曲は韻設計) をまとめて返す。プロンプトに含めるもの:

- 簡易ブリーフ全文 (韻プロファイルを含む) と歌詞言語
- **suno-spec の実効パス** (hook 注入のコンテキスト参照。未注入なら、上書き版 `${XDG_CONFIG_HOME:-~/.config}/suno-cowrite/suno-spec.md` があればそれ、なければ `<プラグインルート>/skills/suno-spec/references/spec.md`) + 「使用モデル・上限・タグ語彙・スライダー定石は必ず spec を読んで従う」という指示
- **制作コア束ねの絶対パス**: `<プラグインルート>/skills/production/references/write_core.md` (毎回必読 = 作曲 + 作詞)。**韻プロファイルが heavy かつ日本語**なら `<プラグインルート>/skills/production/references/rhyme_core.md` も。「無ければ composing/songwriting の原本から必要分を読んでよい」と添える
- **style-vocab の実効パス** (hook 注入のコンテキスト参照。未注入なら、上書き版 `${XDG_CONFIG_HOME:-~/.config}/suno-cowrite/style-vocab.md` があればそれ、なければ `<プラグインルート>/skills/suno-spec/references/style-vocab.md`)
- **条件付きプレイブック (該当する曲だけ)**: 語り主導 (ポエトリー) は `<プラグインルート>/skills/composing/references/06_poetry-spoken.md`、K-POP 系は `<プラグインルート>/skills/composing/references/04_kpop.md`、HIPHOP/ラップ系は `<プラグインルート>/skills/songwriting/references/10_hiphop-genre-ja.md` の絶対パス (「該当節を必読。無ければ束ねの範囲で進めてよい」と添える)
- 返してもらうもの: **Style (フル 1 本、10 タグ前後 — oneshot では Persona は使わない)** / Exclude / Vocal Gender / Weirdness / Style Influence / 使用モデル / セクション演出タグ案 / 韻設計 (heavy のみ) / **作品版歌詞** (漢字かな交じり。難読・当て字にルビ注釈。**入稿版は書かせない** — Step 3 で機械変換する) / タイトル案 / オリジナリティ自己申告

**信頼性 (D40)**: songsmith が「不足: 〇〇」と返したら不足を補って**1 回だけ**再起動する。2 回連続で同じ不足なら止めて P に確認する (多重・無限リトライ禁止)。形式が崩れて返ったら部分成果をそのまま見せて握らせる (全体を止めない)。

## Step 3 — 組み立てと検証

song.json 相当を一時ファイルに書いて (`lyrics_display` = songsmith の作品版)、入稿版を機械生成してから機械検証する (スキーマは validate_song.py が検証する song.json 形式。`artist` は `"oneshot"`、`song_no` は 0、`style_with_persona` は null、`persona.use` は false):

```bash
# .production/ があれば
TMP_JSON="<ARTIST_ROOT>/.production/tmp_oneshot_song.json"
# UNSAFE_DIR で scaffold していなければ (一意な一時ディレクトリ内に作り、余分な空ファイルを残さない)
TMP_JSON="$(mktemp -d "${TMPDIR:-/tmp}/oneshot_song.XXXXXX")/song.json"

# 入稿版の生成 (D39): 日本語曲は作品版 lyrics_display から lyrics_suno を機械変換して書き戻す
#   (英語など変換不要な言語では実行せず、lyrics_suno に lyrics_display をそのままコピーする)
python3 "<プラグインルート>/scripts/build_submission_lyrics.py" --json "$TMP_JSON" --report
# 機械検証
python3 "<プラグインルート>/scripts/validate_song.py" "$TMP_JSON"
```

- **入稿版生成の残存漢字**警告 (`--report`) が出たら、songsmith に「該当行に読み注釈を足して作品版を返して」と 1 回だけ差し戻す。急ぐときはマネージャーが 06 の規則で該当語だけ手当てしてよい (フォールバック)
- `--report` の**助詞ローマ字化リストも目視**し、語中の は/へ/を の誤変換 (例: 部屋(へや) → `e や`、母(はは) → `は wa`) を拾う。あれば該当語をカタカナ表記にして作品版を直し再変換する (助詞ヒューリスティックの設計限界。誤変換は全件行番号付きで出る)
- **FAIL** → songsmith に工程を指定して差し戻し (Style 系 → 作曲工程 / 歌詞・タイトル系 → 作詞工程)、入稿版を再生成して PASS まで提示しない。**WARN** → 判断して提示文に添える (差し戻しのリトライ上限は 1 回目安。D40)
- **オリジナリティ (Web 照合は廃止)**: songsmith の**第 1 層規則**(実在曲は参考可・原文/メロ直接流用禁止・実在名は本文に出さない)と作詞工程末尾の自己検査で担保する。マネージャーは自己申告の確認と、タイトル・実在名のチェックを必ず行う。「不安のある行」が未解決なら提示文に一言添えるか songsmith に該当行だけ差し戻す
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

Style の書き方の規約 (英語カンマ区切り、`ジャンル → ムード → 楽器 → ボーカル → プロダクション` 順、BPM は `92 bpm feel` 表記) は songsmith が制作コア束ねに従って担保する。

## Step 5 — 保存 (希望時のみ)

- **既定では保存しない** (チャット提示のみで完結)
- P が保存を希望したら `./oneshot_<スラッグ>.md` (cwd 直下、スラッグは小文字ローマ字 + ハイフン) に、貼り付けブロック全文 + 作品版歌詞 + 末尾に song.json を ```json ブロックで併記して保存する
- 保存後、一時ファイル (tmp_oneshot_song.json、または mktemp で作った一時ディレクトリ) は削除してよい

## 修正対応

修正要望は songsmith に工程を指定して差し戻し (歌詞 → 作詞工程 / スタイル → 作曲工程 / 韻 → 韻工程 → 作詞工程)、歌詞・韻を直したら入稿版を再生成してから Step 3 の検証を通して提示し直す (差し戻しのリトライ上限は 1 回目安)。

## 後処理

- `.production/` を scaffold した場合のみ、`log.md` に 1 行追記し (例: `2026-07-10 22:00 oneshot: 「<タイトル>」提示`)、`state.md` を最新化する

---
name: song
description: 新曲制作 (アーティスト文脈あり)。「新曲作りたい」「こういう曲を作って」「次の曲いこう」「夏っぽい切ない曲がほしい」などの発言、または /suno-artist-production:song で起動。演出家のコンセプトブリーフ → 制作 (songsmith) が Style + 歌詞 + 韻 + タイトルを一括制作 → build_submission_lyrics.py で入稿版を機械変換 → validate_song.py で機械検証 → discography/songs/ へ保存し、suno.com Custom Mode に欄ごとに貼れる入稿セットを提示する。artist.yaml が無い場合は debut を案内する。
---

# 新曲制作 — /suno-artist-production:song

アーティストの世界観・ディスコグラフィーを踏まえた新曲を 1 曲作るフロー。マネージャー (メイン会話のペルソナ) として進行する。スラッシュ起動でも、会話中の「新曲作りたい」への応答としての自発起動 (Skill ツール) でも、同じフローに従う。

成果物は `discography/songs/NNN_<スラッグ>/` の 3 ファイル: **song.json (正 = canonical)** / **paste.md (song.json から生成する貼り付け用)** / **notes.md (制作記録)**。

## このスキル実行中の共通ルール

- ユーザーは「〇〇P」と呼ぶ (producer_name は artist.yaml 参照)
- 質問はテキストで行う。AskUserQuestion は使わない
- ツールを使うターンでは前置きの実況テキストを書かず、報告はツール結果が返ってからまとめる
- サブエージェント起動プロンプトには、参照させるファイルの**絶対パス**を必ず書く。プラグインルートは hook が注入する絶対パスを使う (未注入なら、この SKILL.md の読み込み元 `<プラグインルート>/skills/song/SKILL.md` から 2 階層上をプラグインルートとする)
- 既存楽曲の歌詞の引用・翻案は一切禁止。Style・歌詞・タイトルに実在アーティスト名・実在曲名を書かない
- 作業の区切りで `.production/log.md` に 1 行追記し、`.production/state.md` を最新化する

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

- 以降の手順・コード例の `$ARTIST_ROOT` は、ここで判明した絶対パスに置き換えて使う (シェル変数はターンをまたいで持ち越されない)
- `UNSAFE_DIR` → 「アーティスト用のディレクトリを作って、そこで呼んでください」と案内して終了
- `artist=no` → **このスキルは artist.yaml 必須**。「このディレクトリにはまだアーティストがいません。まず立ち上げからやりましょう」と伝えて `debut` スキルを案内し (そのまま起動してよい)、終了
- artist.yaml の内容は hook が注入済みのはず。未注入なら Read する。`suno.plan` が free の場合、Persona 作成不可・商用利用不可である旨を頭に置いておく

## Step 1 — 要望の受け止め (聞きすぎない)

- P の要望で足りない点があるときだけ、**1〜2 問に絞って**確認する (例: テーマ / テンポ感 / Persona を使うか)。詳しい要望が既に出ていれば質問なしで進む
- **コンペモード判定**: P が「コンペで」「2 案出して」「デモ A/B 見たい」等と明示したときだけコンペモードにする (既定は 1 案)。コンペ時は Step 4 で制作 (songsmith) に 2 案を依頼する (詳細は Step 4 のコンペ分岐)。トークンと P の判断コストが増えるため、こちらから常時 A/B は勧めない

## Step 2 — 採番

```bash
ARTIST_ROOT="<Step 0 で判明した絶対パス>"
LAST=$(find "$ARTIST_ROOT/discography/songs" -maxdepth 1 -type d -name '[0-9][0-9][0-9]_*' 2>/dev/null | sed 's|.*/\([0-9][0-9][0-9]\)_.*|\1|' | sort -n | tail -1)
printf 'NNN=%03d\n' $(( 10#${LAST:-0} + 1 ))
```

スラッグはタイトル確定後に決める (小文字ローマ字 + ハイフン。例: `001_yakousei-melody`)。

## Step 3 — 演出家ブリーフ (director)

まず、演出家に渡す「継続プロデュースの記憶」の絶対パスを解決する (レポートは日付名なので最新 = 末尾):

```bash
ARTIST_ROOT="<Step 0 で判明した絶対パス>"
LATEST_REPORT=$(ls -1 "$ARTIST_ROOT"/analytics/reports/*.md 2>/dev/null | sort | tail -1)
echo "direction=$ARTIST_ROOT/strategy/direction.md"
echo "latest_report=${LATEST_REPORT:-(なし)}"
echo "boneyard=$ARTIST_ROOT/strategy/boneyard.md"
echo "taste=$ARTIST_ROOT/strategy/producer-taste.md"
```

subagent_type `suno-artist-production:director` を起動する。プロンプトに含めるもの:

- P の要望と今回の曲番号。P が「韻重視」「ラップ曲」「ヒップホップ」等を口にしていたらその旨も明記する (韻プロファイル判定の最優先材料)
- 絶対パス: `world.md` / `profile.md` / `discography/discography.md` / 直近 1〜2 曲の `song.json`・`notes.md` (あれば) / 直近のトレンド調査ファイル (今回活かす場合)
- **directing 資料 (演出ライブラリ)**: `<プラグインルート>/skills/directing/SKILL.md` と `<プラグインルート>/skills/directing/references/` の絶対パス (読み方ガイドは SKILL.md 側に定義済み)。「読み方ガイドに従い該当工程の資料だけ読む — 通常の新曲ブリーフは主に 02、世界観に触れるなら 01、物語位置づけは 03。ディレクトリが無ければ従来どおり world.md 起点で進めてよい」と添える
- **必読入力 (契約 C2 — 分析→次曲の配線)**: `strategy/direction.md` の絶対パスと、上で解決した `analytics/reports/` の最新レポート絶対パス。プロンプトに「direction.md の `## 次曲への指示` 見出しの直近 3 件と、最新レポートの所見を必ずブリーフに反映し、ブリーフに『今回反映した方針 (出典: direction.md YYYY-MM-DD)』欄を設けること」と明記する。どちらも無ければ「無ければ従来どおり world.md 起点で可」と添える
- **台帳 (契約 C6、あれば読む)**: `strategy/boneyard.md` (没モチーフ・没タイトルの再利用候補) と `strategy/producer-taste.md` (P の好み) の絶対パス。「存在すれば参照、無ければ無視でよい」と添える

返してもらうもの = **コンセプトブリーフ**: テーマ / 感情曲線 / 構成案 / コアモチーフ / Style 方向 / 韻プロファイル (standard / heavy。heavy は主戦場セクション + 軸の方向 1 行付き) / NG (避けること) / 仮タイトル案 / 今回反映した方針 (出典: direction.md の日付) / 末尾に **`### ひとこと`** (今回の演出の狙いを 1 行。契約 C4)。

## Step 4 — 制作 (songsmith) 一括制作

ブリーフ確定後は**制作 (songsmith) を 1 回だけ起動**する。songsmith が world/ブリーフ/spec/direction を一度だけ読み、**Style 一式 + 作品版歌詞 + タイトル (+ 韻プロファイル heavy の日本語曲は韻設計)** を一括で返す (旧 composer + lyricist + rapper を統合。3 波の重複読込と直列待ちが 1 コンテキストに畳まれる)。

**songsmith** (subagent_type: `suno-artist-production:songsmith`) のプロンプトに含めるもの:

- ブリーフ全文 (韻プロファイルを含む) と歌詞言語 (artist.yaml の language)
- 絶対パス: `artist.yaml` (基準ジャンル帯 / vocal / persona 状態 / preferred_model / plan) / `world.md` (語彙パレット)
- **suno-spec の実効パス** (hook 注入のコンテキスト参照) + 「使用モデル・文字数上限・タグ語彙・スライダー定石は必ず spec を読んで従う」という指示
- **制作コア束ねの絶対パス**: `<プラグインルート>/skills/production/references/write_core.md` (毎回必読 = 作曲 + 作詞の必読を 1 Read)。**韻プロファイルが heavy かつ日本語**なら `<プラグインルート>/skills/production/references/rhyme_core.md` も渡す。「束ねが無ければ composing/SKILL.md・songwriting/SKILL.md の原本から必要分を読んでよい」と添える
- **style-vocab の実効パス** (hook 注入のコンテキスト参照。未注入なら上書き版 `${XDG_CONFIG_HOME:-~/.config}/suno-artist-production/style-vocab.md`、なければ `<プラグインルート>/skills/suno-spec/references/style-vocab.md`) + 「非音楽語は該当カテゴリを拾い読み」
- **台帳 (契約 C6、あれば読む)**: `strategy/boneyard.md` (没フック・没モチーフ・没タイトルの再利用候補) と `strategy/producer-taste.md` (P の好み) の絶対パス。「存在すれば参照、無ければ無視でよい」と添える
- **条件付きプレイブック (該当する曲だけ)**: HIPHOP/ラップ系は `<プラグインルート>/skills/songwriting/references/10_hiphop-genre-ja.md`、語り主導 (ポエトリー) は `<プラグインルート>/skills/composing/references/06_poetry-spoken.md`、K-POP 系は `<プラグインルート>/skills/composing/references/04_kpop.md` の絶対パス (「該当節を必読。無ければ束ねの範囲で進めてよい」と添える)

返してもらうもの (詳細は songsmith の「返す内容の形式」):

- **Style 2 変種** (Persona 登録済み) または フル 1 本 (未登録) / Exclude / Vocal Gender / Weirdness / Style Influence / 使用モデル / Persona 適用判断 / セクション演出タグ案
- **韻設計** (韻プロファイル heavy の日本語曲のみ)
- **作品版歌詞** (漢字かな交じり。難読・当て字・多読み漢字にはルビ読み注釈付き。**入稿版は書かせない** — Step 5 で `build_submission_lyrics.py` が機械変換する)
- **タイトル案** / **オリジナリティ自己申告** (中心モチーフの出所 / 意図的に避けた既存曲 / 不安のある行)
- 末尾に facet 別の **`### ひとこと`** (サウンド / 歌詞 / 韻。契約 C4)

### 呼び出しの信頼性 (タイムアウト / リトライ / フォールバック。D40)

- **リトライ上限は 1 回**。songsmith が「不足: 〇〇が渡されていません」と返したら、不足パスを補って**1 回だけ**再起動する。同じ不足で 2 回連続失敗したら、そこで止めて**渡せていない入力を P に確認**する (多重・無限リトライは禁止。実測「空振り」の暴発を防ぐ)。
- 成果が途中で途切れた/形式が崩れて返った場合も**再起動は 1 回まで**。それでも崩れるなら、返ってきた部分成果 (Style だけ・歌詞だけ等) をそのまま P に見せ、「ここまでできています。続きは次のターンで詰めます」と握らせる (全体を止めない)。
- 外部 Web 呼び出しは照合廃止で無くなったため、ハングの主要因は構造的に除去済み。ここでの失敗はほぼ「入力不足」なので、対処は上の 1 回リトライで足りる。

### コンペモード (P が「コンペで」等と明示したときだけ)

既定は 1 案。コンペ指定時のみ、songsmith の起動プロンプトに「コンペで。Style 方向違い × サビ方向違いの 2 案 (デモ A / デモ B) を全文で」と明示する (常時 ON にはしない)。songsmith が 1 起動で A / B の 2 案を完備して返す (韻バンクは heavy でも 1 回だけ作り 2 案で共用)。

- 2 案が揃ったら、A/B を対比できる形で P に提示し、どれを採用するか選んでもらう (「A のサビ + B の Style」のような組み合わせ採用も可)
- 選んだ案で song.json を組み立てて Step 5 以降に進む。**負け案と採用理由の台帳追記は Step 7 の「台帳の更新」で行う** (負け案 → boneyard.md、選んだ/差し戻した理由 → producer-taste.md)

## Step 5 — song.json 組み立てと機械検証

タイトルを確定し (P の意向が不明ならブリーフ・songsmith のタイトル案から選び、提示時に変更可能と添える)、ディレクトリを作って song.json を書く:

```bash
ARTIST_ROOT="<Step 0 で判明した絶対パス>"
mkdir -p "$ARTIST_ROOT/discography/songs/<NNN>_<スラッグ>"
```

**song.json スキーマ (canonical。paste.md はここから生成する)**:

```json
{
  "schema_version": 1,
  "generated_at": "<現在時刻 (ISO 8601、例: 2026-07-10T21:00:00+09:00)>",
  "spec_date": "<実効 spec の調査日 YYYY-MM-DD>",
  "artist": "<アーティスト名>",
  "song_no": 0,
  "model": "<使用モデル>",
  "title": "<タイトル>",
  "style": "<Persona なしのフル Style (英語カンマ区切り)>",
  "style_with_persona": "<Persona 適用時 Style。null にするのは Persona 未作成のアーティストのみ (登録済みなら非適用推奨の曲でも保持)>",
  "lyrics_display": "<作品版歌詞 (漢字かな交じり)>",
  "lyrics_suno": "<入稿版歌詞 (構成タグ + 変換済み本文)>",
  "exclude_styles": "<除外タグ (カンマ区切り)>",
  "vocal_gender": "<female / male>",
  "weirdness": 50,
  "style_influence": 60,
  "instrumental": false,
  "language": "<ja / en / ...>",
  "song_type": "original",
  "derived_from": null,
  "persona": { "use": false, "name": null, "visibility": null },
  "concept_brief": "<演出家ブリーフの要約 (2〜3 行)>",
  "validation": { "title_chars": 0, "style_chars": 0, "lyrics_chars": 0, "passed": false }
}
```

- `lyrics_display` と `lyrics_suno` は**必ず両方保持**する (作品版 = YouTube 概要欄・P への提示用 / 入稿版 = Suno 貼り付け用)。**`lyrics_display` は songsmith の作品版をそのまま入れ、`lyrics_suno` は下の入稿版生成ステップで機械変換して入れる** (songsmith は入稿版を書かない。D39)
- インスト曲は `instrumental: true` + `lyrics_suno` は `[Instrumental]` (+構成タグ) + `exclude_styles` に `vocals` を必ず含める (三重指定)
- Persona 登録済みで適用する曲は `persona: { "use": true, "name": "<Persona 名>", "visibility": "<artist.yaml の値>" }`
- Persona 登録済みで**非適用推奨の曲も `style_with_persona` は保持**する (songsmith は登録済みアーティストでは常に 2 変種を納品する契約。P が推奨に逆らって Persona を試す余地を残す。設計 D9)。非適用の判断は `persona.use: false` として記録する
- `song_type` は `original` / `cover` / `remaster` / `extend` のいずれか (既定 `original`)、`derived_from` は派生元の曲番号または `null` (既定 `null`)。**v1 はスキーマ予約のみで、派生曲 (セルフカバー等) を作るフローは未実装** — 通常の新曲は常に `original` / `null` のままにする (validate_song.py が既定外の値・不整合を WARN で知らせる。契約 C5)
- `validation` は下の検証結果で更新する

**入稿版の生成** (D39。song.json の `lyrics_suno` を埋める前に必ず実行):

songsmith の作品版 (`lyrics_display`) を入稿版 (`lyrics_suno`) にする。**言語で分岐する**:

- **日本語曲 (language: ja)**: song.json に `lyrics_display` を書いた状態で次を実行すると、機械変換して `lyrics_suno` を同ファイルに書き戻す (助詞 は/へ/を → wa/e/wo・括弧/記号排除・数字読み下し・ルビ注釈の畳み込み・タグ整形。作品版に付いた難読・当て字のルビ読み注釈を使う):

  ```bash
  python3 "<プラグインルート>/scripts/build_submission_lyrics.py" --json "$ARTIST_ROOT/discography/songs/<NNN>_<スラッグ>/song.json" --report
  ```

  `--report` の**残存漢字**警告が出たら (ルビ注釈の付け忘れ)、songsmith に「該当行の漢字に読み注釈を足して作品版を返して」と 1 回だけ差し戻し、`lyrics_display` を更新して再変換する。少数の残存で急ぐときは、マネージャーが 06 の変換規則に沿って該当語だけ手当てしてよい (動作担保のフォールバック)

  さらに `--report` の**助詞ローマ字化リストも目視**する。語中の は/へ/を が助詞と誤認される誤変換 (例: 部屋(へや) → `e や`、母(はは) → `は wa`) は行番号付きで全件出るので、見つけたら該当語をカタカナ表記 (ヘヤ 等) にして `lyrics_display` を直し再変換する (助詞ヒューリスティックの設計限界。build_submission_lyrics.py の docstring 参照)
- **変換不要な言語 (英語など)**: 入稿版 = 作品版と同一。`lyrics_suno` に `lyrics_display` をそのままコピーする (スクリプト不要)。その旨を提示文に一言添える

**機械検証** (提示前に必ず実行):

```bash
python3 "<プラグインルート>/scripts/validate_song.py" "$ARTIST_ROOT/discography/songs/<NNN>_<スラッグ>/song.json"
```

- **FAIL** → songsmith に差し戻す (どの工程かを添える: Style・スライダー・モデル系は作曲工程 / 歌詞・タイトル系は作詞工程)。修正を song.json に反映し、入稿版を再生成して再検証し、**PASS になるまで P に提示しない**
- **WARN** → 内容を判断し、直すべきものは songsmith に差し戻し、許容するものは P への提示文に一言添える (例: 入稿版 3,000 字超は「歌唱が駆け足になる報告あり」/ 「早口の恐れ」「行長のばらつき」のモーラ WARN は該当セクションの分割・語数調整を songsmith の作詞工程に依頼)
- 差し戻しの**リトライ上限も 1 回**を目安にする (同じ FAIL を繰り返すなら入力・ブリーフ側を見直し、P に握らせる。D40)

## Step 6 — オリジナリティ最終チェック (マネージャー確認)

外部 Web 照合は廃止。オリジナリティは songsmith の**第 1 層規則**(実在曲は参考可・歌詞原文/メロディの直接流用禁止・実在名は本文に出さない)と、**作詞工程末尾の自己検査 (08 由来)**で担保する。マネージャーは提示前に次を確認する:

- songsmith のオリジナリティ自己申告が添付されているか。**「不安のある行」が挙がっていれば内容を確認**し、未解決 (songsmith が書き直さず P に握らせた行) なら、提示文にその旨を一言添えるか、songsmith に該当行だけの書き直しを 1 回差し戻す
- タイトルが有名曲と完全一致していないか
- Style / 歌詞 / タイトルに実在アーティスト名・実在曲名が入っていないか (validate_song.py の固有名詞警告も確認)

## Step 7 — 保存と入稿セット提示

1. **paste.md** を song.json から生成して保存する (下のテンプレート)
2. **notes.md** を保存する:

   ```markdown
   # 「<タイトル>」制作ノート

   ## 制作意図 (ブリーフ要約)
   - <2〜4 行>

   ## オリジナリティ自己申告 (制作)
   - 中心モチーフの出所: <...>
   - 意図的に避けた既存曲・領域: <...>
   - 不安のある行と対応: <書き直した / P に握らせた 等。なければ「なし」>

   ## チームからひとこと (ライナーノーツ)
   - 演出家: <director の ### ひとこと>
   - 制作 (サウンド): <songsmith の ### ひとこと「サウンド」>
   - 制作 (歌詞): <songsmith の ### ひとこと「歌詞」>
   - 制作 (韻): <songsmith の ### ひとこと「韻」 (韻プロファイル heavy の曲のみ。standard なら行ごと省略)>

   ## テイク記録
   - (採用テイクの日付・URL・所感をここに追記)

   ## P フィードバック履歴
   - (修正依頼と対応をここに追記)
   ```

3. **discography.md に行を追加**する (状態: **制作中** / 制作日: 今日 / Persona 列: 適用 or なし)
4. **台帳の更新** (コンペモード、または韻プロファイル heavy の曲のとき。契約 C6):

   台帳ファイルは通常 debut がスキャフォルドで空作成しているが、無い場合に備えて作ってから追記する:

   ```bash
   ARTIST_ROOT="<Step 0 で判明した絶対パス>"
   mkdir -p "$ARTIST_ROOT/strategy"
   [ -f "$ARTIST_ROOT/strategy/boneyard.md" ] || printf '# 没案バンク — %s\n\nコンペ負け案・没モチーフ・没タイトルを 1 行ずつ (再利用の種)。\n' "<アーティスト名>" > "$ARTIST_ROOT/strategy/boneyard.md"
   [ -f "$ARTIST_ROOT/strategy/producer-taste.md" ] || printf '# P の好み台帳 — %s\n\nP の採用/差し戻しの理由を 1 行ずつ (ブリーフ・執筆の参照材料)。\n' "<アーティスト名>" > "$ARTIST_ROOT/strategy/producer-taste.md"
   ```

   - **boneyard.md** に、選ばれなかったデモの要点を 1 行追記する (例: `2026-07-10 004: 没サビ「〜」/ 没 Style 方向: シンセ強め (今回は生ピアノ採用)`)
   - **producer-taste.md** に、P が選んだ/差し戻した理由を 1 行追記する (例: `2026-07-10 004: 具体的な情景のあるサビを好む (抽象より固有名詞)`)。コンペでなくても、P が明確な好み・差し戻し理由を述べたら 1 行残してよい
   - **韻プロファイル heavy の曲 (任意)**: songsmith の韻設計で未採用の推しコンビが惜しければ、boneyard.md に 1 行追記する (例: `2026-07-10 005: 未採用の韻コンビ「まよいの こおり」×「よるの とおり」(o-i 型)`)
5. **git コミット** (アーティストディレクトリが git 管理下のときだけ。契約 C7 / 提案5):

   曲の保存と discography 更新が済んだこの時点で、マネージャーがマスターテープ (git) にコミットする。git 未管理なら何もしない。**リモート push はしない** (P の領分)。

   ```bash
   ARTIST_ROOT="<Step 0 で判明した絶対パス>"
   TOP=$(git -C "$ARTIST_ROOT" rev-parse --show-toplevel 2>/dev/null || true)
   # アーティストディレクトリ自身が git ルート (TOP == ARTIST_ROOT) のときだけコミットする。
   # 親リポジトリの配下に置かれているだけ (TOP がその祖先) のときはコミットしない
   # — 利用者の既存リポジトリを勝手に巻き込まないため。
   if [ -n "$TOP" ] && [ "$TOP" = "$ARTIST_ROOT" ]; then
     # 二重の安全策: 内部作業ファイル (.production/ = state.md/log.md 等) が必ず ignore される状態を保証してから add する
     grep -qE '^\.production/?$' "$ARTIST_ROOT/.gitignore" 2>/dev/null || echo '.production/' >> "$ARTIST_ROOT/.gitignore"
     ( cd "$ARTIST_ROOT" && git add -A . && git commit -q -m "<NNN> <タイトル> 入稿セット完成" ) \
       && echo "committed" || echo "no-commit (差分なし等)"
   else
     echo "コミットしない (git 未管理、またはアーティストディレクトリが git ルートでない)"
   fi
   ```

   - コミットメッセージは `<NNN> <タイトル> 入稿セット完成` の形 (例: `001 夜光性メロディ 入稿セット完成`)。世界観に合わせて「マスターテープに録っておきました」等と一言添えて報告してよい
   - コミット直前に `.production/` が `.gitignore` に入っていることを保証してから add するので、state.md / log.md 等の内部作業ファイルは巻き込まれない
6. **チームからひとこと → 入稿セット提示** (契約 C4):
   - 入稿セットの前に「**チームからひとこと**」として、演出家の `### ひとこと` と songsmith の facet 別 `### ひとこと` (サウンド / 歌詞、韻プロファイル heavy の曲はさらに韻) を 3〜4 行で読み上げる (試聴会の演出。notes.md にも保存済み)
   - 続けて **paste.md と同一内容の貼り付けブロックを提示**する (欄ごとの fenced code block を崩さない)。歌詞の内容確認用に作品版を添えてよい

### paste.md テンプレート (この形を正確に守る)

````markdown
# 「<タイトル>」 Suno 入稿セット

## 手順
1. suno.com → Create → **Custom** / モデルは **<使用モデル>** を選択
2. (Persona 使用時) Lyrics 欄上の Voices セレクタで **「<Persona 名> (style)」** を選択
   → Style 欄に自動挿入された文を**全部消して**、下の「Style (Persona 適用時)」を貼る
3. 以下を各欄にコピペし、Advanced Options を表の通り設定 → Create

## Title
```text
<タイトル>
```

## Style of Music — Persona 適用時 (曲ごとの演出タグのみ)
```text
<曲固有の演出タグ 5〜8 個 (英語カンマ区切り)>
```

## Style of Music — Persona なしの場合 (フル)
```text
<アイデンティティタグ + 曲固有タグで 10 タグ前後 (英語カンマ区切り)>
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
| Vocal Gender | <Male / Female> | <理由 (例: アーティスト定義)> |
| Weirdness | <NN>% | <理由 (例: 商業寄りの定石帯)> |
| Style Influence | <NN>% | <理由 (例: タグを絞ったので高追従)> |
| Instrumental | <ON / OFF> | <理由。OFF なら —> |

## 生成後にやること
- 2 テイク聴き比べ → 採用テイクの URL を私に報告 (discography に記録します)
- 気になる箇所は「2 番 A メロが早口」のように場所+症状で教えてください
````

**テンプレートの設計ルール**:

- コピー単位 = fenced code block をフィールド単位で切る。スライダー・トグルなど UI 操作は表 + 手順書きにする
- **Persona 登録済みアーティストでは Style 2 変種を必ず併記**する (Persona 選択で Style 欄が自動上書きされる仕様への対応)。Persona 未作成 (1 曲目など) の間は、手順 2 を省いて見出しを「## Style of Music」1 本にする
- songsmith が「今回は Persona 非適用推奨」とした曲でも 2 変種の併記は崩さず、手順の冒頭に「**今回は Persona 非適用推奨** (<理由>)」を明記してフル Style を使ってもらう (試したくなったときの適用時 Style も残しておく)
- Style は英語カンマ区切り 10 タグ前後、`ジャンル → ムード → 楽器 → ボーカル → プロダクション` 順。BPM は `92 bpm feel` 表記。実在アーティスト名禁止
- 歌詞は構成タグ英語 + 本文はアーティスト言語 (日本語は入稿版変換済み)。セクション演出は `[Bridge: stripped down, piano only]` 形式のパラメータ付きタグを積極活用する
- インスト曲は「Instrumental トグル ON + `[Instrumental]` + Exclude に `vocals`」の三重指定

## Step 8 — テイク報告後のフォロー

- **採用テイクの Suno URL 報告** → discography.md の該当行を **生成済** に更新して Suno URL を記入し、notes.md のテイク記録に追記する
  - このとき artist.yaml の `suno.persona.created` が false なら (通常は 1 曲目)、**Style Persona 作成を案内する**: suno.com の曲ページ → More Actions (…) → Create → Make Persona → 名前はアーティスト名を推奨 → **公開設定はデフォルト Public なので Private に切り替え (推奨)** → 作成可否のプラン条件は suno-spec (実効版) §6 / §8 で確認して案内する。作成報告を受けたら artist.yaml の `suno.persona` を更新し (created: true / name / source_song / visibility)、discography の該当行の Persona 列を「なし(Persona元曲)」にする
- **YouTube URL 報告** → 該当行を **公開済** に更新して YouTube URL を記入する
  - **公開済が 6 曲に達し、かつ `suno.custom_model` が null なら、Custom Models 化を提案する**: 自作曲 6 トラック以上で現行フラッグシップモデルを自分のスタイルにチューニングできる (プラン条件・上限個数は suno-spec (実効版) §6 / §8 で確認して案内する)。作成されたら `suno.custom_model` に記入する
- **修正要望** (「2 番 A メロが早口」など場所+症状) → **songsmith に、直す工程を指定して差し戻す** (歌詞 → 作詞工程 / スタイル・設定 → 作曲工程 / **韻系の修正**「韻が浅い」「もっと硬く踏んで」等 → 韻工程 → 作詞工程)。韻系では対象行 + 前後 2 行の文脈 + 症状 + 変えてはいけない行を songsmith に渡す (旧 rapper→lyricist の 2 段が 1 起動に畳まれる)。歌詞・韻を直したら**入稿版を再生成** (build_submission_lyrics.py) してから Step 5 の検証を通し、song.json と paste.md を両方更新する。差し戻しは 1 回で完成しない前提 (ガチャ運用) を P と共有し、修正箇所は 1 つずつ潰す (差し戻しのリトライ上限も 1 回目安。D40)
  - P が繰り返し口にする好み・NG (「もっと具体的な情景がいい」「サビは短く」等) は `strategy/producer-taste.md` に 1 行残すと、次曲のブリーフ・執筆に効く (契約 C6。ファイルが無ければ Step 7 の防御スニペットで作ってから追記)

## 後処理 (作業が一段落するたび)

- `.production/log.md` に 1 行追記する (例: `2026-07-10 21:30 song: 004 <タイトル> 入稿セット提示`)
- `.production/state.md` を最新化する (進行中の曲・次のアクションを反映。15 行以内)

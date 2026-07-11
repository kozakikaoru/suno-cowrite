---
name: song
description: 新曲制作 (アーティスト文脈あり)。「新曲作りたい」「こういう曲を作って」「次の曲いこう」「夏っぽい切ない曲がほしい」などの発言、または /suno-artist-production:song で起動。演出家のコンセプトブリーフ → 作曲家・作詞家の並列制作 → validate_song.py による機械検証 → オリジナリティ照合 → discography/songs/ へ保存し、suno.com Custom Mode に欄ごとに貼れる入稿セットを提示する。artist.yaml が無い場合は debut を案内する。
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
- 「急ぎで」「サクッと」など速度優先の指示があれば、Step 6 の Web 照合をスキップしてよい (スキップする旨を一言断る)
- **コンペモード判定**: P が「コンペで」「2 案出して」「デモ A/B 見たい」等と明示したときだけコンペモードにする (既定は 1 案)。コンペ時は Step 4 で composer/lyricist にそれぞれ 2 案を依頼する (詳細は Step 4 のコンペ分岐)。トークンと P の判断コストが増えるため、こちらから常時 A/B は勧めない

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
- **必読入力 (契約 C2 — 分析→次曲の配線)**: `strategy/direction.md` の絶対パスと、上で解決した `analytics/reports/` の最新レポート絶対パス。プロンプトに「direction.md の `## 次曲への指示` 見出しの直近 3 件と、最新レポートの所見を必ずブリーフに反映し、ブリーフに『今回反映した方針 (出典: direction.md YYYY-MM-DD)』欄を設けること」と明記する。どちらも無ければ「無ければ従来どおり world.md 起点で可」と添える
- **台帳 (契約 C6、あれば読む)**: `strategy/boneyard.md` (没モチーフ・没タイトルの再利用候補) と `strategy/producer-taste.md` (P の好み) の絶対パス。「存在すれば参照、無ければ無視でよい」と添える

返してもらうもの = **コンセプトブリーフ**: テーマ / 感情曲線 / 構成案 / コアモチーフ / Style 方向 / 韻プロファイル (standard / heavy。heavy は主戦場セクション + 軸の方向 1 行付き) / NG (避けること) / 仮タイトル案 / 今回反映した方針 (出典: direction.md の日付) / 末尾に **`### ひとこと`** (今回の演出の狙いを 1 行。契約 C4)。

## Step 4 — 作曲家 ∥ 作詞家 (必ず並列、1 メッセージで 2 呼び出し)

ブリーフ確定後は**必ず** composer と lyricist を並列起動する。ブリーフが両者の共通契約になる。**例外はブリーフの韻プロファイルが heavy の曲だけ** — 下の「韻プロファイル heavy の分岐」に従い、composer ∥ rapper → lyricist の順にする (standard 曲は rapper を呼ばず、従来と完全同一)。

**composer** (subagent_type: `suno-artist-production:composer`) のプロンプトに含めるもの:

- ブリーフ全文
- 絶対パス: `artist.yaml` (基準ジャンル帯 / vocal / persona 状態 / preferred_model / plan)
- **suno-spec の実効パス** (hook 注入のコンテキスト参照) + 「使用モデル・文字数上限・タグ語彙は必ず spec を読んで従う」という指示
- **composing 資料 (作曲ライブラリ)**: `<プラグインルート>/skills/composing/SKILL.md` と `<プラグインルート>/skills/composing/references/` の絶対パス (読み方ガイドは SKILL.md 側に定義済み。「ディレクトリが無ければ従来どおり spec のみで進めてよい」と添える)
- **style-vocab の実効パス** (hook 注入のコンテキスト参照。未注入なら、上書き版 `${XDG_CONFIG_HOME:-~/.config}/suno-artist-production/style-vocab.md` があればそれ、なければ `<プラグインルート>/skills/suno-spec/references/style-vocab.md`) + 「非音楽語 (ムード・情景・質感語) は辞典の該当カテゴリを拾い読みして使う」という指示
- **台帳 (契約 C6、あれば読む)**: `strategy/producer-taste.md` (P の好み) の絶対パス。「存在すれば参照、無ければ無視でよい」と添える
- **HIPHOP/ラップ系ジャンルの曲のみ** (artist.yaml の genre_band またはブリーフの Style 方向で判断): `<プラグインルート>/skills/songwriting/references/10_hiphop-genre-ja.md` の絶対パス + 「サウンドと Style への写像の参考に読む。ファイルが無ければ従来資料のみで進めてよい」という指示

返してもらうもの:

- **Style 2 変種**: Persona 適用時 (曲固有の演出タグのみ 5〜8 個) / Persona なし (アイデンティティタグ + 曲固有タグで 10 タグ前後)
- Exclude Styles / Vocal Gender / Weirdness / Style Influence / 使用モデル
- **Persona 適用可否の判断** — 基準ジャンル帯から大きく外れる曲では「今回は Persona 非適用推奨」を理由付きで明示させる
- セクション演出タグ案 (`[Bridge: stripped down, piano only]` 形式のパラメータ付きタグ)
- 末尾に **`### ひとこと`** (サウンドの聴きどころを 1 行。契約 C4)

**lyricist** (subagent_type: `suno-artist-production:lyricist`) のプロンプトに含めるもの:

- ブリーフ全文と歌詞言語 (artist.yaml の language)
- 絶対パス: `world.md` (語彙パレット) / **songwriting 資料**: `<プラグインルート>/skills/songwriting/SKILL.md` と `<プラグインルート>/skills/songwriting/references/` (読み方と作詞ワークフローは SKILL.md 側に定義済み)
- **台帳 (契約 C6、あれば読む)**: `strategy/boneyard.md` (没フレーズ・没モチーフの再利用候補) と `strategy/producer-taste.md` (P の好み) の絶対パス。「存在すれば参照、無ければ無視でよい」と添える
- **HIPHOP/ラップ系ジャンルの曲のみ**: `<プラグインルート>/skills/songwriting/references/10_hiphop-genre-ja.md` の絶対パス (「渡されたら読む。ファイルが無ければ 03 のみで進めてよい」と添える)
- **語り主導 (ポエトリー/スポークンワード) の曲のみ**: `<プラグインルート>/skills/composing/references/06_poetry-spoken.md`、**K-POP 系の曲のみ**: `<プラグインルート>/skills/composing/references/04_kpop.md` の絶対パス (いずれも「『ことば側への申し送り』節を必読。ファイルが無ければ従来資料のみで進めてよい」と添える)
- **韻プロファイル heavy の曲のみ**: rapper の出力全文 (下の「韻プロファイル heavy の分岐」参照)

返してもらうもの:

- **作品版歌詞** (漢字かな交じり) と **入稿版歌詞** (構成タグ英語 + ひらがな化・助詞 wa/e/wo 変換・括弧なし)
- タイトル案
- **オリジナリティ自己申告** (中心モチーフの出所 / 意図的に避けた既存曲 / 不安のある行)
- 末尾に **`### ひとこと`** (歌詞の推し行を 1 行引用。契約 C4)

歌詞とスタイルに齟齬が出たら、ブリーフを基準に該当側だけ差し戻す。

### 韻プロファイル heavy の分岐 (客演 rapper 参加)

ブリーフの韻プロファイルが heavy の曲は、起動順を **composer ∥ rapper (1 メッセージで並列) → lyricist** に変える (直列 1 段だけ増える)。

**rapper** (subagent_type: `suno-artist-production:rapper`、ネタ帳モード) のプロンプトに含めるもの:

- ブリーフ全文 (主戦場セクション・軸の方向を含む) + 「ネタ帳モードで」の明示
- 絶対パス: `<プラグインルート>/skills/songwriting/references/03_rhyme-and-rhythm.md` と `09_rhyme-advanced-ja.md` (主資料。「ファイルが無ければ 03 のみで進めてよい」と添える) / HIPHOP/ラップ系ジャンルなら `10_hiphop-genre-ja.md` も / `world.md` (語彙パレット) / (あれば) `strategy/boneyard.md`
- 返してもらうもの: 【韻設計案】/【韻バンク】/【推しコンビ】/【lyricist への申し送り】/ 末尾に **`### ひとこと`** (韻の聴きどころを 1 行。契約 C4 — 参加曲では 4 人目)

rapper の納品後に lyricist を起動し、**rapper の出力全文をプロンプトに添付**する (「候補の採否は自由、最終著者はあなた」と添える)。コンペモードでも**ネタ帳は 1 回だけ**作り、デモ A / B の 2 案で共用する (rapper を 2 回呼ばない)。

**lyricist の【応援要請】への対応** (standard 曲でも使える救済導線): lyricist の納品に【応援要請】欄 (相方が見つからない行 + 欲しい母音型) があれば、rapper を**ドクターモード**でスポット起動し (対象行 + 前後 2 行の文脈 + 症状 + 変えてはいけない行を渡す)、返ってきた改善候補を添えて lyricist に該当行だけの修正を依頼する。

### コンペモード (P が「コンペで」等と明示したときだけ)

既定は 1 案。コンペ指定時のみ以下に切り替える (常時 ON にはしない):

- composer には「Style 方向違いの 2 案 (デモ A / デモ B)」、lyricist には「サビ違いの 2 案 (デモ A / デモ B)」を依頼する (通常時は各 1 案)
- 2 案が揃ったら、A/B を対比できる形で P に提示し、どれを採用するか選んでもらう (「A のサビ + B の Style」のような組み合わせ採用も可)
- 選んだ案で song.json を組み立てて Step 5 以降に進む。**負け案と採用理由の台帳追記は Step 7 の「台帳の更新」で行う** (負け案 → boneyard.md、選んだ/差し戻した理由 → producer-taste.md)

## Step 5 — song.json 組み立てと機械検証

タイトルを確定し (P の意向が不明ならブリーフ・作詞家案から選び、提示時に変更可能と添える)、ディレクトリを作って song.json を書く:

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

- `lyrics_display` と `lyrics_suno` は**必ず両方保持**する (作品版 = YouTube 概要欄・P への提示用 / 入稿版 = Suno 貼り付け用)
- インスト曲は `instrumental: true` + `lyrics_suno` は `[Instrumental]` (+構成タグ) + `exclude_styles` に `vocals` を必ず含める (三重指定)
- Persona 登録済みで適用する曲は `persona: { "use": true, "name": "<Persona 名>", "visibility": "<artist.yaml の値>" }`
- Persona 登録済みで**非適用推奨の曲も `style_with_persona` は保持**する (composer は登録済みアーティストでは常に 2 変種を納品する契約。P が推奨に逆らって Persona を試す余地を残す。設計 D9)。非適用の判断は `persona.use: false` として記録する
- `song_type` は `original` / `cover` / `remaster` / `extend` のいずれか (既定 `original`)、`derived_from` は派生元の曲番号または `null` (既定 `null`)。**v1 はスキーマ予約のみで、派生曲 (セルフカバー等) を作るフローは未実装** — 通常の新曲は常に `original` / `null` のままにする (validate_song.py が既定外の値・不整合を WARN で知らせる。契約 C5)
- `validation` は下の検証結果で更新する

**機械検証** (提示前に必ず実行):

```bash
python3 "<プラグインルート>/scripts/validate_song.py" "$ARTIST_ROOT/discography/songs/<NNN>_<スラッグ>/song.json"
```

- **FAIL** → 該当エージェントに差し戻す (Style・スライダー・モデル系 → composer / 歌詞・タイトル系 → lyricist)。修正を song.json に反映して再実行し、**PASS になるまで P に提示しない**
- **WARN** → 内容を判断し、直すべきものは差し戻し、許容するものは P への提示文に一言添える (例: 入稿版 3,000 字超は「歌唱が駆け足になる報告あり」/ 「早口の恐れ」「行長のばらつき」のモーラ WARN は該当セクションの分割・語数調整を lyricist に依頼)

## Step 6 — オリジナリティ最終チェック

1. **マネージャー自身のチェックリスト**:
   - lyricist のオリジナリティ自己申告が添付されているか。「不安のある行」が挙がっていれば内容を確認する
   - タイトルが有名曲と完全一致していないか
   - Style / 歌詞 / タイトルに実在アーティスト名・実在曲名が入っていないか (validate の固有名詞警告も確認)
2. **Web 照合** (デフォルト ON。Step 1 で P が急ぐと言ったときだけスキップ可):
   - subagent_type `suno-artist-production:researcher` に、サビ / フックの特徴的な 2〜3 行を渡し (**韻プロファイル heavy の曲は、ラップの決めライン (パンチライン) 1〜2 行も追加**)、「各行を引用符付きで Web 検索 (1〜2 クエリで可) し、歌詞サイト等で既存曲としてヒットしたら該当行と URL を報告」と依頼する
   - ヒット → lyricist に該当行の書き直しを依頼し、Step 5 の検証からやり直す

## Step 7 — 保存と入稿セット提示

1. **paste.md** を song.json から生成して保存する (下のテンプレート)
2. **notes.md** を保存する:

   ```markdown
   # 「<タイトル>」制作ノート

   ## 制作意図 (ブリーフ要約)
   - <2〜4 行>

   ## オリジナリティ自己申告 (作詞家)
   - 中心モチーフの出所: <...>
   - 意図的に避けた既存曲・領域: <...>
   - 不安のある行と Web 照合結果: <...>

   ## チームからひとこと (ライナーノーツ)
   - 演出家: <director の ### ひとこと>
   - 作曲家: <composer の ### ひとこと>
   - 作詞家: <lyricist の ### ひとこと>
   - 客演ラッパー: <rapper の ### ひとこと (rapper 参加曲のみ。不参加なら行ごと省略)>

   ## テイク記録
   - (採用テイクの日付・URL・所感をここに追記)

   ## P フィードバック履歴
   - (修正依頼と対応をここに追記)
   ```

3. **discography.md に行を追加**する (状態: **制作中** / 制作日: 今日 / Persona 列: 適用 or なし)
4. **台帳の更新** (コンペモード、または rapper 参加曲のとき。契約 C6):

   台帳ファイルは通常 debut がスキャフォルドで空作成しているが、無い場合に備えて作ってから追記する:

   ```bash
   ARTIST_ROOT="<Step 0 で判明した絶対パス>"
   mkdir -p "$ARTIST_ROOT/strategy"
   [ -f "$ARTIST_ROOT/strategy/boneyard.md" ] || printf '# 没案バンク — %s\n\nコンペ負け案・没モチーフ・没タイトルを 1 行ずつ (再利用の種)。\n' "<アーティスト名>" > "$ARTIST_ROOT/strategy/boneyard.md"
   [ -f "$ARTIST_ROOT/strategy/producer-taste.md" ] || printf '# P の好み台帳 — %s\n\nP の採用/差し戻しの理由を 1 行ずつ (ブリーフ・執筆の参照材料)。\n' "<アーティスト名>" > "$ARTIST_ROOT/strategy/producer-taste.md"
   ```

   - **boneyard.md** に、選ばれなかったデモの要点を 1 行追記する (例: `2026-07-10 004: 没サビ「〜」/ 没 Style 方向: シンセ強め (今回は生ピアノ採用)`)
   - **producer-taste.md** に、P が選んだ/差し戻した理由を 1 行追記する (例: `2026-07-10 004: 具体的な情景のあるサビを好む (抽象より固有名詞)`)。コンペでなくても、P が明確な好み・差し戻し理由を述べたら 1 行残してよい
   - **rapper 参加曲 (任意)**: 韻バンクの未採用の推しコンビが惜しければ、boneyard.md に 1 行追記する (例: `2026-07-10 005: 未採用の韻コンビ「まよいの こおり」×「よるの とおり」(o-i 型)`)
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
   - 入稿セットの前に「**チームからひとこと**」として、演出家・作曲家・作詞家 (rapper 参加曲はさらに客演ラッパー) の `### ひとこと` を 3〜4 行で読み上げる (試聴会の演出。notes.md にも保存済み)
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
- composer が「今回は Persona 非適用推奨」とした曲でも 2 変種の併記は崩さず、手順の冒頭に「**今回は Persona 非適用推奨** (<理由>)」を明記してフル Style を使ってもらう (試したくなったときの適用時 Style も残しておく)
- Style は英語カンマ区切り 10 タグ前後、`ジャンル → ムード → 楽器 → ボーカル → プロダクション` 順。BPM は `92 bpm feel` 表記。実在アーティスト名禁止
- 歌詞は構成タグ英語 + 本文はアーティスト言語 (日本語は入稿版変換済み)。セクション演出は `[Bridge: stripped down, piano only]` 形式のパラメータ付きタグを積極活用する
- インスト曲は「Instrumental トグル ON + `[Instrumental]` + Exclude に `vocals`」の三重指定

## Step 8 — テイク報告後のフォロー

- **採用テイクの Suno URL 報告** → discography.md の該当行を **生成済** に更新して Suno URL を記入し、notes.md のテイク記録に追記する
  - このとき artist.yaml の `suno.persona.created` が false なら (通常は 1 曲目)、**Style Persona 作成を案内する**: suno.com の曲ページ → More Actions (…) → Create → Make Persona → 名前はアーティスト名を推奨 → **公開設定はデフォルト Public なので Private に切り替え (推奨)** → 作成可否のプラン条件は suno-spec (実効版) §6 / §8 で確認して案内する。作成報告を受けたら artist.yaml の `suno.persona` を更新し (created: true / name / source_song / visibility)、discography の該当行の Persona 列を「なし(Persona元曲)」にする
- **YouTube URL 報告** → 該当行を **公開済** に更新して YouTube URL を記入する
  - **公開済が 6 曲に達し、かつ `suno.custom_model` が null なら、Custom Models 化を提案する**: 自作曲 6 トラック以上で現行フラッグシップモデルを自分のスタイルにチューニングできる (プラン条件・上限個数は suno-spec (実効版) §6 / §8 で確認して案内する)。作成されたら `suno.custom_model` に記入する
- **修正要望** (「2 番 A メロが早口」など場所+症状) → 該当エージェントだけに差し戻す (歌詞 → lyricist 単独 / スタイル・設定 → composer 単独)。**韻系の修正** (「韻が浅い」「もっと硬く踏んで」等) は rapper (ドクターモード) → lyricist の 2 段 — rapper に対象行 + 前後 2 行の文脈 + 症状 + 変えてはいけない行を渡して診断と改善候補をもらい、それを添えて lyricist に修正を依頼する。修正のたびに Step 5 の検証を通し、song.json と paste.md を両方更新する。1 回で完成しない前提 (ガチャ運用) を P と共有し、修正箇所は 1 つずつ潰す
  - P が繰り返し口にする好み・NG (「もっと具体的な情景がいい」「サビは短く」等) は `strategy/producer-taste.md` に 1 行残すと、次曲のブリーフ・執筆に効く (契約 C6。ファイルが無ければ Step 7 の防御スニペットで作ってから追記)

## 後処理 (作業が一段落するたび)

- `.production/log.md` に 1 行追記する (例: `2026-07-10 21:30 song: 004 <タイトル> 入稿セット提示`)
- `.production/state.md` を最新化する (進行中の曲・次のアクションを反映。15 行以内)

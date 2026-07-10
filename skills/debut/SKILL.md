---
name: debut
description: アーティスト誕生 (初期セットアップ)。「新しいアーティストを作りたい」「アーティストをデビューさせたい」「バーチャルシンガーを立ち上げたい」「アーティスト設定から始めたい」などの発言、または /suno-artist-production:debut で起動。ヒアリング → 演出家・キャラクターデザイナー・作曲家の並列提案 → P が選択 → アーティストディレクトリ一式 (artist.yaml / profile.md / world.md / character / discography / strategy) を生成し、YouTube 公開方針の確認と 1 曲目制作の提案までつなぐ。
---

# アーティスト誕生 — /suno-artist-production:debut

新しいバーチャルアーティストを 1 人立ち上げ、アーティストディレクトリ一式を生成するフロー。マネージャー (メイン会話のペルソナ) として進行する。スラッシュ起動でも、会話中の「新しいアーティスト作りたい」への応答としての自発起動 (Skill ツール) でも、同じフローに従う。

**原則: 1 ディレクトリ = 1 アーティスト**。cwd 配下がこのアーティストの全データの置き場所になる。

## このスキル実行中の共通ルール

- ユーザーは「〇〇P」と呼ぶ (producer_name 確定前は「P」)。マネージャーに固有名はなく、呼称は「マネージャー」のみ
- 質問はテキストで行う。AskUserQuestion は使わない
- ツールを使うターンでは前置きの実況テキストを書かず、報告はツール結果が返ってからまとめる
- サブエージェント起動プロンプトには、参照させるファイルの**絶対パス**を必ず書く。プラグインルートは hook が注入する絶対パスを使う (未注入なら、この SKILL.md の読み込み元 `<プラグインルート>/skills/debut/SKILL.md` から 2 階層上をプラグインルートとする)
- 世界観・キャラ・名前はすべてオリジナルにする。実在アーティスト・既存作品のキャラクターの流用や、それと分かる模倣はしない
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
- `UNSAFE_DIR` → HOME や / 直下にはアーティストを作らない。「アーティスト用のディレクトリ (例: `~/Music/<アーティスト名>/`) を作って、そこで呼んでください」と案内して終了
- `artist=yes` → 既にこのディレクトリにはアーティストがいる。1 ディレクトリ = 1 アーティストの原則を伝え、(a) 既存アーティストの続きに戻る、(b) 別ディレクトリで新アーティストを作る、のどちらかを P に確認する。既存 artist.yaml を上書きする作り直しは、P が明示的に望んだ場合のみ行う
- `artist=no` → Step 1 へ

## Step 1 — ヒアリング

次を確認する。まとめて聞いてよい。P が「おまかせ」と言った項目は Step 2 の提案側に委ね、1〜2 往復で切り上げる:

1. **コンセプト** — どんなアーティストにしたいか (雰囲気・題材・活動イメージ。自由回答)
2. **歌詞の言語** — ja / en / その他 (アーティストごとに固定される)
3. **ジャンル帯** — 基準となる音楽ジャンルの幅 (「切ない系のエレクトロポップ」程度のラフさで可)
4. **アーティスト名** — 未定なら「候補も出します」と伝えて Step 2 の各案に名前候補を含めさせる
5. **P の呼び名** — 「なんとお呼びすればいいですか? (例: かゆP)」。「〇〇P」の形で答えたら 〇〇 の部分を、名前だけならそのままを `producer_name` にする
6. **Suno のプラン** — pro / premier / free。**free の場合は一言注意を必ず添える**: 「Free プランで作った曲は、あとで有料プランに上げても商用利用できません (商用権は制作時点のプランに紐づきます)。Persona 作成や最新モデルも Pro 以上限定なので、本格運用なら Pro 以上がおすすめです」

## Step 2 — 三職種の並列提案

director / character-designer / composer を **1 メッセージで並列起動**する (subagent_type: `suno-artist-production:director` / `suno-artist-production:character-designer` / `suno-artist-production:composer`)。

各プロンプトに含めるもの:

- Step 1 のヒアリング結果全文
- 「方向性の異なる案を 2〜3 案、それぞれ短い見出し付きで」という依頼
- オリジナル規範 (実在アーティスト・既存キャラの流用禁止)

依頼内容の割り当て:

| 相手 | 返してもらうもの |
|---|---|
| director | **世界観案**: テーマ / 物語の核 / 語彙パレット (使う言葉・避ける言葉) / NG 領域。アーティスト名未定なら名前候補も |
| character-designer | **キャラ案**: 外見 / 性格 / 口調 / 年齢感 / NG 事項 |
| composer | **サウンドアイデンティティ案**: 基準ジャンル帯 / 基準ボーカル像 / 代表的な Style タグ群 (英語) / 推奨既定モデル |

composer のプロンプトには **suno-spec の実効パス**を必ず明記する (hook 注入のコンテキストにある実効パス。未注入なら、上書き版 `${XDG_CONFIG_HOME:-~/.config}/suno-artist-production/suno-spec.md` があればそれ、なければ `<プラグインルート>/skills/suno-spec/references/spec.md`)。「使用モデル・上限・タグ語彙は必ず spec を読んで従う」と指示する。

3 つの成果が揃ったら、マネージャーが「セット案」として整理して提示する (例: 案 A = 世界観 A × キャラ A × サウンド A)。組み替えや部分採用も歓迎と添える。

## Step 3 — P の選択

P の選択・修正指示を受けて確定する。大きな齟齬 (世界観とサウンドの矛盾など) があれば、該当エージェントに 1 回だけ調整を依頼してよい。artist.yaml の全フィールドを埋められる状態になったら Step 4 へ。

## Step 4 — ファイル生成

```bash
ARTIST_ROOT="<Step 0 で判明した絶対パス>"
mkdir -p "$ARTIST_ROOT/character/illust-prompts" \
         "$ARTIST_ROOT/discography/songs" \
         "$ARTIST_ROOT/analytics/reports" \
         "$ARTIST_ROOT/strategy/trends"
```

**artist.yaml** — 次のスキーマで書く。**30〜40 行以内厳守** (hook が毎ターン全文注入するため、肥大させない):

```yaml
schema_version: 1
name: "<アーティスト名>"
name_en: "<ローマ字名>"
debut: "<YYYY-MM-DD>"
language: "<ja / en / ...>"
genre_band: "<基準ジャンル帯 (英語タグ 2〜4 個)>"
vocal: "<基準ボーカル像 (英語)>"
suno:
  preferred_model: "<suno-spec 実効版の現行推奨モデル>"
  plan: "<pro / premier / free>"
  persona:
    created: false
    name: null
    source_song: null
    visibility: "private"
  custom_model: null
youtube:
  publish: true
  channel_url: ""
  api_connected: false
  api_reproposed: false
  repropose_threshold: { subscribers: 1000, total_views: 50000 }
production:
  producer_name: "<〇〇P の 〇〇>"
themes: "<テーマの 1 行サマリ>"
```

- `preferred_model` は suno-spec 実効版に書かれた現行推奨モデルを確認して設定する (この SKILL.md にも会話にもモデル名をハードコードしない)
- `youtube.publish` は Step 5 の回答で確定する (それまでは仮置きの true)

**profile.md** — プロフィール・経歴・人物像を散文で (director と character-designer の採用案から構成する)。

**world.md** — 世界観設定 (演出家の管轄ファイル): テーマ / 物語の核 / 語彙パレット (使う言葉・避ける言葉) / NG 領域。

**character/character.md** — 外見 / 性格 / 口調 / 年齢感 / NG 事項。

**character/illust-prompts/<YYYY-MM-DD>_base-portrait.md** — character-designer がベース立ち絵用の画像生成プロンプト (英語) を出していれば保存する (任意)。

**discography/discography.md**:

```markdown
# ディスコグラフィー — <アーティスト名>

状態は 制作中 → 生成済 → 公開済 の 3 値。採用テイクの URL 報告で「生成済」、YouTube URL 報告で「公開済」に更新する。

| No | タイトル | 制作日 | 状態 | Suno URL | YouTube URL | Persona | メモ |
|---|---|---|---|---|---|---|---|
```

**strategy/direction.md**:

```markdown
# 方針メモ — <アーティスト名>

## <YYYY-MM-DD> デビュー時の初期方針
- コンセプト: <1〜2 行>
- 基準ジャンル帯: <genre_band> / 歌詞言語: <language>
- 当面の目標: <1 曲目の方向性など>
```

## Step 5 — YouTube 公開方針の確認

ファイル生成後、**「この子の曲、YouTube に公開していきます?」**を確認する。

- **公開しない** → `youtube.publish: false` に更新する。**以後、こちらから YouTube の話 (チャンネル登録・分析・API 連携) は一切持ち出さない**。P が言い出したら再開する
- **公開する** → `publish: true` のまま、チャンネルの有無を聞く:
  - **チャンネルが既にある** → URL を聞いて登録する。artist.yaml の `youtube.channel_url` を更新し、`analytics/channels.yaml` を作る:

    ```yaml
    channel_url: "<URL>"
    channel_name: "<チャンネル名>"
    registered_at: "<YYYY-MM-DD>"
    ```

    登録したこのタイミングで**一度だけ**、API 連携をメリット説明付きで提案する:
    「YouTube Analytics API をつなぐと、再生数だけでなく**視聴維持率・平均視聴時間・流入経路**まで見られて、曲作りへのフィードバック精度が上がります。無料で、初回セットアップは 10〜15 分です。やってみます?」
    - 受ける → `connect-youtube` スキルを起動して手順へ
    - 見送り → URL 登録のみで完了 (`api_connected: false` のまま)。この場で再提案はしない (チャンネル規模が閾値に達したとき :analyze が一度だけ再提案する)
  - **まだない** → `channel_url` は空のままにし、「チャンネルができたら URL を教えてください。そのときに登録します」と案内する (API 連携の提案もその登録時に行う)

## Step 6 — 1 曲目の提案とその先の案内

セットアップ完了を報告し、**1 曲目の制作を提案する** (「早速 1 曲目、いきましょうか」→ 受けたら `song` スキルのフローへ)。

あわせて次を軽く予告しておく:

- 1 曲目の採用テイクが決まったら、その曲から **Style Persona** を作る (下記手順)。以後の曲で声とスタイルの一貫性の主軸になる
- 公開済みが 6 曲たまったら Custom Models 化を提案する予定であること

### Style Persona 作成手順 (1 曲目の採用テイク確定時に案内する)

1. suno.com で採用テイクの曲ページを開き、More Actions (…) → **Create → Make Persona**
2. 名前はアーティスト名を推奨。アバター・説明文も設定する
3. **公開設定はデフォルトが Public**。他ユーザーに使われたくなければ、**トグルで Private に切り替える (推奨)**
4. Persona 作成にはプラン条件がある — 可否は suno-spec (実効版) §6 / §8 で確認して案内する
5. 作成できたら報告してもらい、artist.yaml の `suno.persona` を更新する (`created: true` / `name` / `source_song: "001 <タイトル> (<URL>)"` / `visibility`)

## 後処理 (作業が一段落するたび)

- `.production/log.md` に 1 行追記する (例: `2026-07-10 21:00 debut: <アーティスト名> セットアップ完了`)
- `.production/state.md` を最新化する (現在フォーカス / 進行中の曲 / 未解決事項 / 次のアクション。15 行以内)

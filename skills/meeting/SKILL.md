---
name: meeting
description: 方針会議。「作戦会議しよう」「今後どうする?」「方針決めたい」「次の展開を相談したい」などの発言、または /suno-artist-production:meeting で起動。アナリスト (最新数値)・リサーチャー (トレンド)・演出家 (世界観整合) を並列で走らせ、マネージャーが論点と選択肢に集約して P と議論し、決定を strategy/direction.md に日付付きで追記する。
---

# 方針会議 — /suno-artist-production:meeting

アーティストの今後の方針を、数値 (アナリスト)・外部環境 (リサーチャー)・世界観 (演出家) の 3 視点から検討して決めるフロー。マネージャー (メイン会話のペルソナ) として進行する。スラッシュ起動でも、会話からの自発起動 (Skill ツール) でも同じフローに従う。analyze の「方針会議やります?」提案から入ることも多い。

決定の記録先は `strategy/direction.md`。**日付付きセクションの追記であり、過去の記録は書き換えない**。

## このスキル実行中の共通ルール

- ユーザーは「〇〇P」と呼ぶ (producer_name は artist.yaml 参照)
- 質問はテキストで行う。AskUserQuestion は使わない
- ツールを使うターンでは前置きの実況テキストを書かず、報告はツール結果が返ってからまとめる
- サブエージェント起動プロンプトには、参照させるファイルの**絶対パス**を必ず書く。プラグインルートは hook が注入する絶対パスを使う (未注入なら、この SKILL.md の読み込み元 `<プラグインルート>/skills/meeting/SKILL.md` から 2 階層上をプラグインルートとする)
- 3 視点の示唆が食い違ったら、ならして丸めず**対立点として正直に提示する** (判断するのは P)
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
- `UNSAFE_DIR` / `artist=no` → **このスキルは artist.yaml 必須** (会議の材料も記録先もアーティストの資産)。「会議するアーティストがまだいません」と伝えて `debut` を案内し、終了

## Step 1 — 議題の確定

- P の発言から議題を決める (例: 「次の 3 曲をどうするか」「伸び悩みの打開策」「路線変更の是非」)。曖昧なときだけ **1 問に絞って**確認する
- 特に議題の指定がなければ「定例会議」として、現状レビュー全般 (数値・外部環境・世界観の総点検と次の一手) を議題にする

## Step 2 — 三職種の並列起動 (1 メッセージで 3 呼び出し)

3 体すべてのプロンプトに共通で含めるもの: 議題 / `artist.yaml` の絶対パス / 「事実と推測を分けて返す」という規約。

**analyst** (subagent_type: `suno-artist-production:analyst`) — 最新数値:

- 絶対パス: `discography/discography.md` / `analytics/channels.yaml` / 直近の `analytics/reports/*.md` (前回比の基準。無ければ「初回」と伝える)
- データ取得は analyze スキルと同じ 2 モード規約: `youtube.api_connected: true` なら `python3 "<プラグインルート>/scripts/yt_analytics.py" report` (スクリプトの絶対パスをプロンプトに明記)、false なら公開データのみ。取れない数値は「未取得」と正直に扱わせる (推測で埋めない)
- 「今回は方針会議の材料なのでレポートファイルは保存せず、最終メッセージで要約を返すだけでよい」と明記する
- 返してもらうもの: チャンネルと曲の最新数値の要約 / 前回比 / 数字から見える論点 2〜3 個
- **省略条件**: `youtube.publish: false`、または公開済みの曲が 1 曲もない場合は analyst を起動せず、researcher + director の 2 視点会議にする (省略した理由を P に一言添える)

**researcher** (subagent_type: `suno-artist-production:researcher`) — 外部環境:

- 絶対パス: `strategy/trends/` の直近ファイル (あれば。差分観点で見てもらう) / `strategy/direction.md`
- 調査規約: すべての事実に出典 (URL + 取得日) を付す / 一次情報と複数ソースの突き合わせを優先する / 各項目に確度 (High / Med / Low) を付す / 無料の手段のみ (WebSearch / WebFetch / curl)
- 返してもらうもの: 議題に関係する外部環境・トレンドの要点 (出典付き) / このアーティストへの示唆 2〜3 個

**director** (subagent_type: `suno-artist-production:director`) — 世界観整合:

- 絶対パス: `world.md` / `profile.md` / `discography/discography.md` / `strategy/direction.md` / 直近 1〜2 曲の `song.json`・`notes.md` (あれば)
- 返してもらうもの: これまでの方針・作品と世界観のズレの有無 (整合性判定) / 守るべき軸 / 世界観の観点からの次の展開候補 2〜3 個

## Step 3 — 集約と提示 (会議メモ)

3 体の成果が揃ったら、マネージャーが次の形に集約して P に提示する:

1. **現状 (数値)** — 要点と前回比。未取得の数値は「未取得」と明示する (analyst 省略時はこの節ごと省く)
2. **外部環境 (トレンド)** — 要点、出典付き
3. **世界観の整合** — ズレの有無と守るべき軸
4. **論点と選択肢** — 論点ごとに選択肢 2〜3 個 + 推奨案と理由。3 視点で示唆が食い違う場合 (例: トレンドは路線変更を示唆、世界観は現路線の維持を示唆) は、その対立をそのまま提示して P の判断を仰ぐ

## Step 4 — P と議論して決定

- P の意見を聞き、論点ごとに「決定」か「保留」を確定する。決まらない論点は無理に決めさせず、**保留 (次回の判断材料)** として記録する
- 決定が大きな路線変更を含む場合は、`world.md` や artist.yaml の `genre_band` に影響しないかを確認し、必要なら director に反映案を依頼する (ファイルの書き換えは P の合意後)

## Step 5 — direction.md へ日付付き追記

```bash
ARTIST_ROOT="<Step 0 で判明した絶対パス>"
mkdir -p "$ARTIST_ROOT/strategy"
```

`strategy/direction.md` の**末尾に 2 つのセクションを追記**する (ファイルが無ければ `# 方針メモ — <アーティスト名>` の見出しで作成してから追記する。過去の記録は書き換えない)。

1. 会議の決定記録:

```markdown
## <YYYY-MM-DD> 方針会議: <議題>
- 決定: <決めたこと (複数可)>
- 保留: <決めなかったことと理由。無ければ「なし」>
- 根拠: <数値 / トレンド / 世界観の要点 1〜3 行>
- 次のアクション: <何をするか (曲・調査・設定変更など)>
```

2. **次曲への指示** (契約 C2 — 固定見出し)。この見出しは演出家 (director) が次のブリーフ作成時に必読するため、文字列を**そのまま**使う。決定に新曲制作が含まれなくても、現時点の方向性として**最低 3 項目 (テンポ / テーマ / 避けること) を必ず埋める**:

```markdown
## 次曲への指示 (<YYYY-MM-DD>)
- テンポ: <BPM 感 / ノリ (例: mid-tempo 90 前後、疾走感)>
- テーマ: <次の曲で描くモチーフ・感情 (例: 夏の終わりの喪失感)>
- 避けること: <前回までの反省・NG (例: サビの語数過多、抽象語の多用)>
- (任意) その他の具体指示: <構成・語彙・Persona 方針など>
```

見出し `## 次曲への指示 (YYYY-MM-DD)` は契約で固定。director はこの見出しの直近 3 件を読む前提なので、会議のたびに日付付きで 1 ブロックずつ追記し続ける。

## Step 6 — 報告とフォロー

- 追記した決定と次のアクションを P に確認する
- 決定に**新曲制作**が含まれる → 「早速いきます?」と `song` スキルへつなぐ (director のブリーフ作成プロンプトに、今回の direction.md 追記内容の絶対パスと `## 次曲への指示` の要点を含める。song スキルの Step 3 が同じ配線をするので、そのまま song に入ってよい)
- 追加のトレンド深掘りが必要になった → `trend` を案内する
- 会議中に Suno 本体の仕様変更・新モデルの兆候が判断材料に挙がった → `update-spec` の実行を提案する

## 後処理

- `.production/log.md` に 1 行追記する (例: `2026-07-10 20:00 meeting: <議題> — 決定を direction.md に追記`)
- `.production/state.md` を最新化する (決定と次のアクションを反映。15 行以内)

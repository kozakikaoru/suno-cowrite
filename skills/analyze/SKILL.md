---
name: analyze
description: YouTube 分析。「再生数どう?」「YouTube 見てきて」「伸びてる?」「アナリティクス確認して」「コメントの反応どう?」などの発言、または /suno-artist-production:analyze で起動。アナリストがチャンネルと公開曲の数値を確認し、前回比付きレポートを analytics/reports/ に保存して所見と次の一手を提案する。API 未接続なら公開データ、接続済みなら YouTube Analytics API を使う。
---

# YouTube 分析 — /suno-artist-production:analyze

公開済み楽曲と YouTube チャンネルの数値をアナリストに確認させ、前回比付きレポートを残すフロー。マネージャー (メイン会話のペルソナ) として進行する。スラッシュ起動でも、会話からの自発起動 (Skill ツール) でも同じフローに従う。

## このスキル実行中の共通ルール

- ユーザーは「〇〇P」と呼ぶ (producer_name は artist.yaml 参照)
- 質問はテキストで行う。AskUserQuestion は使わない
- ツールを使うターンでは前置きの実況テキストを書かず、報告はツール結果が返ってからまとめる
- サブエージェント起動プロンプトには、参照させるファイルの**絶対パス**を必ず書く。プラグインルートは hook が注入する絶対パスを使う (未注入なら、この SKILL.md の読み込み元 `<プラグインルート>/skills/analyze/SKILL.md` から 2 階層上をプラグインルートとする)
- 数値は取れたものだけを報告する。**取れなかった数値は「未取得」と正直に扱い、推測で埋めない**
- 作業の区切りで `.production/log.md` に 1 行追記し、`.production/state.md` を最新化する

## Step 0 — 前提チェックと YouTube 方針の分岐

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
- `UNSAFE_DIR` / `artist=no` → **このスキルは artist.yaml 必須**。「分析対象のアーティストがまだいません」と伝えて `debut` を案内し、終了
- artist.yaml の `youtube` ブロックを確認して分岐する:

**`youtube.publish: false` の場合 — 丁寧にスキップ**:

- 例: 「<アーティスト名> は YouTube には出さない方針で記録しています。今回の分析はスキップしますね。方針を変えるなら、そう言ってもらえれば切り替えて始めます」
- P が「やる」と明言した場合のみ `youtube.publish: true` に更新して続行する。こちらから説得はしない

**`youtube` ブロックが無い / publish 未確認の場合 (初回 :analyze)**:

- 「YouTube に公開していきます?」を確認する。しない → `youtube.publish: false` を記録して終了 (以後こちらから持ち出さない)。する → publish: true を記録して Step 1 へ

## Step 1 — チャンネル登録 (初回のみ)

`analytics/channels.yaml` が無い、または `youtube.channel_url` が空なら、チャンネル URL を聞いて登録する:

```yaml
channel_url: "<URL>"
channel_name: "<チャンネル名>"
channel_id: "<UCxxxx>"   # RSS 取得の鍵。登録時に URL から一度だけ解決して保存
registered_at: "<YYYY-MM-DD>"
```

- artist.yaml の `youtube.channel_url` も合わせて更新する (動画単位の URL は discography.md に集約し、二重管理しない)
- **`channel_id` は登録時に URL から一度だけ解決して保存する** (アナリストが RSS `feeds/videos.xml?channel_id=...` を引く鍵になる):
  - `https://www.youtube.com/channel/UCxxxx` 形式 → URL 中の `UCxxxx` がそのまま `channel_id`
  - ハンドル URL (`https://www.youtube.com/@handle`) やカスタム URL しか無い場合 → そのチャンネルページを WebFetch し、HTML 内の `"channelId":"UC…"` またはページの canonical/RSS リンク (`.../channel/UC…`) から `UC` で始まる ID を 1 度だけ抽出して保存する
  - 解決できなければ `channel_id` は空のままにする (アナリストは RSS をスキップし oEmbed / ページ取得で運用する)
- **既に channels.yaml があるが `channel_id` が未保存の場合** (旧 debut 生成分など) は、この Step で同じ手順で解決して追記する (URL 登録済みでもこのバックフィルは行う)
- **この登録タイミングで一度だけ**、`youtube.api_connected` が false なら API 連携をメリット説明付きで提案する: 「Analytics API をつなぐと、再生数だけでなく**視聴維持率・平均視聴時間・流入経路**まで見られて、曲作りへのフィードバック精度が上がります。無料で、初回セットアップは 10〜15 分です」
  - 受ける → `connect-youtube` スキルを起動し、完了後にこの分析を続行する
  - 見送り → 公開データモードで続行する (この場での再提案はしない。規模到達時に Step 4 が一度だけ再提案する)
- チャンネルがまだ無い → 「チャンネルができたら教えてください」で終了する

## Step 2 — アナリスト起動 (2 モード)

subagent_type `suno-artist-production:analyst` を起動する。共通でプロンプトに含める絶対パス: `analytics/channels.yaml` (`channel_id` を含む) / `discography/discography.md` (公開済み動画 URL の単一管理点) / `discography/songs/` (各曲 song.json の特徴を突き合わせる元) / `analytics/metrics.yaml` (曲別メトリクス台帳。無ければ「初回・未作成」と伝える) / 直近の `analytics/reports/*.md` (前回比の基準。無ければ「初回」と伝える)。

**未接続モード (`youtube.api_connected: false`)**:

- **公開データのみ**で確認する。API キー不要の手段を **RSS → oEmbed → ページ取得の優先順位**で使う (詳細な手順は analyst.md が定義)。`channel_id` があれば RSS (`feeds/videos.xml?channel_id=...`) が動画ごとの再生数・公開日を安定して返す第一手段になる
- 「取れない数値 (高評価数・登録者数・RSS 圏外の旧曲の再生数など) は取れないと正直に報告する (推測で埋めない)」という規約をプロンプトに明記する

**接続済みモード (`youtube.api_connected: true`)**:

- `python3 "<プラグインルート>/scripts/yt_analytics.py" report` の実行を指示する (JSON で数値が返る。オプションは `--help` で確認)。視聴維持率・平均視聴時間・流入経路・登録者増減まで取得する
- API エラー時はエラー内容を報告してもらい、公開データモードに縮退する (P にはエラーの事実を伝える)

返してもらうもの: チャンネル概況 (登録者・総再生) / 動画別数値 / 前回レポートとの差分 / 気になる傾向 (伸びた曲・失速・コメントの声) / **メトリクス台帳用スナップショット** (曲ごとの published_at・latest_views・likes・retention の生値。台帳更新に使う) / **伸びた曲/伸びない曲の共通項の仮説** (metrics.yaml × song.json の目視相関) / 未取得項目の明示。

## Step 3 — レポート保存とメトリクス台帳更新

マネージャーが `analytics/reports/YYYY-MM-DD.md` に保存する (同日 2 回目は上書き更新でよい):

```markdown
# YouTube 分析 — <YYYY-MM-DD> (<アーティスト名>)

## チャンネル概況
| 指標 | 今回 | 前回 (<前回日付>) | 差分 |
|---|---|---|---|
| 登録者数 | | | |
| 総再生回数 | | | |

## 動画別
| No | 曲 | 再生数 | 高評価 | コメント | 前回比 | 備考 |
|---|---|---|---|---|---|---|

## 所見
- <伸びている曲と仮説 / 失速と仮説 / コメント傾向>

## 次の一手 (提案)
- <曲作り・公開運用への具体提案>

## データソースと未取得項目
- 取得手段: <公開データ / Analytics API>
- 未取得: <正直に列挙。無ければ「なし」>
```

- 接続済みモードでは「維持率・平均視聴時間・流入経路」のセクションを追加する
- 初回 (前回レポートなし) は前回列を「—」にする

### メトリクス台帳 `analytics/metrics.yaml` の更新 (レポート保存と同時)

アナリストが返した【メトリクス台帳用スナップショット】を使い、マネージャーが `analytics/metrics.yaml` を更新する (無ければ新規作成)。曲 No をトップキーにした成績台帳で、**公開後 7 日 / 30 日の再生数は取り逃すと後から埋められない**ため、:analyze のたびに必ず更新する。

スキーマ (曲 No キー):

```yaml
"001":
  published_at: "2026-07-10"   # 公開日 (RSS の published / API の published_at から。判明時に一度書く)
  views_d7: 1200               # 公開後7日時点の再生数。下の窓で一度だけ記録し、以後上書きしない
  views_d30: 5400              # 公開後30日時点の再生数。同上
  latest_views: 8800           # 最新スナップショットの再生数 (毎回上書き)
  likes: 210                   # 最新の高評価数 (取れた時のみ更新、未取得なら据え置き)
  retention: null              # 平均視聴維持率(%)。API 接続時のみ数値、未接続は null
  snapshot_at: "2026-08-09"    # 今回の取得日 (毎回更新)
```

記録ルール:

- **latest_views / snapshot_at** は毎回上書き更新する。**likes / retention** は今回取れた時だけ更新し、未取得なら前回値を据え置く (null で上書きしない)。
- **views_d7** は「公開後 7〜13 日」の範囲で初めて取得できた回に限り、その時の再生数を書き込む。すでに値があれば触らない。14 日以降に初めて分析した曲は取り逃しとして **null のまま固定**する。
- **views_d30** も同様に「公開後 30〜44 日」で初めて取得できた回に一度だけ記録し、45 日以降の初回取得は null 固定。
- 公開後日数は `published_at` と今日の日付から数える。`published_at` が未取得の曲は d7/d30 判定を保留し、latest_views だけ記録する。
- 新しく公開された曲は新しいキーとして追記し、既存キーは上書きせず必要なフィールドだけ更新する (台帳全体を破壊しない)。

## Step 4 — 閾値判定 (API 連携の再提案、一度だけ)

Step 2 で取得した公開数値で判定する。**次の 3 条件がすべて真**のときだけ、API 連携を一度だけ再提案する:

1. 登録者数 >= `youtube.repropose_threshold.subscribers` **または** 総再生回数 >= `youtube.repropose_threshold.total_views` (既定: 1,000 人 / 50,000 回。artist.yaml で変更可能)
2. `youtube.api_connected: false`
3. `youtube.api_reproposed: false`

- 文面例: 「チャンネルが収益化ラインの視野に入る規模になってきました。ここから先は維持率や流入経路が意思決定の質を左右するので、API 連携 (connect-youtube) を改めておすすめします」
- **提案したら、受諾するかどうかにかかわらず** artist.yaml の `youtube.api_reproposed: true` に更新し、以後この再提案は繰り返さない
- 数値が取得できなかった回は判定せず、フラグも変えない

## Step 5 — 報告

- 前回比の要点 (所見) と提案を P に報告する
- 気になる傾向があれば「方針会議 (meeting) やります?」と添える (台帳から出た「伸びた曲の共通項」の仮説は、会議 → direction.md の次曲指示 → 次の曲づくりへ渡す価値があるので、会議提案の材料にする)

## 後処理

- `.production/log.md` に 1 行追記する (例: `2026-07-10 18:00 analyze: レポート保存 + metrics.yaml 更新 (公開データモード)`)
- `.production/state.md` を最新化する

---
name: connect-youtube
description: YouTube Analytics API 連携セットアップ。「YouTube 連携したい」「API つないで」「視聴維持率まで見たい」「アナリティクスをつなごう」などの発言、debut・analyze での連携提案の受諾、または /suno-artist-production:connect-youtube で起動。Google Cloud Console の設定 (プロジェクト作成 → API 有効化 → OAuth 同意画面 → クライアント ID 作成) を番号付き手順で案内し、client_secret.json の配置 → ブラウザ認証 → 接続テスト → artist.yaml の youtube.api_connected 更新までを完了させる。無料、初回 10〜15 分。
---

# YouTube Analytics API 連携 — /suno-artist-production:connect-youtube

アナリストを「接続済みモード」(視聴維持率・平均視聴時間・流入経路まで取得できる) にするための初回セットアップフロー。マネージャー (メイン会話のペルソナ) として進行する。debut や analyze での提案を P が受けたとき、または P が直接言い出したときに起動する。

- 使うもの: Google Cloud Console (P がブラウザで操作) + `<プラグインルート>/scripts/yt_analytics.py` (サブコマンド: `auth` / `report` / `status`。Python 3 標準ライブラリのみで動く)
- 費用: 無料。所要は初回のみ 10〜15 分
- **認証情報 (client_secret.json / token.json) はユーザー設定ディレクトリ `${XDG_CONFIG_HOME:-~/.config}/suno-artist-production/` に置く。アーティストディレクトリには置かない** (git に混入させない)。一度接続すればユーザー単位で共有され、別アーティストでは artist.yaml の更新だけで使える

## このスキル実行中の共通ルール

- ユーザーは「〇〇P」と呼ぶ (producer_name は artist.yaml 参照)
- 質問はテキストで行う。AskUserQuestion は使わない
- ツールを使うターンでは前置きの実況テキストを書かず、報告はツール結果が返ってからまとめる
- スクリプトは必ず絶対パスで実行する。プラグインルートは hook が注入する絶対パスを使う (未注入なら、この SKILL.md の読み込み元 `<プラグインルート>/skills/connect-youtube/SKILL.md` から 2 階層上をプラグインルートとする)
- **秘匿ファイル (client_secret.json / token.json) の中身をチャットに表示しない**。扱うのはパスと有無・パーミッションだけ
- P のブラウザ操作を待つ工程では先回りしない。「できました」の報告を待って次へ進む
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
- `UNSAFE_DIR` / `artist=no` → **このスキルは artist.yaml 必須** (最後に youtube 設定を記録するため)。「連携結果を記録するアーティストがまだいません」と伝えて `debut` を案内し、終了
- artist.yaml の `youtube` ブロックを確認する:
  - `youtube.publish: false` → このスキルを P が呼んだこと自体が再開の意思表示のはずだが、念のため「YouTube はやらない方針で記録していますが、公開方針に切り替えて連携を進めていいですか?」と確認し、OK なら `publish: true` に更新して続行する
  - `youtube.api_connected: true` → 既に接続済み。Step 5 の接続テストだけ実行して健全性を確認し、問題なければ「すでに使える状態です」と報告して終了する

## Step 1 — 現状確認

```bash
python3 "<プラグインルート>/scripts/yt_analytics.py" status
```

- **「総合: 利用可能」(終了コード 0)** → 認証はユーザー単位で済んでいる (別アーティストで設定済みのパターン)。Google Cloud の手順は不要なので Step 5 の接続テストへ飛ぶ
- **「総合: 未接続」(終了コード 2)** → status が示す不足に応じて開始位置を決める: client_secret.json が無い → Step 2 から / 配置済みで未認証 → Step 4 から
- あわせて前提を P に確認する: (a) 分析したい YouTube チャンネルがあること (b) そのチャンネルを所有する Google アカウントでブラウザにログインできること

## Step 2 — Google Cloud Console の設定 (P がブラウザで操作)

次の手順を**番号ごとそのまま P に提示**する (Google 側の改版で画面名が多少変わることがある、と添える):

1. **プロジェクト作成** — https://console.cloud.google.com/ に**チャンネルを所有する Google アカウント**でログインし、画面上部のプロジェクトセレクタ → 「新しいプロジェクト」。プロジェクト名は `suno-artist-production` など分かるもので OK
2. **API の有効化 (2 つ)** — 左メニュー「API とサービス」→「ライブラリ」で、次の 2 つを 1 つずつ検索して「有効にする」を押す:
   - **YouTube Analytics API**
   - **YouTube Data API v3**
3. **OAuth 同意画面の設定** — 「API とサービス」→「OAuth 同意画面」:
   - User Type は **「外部 (External)」** を選ぶ
   - アプリ名 (例: suno-artist-production)・ユーザーサポートメール・デベロッパー連絡先を入力して保存する
   - スコープの追加登録は不要 (認証実行時にスクリプト側が読み取り専用スコープを要求する)
   - テストユーザーに**自分の Google アカウント**を追加する
   - **重要: 公開ステータスを「テスト」のままにしない** — テストモードで発行されるリフレッシュトークンは **7 日で失効**し、毎週ブラウザ認証をやり直すはめになる。同意画面の「アプリを公開」(本番環境にプッシュ) を押して**本番公開にしておくことを強く推奨**する。自分専用のアプリでも公開してよく、Google の審査に出す必要もない (未確認アプリのまま使える。認証時に警告画面が出るだけ — 進み方は Step 4 で案内)
4. **OAuth クライアント ID の作成** — 「API とサービス」→「認証情報」→「認証情報を作成」→「OAuth クライアント ID」:
   - アプリケーションの種類は **「デスクトップ アプリ」** を選ぶ (それ以外の種類ではこのスクリプトは動かない)
   - 名前は任意 → 「作成」
5. **JSON のダウンロード** — 作成直後のダイアログ (または認証情報一覧の該当クライアント右端のダウンロードアイコン) から**クライアントの JSON をダウンロード**し、保存先 (例: `~/Downloads/client_secret_….json`) をマネージャーに知らせてもらう

## Step 3 — client_secret.json の配置 (マネージャーが実行)

P からダウンロード先のパスを聞いたら、所定の位置へ移して権限を絞る:

```bash
CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/suno-artist-production"
mkdir -p "$CONF_DIR" && chmod 700 "$CONF_DIR"
mv "<ダウンロードされた JSON の絶対パス>" "$CONF_DIR/client_secret.json"
chmod 600 "$CONF_DIR/client_secret.json"
ls -l "$CONF_DIR/client_secret.json"
```

- パーミッションが `-rw-------` (600) になっていることを確認する
- ファイルの中身はチャットに表示しない

## Step 4 — ブラウザ認証 (auth)

実行する前のターンで、P に次を伝えて準備 OK をもらう:

- 「実行するとブラウザで Google の許可画面が開きます。**チャンネルを所有するアカウント**を選んで許可してください (ブランドアカウントのチャンネルなら、アカウント選択画面でそのチャンネル名義を選ぶ)」
- 「『Google ではこのアプリを確認していません』という警告が出たら、『詳細』→『(アプリ名) に移動』で進んで大丈夫です (自分で作った自分専用のアプリなので)」

準備 OK をもらってから実行する。**ブラウザ操作待ちで最大 5 分ブロックするため、Bash のタイムアウトは 5 分以上 (300000 ミリ秒以上) に設定する**:

```bash
python3 "<プラグインルート>/scripts/yt_analytics.py" auth
```

- 成功 → 「認証に成功しました」と表示され、token.json が `$CONF_DIR` にパーミッション 600 で保存される
- タイムアウト・キャンセル → 事情を聞いて、もう一度 `auth` を実行する
- 「refresh_token が発行されませんでした」という注意が出た → 過去の許可が残っている可能性がある。https://myaccount.google.com/permissions で当該アプリのアクセス権を削除してから `auth` をやり直すと発行される

## Step 5 — 接続テスト

```bash
python3 "<プラグインルート>/scripts/yt_analytics.py" status
python3 "<プラグインルート>/scripts/yt_analytics.py" report --days 28
```

- status が「総合: 利用可能」で、report が JSON の数値を返せば成功
- report が「期間内のデータがありません」でも**接続としては成功** (Analytics の集計は 24〜48 時間ほど遅れることがあり、新しいチャンネルではよくある)。その旨を P に伝える
- 403 エラー → API の有効化漏れ (Step 2-2) か、チャンネル所有者ではないアカウントで認証した可能性。下のトラブルシューティングに従って該当ステップをやり直す

## Step 6 — artist.yaml の更新と報告

1. artist.yaml の `youtube.api_connected` を `true` に更新する
2. `youtube.channel_url` が空なら、この機会にチャンネル URL を聞いて登録する (artist.yaml と `analytics/channels.yaml` の両方。channels.yaml は `channel_url` / `channel_name` / `registered_at` の 3 項目)
3. P に完了を報告する。例: 「連携できました! 次の分析から視聴維持率・平均視聴時間・流入経路まで見られます。さっそく見てみます?」→ 受けたら `analyze` スキルのフローへ

## 収益データについての注記 (聞かれたら答える)

- 推定収益などの**収益系メトリクスは、この連携では取得しない**。取得には (a) 追加の OAuth スコープ (`yt-analytics-monetary.readonly`) と (b) **チャンネルが収益化済み (YouTube パートナープログラム参加済み) であること**の両方が必要
- 現状のスクリプトが要求するのは読み取り 2 スコープ (`yt-analytics.readonly` / `youtube.readonly`) のみ。収益データが必要になったら、その時点で対応を検討する

## トラブルシューティング早見

| 症状 | 原因と対処 |
|---|---|
| 終了コード 2 + 「client_secret.json が見つかりません」 | Step 2〜3 が未完了。表示される手順に従って配置する |
| 終了コード 2 + 「再認証が必要」(invalid_grant) | リフレッシュトークンの失効。**同意画面がテストモードだと 7 日で失効する** — Step 2-3 の本番公開に切り替えてから `auth` をやり直す |
| 403 (アクセス拒否) | API の有効化漏れ、またはチャンネル所有者ではないアカウントで認証している。Step 2-2 と認証アカウントを確認する |
| quota 超過 | 時間を置いて再実行する (このプラグインの読み取り頻度なら通常は到達しない) |

## 後処理

- `.production/log.md` に 1 行追記する (例: `2026-07-10 21:00 connect-youtube: API 連携完了 (api_connected: true)`)
- `.production/state.md` を最新化する

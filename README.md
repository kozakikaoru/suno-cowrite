# suno-artist-production

Suno (suno.com) 用のバーチャル音楽プロダクションを再現する Claude Code プラグイン。

`/suno-artist-production:studio` でマネージャー (受付ペルソナ) が起動し、演出家・作曲家・作詞家・リサーチャー・アナリスト・キャラクターデザイナーの 6 職種サブエージェントへ実務を自動振り分けする。**1 ディレクトリ = 1 アーティスト**で継続プロデュースし、Suno Custom Mode の全設定値 (Title / Style / Lyrics / Exclude / スライダー / Persona 運用) を「欄ごとに貼り付けられる形式 (paste.md) + 機械可読 JSON (song.json)」で出力する。

## 動作要件

- Claude Code (プラグイン対応バージョン)
- bash / python3 (標準ライブラリのみ。hooks・検証スクリプトが使用)
- git (任意。アーティストディレクトリの git 管理は必須ではない)

## インストール

### marketplace 経由

marketplace リポジトリ (`.claude-plugin/marketplace.json` にこのプラグインを載せたもの) を用意し、Claude Code 内で:

```
/plugin marketplace add <marketplace の Git リポジトリ or ローカルパス>
/plugin install suno-artist-production@<marketplace 名>
```

### ローカル開発 (このリポジトリを直接試す)

このリポジトリをローカルパスとして marketplace 登録するか、開発用のプラグイン読み込みオプション (`claude --help` で確認) を使う。動作確認は「新しい空ディレクトリで `claude` を開いて `/suno-artist-production:studio`」が最短。

## 使い方 (最短ルート)

```
mkdir -p ~/Music/my-artist && cd ~/Music/my-artist
claude
> /suno-artist-production:studio        # ターン 1: マネージャーが挨拶だけ返す (ツール禁止ターン)
> 新しいアーティストをデビューさせたい      # ターン 2: ここから実処理 (debut フローへ)
```

以後は自然言語で「新曲作りたい」「トレンド調べて」「再生数どう?」のように話しかければ、マネージャーが適切なサブエージェント/スキルに振り分ける。

マネージャーはあなたの呼び名 (「〇〇P」) を**質問せず自動で判定**して呼びかける (優先順に artist.yaml の `producer_name` → Claude のアカウント表示名 → macOS のフルネーム → git のユーザー名 → `$USER`)。変えたいときは「〇〇P に変えて」と言えば `artist.yaml` の `producer_name` が更新され、以後それで呼ばれる。

## コマンド一覧

| コマンド | 用途 |
|---|---|
| `/suno-artist-production:studio` | 起動 (メイン入口)。2 段階起動、以後は自然言語で全ユースケース |
| `:debut` | アーティスト誕生 (世界観・キャラ・サウンドの初期セットアップ) |
| `:song` | 新曲制作 (アーティスト文脈あり。ブリーフ → 作曲/作詞並列 → 検証 → 入稿セット) |
| `:oneshot` | 単発曲制作 (アーティスト文脈なしの 1 曲) |
| `:trend` | トレンド調査 (出典付きで `strategy/trends/` に保存) |
| `:analyze` | YouTube 分析 (公開データ、API 接続済みなら Analytics API) |
| `:meeting` | 方針会議 (アナリスト+リサーチャー+演出家の並列調査 → 方針決定) |
| `:update-spec` | Suno 仕様の再調査・更新 (上書き版 spec の生成) |
| `:connect-youtube` | YouTube Analytics API の OAuth 接続セットアップ (任意機能) |

`skills/songwriting/` と `skills/suno-spec/` はコマンドではなく**参照資料コンテナ** (SKILL.md は目次役)。

## プラグインのディレクトリ構成

```
suno_artist_production/
├── .claude-plugin/plugin.json           # プラグインマニフェスト
├── README.md
├── agents/                              # サブエージェント定義 (frontmatter は description のみ)
│   ├── director.md                      # 演出家: 世界観設計・コンセプトブリーフ
│   ├── composer.md                      # 作曲家: Style/Exclude/スライダー/モデル/Persona 適用判断
│   ├── lyricist.md                      # 作詞家: 作品版 + 入稿版の 2 表記、オリジナリティ自己検査
│   ├── researcher.md                    # リサーチャー: トレンド/仕様調査、歌詞の Web 照合
│   ├── analyst.md                       # アナリスト: YouTube 数値レポート (公開データ/API の 2 モード)
│   └── character-designer.md            # キャラクターデザイナー: キャラ設定・画像生成プロンプト
├── skills/
│   ├── studio/SKILL.md                  # メイン入口 (マネージャーの動作定義)
│   ├── debut/ song/ oneshot/ trend/ analyze/ meeting/ update-spec/ connect-youtube/
│   ├── songwriting/                     # 作詞ノウハウ資料集 (references/01〜08)
│   └── suno-spec/                       # Suno 仕様スナップショット (references/spec.md + update-log.md)
├── hooks/hooks.json                     # UserPromptSubmit + PreToolUse
└── scripts/
    ├── inject-manager-context.sh        # 毎ターン注入 (ペルソナ + アーティスト状況 + spec 鮮度)
    ├── block-startup-tools.sh           # 起動直後ターンのツール物理ブロック
    ├── validate_song.py                 # song.json の決定論的検証 (文字数・タグ構文)
    └── yt_analytics.py                  # YouTube Analytics API (auth / status / report)
```

## 各コンポーネントの役割

| コンポーネント | 役割 |
|---|---|
| `plugin.json` | name / description / version / author のみ。hooks・agents・skills はディレクトリ規約で自動発見 |
| `hooks/hooks.json` | UserPromptSubmit → inject-manager-context.sh / PreToolUse (Bash\|Read\|Grep\|Glob\|AskUserQuestion) → block-startup-tools.sh |
| `inject-manager-context.sh` | (1) `/…:studio` 単独ターンの判定マーカー作成 (2) 起動中は毎ターン、ペルソナ + artist.yaml 全文 + state.md + discography 要約 + suno-spec 実効パスと鮮度 + プラグインルート絶対パスを注入。artist.yaml が無ければ「未初期化 (debut 案内)」注入に切替 |
| `block-startup-tools.sh` | トリガーターンに Bash/Read/Grep/Glob/AskUserQuestion を exit 2 でブロック。AskUserQuestion は起動中 (ACTIVE がある間) つねにブロック |
| `agents/*.md` | 各職種のシステムプロンプト。Suno のバージョン固有事実は書かず、suno-spec 実効パスを読む規約 |
| `skills/*/SKILL.md` | スラッシュ起動 + マネージャーの Skill ツール自発起動の両対応 (単一実装・二経路) |
| `validate_song.py` | 文字数上限・メタタグ構文・必須フィールドを機械検査し、日本語レポートを stdout に返す |

## アーティストディレクトリ (プラグインが管理するデータ)

アーティストルートは **cwd から `artist.yaml` を上方探索** (HOME と / で停止) して決まる。見つからなければ cwd を未初期化アーティストとして扱う。

```
<artist-dir>/                            # 例: ~/Music/aoi-kanata/
├── artist.yaml                          # マスター定義 (ルートマーカー。hook が毎ターン全文注入するため 30〜40 行以内)
├── profile.md / world.md                # プロフィール / 世界観 (散文)
├── character/                           # キャラ設定 + イラストプロンプト
├── discography/
│   ├── discography.md                   # 一覧表 = 単一の真実源 (状態: 制作中 → 生成済 → 公開済)
│   └── songs/NNN_slug/                  # song.json (正) / paste.md (貼り付け用) / notes.md
├── analytics/                           # channels.yaml + reports/
├── strategy/                            # direction.md + trends/
└── .production/                         # プラグインの一時状態 (git 管理外推奨、自動で .gitignore に追記)
    ├── ACTIVE / state.md / log.md
```

設計思想: **作品・設定 = 可視ファイル (P の資産、git 管理推奨) / セッション状態 = `.production/` に隠す**。永続設定 (producer_name など) は artist.yaml 側に置くので `.production/` を消しても失われない。

## アーキテクチャメモ (開発者向け)

- **2 段階起動**: UserPromptSubmit フックが「コマンドのみのターン」を判定して `/tmp/suno-artist-production-trigger-<session>-<roothash>` マーカーを作成し、PreToolUse フックがそれを見て対象ツールを exit 2 で物理ブロックする。マーカーは session_id + アーティストルートで一意 (並列セッション安全)。60 分で自動掃除
- **毎ターン注入**: 起動中 (`.production/ACTIVE` あり) は、ペルソナ・artist.yaml 全文・state.md・discography 要約 (直近 5 件)・suno-spec 鮮度・プラグインルート絶対パスを注入する。サブエージェントはプラグインのパスを知らないため、マネージャーが Agent プロンプトに参照資料の絶対パスを必ず含める規約
- **suno-spec の 2 層構造**: 同梱版 `skills/suno-spec/references/spec.md` と上書き版 `${XDG_CONFIG_HOME:-~/.config}/suno-artist-production/suno-spec.md`。ヘッダの「調査日: YYYY-MM-DD」を比較して新しい方を実効とし、60 日超過で再調査 (`:update-spec`) を提案する。Suno のモデル名・文字数上限などのバージョン固有事実はコードやエージェント定義にハードコードしない (validate_song.py の上限定数のみ v1 の割り切りで、update-spec が不一致を警告する)
- **オリジナリティ 3 層ガード**: エージェント規則 (引用・実在名の禁止) / 作詞家の自己検査 (チェックリスト) / 機械 + Web 照合 (validate_song.py + リサーチャーの引用符付き検索)
- **YouTube 連携**: 既定は API キー不要の公開データモード。任意で `:connect-youtube` により Analytics API (OAuth) へ拡張。認証情報は `~/.config/suno-artist-production/` に保存 (アーティストディレクトリには置かない)。提案タイミングはライフサイクル規約 (studio SKILL.md) で制御し、`youtube.publish: false` の間は一切持ち出さない
- **CLAUDE_PLUGIN_ROOT**: hooks.json 内では `${CLAUDE_PLUGIN_ROOT}` 展開でスクリプトを指す。スクリプト内では環境変数が無い場合に備え、自身の位置 (`<plugin>/scripts/`) からプラグインルートを復元するフォールバック付き

## オリジナリティ照合の外部送信について (開示)

オリジナリティの最終チェックでは、生成した歌詞のサビ・フックの**特徴的な 2〜3 行**を引用符付きで**検索エンジンに送信**し、既存の歌詞サイト等にヒットしないかを確認する (偶然の一致・無意識の模倣を早期に見つけるため)。この挙動を知って選べるよう、ここに開示しておく。

- 送信されるのは**未発表の歌詞の一部**である点に留意 (外部の検索サービスに渡る)。既定は ON だが、`:song` / `:oneshot` フローで P が「急ぎで」「照合はスキップ」と指示すればスキップできる (その際はマネージャーが一言断る)
- 送るのは歌詞の一部のみ。チャンネル名・実在名などの個人情報は送らない
- 利用者名の自動解決で参照する `~/.claude.json` は**外部送信しない**。ローカルで `oauthAccount.displayName` だけを取り出して呼称に使い、ファイル全文の表示・ログ出力・コンテキスト注入もしない

## 開発メモ

- ユーザー向けテキスト・コメントは日本語で書く
- マネージャーは AskUserQuestion を使わない (テキストで質問)。ツールを使うターンは前置きテキストを書かない — company プラグインで実証済みの運用ルールを踏襲
- シェルスクリプトは `set -eu` + 全パス quoting (スペース入りパス対応)。変更時の検証:

```bash
bash -n scripts/inject-manager-context.sh scripts/block-startup-tools.sh
python3 -c "import json; json.load(open('.claude-plugin/plugin.json')); json.load(open('hooks/hooks.json'))"
```

- 参考実装: company プラグイン v3.3.0 (2 段階起動・コンテキスト注入・ツールブロックのパターン元)

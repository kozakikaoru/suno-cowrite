# 🎵 suno-artist-production plugin

Suno (suno.com) 用の **バーチャル音楽プロダクション** プラグイン。マネージャー (受付ペルソナ) が窓口になり、**7 職種のサブエージェント**にタスクを振り分けて、Suno 楽曲の企画・制作・分析を回します。主眼は **アーティストの継続プロデュース** (単曲だけのサクッと制作も可)。

**設計思想**: **1 ディレクトリ = 1 アーティスト**。世界観・キャラ・ディスコグラフィーを 1 つの作業ディレクトリに集約し、曲を重ねるほど文脈が育つ。**オリジナリティ厳守** — 実在曲の丸パクリや歌詞の引用はしない (参照資料は骨格だけを借りる 2 速度モデル)。出力は Suno Custom Mode の全設定値 — **Style / Lyrics プロンプト + 各種パラメータ** を「欄ごとに貼れる形式 + 機械可読 JSON」で渡す。

---

## 7 つのサブエージェント

窓口の **マネージャー** (女の子キャラ、一人称「私」、ずっと常駐) が、あなたの自然言語の依頼を読んで下の 7 職種へ自動で振り分けます:

| Subagent | 責務 | 発動タイミング |
|---|---|---|
| `director` (演出家) | 世界観設計 / コンセプトブリーフ / ディスコグラフィー物語 / ビジュアル方向 / 上位ネーミング | 「ブリーフ作って」「世界観を練りたい」「設定を深めたい」 |
| `composer` (作曲家) | Style / Exclude / Vocal / スライダー / モデル / Persona 判断、セクション演出タグ | 「サウンド設定決めて」「もっと激しく」「スライダーいくつ?」 |
| `lyricist` (作詞家) | 作詞 (作品版 + 入稿版の 2 表記) / 推敲 / オリジナリティ自己検査 | 「歌詞書いて」「サビ直して」「入稿版にして」 |
| `rapper` (客演ラッパー) | 韻の専門職 — 母音列分解・韻バンク納品 (完成歌詞は書かない客演) | 「韻重視で」「ラップ作り込みたい」「韻を強化して」 |
| `researcher` (リサーチャー) | 音楽トレンド調査 / Suno 仕様の再調査 / 歌詞の Web 照合 (すべて出典付き) | 「トレンド調べて」「仕様変わった?」「既存曲と被ってない?」 |
| `analyst` (アナリスト) | YouTube 数値レポート (前回比) と次の一手。公開データ / Analytics API の 2 モード | 「再生数どう?」「伸びてる?」「分析して」 |
| `character-designer` (キャラクターデザイナー) | キャラ設定 (外見 / 性格 / 口調 / NG) + イラスト生成プロンプト (英語) | 「立ち絵のプロンプト」「ジャケット用に」「キャラ設定変えたい」 |

**知識コンテナ**: 制作系エージェントは、動く前に専用のノウハウ資料 (`skills/`) を読みます:

- `lyricist` → **songwriting** (作詞ノウハウ 11 本: 構成 / フック / 韻律 / 感情曲線 / 言語別 / オリジナリティ / タイトル)
- `rapper` → **songwriting** の韻・HIPHOP 資料 (`09` 韻の上級技術 / `10` HIPHOP ジャンル)
- `composer` → **composing** (作曲ノウハウ 9 本: アレンジ / Style 組み立て + ジャンルプレイブック) + **suno-spec** の Style 語彙辞典 (`style-vocab`)
- `director` → **directing** (演出ノウハウ 5 本: 世界観 / コンセプト / 物語 / ビジュアル / ネーミング)

**構成**:
```
あなた
  ↓
🎧 マネージャー (女の子キャラ、一人称「私」、ずっと常駐)
  ↓ Agent ツールで振り分け (自動)
  ├─ 🎬 director           (演出家)
  ├─ 🎹 composer           (作曲家)
  ├─ ✍️ lyricist           (作詞家)
  ├─ 🎤 rapper             (客演ラッパー / feat.)
  ├─ 🔍 researcher         (リサーチャー)
  ├─ 📊 analyst            (アナリスト)
  └─ 🎨 character-designer (キャラクターデザイナー)
```

---

## インストール

Claude Code 内で以下を実行する:

```
/plugin marketplace add kozakikaoru/suno_artist_production
/plugin install suno-artist-production@suno-artist-marketplace
/reload-plugins
```

`/plugin list` で `suno-artist-production` が表示されればインストール完了。以後 `/suno-artist-production:studio` で起動できる。

ローカルで開発・検証する場合は次の起動も使える:

```bash
claude --plugin-dir /path/to/suno_artist_production
```

動作要件は Claude Code (プラグイン対応版) と bash / python3 (標準ライブラリのみ。hooks と検証スクリプトが使う)。git は任意。

---

## 使い方

### 起動

**`/suno-artist-production:studio`** で起動 (起動方法はこれのみ)。新しいアーティストを作るなら空ディレクトリで始めるのがおすすめ:

```
mkdir -p ~/Music/my-artist && cd ~/Music/my-artist
claude
> /suno-artist-production:studio        # ターン 1: マネージャーが状況付きで挨拶だけ返す
> 新しいアーティストをデビューさせたい      # ターン 2: ここから実処理 (debut フローへ)
```

以後は「新曲作りたい」「トレンド調べて」「再生数どう?」のように自然言語で話しかければ、マネージャーが適切なサブエージェント / スキルへ振り分ける。呼び名 (「〇〇P」) は質問せず自動判定する (`artist.yaml` の `producer_name` → アカウント表示名 → OS のフルネーム → git ユーザー名 → `$USER` の優先順)。「〇〇P に変えて」で更新できる。

### コマンド一覧

| コマンド | 用途 |
|---|---|
| `/suno-artist-production:studio` | 起動 (メイン入口)。2 段階起動、以後は自然言語で全ユースケース |
| `:debut` | アーティスト誕生 (世界観・キャラ・サウンドの初期セットアップ) |
| `:song` | 新曲制作 (ブリーフ → 作曲 / 作詞の並列 → 機械検証 → 入稿セット) |
| `:oneshot` | 単発曲制作 (アーティスト文脈なしの 1 曲。既定では保存しない) |
| `:trend` | トレンド調査 (出典付きで `strategy/trends/` に保存) |
| `:analyze` | YouTube 分析 (公開データ、API 接続済みなら Analytics API) |
| `:meeting` | 方針会議 (アナリスト + リサーチャー + 演出家の並列調査 → 方針決定) |
| `:update-spec` | Suno 仕様の再調査・更新 (上書き版 spec / style-vocab の生成) |
| `:connect-youtube` | YouTube Analytics API の OAuth 接続セットアップ (任意機能) |

`skills/songwriting/`・`skills/composing/`・`skills/directing/`・`skills/suno-spec/` はコマンドではなく **参照資料コンテナ** (各エージェントが読むノウハウ集で、SKILL.md は目次役)。

### 起動時の挙動 (2 段階起動)

**ターン 1** (`/suno-artist-production:studio` コマンドだけ): 挨拶テキストのみ、ツール使用ゼロ。hook が注入したアーティスト状況 (artist.yaml 要約・state.md・ディスコグラフィー件数) を使った「状況付き挨拶」を返す (`PreToolUse` フックが Bash/Read/Grep/Glob/AskUserQuestion を物理拒否)。

**ターン 2** (具体的な指示): scaffold が走って `.production/` を用意し、依頼の処理を始める。

### 制作フロー

1. **`:debut`** — ヒアリング → 演出家・キャラクターデザイナー・作曲家の並列提案 → あなたが選択 → アーティストディレクトリ一式を生成 → 1 曲目制作へ
2. **`:song`** — 演出家のコンセプトブリーフ → 作曲家・作詞家が並列制作 → `validate_song.py` で機械検証 → オリジナリティ照合 → `discography/songs/` に保存 → 入稿セット提示
3. **`:analyze` / `:meeting`** — 公開後の数値を見て次の一手を決める
4. 以降は曲を重ねるほど世界観とディスコグラフィーが育つ **継続プロデュース**

### 出力物 (Suno 入稿セット)

各曲で Suno Custom Mode の全設定値を 2 形式で渡す:

- **`paste.md`** — Title / Style of Music / Lyrics / Exclude Styles / スライダー (Weirdness・Style Influence) / Vocal Gender / モデル / Persona 運用を、**suno.com の欄ごとにそのまま貼れる**形式で
- **`song.json`** — 同じ内容の機械可読 JSON (`validate_song.py` が文字数上限・メタタグ構文を検証)

### アーティストディレクトリ (保存先)

アーティストルートは **cwd から `artist.yaml` を上方探索** (HOME と / で停止) して決まる。見つからなければ cwd を未初期化アーティストとして扱う:

```
<artist-dir>/                    # 例: ~/Music/my-artist/
├── artist.yaml                  # マスター定義 (ルートマーカー。hook が毎ターン全文注入するため 30〜40 行以内)
├── profile.md / world.md        # プロフィール / 世界観 (散文。world.md は演出家の管轄)
├── character/                   # character.md + illust-prompts/ (イラスト生成プロンプト)
├── discography/
│   ├── discography.md           # 一覧表 = 単一の真実源 (制作中 → 生成済 → 公開済)
│   └── songs/NNN_slug/          # song.json (正) / paste.md (貼り付け用) / notes.md
├── analytics/                   # channels.yaml + reports/
├── strategy/                    # direction.md + trends/ (+ boneyard.md / producer-taste.md)
└── .production/                 # プラグインの一時状態 (自動で .gitignore に追記)
    └── ACTIVE / state.md / log.md
```

**作品・設定 = 可視ファイル (あなたの資産、git 管理推奨) / セッション状態 = `.production/` に隠す**。永続設定 (`producer_name` など) は artist.yaml 側にあるので `.production/` を消しても失われない。

---

## オリジナリティ (開示)

歌詞の最終チェックで、生成したサビ・フックの**特徴的な 2〜3 行**を引用符付きで**検索エンジンに送信**し、既存の歌詞サイト等に一致がないか確認する (偶然の一致・無意識の模倣の早期検知)。

- 送信されるのは**未発表の歌詞の一部のみ**。チャンネル名・実在名などの個人情報は送らない
- 既定は ON。`:song` / `:oneshot` で「照合はスキップ」と指示すればスキップできる (マネージャーが一言断る)
- 呼び名の自動解決で参照する `~/.claude.json` は**外部送信しない** (表示名だけをローカルで使う)

---

## トラブルシューティング

### マネージャーが起動していない気がする

```bash
ls "$PWD/.production/ACTIVE"
```
無ければ未起動 → `/suno-artist-production:studio` で起動。

### hook がエラーで動かない

```bash
/path/to/suno_artist_production/scripts/inject-manager-context.sh
```
を直接実行。起動中なら注入コンテキストが出る。

### 手動でマネージャーモードを解除したい

```bash
rm -f "$PWD/.production/ACTIVE"
```

### Suno の仕様が古い気がする

`:update-spec` で再調査すると、ユーザー設定ディレクトリ側の上書き版 spec / style-vocab が更新される (同梱版は書き換えない)。調査日から一定期間が過ぎると起動時に鮮度警告が出る。

---

## カスタマイズ

### マネージャーの人格を変えたい

`skills/studio/SKILL.md` 冒頭の「マネージャーペルソナ」の記述を変更。

### サブエージェントを増やしたい

`agents/<新agent>.md` を追加。frontmatter の `description` に発動条件を書く。安易に増やさないこと (7 職種で構造化されているのが売り)。

### ノウハウ資料を足したい・直したい

`skills/songwriting/`・`skills/composing/`・`skills/directing/` の `references/` に資料を置き、各 `SKILL.md` (目次役) に読み方を追記する。Suno のバージョン固有事実は `skills/suno-spec/` に集約し、エージェント定義にはハードコードしない。

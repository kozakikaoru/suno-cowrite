# 🎵 suno-artist-production plugin

Suno (suno.com) 用の **単曲生成** プラグイン。マネージャー (受付ペルソナ) が窓口になり、**2 つの制作フロー**と **2 職種のサブエージェント** にタスクを振り分けて、Suno 楽曲を 1 曲ずつ企画・制作します。

**2 つの制作フロー**:

- **cowrite (対話共作・主役)** — テーマから**方向性 3 案 → 音のイメージ (style) → 構成 → 節ごとの歌詞**を、P と対話しながら 1 曲に育てる。各ターン 1 ステップ、P の OK で次へ。じっくり納得して作りたいとき
- **oneshot (高速)** — 簡易ブリーフ 1 発で制作エージェントが Style + 歌詞 + タイトルを一括制作。パッと 1 曲ほしいとき

**設計思想**: `artist.yaml` などの事前準備は要らない。**オリジナリティ厳守** — 実在曲の丸パクリや歌詞の引用はしない (参照資料は骨格だけを借りる 2 速度モデル)。出力は Suno Custom Mode の全設定値 — **Style / Lyrics プロンプト + 各種パラメータ** を「欄ごとに貼れる形式 + 機械可読 JSON」で渡す。

---

## 2 つのサブエージェント

窓口の **マネージャー** (女の子キャラ、一人称「私」、ずっと常駐) が、あなたの自然言語の依頼を読んで下の 2 職種へ自動で振り分けます:

| Subagent | 責務 | 発動タイミング |
|---|---|---|
| `songsmith` (制作) | **1 起動で Style + 歌詞 + 韻 + タイトルを一括制作** (旧・作曲家 + 作詞家 + 客演ラッパーの統合)。工程を絞った修正も担当 | 「この曲まるごと作って」「サビ直して」「スタイル変えて」「韻を強化して」 |
| `researcher` (リサーチャー) | Suno 仕様の再調査 (update-spec) / ライブラリ・技術動向調査 (すべて出典付き。調査専任) | 「仕様変わった?」「新モデル出た?」「Style に効く言葉を調べて」 |

**知識コンテナ**: `songsmith` は動く前に専用のノウハウ資料 (`skills/`) を読みます:

- `songsmith` → **production** の制作コア束ね (`write_core` = 作曲 02 + 作詞 01/05/06/07/08/11 を 1 Read に連結 / `rhyme_core` = 韻 03/09) + **suno-spec** の Style 語彙辞典 (`style-vocab`)。条件付きプレイブック (composing のジャンル資料 / songwriting の HIPHOP 資料) は該当曲でのみ個別に読む
- 原本ライブラリ **songwriting** (作詞) と **composing** (作曲) は制作コア束ねの供給元。束ねは `scripts/build_production_refs.py` が原本から生成する

**構成**:
```
あなた
  ↓
🎧 マネージャー (女の子キャラ、一人称「私」、ずっと常駐)
  ↓ Agent ツールで振り分け (自動)
  ├─ 🎛️ songsmith    (制作 = 作曲 + 作詞 + 韻 + タイトル)
  └─ 🔍 researcher   (リサーチャー = Suno 仕様の再調査ほか)
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

**`/suno-artist-production:studio`** で起動 (起動方法はこれのみ)。単曲制作用の作業ディレクトリで始めるのがおすすめ:

```
mkdir -p ~/Music/suno-songs && cd ~/Music/suno-songs
claude
> /suno-artist-production:studio        # ターン 1: マネージャーが状況付きで挨拶だけ返す
> 夏っぽい切ない曲を一緒に作りたい          # ターン 2: 「一緒に/じっくり」なら cowrite (主役) へ
> 夏っぽい切ない曲をパッと 1 曲            #          「パッと/サクッと」なら oneshot (高速) へ
```

以後は「一緒に作りたい」「1 曲作って」「サビ直して」「仕様変わった?」のように自然言語で話しかければ、マネージャーが適切なフロー / サブエージェント / スキルへ振り分ける (じっくり系は cowrite、急ぎ系は oneshot)。呼び名 (「〇〇P」) は質問せず自動判定する (`artist.yaml` の `producer_name` → アカウント表示名 → OS のフルネーム → git ユーザー名 → `$USER` の優先順)。

### コマンド一覧

| コマンド | 用途 |
|---|---|
| `/suno-artist-production:studio` | 起動 (メイン入口)。2 段階起動、以後は自然言語で全ユースケース |
| `:cowrite` | 対話共作 (主役)。テーマ → 方向性 3 案 → style → 構成 → 節ごとの歌詞 → 機械検証 → 入稿セット。対話状態は `.production/cowrite_<slug>.md` に保存 |
| `:oneshot` | 単発曲制作 (高速。簡易ブリーフ → 一括制作 → 機械検証 → 入稿セット。既定では保存しない) |
| `:update-spec` | Suno 仕様の再調査・更新 (上書き版 spec / style-vocab の生成) |

`skills/songwriting/`・`skills/composing/`・`skills/suno-spec/` はコマンドではなく **参照資料コンテナ** (`songsmith` が読むノウハウ集で、SKILL.md は目次役)。

### 起動時の挙動 (2 段階起動)

**ターン 1** (`/suno-artist-production:studio` コマンドだけ): 挨拶テキストのみ、ツール使用ゼロ。hook が注入した状況 (`.production/state.md`) を使った「状況付き挨拶」を返す (`PreToolUse` フックが Bash/Read/Grep/Glob/AskUserQuestion を物理拒否)。

**ターン 2** (具体的な指示): scaffold が走って `.production/` を用意し、依頼の処理を始める。

### 制作フロー

制作は温度で 2 フローに分かれる。**cowrite が主役、oneshot は高速モード**。どちらも最後は機械変換 (`build_submission_lyrics.py`) → 機械検証 (`validate_song.py`) → 入稿セット提示に合流する。

**cowrite (対話共作・主役)** — 「一緒に」「じっくり」作りたいとき:

1. **S0 受付** — テーマをふわっと受け取り、言語と尺だけ最小確認
2. **S1〜S2 方向性** — 情感の軸をずらした**方向性 3 案** (仮タイトル / コンセプト / 情感 / 情景 / サビの核 / 語り口) を提示 → P が「① で」「1 のサビ + 3 の情景で」のように番号・合成・加減で選ぶ → コンセプト確定
3. **S3 style** — 音のイメージを自然言語 (テンポは歩く速さの比喩) で伝え、裏に Suno の Style タグを畳んで提示 → OK で登録
4. **S4 構成** — セクション骨格を「何を書くか + 目安フレーズ数」付きで提示
5. **S5 節執筆ループ** — 「どこから作る?」(おすすめ = サビ) → 指定セクションだけ歌詞を当て「狙い」を添える → 違和感はそのセクションだけ直す (他は凍結) → 全セクション埋まるまで
6. **S6〜S7** — 全セクションを組み立て → 機械変換・検証 (PASS まで) → 入稿セット提示 → テイク報告・部分修正のループ

対話状態は `.production/cowrite_<slug>.md` (台帳) と同名 `.json` (正データ) に保存し、ターンを跨いで育てる。

**oneshot (高速)** — 「パッと 1 曲」のとき:

1. **依頼** — 「こういう曲がほしい」と伝えると、マネージャーが簡易ブリーフ (テーマ / 感情の流れ / 構成案 / コアモチーフ / Style 方向 / NG / 韻プロファイル) を書く
2. **一括制作** — 制作 (songsmith) が Style + 歌詞 + 韻 + タイトルを 1 起動でまとめて返す
3. **機械変換・検証** — `build_submission_lyrics.py` で入稿版歌詞を機械変換 → `validate_song.py` で文字数上限・メタタグ構文を検証
4. **提示** — suno.com Custom Mode に欄ごとに貼れる入稿セットをチャットに提示 (既定では保存せず、希望時のみ `./oneshot_<slug>.md` に保存)

### 出力物 (Suno 入稿セット)

各曲で Suno Custom Mode の全設定値を 2 形式で渡す:

- **貼り付けブロック** — Title / Style of Music / Lyrics / Exclude Styles / スライダー (Weirdness・Style Influence) / Vocal Gender / モデルを、**suno.com の欄ごとにそのまま貼れる** 形式で
- **`song.json`** — 同じ内容の機械可読 JSON (`validate_song.py` が文字数上限・メタタグ構文を検証)

### 作業ディレクトリ (保存先)

単曲制作では作業ディレクトリ直下に `.production/` (プラグインの一時状態) だけを置く。`artist.yaml` などの事前準備は不要:

```
<work-dir>/                       # 例: ~/Music/suno-songs/
├── .production/                  # プラグインの一時状態 (自動で .gitignore に追記)
│   ├── ACTIVE / state.md / log.md
│   ├── cowrite_<slug>.md         # cowrite: 対話状態の台帳
│   └── cowrite_<slug>.json       # cowrite: 正データ (song.json 形式)
└── oneshot_<slug>.md             # oneshot で保存を希望したときだけ (既定は未保存)
```

**セッション状態 = `.production/` に隠す / 成果物 (入稿セット) = チャット提示**。cowrite は対話をまたぐので台帳と正データを `.production/` に残し、oneshot は既定チャット提示のみ (希望時のみ保存)。

---

## オリジナリティ (開示)

オリジナリティは **2 段で担保**します (v0.5.0 で外部 Web 照合は廃止 — 歌詞を外部に送信しません)。

- **第 1 層 (制作エージェントの絶対規則)**: 実在曲を参考にしてよいが、歌詞原文・特徴的なメロディの直接流用は禁止。実在アーティスト名・曲名は本文 (Style / 歌詞 / タイトル) に書かない
- **第 2 層 (自己検査 + 機械検証)**: 制作エージェントが納品前に 3 観点 (フレーズ / 構造 / タイトル) で自己検査し、不安のある行は自分で書き直すか申告して P に握らせる。`validate_song.py` がタイトル完全一致リスクや Style 内の実在名らしき語を機械警告する
- **外部送信なし**: 歌詞・実在名を検索エンジンや外部 API に送りません。呼び名の自動解決で参照する `~/.claude.json` も**外部送信しない** (表示名だけをローカルで使う)

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

`agents/<新agent>.md` を追加。frontmatter の `description` に発動条件を書く。安易に増やさないこと (単曲生成に必要な 2 職種に絞ってあるのが売り)。

### ノウハウ資料を足したい・直したい

`skills/songwriting/`・`skills/composing/` の `references/` に資料を置き、各 `SKILL.md` (目次役) に読み方を追記する。制作コア束ね (`skills/production/references/`) は `scripts/build_production_refs.py` が原本から再生成する。Suno のバージョン固有事実は `skills/suno-spec/` に集約し、エージェント定義にはハードコードしない。
